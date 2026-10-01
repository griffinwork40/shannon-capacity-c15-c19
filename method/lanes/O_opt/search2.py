"""Lane O search v2: beam search over BPZ layered schedules, only BPZ's Lean tables / codes / sigma.

Grammar (all certifiable with Layered.lean w_multiSubst / le_indepNum_multiCode and Reindex.lean):
  R1, Rf (= sigma-reindexed base), S(c1..cq) for any S in Substitutions.lean,
  tail(y, S, p, z, J) = J-fold y <- S(..y at slot p.., z elsewhere), z over {R1, Rf}.
  Terminal: any code K in TerminalCodes.lean on (possibly different) children.
Every node tracks its Lean node count (distinct multiSubst nodes, tail of length J = J nodes),
so a node budget can be imposed (BPZ-sized certificates).

usage: python search2.py N WIDTH GENS EMAX MAXNODES OUTTAG
"""
import itertools
import json
import os
import sys
import time
from math import log, exp

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from certs import parse_cert, SUBS, CODES, SIGMA, BPZ  # noqa: E402
from lean_parse import LETTERS  # noqa: E402

IDX = {L: i for i, L in enumerate(LETTERS)}


def tens_sub(tab):
    q = len(next(w for ws in tab.values() for w in ws))
    T = np.zeros((7,) + (7,) * q)
    for a, ws in tab.items():
        for w in ws:
            T[(IDX[a],) + tuple(IDX[L] for L in w)] += 1
    return T


SUBT = {k: tens_sub(v) for k, v in SUBS.items()}
AR = {k: T.ndim - 1 for k, T in SUBT.items()}
CODEW = {k: np.array([[IDX[L] for L in w] for w in v]) for k, v in CODES.items()}
CODET = {}
for k, W in CODEW.items():
    T = np.zeros((7,) * W.shape[1])
    for w in W:
        T[tuple(w)] += 1
    CODET[k] = T

_ID = [0]


class Node:
    __slots__ = ("v", "L", "e", "expr", "pot", "potarg", "nodes", "id")

    def __init__(self, v, L, e, expr, nodes):
        s = float(v.max())
        self.v = v / s
        self.L = L + log(s)
        self.e = e
        self.expr = expr
        self.pot = None
        self.potarg = None
        self.nodes = nodes          # dict id -> Lean node count
        _ID[0] += 1
        self.id = _ID[0]

    def nn(self):
        return sum(self.nodes.values())


def contract(T, vecs):
    out = T
    for x in reversed(vecs):
        out = out @ x
    return out


def mk_sub(s, kids):
    nodes = {}
    for k in kids:
        nodes.update(k.nodes)
    nd = Node(contract(SUBT[s], [k.v for k in kids]), sum(k.L for k in kids), sum(k.e for k in kids),
              (s,) + tuple(k.expr for k in kids), nodes)
    nd.nodes = dict(nodes)
    nd.nodes[nd.id] = 1
    return nd


class Tail:
    def __init__(self, s, p, zs, zvec, Jmax, step):
        Mm = np.moveaxis(SUBT[s], p + 1, 1)
        for z in reversed(zs):
            Mm = Mm @ zvec[z]
        self.s, self.p, self.zs, self.q, self.step = s, p, zs, AR[s], step
        Js = list(range(0, Jmax + 1, step))
        P = np.empty((len(Js), 7, 7))
        lP = np.empty(len(Js))
        A, lA = np.eye(7), 0.0
        mx = np.abs(Mm).max()
        Ms = np.linalg.matrix_power(Mm / mx, step)
        lMs = step * log(mx)
        for i in range(len(Js)):
            P[i], lP[i] = A, lA
            A = Ms @ A
            m = np.abs(A).max()
            A /= m
            lA += lMs + log(m)
        self.Js, self.P, self.lP = np.array(Js), P, lP
        self.rho = max(abs(np.linalg.eigvals(Mm)))
        self.M1 = Mm

    def name(self):
        return f"{self.s}@{self.p}[{''.join(self.zs)}]"


def code_vals(Y, W):
    return Y[:, W].prod(axis=2).sum(axis=1)


