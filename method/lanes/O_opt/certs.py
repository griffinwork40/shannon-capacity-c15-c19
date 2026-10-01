"""Lane O: generic parser + exact evaluator for BPZ CertC{n}.lean schedules (n in 7,11,13,15,19,23).

Parses (from the Lean text, no Lean needed):
  substitution aliases (abbrev X : Subst ... := Substitutions.S..), terminal code alias,
  w0 (and w0f = sigma-reindexed base, C7 only), every node R<name> = multiSubst e<name> (ch<name> R) X
  with its children, every intermediate literal w<name>, the terminal children, M, and the base
  dimension d from CapCertC{n}.lean (strongPower_mul_iso BaseCn.Cycn d E).
Evaluates exactly with Python ints and checks every intermediate literal and M.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "verifier"))
sys.set_int_max_str_digits(0)
from lean_parse import LETTERS, REPO, substitutions, terminal_codes  # noqa: E402

SUBS = substitutions()
CODES = terminal_codes()
SIGMA = dict(B="B", N="N", A="D", D="A", O="O", H="V", V="H")
BPZ = {7: "3.258827985920007", 11: "5.295492315784620", 13: "6.302926729310108",
       15: "7.301628695930103", 19: "9.357200030000796", 23: "11.334557922754518"}


def _read(name):
    with open(os.path.join(REPO, name)) as f:
        return f.read()


def wblock(t, name):
    m = re.search(r"def " + name + r" : Letter → Nat\n(.*?)\n\n", t, re.S)
    if not m:
        return None
    return {L: int(v) for L, v in re.findall(r"\| \.?([BNADOHV]) => (\d+)", m.group(1))}


def parse_cert(n):
    t = _read(f"CertC{n}.lean")
    alias = dict(re.findall(r"abbrev (\w+) : Subst Letter Letter\.sep \d := Substitutions\.(S\d[a-h])", t))
    term = re.search(r"abbrev K : Code Letter Letter\.sep \d := TerminalCodes\.(K\d[a-z])", t).group(1)
    w0 = wblock(t, "w0")
    w0f = wblock(t, "w0f")
    nodes = []
    for m in re.finditer(r"def R(\w+) \(R : Realisation Letter Letter\.sep G\) :\n\s*Realisation Letter "
                         r"Letter\.sep \(SimpleGraph\.strongPower G (\d+)\) :=\n\s*Realisation\.multiSubst "
                         r"e\w+ \(ch(\w+) R\) (\w+)", t):
        name, exp, chname, sub = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        ch = re.search(r"def ch" + chname + r" .*?:=\n\s*(Fin\.cases.*?)\n", t, re.S).group(1)
        kids = re.findall(r"(R\w+) R\b", ch)
        nodes.append(dict(name="R" + name, kids=kids, subst=alias[sub], exp=exp, w=wblock(t, "w" + name)))
    tch = re.search(r"def terminalChildren .*?:=\n\s*(Fin\.cases.*?)\n", t, re.S).group(1)
    tkids = re.findall(r"(R\w+) R\b", tch)
    M = int(re.search(r"def M : Nat :=\s*(\d+)", t).group(1))
    E = int(re.search(r"M ≤ \(SimpleGraph\.strongPower G (\d+)\)\.indepNum", t).group(1))
    cap = _read(f"CapCertC{n}.lean")
    d, E2 = map(int, re.search(r"strongPower_mul_iso BaseC\d+\.Cyc\d+ (\d+) (\d+)", cap).groups())
    assert E == E2
    return dict(n=n, alias=alias, terminal=term, w0=w0, w0f=w0f, nodes=nodes, terminal_kids=tkids,
                M=M, E=E, d=d)


def apply_sub(tab, vecs):
    out = {}
    for a in LETTERS:
        s = 0
        for x in tab[a]:
            pr = 1
            for i, L in enumerate(x):
                pr *= vecs[i][L]
            s += pr
        out[a] = s
    return out


def apply_code(words, vecs):
    s = 0
    for x in words:
        pr = 1
        for i, L in enumerate(x):
            pr *= vecs[i][L]
        s += pr
    return s


def base_vals(c):
    vals = {"R1": (c["w0"], 1)}
    vals["Rf"] = ({L: c["w0"][SIGMA[L]] for L in LETTERS}, 1)
    if c["w0f"] is not None:
        assert vals["Rf"][0] == c["w0f"]
    return vals


def run(c, check=True):
    vals = base_vals(c)
    for nd in c["nodes"]:
        kids = [vals[k] for k in nd["kids"]]
        w = apply_sub(SUBS[nd["subst"]], [k[0] for k in kids])
        e = sum(k[1] for k in kids)
        if check:
            assert e == nd["exp"], (nd["name"], e, nd["exp"])
            assert w == nd["w"], ("size mismatch", nd["name"])
        vals[nd["name"]] = (w, e)
    kids = [vals[k] for k in c["terminal_kids"]]
    M = apply_code(CODES[c["terminal"]], [k[0] for k in kids])
    E = sum(k[1] for k in kids)
    return M, E


def root_decimal(M, D, digits=18):
    scale = 10 ** digits
    # Newton-free bisection seeded from float estimate
    from math import log, exp
    k = max(M.bit_length() - 60, 0)
    est = exp((log(M >> k) + k * log(2)) / D) * scale
    lo, hi = int(est * (1 - 1e-12)) - 2, int(est * (1 + 1e-12)) + 2
    assert lo ** D <= M * scale ** D < hi ** D
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** D <= M * scale ** D:
            lo = mid
        else:
            hi = mid
    s = str(lo).rjust(digits + 1, "0")
    return s[:-digits] + "." + s[-digits:]


if __name__ == "__main__":
    for n in (7, 11, 13, 15, 19, 23):
        c = parse_cert(n)
        M, E = run(c, check=True)
        assert M == c["M"] and E == c["E"], n
        dim = c["d"] * E
        dec = root_decimal(M, dim, 15)
        ok = dec == BPZ[n]
        print(f"C{n}: {len(c['nodes'])} nodes, subs {sorted(set(c['alias'].values()))}, code {c['terminal']}, "
              f"base d={c['d']}, w0={c['w0']}, E={E}, dim={dim}, digits={len(str(M))}, "
              f"M exact match, root={dec} {'== BPZ' if ok else '!= BPZ ' + BPZ[n]}", flush=True)
        assert ok
