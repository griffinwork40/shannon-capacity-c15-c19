"""Independent verifier for Shannon-capacity constructions on odd cycles C_n.

Deliberately self-contained (stdlib only) and written separately from any
search code. It checks:
  * independence of a point set in the strong power C_n^{\\boxtimes d};
  * validity of a Gao/BPZ "valid tuple" (I, S, f0, f1, X) and its profile;
  * the exact profile product (Buys-Polak-Zuiddam 2026, Theorem 1 / Gao 2026 Lemma 4);
  * exact integer comparison of a claimed bound M^{1/D} against a baseline b^{1/e}.

Definitions (BPZ arXiv:2607.29681, Section 2):
  tau = (I, S, f0, f1, X) is valid for G if I is independent, S subset of I, and
  for every s in S exactly one of f0(s), f1(s) equals s, while N[f_i(s)] cap I = {s}
  for i in {0,1}; f0(S), f1(S), X are independent; X cap N[f0(S)] cap N[f1(S)] = empty.
  Profile = (|I|, |S|, |X|, |X minus (N[f0(S)] cup N[f1(S)])|).
  (a1,b1,c1,d1)*(a2,b2,c2,d2) = ((a1-b1)(a2-b2)+c1 b2+b1 c2, d1 b2+b1 d2, c1 c2,
                                 d1 d2+(c1-d1)(c2-d2)).
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction


def confusable(n: int, x, y) -> bool:
    """Closed adjacency in C_n^d: every coordinate differs by 0 or +-1 mod n."""
    for a, b in zip(x, y):
        dlt = (a - b) % n
        if dlt not in (0, 1, n - 1):
            return False
    return True


def closed_nbhd(n: int, x):
    d = len(x)
    for delta in itertools.product((-1, 0, 1), repeat=d):
        yield tuple((x[i] + delta[i]) % n for i in range(d))


def _norm(n, d, pts):
    out = []
    for p in pts:
        p = tuple(int(c) % n for c in p)
        if len(p) != d:
            raise ValueError(f"point {p} has wrong dimension (want {d})")
        out.append(p)
    return out


def is_independent(n: int, d: int, pts) -> bool:
    pts = _norm(n, d, pts)
    s = set(pts)
    if len(s) != len(pts):
        return False  # duplicates
    for p in pts:
        for q in closed_nbhd(n, p):
            if q != p and q in s:
                return False
    return True


def nbhd_set(n, S):
    out = set()
    for p in S:
        out.update(closed_nbhd(n, p))
    return out


def check_valid_tuple(n: int, d: int, I, S, f0, f1, X):
    """Return the profile (a,t,x,o) or raise AssertionError explaining failure.

    S is a list of points of I; f0, f1 are lists aligned with S.
    """
    I = _norm(n, d, I); S = _norm(n, d, S); f0 = _norm(n, d, f0)
    f1 = _norm(n, d, f1); X = _norm(n, d, X)
    Iset = set(I)
    assert len(Iset) == len(I), "I has duplicates"
    assert is_independent(n, d, I), "I not independent"
    assert len(set(S)) == len(S), "S has duplicates"
    assert len(S) == len(f0) == len(f1), "S/f0/f1 length mismatch"
    for s, a, b in zip(S, f0, f1):
        assert s in Iset, f"{s} in S but not in I"
        assert (a == s) != (b == s), f"exactly one of f0(s), f1(s) must equal s={s}"
        for img in (a, b):
            hits = [p for p in closed_nbhd(n, img) if p in Iset]
            assert hits == [s] or sorted(hits) == [s], f"N[{img}] cap I = {hits} != {{{s}}}"
    assert len(set(f0)) == len(f0) and is_independent(n, d, f0), "f0(S) not independent"
    assert len(set(f1)) == len(f1) and is_independent(n, d, f1), "f1(S) not independent"
    assert is_independent(n, d, X), "X not independent"
    N0 = nbhd_set(n, f0); N1 = nbhd_set(n, f1)
    Xs = set(X)
    assert not (Xs & N0 & N1), "X meets N[f0(S)] cap N[f1(S)]"
    o = len(Xs - (N0 | N1))
    return (len(I), len(S), len(X), o)


def star(p, q):
    a1, b1, c1, d1 = p
    a2, b2, c2, d2 = q
    return ((a1 - b1) * (a2 - b2) + c1 * b2 + b1 * c2,
            d1 * b2 + b1 * d2,
            c1 * c2,
            d1 * d2 + (c1 - d1) * (c2 - d2))


def eval_tree(tree, profiles):
    """tree: an int (index into profiles, a base block) or [left, right].
    profiles: list of (profile, dim). Returns (profile, dim)."""
    if isinstance(tree, int):
        return profiles[tree]
    l, r = tree
    pl, dl = eval_tree(l, profiles)
    pr, dr = eval_tree(r, profiles)
    return star(pl, pr), dl + dr


def beats(M: int, D: int, base: int, e: int) -> bool:
    """Exact test M^{1/D} > base^{1/e}  <=>  M^e > base^D."""
    return M ** e > base ** D


def root_decimal(M: int, D: int, digits: int = 30) -> str:
    """M^{1/D} to `digits` decimals by integer bisection (exact floor)."""
    scale = 10 ** digits
    lo, hi = 0, 1
    while hi ** D <= M * scale ** D:
        hi *= 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** D <= M * scale ** D:
            lo = mid
        else:
            hi = mid
    s = str(lo).rjust(digits + 1, "0")
    return s[:-digits] + "." + s[-digits:]


def main(path: str):
    """Verify a certificate JSON:
    {"n":9, "bases":[{"d":3,"I":[...],"S":[...],"f0":[...],"f1":[...],"X":[...]}, ...],
     "tree": <nested lists of base indices>, "baseline":[81,3]}
    or {"n":9,"d":6,"independent_set":[...],"baseline":[81,3]}.
    """
    cert = json.load(open(path))
    n = cert["n"]
    base, e = cert.get("baseline", [81, 3])
    if "independent_set" in cert:
        d = cert["d"]; pts = cert["independent_set"]
        ok = is_independent(n, d, pts)
        M, D = len(pts), d
        print(f"direct set: n={n} d={d} size={M} independent={ok}")
        if not ok:
            sys.exit(1)
    else:
        profs = []
        for i, b in enumerate(cert["bases"]):
            prof = check_valid_tuple(n, b["d"], b["I"], b["S"], b["f0"], b["f1"], b["X"])
            print(f"base {i}: d={b['d']} profile={prof}")
            profs.append((prof, b["d"]))
        (M, t, x, o), D = eval_tree(cert["tree"], profs)
        print(f"tree result: dim={D} |I|={M}")
    print(f"bound: Theta(C_{n}) >= {M}^(1/{D}) = {root_decimal(M, D)}")
    print(f"baseline {base}^(1/{e}) = {root_decimal(base, e)}")
    print("BEATS BASELINE (exact integer check):", beats(M, D, base, e))


if __name__ == "__main__":
    main(sys.argv[1])


# ---------------------------------------------------------------------------
# Generalised valid tuples (this project): the condition
#   X cap N[f0(S)] cap N[f1(S)] = empty  is DROPPED; such points form a class Z.
# Profile (a, t, x, o, z):  z = |X cap N[f0 S] cap N[f1 S]|,
#                           o = |X minus (N[f0 S] cup N[f1 S])|.
# Product (proved in NOTES.md, fuzz-tested in tests/test_generalised.py):
#   a12 = (a1-t1)(a2-t2) + t1 (x2-z2) + (x1-z1) t2
#   t12 = t1 o2 + o1 t2 ; x12 = x1 x2 ; o12 = o1 o2 + (x1-o1)(x2-o2) ; z12 = z1 o2 + o1 z2
# With z = 0 this is exactly the BPZ/Gao product.
# ---------------------------------------------------------------------------
def check_gen_tuple(n: int, d: int, I, S, f0, f1, X):
    I = _norm(n, d, I); S = _norm(n, d, S); f0 = _norm(n, d, f0)
    f1 = _norm(n, d, f1); X = _norm(n, d, X)
    Iset = set(I)
    assert len(Iset) == len(I) and is_independent(n, d, I), "I not independent"
    assert len(set(S)) == len(S) and len(S) == len(f0) == len(f1)
    for s, a, b in zip(S, f0, f1):
        assert s in Iset, f"{s} in S but not in I"
        assert (a == s) != (b == s), "exactly one of f0(s), f1(s) must equal s"
        for img in (a, b):
            hits = [p for p in closed_nbhd(n, img) if p in Iset]
            assert hits == [s], f"N[{img}] cap I = {hits} != [{s}]"
    assert len(set(f0)) == len(f0) and is_independent(n, d, f0), "f0(S) not independent"
    assert len(set(f1)) == len(f1) and is_independent(n, d, f1), "f1(S) not independent"
    assert is_independent(n, d, X), "X not independent"
    N0 = nbhd_set(n, f0); N1 = nbhd_set(n, f1); Xs = set(X)
    return (len(I), len(S), len(X), len(Xs - (N0 | N1)), len(Xs & N0 & N1))


def star5(p, q):
    a1, t1, x1, o1, z1 = p
    a2, t2, x2, o2, z2 = q
    return ((a1 - t1) * (a2 - t2) + t1 * (x2 - z2) + (x1 - z1) * t2,
            t1 * o2 + o1 * t2, x1 * x2, o1 * o2 + (x1 - o1) * (x2 - o2), z1 * o2 + o1 * z2)


def eval_tree5(tree, profiles):
    if isinstance(tree, int):
        return profiles[tree]
    (pl, dl), (pr, dr) = eval_tree5(tree[0], profiles), eval_tree5(tree[1], profiles)
    return star5(pl, pr), dl + dr