class Searcher:
    def __init__(self, n, Emax, maxnodes, ntails=8, npts=500):
        self.c = parse_cert(n)
        self.n, self.d = n, self.c["d"]
        w0 = self.c["w0"]
        self.wv = np.array([w0[L] for L in LETTERS], float)
        self.sv = np.array([w0[SIGMA[L]] for L in LETTERS], float)
        self.R1 = Node(self.wv.copy(), 0.0, 1, "R1", {})
        self.Rf = Node(self.sv.copy(), 0.0, 1, "Rf", {})
        self.Emax, self.maxnodes = Emax, maxnodes
        Jcap = min(Emax, maxnodes)
        step = max(1, Jcap // npts)
        zvec = {"w": self.wv, "s": self.sv}
        tails = []
        for s in SUBT:
            q = AR[s]
            for p in range(q):
                for zs in itertools.product("ws", repeat=q - 1):
                    t = Tail(s, p, zs, zvec, Jcap, step)
                    if t.rho > 0:
                        tails.append((log(t.rho) / (q - 1), t))
        tails.sort(key=lambda z: -z[0])
        self.tails = [t for _, t in tails[:ntails]]
        self.coarse = max(1, len(self.tails[0].Js) // 25)

    def potential(self, nd, coarse=False):
        best, arg = -1e9, None
        for k, W in CODEW.items():
            r = W.shape[1]
            if r * nd.e > self.Emax:
                continue
            val = code_vals(nd.v[None, :], W)[0]
            rate = (log(val) + r * nd.L) / (self.d * r * nd.e)
            if rate > best:
                best, arg = rate, (k, None, 0)
        nn = nd.nn()
        sl = slice(None, None, self.coarse) if coarse else slice(None)
        for ti, t in enumerate(self.tails):
            Js = t.Js[sl]
            Y = t.P[sl] @ nd.v
            sc = Y.max(axis=1)
            Y = Y / sc[:, None]
            lsc = np.log(sc) + t.lP[sl] + nd.L
            Es = nd.e + Js * (t.q - 1)
            okn = nn + Js <= self.maxnodes
            for k, W in CODEW.items():
                r = W.shape[1]
                ok = okn & (r * Es <= self.Emax)
                if not ok.any():
                    continue
                vals = code_vals(Y, W)
                with np.errstate(divide="ignore"):
                    rates = (np.log(vals) + r * lsc) / (self.d * r * Es)
                rates[~ok] = -1e9
                i = int(np.argmax(rates))
                if rates[i] > best:
                    best, arg = float(rates[i]), (k, ti, int(Js[i]))
        nd.pot, nd.potarg = best, arg
        return best

    def tail_node(self, nd, ti, J):
        t = self.tails[ti]
        i = J // t.step
        y = t.P[i] @ nd.v
        m = Node(y, nd.L + t.lP[i], nd.e + J * (t.q - 1), ("tail", nd.expr, t.s, t.p, "".join(t.zs), J),
                 dict(nd.nodes))
        m.nodes[m.id] = J
        return m

    def mixed_terminal(self, nodes):
        """Best code over heterogeneous children drawn from `nodes` (respecting Emax, maxnodes)."""
        V = np.array([x.v for x in nodes])
        Ls = np.array([x.L for x in nodes])
        Es = np.array([x.e for x in nodes], float)
        best, arg = -1e9, None
        K = len(nodes)
        for k, T in CODET.items():
            r = T.ndim
            out = T
            for _ in range(r):
                out = np.tensordot(out, V, axes=([0], [1]))   # contracts first axis, appends child axis
            # out axes now (child_1..child_r) in order
            grids = np.meshgrid(*([np.arange(K)] * r), indexing="ij")
            Ltot = sum(Ls[g] for g in grids)
            Etot = sum(Es[g] for g in grids)
            with np.errstate(divide="ignore"):
                rate = (np.log(out) + Ltot) / (self.d * Etot)
            rate[Etot > self.Emax] = -1e9
            # node budget: approximate check after selection
            flat = np.argsort(rate, axis=None)[::-1][:50]
            for f in flat:
                idx = np.unravel_index(f, rate.shape)
                nodes_u = {}
                for i in idx:
                    nodes_u.update(nodes[i].nodes)
                if sum(nodes_u.values()) <= self.maxnodes:
                    if rate[idx] > best:
                        best, arg = float(rate[idx]), (k, [nodes[i] for i in idx])
                    break
        return best, arg

    def run(self, width, gens, seeds, logf, tlimit, init=None):
        T0 = time.time()
        pool = [self.R1, self.Rf] + list(seeds)
        for nd in pool:
            self.potential(nd)
        top = max(pool, key=lambda z: z.pot)
        best = (top.pot, ("copies", top))
        if init is not None and init[0] > best[0]:
            best = init
        for g in range(gens):
            t0 = time.time()
            cand = []
            for s, q in AR.items():
                for kids in itertools.product(pool, repeat=q):
                    if sum(k.e for k in kids) > self.Emax:
                        continue
                    nd = mk_sub(s, kids)
                    if nd.nn() > self.maxnodes:
                        continue
                    self.potential(nd, coarse=True)
                    cand.append(nd)
            cand.sort(key=lambda z: -z.pot)
            cand = cand[:max(250, 4 * width)]
            for nd in cand:
                self.potential(nd)
            cand.sort(key=lambda z: -z.pot)
            ext = []
            for nd in cand[:8]:
                k, ti, J = nd.potarg
                if ti is not None and J > 0:
                    for frac in (1.0, 0.5, 0.25):
                        JJ = int(J * frac) // self.tails[ti].step * self.tails[ti].step
                        if JJ > 0:
                            m = self.tail_node(nd, ti, JJ)
                            self.potential(m)
                            ext.append(m)
            cand += ext
            cand.sort(key=lambda z: -z.pot)
            if cand and cand[0].pot > best[0]:
                best = (cand[0].pot, ("copies", cand[0]))
            newpool, seen, exps = [self.R1, self.Rf], set(), set()
            for nd in cand:
                key = (nd.e, round(nd.pot, 12))
                if key in seen or nd.e in exps:
                    continue
                seen.add(key)
                exps.add(nd.e)
                newpool.append(nd)
                if len(newpool) >= 2 + width // 2:
                    break
            for nd in cand:
                key = (nd.e, round(nd.pot, 12))
                if key in seen:
                    continue
                seen.add(key)
                newpool.append(nd)
                if len(newpool) >= width:
                    break
            for sd in list(seeds) + [best[1][1]] if best[1][0] == "copies" else list(seeds):
                if sd not in newpool:
                    newpool.append(sd)
            pool = newpool
            # mixed terminal over pool + their tail-extended versions
            mt = list(pool) + [m for m in ext[:6]]
            mt = mt[:18]
            r, arg = self.mixed_terminal(mt)
            if r > best[0]:
                best = (r, ("mixed", arg))
            msg = f"C{self.n} gen {g}: {len(cand)} kept, best {exp(best[0]):.13f} kind {best[1][0]} ({time.time()-t0:.1f}s)"
            print(msg, flush=True)
            with open(logf, "a") as f:
                f.write(json.dumps(dict(gen=g, rate=exp(best[0]), kind=best[1][0])) + "\n")
            if time.time() - T0 > tlimit:
                print("time limit", flush=True)
                break
        return best

    def to_sched(self, best):
        kind, obj = best[1]
        if kind == "copies":
            k, ti, J = obj.potarg
            node = obj if ti is None or J == 0 else self.tail_node(obj, ti, J)
            r = CODEW[k].shape[1]
            return dict(n=self.n, code=k, terminal=[node.expr] * r, float_rate=exp(best[0]))
        k, kids = obj
        return dict(n=self.n, code=k, terminal=[x.expr for x in kids], float_rate=exp(best[0]))


def seed_nodes(S):
    c = S.c
    vals = {"R1": S.R1, "Rf": S.Rf}
    for nd in c["nodes"]:
        vals[nd["name"]] = mk_sub(nd["subst"], [vals[k] for k in nd["kids"]])
    return vals


if __name__ == "__main__":
    n, width, gens, Emax, maxnodes = map(int, sys.argv[1:6])
    tag = sys.argv[6]
    tlimit = float(sys.argv[7]) if len(sys.argv) > 7 else 600
    S = Searcher(n, Emax, maxnodes)
    print(f"C{n}: BPZ {BPZ[n]}; Emax {Emax} maxnodes {maxnodes}; tails:",
          [(t.name(), round(exp(log(t.rho) / (t.q - 1) / S.d), 9)) for t in S.tails], flush=True)
    sv = seed_nodes(S)
    tk = [sv[k] for k in S.c["terminal_kids"]]
    r, arg = S.mixed_terminal(list(dict.fromkeys(tk)))
    print(f"float control (BPZ terminal children): {exp(r):.15f}", flush=True)
    seeds = [sv[k] for k in sv if k not in ("R1", "Rf")]
    for sd in seeds:
        S.potential(sd)
    seeds.sort(key=lambda z: -z.pot)
    seeds = list(dict.fromkeys(seeds[:4] + tk))
    init = (r, ("mixed", arg)) if (arg is not None and len(tk) == len(arg[1])) else None
    best = S.run(width, gens, seeds, os.path.join(HERE, "logs", f"{tag}.jsonl"), tlimit, init=init)
    sched = S.to_sched(best)
    out = os.path.join(HERE, f"best_{tag}.json")
    json.dump(sched, open(out, "w"))
    print("FINAL", n, exp(best[0]), "wrote", out, flush=True)
