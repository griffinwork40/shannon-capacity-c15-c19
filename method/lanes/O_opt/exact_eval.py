"""Lane O: exact (Python int) evaluation + DAG serialisation + local refinement of a schedule.

A schedule is a JSON object {"n": N, "code": "K4b", "terminal": [expr, expr, ...]} where expr is
  "R1" | "Rf" | [S, expr, ..., expr] | ["tail", expr, S, p, zs, J]
("tail" = J-fold y <- S(... y at slot p ..., z elsewhere), zs a string over w=R1, s=Rf).
The exact evaluator re-checks admissibility of every used table and the pairwise separation of
the code against Letter.sep (PortRealisation.lean), as G's recursion.py does.

usage: python exact_eval.py schedule.json [--refine]
"""
import json
import os
import sys
import time
from math import log, exp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.set_int_max_str_digits(0)
from certs import parse_cert, SUBS, CODES, SIGMA, BPZ, apply_sub, apply_code, root_decimal  # noqa: E402
from lean_parse import LETTERS  # noqa: E402
from recursion import check_admissible, check_code  # noqa: E402


def to_t(x):
    return tuple(to_t(y) for y in x) if isinstance(x, list) else x


def used(expr, subs):
    if isinstance(expr, tuple):
        if expr[0] == "tail":
            subs.add(expr[2])
            used(expr[1], subs)
        else:
            subs.add(expr[0])
            for k in expr[1:]:
                used(k, subs)


def evaluate(sched, exact=True):
    """Returns (M or log M, E_total) for exact=True (int) / False (float log)."""
    c = parse_cert(sched["n"])
    w0 = c["w0"]
    if exact:
        base = {"R1": (dict(w0), 1), "Rf": ({L: w0[SIGMA[L]] for L in LETTERS}, 1)}
    else:
        import numpy as np
        base = {"R1": (np.array([float(w0[L]) for L in LETTERS]), 0.0, 1),
                "Rf": (np.array([float(w0[SIGMA[L]]) for L in LETTERS]), 0.0, 1)}
    memo = {}
    nodes = [0]

    def ev(x):
        if x in base:
            return base[x]
        if x in memo:
            return memo[x]
        if x[0] == "tail":
            _, y, s, p, zs, J = x
            v = ev(y)
            zz = [base["R1" if ch == "w" else "Rf"] for ch in zs]
            for _ in range(J):
                kids = zz[:p] + [v] + zz[p:]
                v = comb(s, kids)
                nodes[0] += 1
        else:
            v = comb(x[0], [ev(k) for k in x[1:]])
            nodes[0] += 1
        memo[x] = v
        return v

    def comb(s, kids):
        if exact:
            return apply_sub(SUBS[s], [k[0] for k in kids]), sum(k[1] for k in kids)
        from search import SUBT, contract
        out = contract(SUBT[s], [k[0] for k in kids])
        m = float(out.max())
        return out / m, sum(k[1] for k in kids) + log(m), sum(k[2] for k in kids)

    kids = [ev(to_t(x)) for x in sched["terminal"]]
    words = CODES[sched["code"]]
    if exact:
        return apply_code(words, [k[0] for k in kids]), sum(k[1] for k in kids), nodes[0], c["d"]
    tot = 0.0
    for w in words:
        pr = 1.0
        for i, L in enumerate(w):
            pr *= kids[i][0][LETTERS.index(L)]
        tot += pr
    return log(tot) + sum(k[1] for k in kids), sum(k[2] for k in kids), nodes[0], c["d"]


def float_rate(sched):
    lg, E, _, d = evaluate(sched, exact=False)
    return lg / (d * E)


def tails_in(expr, path=()):
    """Yield paths to every tail J in a nested list expr."""
    if isinstance(expr, list):
        if expr and expr[0] == "tail":
            yield path
            yield from tails_in(expr[1], path + (1,))
        else:
            for i, k in enumerate(expr[1:], 1):
                yield from tails_in(k, path + (i,))


def get_set(expr, path, val=None):
    x = expr
    for i in path:
        x = x[i]
    if val is None:
        return x[5]
    x[5] = val


def n_nodes(sched):
    return evaluate(sched, exact=False)[2]


def refine(sched, rounds=6, steps=(16, 8, 4, 2, 1), maxnodes=None):
    """Coordinate descent on every tail length J (float), terminal-child choice kept.
    maxnodes: optional cap on the number of Lean multiSubst nodes (tail of length J = J nodes)."""
    best = float_rate(sched)
    for st in steps:
        improved = True
        it = 0
        while improved and it < rounds * 10:
            improved = False
            it += 1
            for ti, term in enumerate(sched["terminal"]):
                for path in list(tails_in(term)):
                    J = get_set(term, path)
                    for dJ in (st, -st):
                        if J + dJ < 0:
                            continue
                        get_set(term, path, J + dJ)
                        r = float_rate(sched)
                        if maxnodes is not None and dJ > 0 and n_nodes(sched) > maxnodes:
                            r = -1e9
                        if r > best + 1e-16:
                            best, J, improved = r, J + dJ, True
                        else:
                            get_set(term, path, J)
    return exp(best)


def dag_lines(sched):
    """Readable DAG listing with shared nodes named once."""
    names = {}
    lines = []

    def nm(x):
        if x in ("R1", "Rf"):
            return x
        if x in names:
            return names[x]
        if x[0] == "tail":
            inner = nm(x[1])
            _, _, s, p, zs, J = x
            slots = ["y"] * 0
            z = ["R1" if ch == "w" else "Rf" for ch in zs]
            args = z[:p] + ["y"] + z[p:]
            k = f"t{len(names)}"
            lines.append(f"{k} = {J} x [y <- {s}({', '.join(args)})] starting at y = {inner}")
        else:
            args = [nm(c) for c in x[1:]]
            k = f"n{len(names)}"
            lines.append(f"{k} = {x[0]}({', '.join(args)})")
        names[x] = k
        return k

    term = [nm(to_t(x)) for x in sched["terminal"]]
    lines.append(f"M = {sched['code']}({', '.join(term)})")
    return lines


def report(sched, verbose=True):
    subs = set()
    for x in sched["terminal"]:
        used(to_t(x), subs)
    for s in subs:
        check_admissible(SUBS[s])
    check_code(CODES[sched["code"]])
    t0 = time.time()
    M, E, nnodes, d = evaluate(sched, exact=True)
    dim = d * E
    dec = root_decimal(M, dim, 18)
    n = sched["n"]
    a = int(BPZ[n].replace(".", ""))
    beats = (a + 1) ** dim <= M * 10 ** (15 * dim)   # exact: M^(1/dim) >= BPZ + 1e-15
    out = dict(n=n, value=dec, dim=dim, E=E, base_d=d, digits=len(str(M)), lean_nodes=nnodes,
               beats_bpz_exact=beats, bpz=BPZ[n], secs=round(time.time() - t0, 1))
    if verbose:
        for ln in dag_lines(sched):
            print("  " + ln)
        print(json.dumps(out))
    return out, M


if __name__ == "__main__":
    sched = json.load(open(sys.argv[1]))
    mx = None
    for a in sys.argv:
        if a.startswith("--maxnodes="):
            mx = int(a.split("=")[1])
    if "--refine" in sys.argv:
        print("float before", exp(float_rate(sched)), "nodes", n_nodes(sched))
        r = refine(sched, maxnodes=mx)
        print("float after refine", r)
        json.dump(sched, open(sys.argv[1].replace(".json", "_ref.json"), "w"))
    report(sched)
