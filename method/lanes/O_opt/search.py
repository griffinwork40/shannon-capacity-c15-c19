"""Lane O: beam search over BPZ layered schedules (only BPZ's Lean tables/codes/reindex).

Node grammar (every node is certifiable by Layered.lean's w_multiSubst with heterogeneous children,
and Reindex.lean's sigma reindexing of the base):
   R1            base realisation (exponent 1)
   Rf            sigma-reindexed base (A<->D, H<->V), same graph, exponent 1   (used by CertC7)
   S(c1..cq)     any table S in Substitutions.lean with children from the pool (exponent = sum)
   tail(y,S,p,z,J)  J-fold y <- S(..y at slot p.., z elsewhere), z a string over {w=R1, s=Rf}
Terminal: any code K in TerminalCodes.lean on r copies of a (tail-extended) node; refinement
also tries mixed terminal children.
Scores are log-scaled floats; the winner is re-evaluated exactly by exact_eval.py.

usage: python search.py N [width] [gens] [Emax] [seed_cert(0/1)]
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


class Node:
    __slots__ = ("v", "L", "e", "expr", "pot", "potarg")

    def __init__(self, v, L, e, expr):
        s = float(v.max())
        self.v = v / s
        self.L = L + log(s)
        self.e = e
        self.expr = expr
        self.pot = None
        self.potarg = None


def contract(T, vecs):
    out = T
    for x in reversed(vecs):
        out = out @ x
    return out


def mk_sub(s, kids):
    return Node(contract(SUBT[s], [k.v for k in kids]), sum(k.L for k in kids), sum(k.e for k in kids),
                (s,) + tuple(k.expr for k in kids))


class Tail:
    """y -> S(.., y at slot p, ..) with base vectors z elsewhere; precomputed normalized powers."""

    def __init__(self, s, p, zs, zvec, Jmax, step):
        T = SUBT[s]
        q = AR[s]
        Mm = np.moveaxis(T, p + 1, 1)
        for z in reversed(zs):
            Mm = Mm @ zvec[z]
        # Mm[a, y]
        self.M = Mm
        self.s, self.p, self.zs, self.q = s, p, zs, q
        self.step = step
        Js = list(range(0, Jmax + 1, step))
        P = np.empty((len(Js), 7, 7))
        lP = np.empty(len(Js))
        A = np.eye(7)
        lA = 0.0
        Ms = np.linalg.matrix_power(Mm / np.abs(Mm).max(), step)
        lMs = step * log(np.abs(Mm).max())
        for i in range(len(Js)):
            P[i] = A
            lP[i] = lA
            A = Ms @ A
            m = np.abs(A).max()
            A /= m
            lA += lMs + log(m)
        self.Js = np.array(Js)
        self.P, self.lP = P, lP
        self.rho = max(abs(np.linalg.eigvals(Mm)))

    def name(self):
        return f"{self.s}@{self.p}[{''.join(self.zs)}]"


def code_vals(Y, W):
    """Y: (G,7) nonneg rows; returns sum_w prod_i Y[:, w_i]."""
    return Y[:, W].prod(axis=2).sum(axis=1)


class Searcher:
    def __init__(self, n, Jmax=1500, step=5, ntails=8, Emax=4000):
        self.c = parse_cert(n)
        self.n, self.d = n, self.c["d"]
        w0 = self.c["w0"]
        self.wv = np.array([w0[L] for L in LETTERS], float)
        self.sv = np.array([w0[SIGMA[L]] for L in LETTERS], float)
        self.R1 = Node(self.wv.copy(), 0.0, 1, "R1")
        self.Rf = Node(self.sv.copy(), 0.0, 1, "Rf")
        zvec = {"w": self.wv, "s": self.sv}
        tails = []
        for s in SUBT:
            q = AR[s]
            for p in range(q):
                for zs in itertools.product("ws", repeat=q - 1):
                    try:
                        t = Tail(s, p, zs, zvec, Jmax, step)
                    except Exception:
                        continue
                    if t.rho > 0:
                        tails.append((log(t.rho) / (q - 1), t))
        tails.sort(key=lambda z: -z[0])
        # keep the top ntails distinct (s,p) by asymptotic rate, z preferring 'ww'
        self.tails = [t for _, t in tails[:ntails]]
        self.Emax = Emax

    def term_rate_node(self, nd):
        best = -1e9
        arg = None
        for k, W in CODEW.items():
            r = W.shape[1]
            val = code_vals(nd.v[None, :], W)[0]
            rate = (log(val) + r * nd.L) / (self.d * r * nd.e)
            if rate > best:
                best, arg = rate, (k, None, 0)
        return best, arg

    def potential(self, nd):
        best, arg = self.term_rate_node(nd)
        for ti, t in enumerate(self.tails):
            Y = t.P @ nd.v                      # (G,7)
            sc = Y.max(axis=1)
            Y = Y / sc[:, None]
            lsc = np.log(sc) + t.lP + nd.L
            Es = nd.e + t.Js * (t.q - 1)
            ok = Es <= self.Emax
            if not ok.any():
                continue
            for k, W in CODEW.items():
                r = W.shape[1]
                vals = code_vals(Y, W)
                with np.errstate(divide="ignore"):
                    rates = (np.log(vals) + r * lsc) / (self.d * r * Es)
                rates[~ok] = -1e9
                i = int(np.argmax(rates))
                if rates[i] > best:
                    best, arg = float(rates[i]), (k, ti, int(t.Js[i]))
        nd.pot, nd.potarg = best, arg
        return best

    def tail_node(self, nd, ti, J):
        t = self.tails[ti]
        i = J // t.step
        y = t.P[i] @ nd.v
        return Node(y, nd.L + t.lP[i], nd.e + J * (t.q - 1), ("tail", nd.expr, t.s, t.p, "".join(t.zs), J))

    def run(self, width=14, gens=7, seeds=(), log_f=None):
        pool = [self.R1, self.Rf] + list(seeds)
        for nd in pool:
            self.potential(nd)
        best = max(pool, key=lambda z: z.pot)
        hist = []
        for g in range(gens):
            t0 = time.time()
            cand = []
            for s, q in AR.items():
                for kids in itertools.product(pool, repeat=q):
                    e = sum(k.e for k in kids)
                    if e > self.Emax:
                        continue
                    nd = mk_sub(s, kids)
                    self.potential(nd)
                    cand.append(nd)
            # tail-extended versions of the top candidates become pool members too
            cand.sort(key=lambda z: -z.pot)
            ext = []
            for nd in cand[:6]:
                k, ti, J = nd.potarg
                if ti is not None and J > 0:
                    for frac in (1.0, 0.5):
                        JJ = int(J * frac) // self.tails[ti].step * self.tails[ti].step
                        if JJ > 0:
                            m = self.tail_node(nd, ti, JJ)
                            self.potential(m)
                            ext.append(m)
            cand += ext
            cand.sort(key=lambda z: -z.pot)
            if cand and cand[0].pot > best.pot:
                best = cand[0]
            newpool, seen, exps = [self.R1, self.Rf], set(), set()
            for nd in cand:                       # first pass: distinct exponents
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
            # keep the best ever-seen node too (elitism) and the seeds
            for sd in [best] + list(seeds):
                if sd not in newpool:
                    newpool.append(sd)
            pool = newpool
            msg = (f"C{self.n} gen {g}: {len(cand)} cand, best pot {exp(best.pot):.13f} "
                   f"arg {best.potarg} e={best.e}  ({time.time()-t0:.1f}s)")
            print(msg, flush=True)
            hist.append(dict(gen=g, rate=exp(best.pot), arg=best.potarg, e=best.e, expr=best.expr))
            if log_f:
                with open(log_f, "a") as f:
                    f.write(json.dumps(dict(n=self.n, gen=g, rate=exp(best.pot), potarg=best.potarg,
                                            tail=self.tails[best.potarg[1]].name() if best.potarg[1] is not None else None,
                                            e=best.e, expr=best.expr)) + "\n")
        return best, hist


def cert_seed_nodes(S):
    """Float nodes for every node of BPZ's own certificate (lets the beam extend BPZ's DAG)."""
    c = S.c
    vals = {"R1": S.R1, "Rf": S.Rf}
    for nd in c["nodes"]:
        vals[nd["name"]] = mk_sub(nd["subst"], [vals[k] for k in nd["kids"]])
    return vals


if __name__ == "__main__":
    n = int(sys.argv[1])
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    gens = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    Emax = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
    useseed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    step = max(1, Emax // 600)
    S = Searcher(n, Jmax=Emax, step=step, Emax=Emax)
    print(f"C{n}: BPZ {BPZ[n]}; tails:", [(t.name(), round(exp(log(t.rho) / (t.q - 1) / S.d), 9)) for t in S.tails])
    seeds = []
    if useseed:
        sv = cert_seed_nodes(S)
        seeds = [sv[k] for k in sv if k not in ("R1", "Rf")]
        # positive control in float
        kids = [sv[k] for k in S.c["terminal_kids"]]
        W = CODEW[S.c["terminal"]]
        lg = 0.0
        tot = 0.0
        for w in W:
            pr = 1.0
            for i, L in enumerate(w):
                pr *= kids[i].v[L]
            tot += pr
        lg = log(tot) + sum(k.L for k in kids)
        E = sum(k.e for k in kids)
        print(f"float control: BPZ cert rate {exp(lg/(S.d*E)):.15f}", flush=True)
        # keep only the larger seeds (top by potential) to bound the pool
        for sd in seeds:
            S.potential(sd)
        seeds.sort(key=lambda z: -z.pot)
        seeds = seeds[:4]
    best, hist = S.run(width=width, gens=gens, seeds=seeds, log_f=os.path.join(HERE, f"search_C{n}_E{Emax}_w{width}.jsonl"))
    print("FINAL", n, exp(best.pot), best.potarg, best.e)
    k, ti, J = best.potarg
    node = best if ti is None or J == 0 else S.tail_node(best, ti, J)
    r = CODEW[k].shape[1]
    sched = dict(n=n, code=k, terminal=[node.expr] * r, float_rate=exp(best.pot))
    out = sys.argv[6] if len(sys.argv) > 6 else os.path.join(HERE, f"best_C{n}_E{Emax}_w{width}.json")
    json.dump(sched, open(out, "w"))
    print("wrote", out)
