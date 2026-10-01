"""Deliverable 2: reproduce Theta(C19) >= 9.357200030000796 in Python, independently of Lean.

Implements the BPZ "layered" recursion from the definitions in Layered.lean
(w_multiSubst: w'(a) = sum_{x in T(a)} prod_i w_i(x_i); terminal code: sum_{x in K} prod_i w_i(x_i)),
with the substitution tables / terminal code parsed from Substitutions.lean / TerminalCodes.lean,
and the schedule parsed from CertC19.lean.  Every intermediate size wu0..wu15 and the final M
are compared with the literals in CertC19.lean.  Also re-checks the admissibility of the
used tables against the separation table of PortRealisation.lean (independent of native_decide).

Also: the paper's binary star-product doubling (arXiv:2607.29681 Sec. 3, C19 paragraph) using the
FIXED checker's verify.star, and the exact decimal of both bounds.
"""
import os
import sys
from math import log, exp

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(P, "verifier"))
sys.path.insert(0, HERE)
sys.set_int_max_str_digits(0)
import verify  # noqa: E402
from lean_parse import LETTERS, cert_c19, substitutions, terminal_codes, sep_table  # noqa: E402

SUBS = substitutions()
CODES = terminal_codes()
SEP = sep_table()


def sep(a, b):
    return (a, b) in SEP


def check_admissible(tab):
    """hin: distinct words of one letter separated somewhere; hcross: words of separated letters separated."""
    for a in LETTERS:
        ws = tab[a]
        assert len(set(ws)) == len(ws)
        for i, x in enumerate(ws):
            for y in ws[i + 1:]:
                assert any(sep(p, q) for p, q in zip(x, y)), ("hin", a, x, y)
    for a in LETTERS:
        for b in LETTERS:
            if sep(a, b):
                for x in tab[a]:
                    for y in tab[b]:
                        assert any(sep(p, q) for p, q in zip(x, y)), ("hcross", a, b, x, y)


def check_code(words):
    for i, x in enumerate(words):
        for y in words[i + 1:]:
            assert any(sep(p, q) for p, q in zip(x, y)), ("code", x, y)


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


def run_cert(w0, cert, check_lean=False):
    """Evaluate the CertC19 schedule on base sizes w0. Returns (M, E) with E the G4-exponent."""
    vals = {"R1": (w0, 1)}
    for nd in cert["nodes"]:
        kids = [vals[k] for k in nd["kids"]]
        w = apply_sub(SUBS[nd["subst"]], [k[0] for k in kids])
        e = sum(k[1] for k in kids)
        if check_lean:
            assert e == nd["exp"], (nd["name"], e, nd["exp"])
            assert w == nd["w"], ("size mismatch at", nd["name"])
        vals["R" + nd["name"]] = (w, e)
    kids = [vals[k] for k in cert["terminal_kids"]]
    M = apply_code(CODES[cert["terminal"]], [k[0] for k in kids])
    return M, sum(k[1] for k in kids)


def root_float(M, D):
    """M^(1/D) as float via log of a big int."""
    k = M.bit_length() - 60
    return exp((log(M >> k) + k * log(2)) / D) if k > 0 else M ** (1 / D)


if __name__ == "__main__":
    cert = cert_c19()
    print("CertC19 substitutions:", cert["alias"], "terminal:", cert["terminal"])
    for nm in set(cert["alias"].values()):
        check_admissible(SUBS[nm])
    check_code(CODES[cert["terminal"]])
    print("admissibility of", sorted(set(cert["alias"].values())), "and", cert["terminal"],
          "re-checked in Python against Letter.sep: OK")
    print("schedule:")
    for nd in cert["nodes"]:
        print(f"  {nd['name']}: {nd['subst']}({', '.join(nd['kids'])})  exp {nd['exp']}")
    M, E = run_cert(cert["w0"], cert, check_lean=True)
    print("all 16 intermediate size vectors wu0..wu15 equal the CertC19.lean literals")
    assert M == cert["M"], "final M differs from CertC19.M"
    dim = 4 * E
    print(f"final M equals CertC19.M exactly ({len(str(M))} digits), dim = 4*{E} = {dim}")
    dec = verify.root_decimal(M, dim, 18)
    print(f"Theta(C19) >= M^(1/{dim}) = {dec}")
    a = 9357200030000796
    assert a ** dim <= M * 10 ** (15 * dim) < (a + 1) ** dim
    print("exact integer check: 9.357200030000796 <= M^(1/11856) < 9.357200030000797  (matches CapCertC19 'tight')")

    # paper's binary doubling: pi_{2r} = pi_r * pi_r, r = 1..2048
    p = (7666, 2, 7666, 7661)
    for _ in range(12):
        p = verify.star(p, p)
    print(f"paper schedule (pi_4096, dim 16384): a^(1/16384) = {verify.root_decimal(p[0], 16384, 15)}"
          "   [paper states 9.357192705918...]")
    # best simple binary star growth: deep doubling
    q = (7666, 2, 7666, 7661)
    print("binary star doubling, a^(1/dim):")
    for k in range(1, 15):
        q = verify.star(q, q)
        if k in (1, 2, 4, 8, 12, 14):
            print(f"   dim {4 * 2 ** k:6d}: {verify.root_decimal(q[0], 4 * 2 ** k, 15)}")
    print("7666^(1/4) =", verify.root_decimal(7666, 4, 15))
