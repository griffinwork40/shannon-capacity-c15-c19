"""Parsers for the BPZ Lean repo (commit aa21eeb) data used by Lane G.

Reads the Lean source text directly (no Lean needed):
  * BaseC19Data.lean : Iraw, Xraw (base-19 codes), maskI, maskX, pairsRaw
  * Substitutions.lean : the substitution tables T2a, T2b, T3a..T3h
  * TerminalCodes.lean : the terminal codes C3a, C4a, C4b
  * CertC19.lean : w0, the schedule (node children / substitution used), the
    intermediate sizes wu0..wu15 and the final M
"""
from __future__ import annotations

import os
import re
import sys

sys.set_int_max_str_digits(0)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("BPZ_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", "data", "bpz", "ShannonBounds"))
LETTERS = ["B", "N", "A", "D", "O", "H", "V"]


def _read(name):
    with open(os.path.join(REPO, name)) as f:
        return f.read()


def _list_after(text, header):
    i = text.index(header)
    j = text.index("[", i)
    k = text.index("]", j)
    return [int(s) for s in re.findall(r"\d+", text[j + 1:k])]


def base_c19():
    t = _read("BaseC19Data.lean")
    I = _list_after(t, "def Iraw : List Nat :=")
    X = _list_after(t, "def Xraw : List Nat :=")
    maskI = int(re.search(r"def maskI : Nat := (0x[0-9a-fA-F]+)", t).group(1), 16)
    maskX = int(re.search(r"def maskX : Nat := (0x[0-9a-fA-F]+)", t).group(1), 16)
    m = re.search(r"def pairsRaw : List \(Nat × Nat × Bool\) := \[(.*?)\]\n", t)
    pairs = [(int(a), int(b), c == "true")
             for a, b, c in re.findall(r"\((\d+),\s*(\d+),\s*(true|false)\)", m.group(1))]
    return dict(I=I, X=X, maskI=maskI, maskX=maskX, pairs=pairs)


def decode(u, n=19, d=4):
    """Lean convention: coordinate k of code u is (u / n^k) % n."""
    return tuple((u // n ** k) % n for k in range(d))


def _parse_table_block(block):
    """block: text of one `def Txx : Letter → Finset (Fin q → Letter)` body."""
    out = {}
    parts = re.split(r"\|\s*\.?([BNADOHV])\s*=>", block)
    # parts = [pre, L1, body1, L2, body2, ...]
    for i in range(1, len(parts), 2):
        lab, body = parts[i], parts[i + 1]
        words = re.findall(r"!\[([^\]]*)\]", body)
        out[lab] = [tuple(w.replace(".", "").replace(" ", "").split(",")) for w in words]
    return out


def substitutions():
    t = _read("Substitutions.lean")
    tabs = {}
    for m in re.finditer(r"def (T\d[a-z]) : Letter → Finset \(Fin (\d) → Letter\)[^\n]*\n(.*?)\n\n", t, re.S):
        name, q, body = m.group(1), int(m.group(2)), m.group(3)
        tab = _parse_table_block(body)
        assert set(tab) == set(LETTERS), (name, tab.keys())
        assert all(len(w) == q for ws in tab.values() for w in ws), name
        tabs["S" + name[1:]] = tab
    return tabs


def terminal_codes():
    t = _read("TerminalCodes.lean")
    codes = {}
    for m in re.finditer(r"def (C\d[a-z]) : Finset \(Fin (\d) → Letter\)[^\n]*\n(.*?)\n\n", t, re.S):
        name, r, body = m.group(1), int(m.group(2)), m.group(3)
        words = [tuple(w.replace(".", "").replace(" ", "").split(","))
                 for w in re.findall(r"!\[([^\]]*)\]", body)]
        assert all(len(w) == r for w in words)
        codes["K" + name[1:]] = words
    return codes


def sep_table():
    t = _read("PortRealisation.lean")
    blk = t[t.index("def sep : Letter → Letter → Bool"):t.index("| _, _ => false")]
    pairs = set(re.findall(r"([BNADOHV]), ([BNADOHV]) => true", blk))
    return pairs


def cert_c19():
    """Parse CertC19.lean: substitution aliases, w0, per-node (children, subst), wu*, M."""
    t = _read("CertC19.lean")
    alias = dict(re.findall(r"abbrev (S[abc]) : Subst Letter Letter.sep 3 := Substitutions\.(S3[a-h])", t))
    term = re.search(r"abbrev K : Code Letter Letter.sep 4 := TerminalCodes\.(K4[a-z])", t).group(1)

    def wblock(name):
        m = re.search(r"def " + name + r" : Letter → Nat\n(.*?)\n\n", t, re.S)
        return {L: int(v) for L, v in re.findall(r"\| \.([BNADOHV]) => (\d+)", m.group(1))}

    w0 = wblock("w0")
    nodes = []
    k = 0
    while ("def Ru%d " % k) in t:
        ch = re.search(r"def chu%d .*?:=\n\s*(Fin\.cases.*?)\n" % k, t, re.S).group(1)
        kids = re.findall(r"\((R1|Ru\d+) R\)", ch)
        sub = re.search(r"Realisation\.multiSubst eu%d \(chu%d R\) (S[abc])" % (k, k), t).group(1)
        dims = re.search(r"def Ru%d .*?strongPower G (\d+)\)" % k, t, re.S).group(1)
        nodes.append(dict(name="u%d" % k, kids=kids, subst=alias[sub], exp=int(dims), w=wblock("wu%d" % k)))
        k += 1
    M = int(re.search(r"def M : Nat :=\s*(\d+)", t).group(1))
    tch = re.search(r"def terminalChildren .*?:=\n\s*(Fin\.cases.*?)\n", t, re.S).group(1)
    tkids = re.findall(r"\((R1|Ru\d+) R\)", tch)
    return dict(alias=alias, terminal=term, w0=w0, nodes=nodes, M=M, terminal_kids=tkids)
