"""Lane L2: generate a BPZ-framework Lean certificate (Cert + CapCert) from a lane-O DAG schedule.

usage: python gen_dag.py SCHEDULE.json NAME [--neg]
  NAME e.g. C15b -> writes out/CertC15b.lean, out/CapCertC15b.lean, out/NAME.json (literals).
  --neg also writes neg/CertNAMEneg.lean with M+1 (negative control; standalone file).

The schedule format is lane O's (see lanes/O_opt/exact_eval.py).  Shared sub-expressions are
hash-consed into one Lean node each.  Every non-tail node is one `multiSubst`; every tail
["tail", y, S, 0, zs, J] becomes one `DagTail.tailIter` node (J > 0) whose sizes are proved by
the generic induction `DagTail.w_tailIter`.  Sizes are never written as literals: each node gets a
`Sizes` definition (`node2`/`node3`/`tailW` of its children's), and the single literal `M` is
checked against `code4 K ...` by one `native_decide`.  This generator recomputes M with its own
evaluator and cross-checks it against lane O's exact_eval (read-only import).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(HERE, "..", "O_opt")
sys.path.insert(0, O)
sys.set_int_max_str_digits(0)
import exact_eval  # noqa: E402  (lane O, read-only)
from certs import parse_cert, SUBS, CODES, SIGMA, BPZ, apply_sub, apply_code  # noqa: E402
from lean_parse import LETTERS  # noqa: E402
from recursion import check_admissible, check_code  # noqa: E402

LET = "BNADOHV"
CAPN = {15: "C15", 19: "C19"}


def to_t(x):
    return tuple(to_t(y) for y in x) if isinstance(x, list) else x


def build(sched):
    """Hash-cons the DAG.  Returns (nodes, terminal_refs).  node = dict(kind, ...)."""
    nodes = []
    ids = {}

    def go(x):
        if x in ("R1", "Rf"):
            return x
        if x in ids:
            return ids[x]
        if x[0] == "tail":
            _, y, s, p, zs, J = x
            assert p == 0, "only slot-0 tails are supported"
            assert len(zs) == 2, "only arity-3 tails"
            start = go(y)
            if J == 0:
                ids[x] = start
                return start
            zz = ["R1" if ch == "w" else "Rf" for ch in zs]
            nd = dict(kind="tail", sub=s, start=start, z=zz, J=J)
        else:
            kids = [go(k) for k in x[1:]]
            nd = dict(kind="node", sub=x[0], kids=kids)
        key = json.dumps(nd, sort_keys=True)
        for i, o in enumerate(nodes):          # identical structure -> same node
            if json.dumps(o, sort_keys=True) == key:
                ids[x] = f"n{i}"
                return ids[x]
        nodes.append(nd)
        ids[x] = f"n{len(nodes) - 1}"
        return ids[x]

    term = [go(to_t(x)) for x in sched["terminal"]]
    return nodes, term


def evaluate(nodes, term, w0, code):
    val = {"R1": (dict(w0), 1), "Rf": ({L: w0[SIGMA[L]] for L in LETTERS}, 1)}
    for i, nd in enumerate(nodes):
        if nd["kind"] == "node":
            ks = [val[k] for k in nd["kids"]]
            val[f"n{i}"] = (apply_sub(SUBS[nd["sub"]], [k[0] for k in ks]), sum(k[1] for k in ks))
        else:
            v, e = val[nd["start"]]
            zz = [val[z] for z in nd["z"]]
            for _ in range(nd["J"]):
                v = apply_sub(SUBS[nd["sub"]], [v] + [z[0] for z in zz])
                e += sum(z[1] for z in zz)
            val[f"n{i}"] = (v, e)
    ks = [val[k] for k in term]
    return apply_code(CODES[code], [k[0] for k in ks]), [k[1] for k in ks], val


def ref(k):
    return {"R1": "(R1 R)", "Rf": "(Rf R)"}.get(k, f"(R{k} R)")


def sref(k):
    return {"R1": "s1", "Rf": "sf"}.get(k, f"s{k}")


def wref(k):
    return {"R1": "w1 R h", "Rf": "wf R h"}.get(k, f"w{k} R h")


def fincases(xs):
    if len(xs) == 1:
        return f"(fun _ => {xs[0]})"
    s = f"(fun _ => {xs[-1]})"
    for x in reversed(xs[:-1]):
        s = f"(Fin.cases {x} {s})"
    return s[1:-1] if s.startswith("(Fin.cases") else s


def largest_decimal(M, dim, digits=15):
    from math import log, exp
    k = max(M.bit_length() - 60, 0)
    est = exp((log(M >> k) + k * log(2)) / dim) * 10 ** digits
    lo, hi = int(est * (1 - 1e-12)) - 2, int(est * (1 + 1e-12)) + 2
    S = 10 ** (digits * dim)
    assert lo ** dim <= M * S < hi ** dim
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** dim <= M * S:
            lo = mid
        else:
            hi = mid
    assert lo ** dim <= M * S < (lo + 1) ** dim
    return lo


def decstr(a, digits=15):
    s = str(a)
    return s[:-digits] + "." + s[-digits:]


def wblock(name, doc, w):
    s = f"/-- {doc} -/\ndef {name} : Letter → Nat\n"
    s += "".join(f"  | .{a} => {w[a]}\n" for a in LET)
    return s


def gen(sched_path, name, neg=False, prev=None):
    sched = json.load(open(sched_path))
    n = sched["n"]
    Cn = CAPN[n]
    c = parse_cert(n)
    w0, d = c["w0"], c["d"]
    code = sched["code"]
    subs = set()
    for x in sched["terminal"]:
        exact_eval.used(to_t(x), subs)
    for s in subs:
        check_admissible(SUBS[s])
    check_code(CODES[code])
    nodes, term = build(sched)
    M, eT, val = evaluate(nodes, term, w0, code)
    Mref, Eref, _, dref = exact_eval.evaluate(sched, exact=True)
    assert M == Mref and sum(eT) == Eref and d == dref, "generator disagrees with lane O exact_eval"
    E = sum(eT)
    dim = d * E
    a = largest_decimal(M, dim)
    bpz = int(BPZ[n].replace(".", ""))
    assert a > bpz
    uses_f = any("Rf" in (nd.get("kids", []) + nd.get("z", []) + [nd.get("start")]) for nd in nodes) or "Rf" in term
    ns = f"Cert{name}"
    L = []
    L.append(f"""/-
Copyright (c) 2026 Pjotr Buys, Sven Polak, Jeroen Zuiddam. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Pjotr Buys, Sven Polak, Jeroen Zuiddam
(This file: generated by lanes/L2_lean/gen_dag.py from {os.path.basename(sched_path)}; a DAG schedule
in the framework of `Cert{Cn}.lean`, with the same base.)
-/
import ShannonBounds.PortRealisation
import ShannonBounds.Layered
import ShannonBounds.Reindex
import ShannonBounds.Substitutions
import ShannonBounds.TerminalCodes
import ShannonBounds.DagTail

set_option maxRecDepth 4000000
set_option maxHeartbeats 0
set_option synthInstance.maxSize 4000
set_option exponentiation.threshold 20000

/-!
# `Theta ({Cn}) >= {decstr(a)}`, a DAG schedule with several tails

The same `{Cn}^(box {d})` base as `Cert{Cn}`.  {len(nodes)} distinct nodes (shared sub-schedules are
defined once), {sum(1 for x in nodes if x['kind'] == 'tail')} of them iterated tails `y ↦ S (y, z1, z2)` written with `DagTail.tailIter`
and sized by the induction `DagTail.w_tailIter`.  The terminal code `K` is applied to nodes of
exponents `{tuple(eT)}`, so `E = {E}`, hence `{Cn}^(box {dim})`.

Node sizes are not literals: each node carries a `Sizes` value computed from its children's
(`node2`, `node3`, `tailW`); `stepM` checks the one literal `M` by `native_decide`.

Schedule (`t = J x [y <- S(y, z1, z2)]` from `y = start`):
""")
    for i, nd in enumerate(nodes):
        if nd["kind"] == "node":
            L.append(f"    n{i} = {nd['sub']}({', '.join(nd['kids'])})\n")
        else:
            L.append(f"    n{i} = {nd['J']} x [y <- {nd['sub']}(y, {', '.join(nd['z'])})] from y = {nd['start']}\n")
    L.append(f"    M = {code}({', '.join(term)})\n")
    L.append(f"""-/
namespace ShannonBounds
namespace {ns}

open SimpleGraph DagTail

/-- The terminal code. -/
abbrev K : Code Letter Letter.sep 4 := TerminalCodes.{code}

""")
    L.append(wblock("w0", "The size of each of the seven families of the base port system.", w0))
    L.append("\n")
    if uses_f:
        L.append(wblock("w0f", "The same sizes after reindexing by `sigma`: `A`/`D` and `H`/`V` are exchanged.",
                        {x: w0[SIGMA[x]] for x in LET}))
        L.append("\n")
    Mlit = M + 1 if neg else M
    L.append(f"""/-- The size of the independent set the construction produces. -/
def M : Nat :=
  {Mlit}

/-- Sizes of the base. -/
def s1 : Sizes := Sizes.ofFun w0
""")
    if uses_f:
        L.append("""
/-- Sizes of the reindexed base. -/
def sf : Sizes := Sizes.ofFun w0f
""")
    L.append("""
variable {α : Type*} [Fintype α] [DecidableEq α]
  {G : SimpleGraph α} [DecidableRel G.Adj]

/-- The base realisation, seen in the first strong power. -/
def R1 (R : Realisation Letter Letter.sep G) :
    Realisation Letter Letter.sep (SimpleGraph.strongPower G 1) :=
  R.mapIso (strongPower_one_iso G).symm

lemma w1 (R : Realisation Letter Letter.sep G) (h : ∀ a, R.w a = w0 a) (b : Letter) :
    (R1 R).w b = s1.get b := by
  show (R1 R).w b = (Sizes.ofFun w0).get b
  rw [Sizes.get_ofFun, ← h b]
  simp [R1]
""")
    if uses_f:
        L.append("""
/-- The base realisation reindexed by `sigma`, in the same graph. -/
def Rf (R : Realisation Letter Letter.sep G) :
    Realisation Letter Letter.sep (SimpleGraph.strongPower G 1) :=
  (R1 R).reindex Letter.sigma Letter.sigma_sep

lemma wf (R : Realisation Letter Letter.sep G) (h : ∀ a, R.w a = w0 a) (b : Letter) :
    (Rf R).w b = sf.get b := by
  show (Rf R).w b = (Sizes.ofFun w0f).get b
  rw [Sizes.get_ofFun, Rf, Realisation.w_reindex, w1 R h]
  show (Sizes.ofFun w0).get _ = _
  rw [Sizes.get_ofFun]
  cases b <;> rfl
""")
    for i, nd in enumerate(nodes):
        k = f"n{i}"
        e = val[k][1]
        S = f"Substitutions.{nd['sub']}"
        if nd["kind"] == "node":
            q = len(nd["kids"])
            es = [str(val[c][1]) for c in nd["kids"]]
            assert sum(int(x) for x in es) == e
            hs = " ".join(f"(fun b => {wref(c)} b)" for c in nd["kids"])
            ss = " ".join(sref(c) for c in nd["kids"])
            L.append(f"""
/-! ### Node `{k}` = `{nd['sub']}({', '.join(nd['kids'])})`, exponent `{e}` -/

/-- The child exponents of node `{k}`. -/
def e{k} : Fin {q} → Nat := {fincases(es)}

/-- The children of node `{k}`. -/
def ch{k} (R : Realisation Letter Letter.sep G) :
    (i : Fin {q}) → Realisation Letter Letter.sep (SimpleGraph.strongPower G (e{k} i)) :=
  {fincases([ref(c) for c in nd['kids']])}

/-- Node `{k}`. -/
def R{k} (R : Realisation Letter Letter.sep G) :
    Realisation Letter Letter.sep (SimpleGraph.strongPower G {e}) :=
  Realisation.multiSubst e{k} (ch{k} R) {S}

/-- The sizes at node `{k}`. -/
def s{k} : Sizes := node{q} {S} {ss}

/-- Node `{k}` has the sizes `s{k}`. -/
lemma w{k} (R : Realisation Letter Letter.sep G) (h : ∀ a, R.w a = w0 a) (a : Letter) :
    (R{k} R).w a = s{k}.get a :=
  w_node{q} {S} (ch{k} R) {ss}
    {hs} a
""")
        else:
            e0 = val[nd["start"]][1]
            k1, k2 = (val[z][1] for z in nd["z"])
            assert e0 + nd["J"] * (k1 + k2) == e
            z1, z2 = nd["z"]
            L.append(f"""
/-! ### Tail node `{k}` = `{nd['J']} x [y <- {nd['sub']}(y, {z1}, {z2})]` from `y = {nd['start']}`, exponent `{e}` -/

/-- Tail node `{k}`. -/
def R{k} (R : Realisation Letter Letter.sep G) :
    Realisation Letter Letter.sep (SimpleGraph.strongPower G {e}) :=
  castR (by norm_num) (tailIter {S} {ref(nd['start'])} {ref(z1)} {ref(z2)} {nd['J']})

/-- The sizes at tail node `{k}`. -/
def s{k} : Sizes := tailW {S} {sref(nd['start'])} {sref(z1)} {sref(z2)} {nd['J']}

/-- Tail node `{k}` has the sizes `s{k}` (by the tail induction `w_tailIter`). -/
lemma w{k} (R : Realisation Letter Letter.sep G) (h : ∀ a, R.w a = w0 a) (a : Letter) :
    (R{k} R).w a = s{k}.get a :=
  (w_castR _ _ a).trans
    (w_tailIter {S} {ref(nd['start'])} {ref(z1)} {ref(z2)} {sref(nd['start'])} {sref(z1)} {sref(z2)}
      (fun b => {wref(nd['start'])} b) (fun b => {wref(z1)} b) (fun b => {wref(z2)} b) {nd['J']} a)
""")
    tk = term
    L.append(f"""
/-! ### The bound -/

/-- `M` is the size of the terminal code on the four terminal nodes. -/
theorem stepM : M = code4 K {' '.join(sref(x) for x in tk)} := by
  native_decide

/-- The exponents of the 4 terminal children. -/
def eT : Fin 4 → Nat := {fincases([str(x) for x in eT])}

/-- The terminal children. -/
def terminalChildren (R : Realisation Letter Letter.sep G) :
    (i : Fin 4) → Realisation Letter Letter.sep (SimpleGraph.strongPower G (eT i)) :=
  {fincases([ref(x) for x in tk])}

/-- **The bound.**  A port system whose seven families have the sizes of `w0` gives an
independent set of size `M` in `G^(box {E})`. -/
theorem bound (S : RichPortSystem G) (hw : ∀ a, (S.fam a).card = w0 a) :
    M ≤ (SimpleGraph.strongPower G {E}).indepNum := by
  have h : ∀ a, S.toRealisation.w a = w0 a := hw
  have hc := sum_code4 K (terminalChildren S.toRealisation) {' '.join(sref(x) for x in tk)}
    {' '.join(f'(fun b => {wref(x).replace(" R h", " S.toRealisation h")} b)' for x in tk)}
  exact le_trans (le_of_eq (stepM.trans hc.symm))
    (le_indepNum_multiCode eT (terminalChildren S.toRealisation) K)

end {ns}
end ShannonBounds
""")
    cert = "".join(L)
    # ---- CapCert ----
    prevs = [(BPZ[n], f"`CapCert{Cn}` (BPZ)")]
    if prev:
        prevs.append(prev)
    imp = "\n".join(f"""
/-- Strictly improves the bound of {lab}. -/
theorem improves{'' if j == 0 else '_' + str(j)} : ({v} : ℝ) < {decstr(a)} := by norm_num
""" for j, (v, lab) in enumerate(prevs))
    cap = f"""/-
Copyright (c) 2026 Pjotr Buys, Sven Polak, Jeroen Zuiddam. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Pjotr Buys, Sven Polak, Jeroen Zuiddam
(This file: a variant of `CapCert{Cn}.lean` for the schedule of `Cert{name}.lean`.)
-/
import ShannonBounds.Cert{name}
import ShannonBounds.Cap{Cn}
import ShannonBounds.Decimal

/-!
# `Theta ({Cn}) >= {decstr(a)}`

`Cert{name}.bound` is conditional on a port system whose seven families have the sizes in
`w0`.  The base system of `Base{Cn}` has exactly those sizes, all proved there.  Transporting
along `strongPower Cyc{n} {dim} ≃g strongPower G4 {E}` gives the capacity bound.
-/

namespace ShannonBounds
namespace CapCert{name}

open SimpleGraph

/-- The seven families of the `{Cn}` base system have the sizes recorded in `w0`. -/
theorem base_fam_card : ∀ a, (Base{Cn}.base.fam a).card = Cert{name}.w0 a := by
  intro a
  cases a
  · rw [RichPortSystem.card_fam_B, Base{Cn}.base_N, Base{Cn}.base_d]; rfl
  · rw [RichPortSystem.card_fam_N, Base{Cn}.base_eta]; rfl
  · exact Base{Cn}.base_Xc_false
  · exact Base{Cn}.base_Xc_true
  · rw [RichPortSystem.card_fam_O, Base{Cn}.base_d]; rfl
  · rw [RichPortSystem.card_fam_H, Base{Cn}.base_d]; rfl
  · rw [RichPortSystem.card_fam_V, Base{Cn}.base_d]; rfl

/-- The independent set, in the `{E}`-th strong power of the base graph. -/
theorem alpha_G4_ge : Cert{name}.M ≤ (strongPower Base{Cn}.G4 {E}).indepNum :=
  Cert{name}.bound Base{Cn}.base base_fam_card

/-- `{Cn}^(box {dim})` is the `{E}`-th strong power of `{Cn}^(box 4)`. -/
def iso{dim} : strongPower Base{Cn}.Cyc{n} {dim} ≃g strongPower Base{Cn}.G4 {E} :=
  (strongPower_mul_iso Base{Cn}.Cyc{n} 4 {E}).trans
    (strongPower_congr Cap{Cn}.G4_iso {E}).symm

/-- The independent set, in `{Cn}^(box {dim})`. -/
theorem alpha_strongPower_ge :
    Cert{name}.M ≤ (strongPower Base{Cn}.Cyc{n} {dim}).indepNum := by
  rw [independenceNumber_iso iso{dim}]
  exact alpha_G4_ge

/-- The capacity bound, in exact root form. -/
theorem shannonCapacity_Cyc_ge :
    ((Cert{name}.M : ℕ) : ℝ) ^ ((1 : ℝ) / ({dim} : ℕ)) ≤ shannonCapacity Base{Cn}.Cyc{n} := by
  calc ((Cert{name}.M : ℕ) : ℝ) ^ ((1 : ℝ) / ({dim} : ℕ))
      ≤ (((strongPower Base{Cn}.Cyc{n} {dim}).indepNum : ℕ) : ℝ) ^ ((1 : ℝ) / ({dim} : ℕ)) := by
        apply Real.rpow_le_rpow (by positivity) _ (by positivity)
        exact_mod_cast alpha_strongPower_ge
    _ ≤ shannonCapacity Base{Cn}.Cyc{n} :=
        shannonCapacity_ge_root Base{Cn}.Cyc{n} {dim} (by norm_num)

theorem shannonCapacity_cycleGraph_ge :
    ((Cert{name}.M : ℕ) : ℝ) ^ ((1 : ℝ) / ({dim} : ℕ))
      ≤ shannonCapacity (SimpleGraph.cycleGraph {n}) := by
  rw [← Cap{Cn}.Cyc_eq_cycleGraph]
  exact shannonCapacity_Cyc_ge

/-- **`Theta (cycleGraph {n}) >= {decstr(a)}`**. -/
theorem shannonCapacity_cycleGraph_{n}_ge :
    ({decstr(a)} : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph {n}) := by
  have h := shannonCapacity_cycleGraph_ge
  refine le_trans ?_ h
  rw [show (({decstr(a)} : ℝ))
      = (({a} : ℕ) : ℝ) / ((1000000000000000 : ℕ) : ℝ) by norm_num]
  exact Decimal.decimal_le (by norm_num) (by norm_num) (by native_decide) le_rfl

/-- The truncation is tight. -/
theorem tight :
    {a} ^ {dim} ≤ Cert{name}.M * (10 ^ 15) ^ {dim} ∧
      Cert{name}.M * (10 ^ 15) ^ {dim} < {a + 1} ^ {dim} := by
  constructor <;> native_decide
{imp}
end CapCert{name}
end ShannonBounds

#print axioms ShannonBounds.Cert{name}.bound
#print axioms ShannonBounds.CapCert{name}.shannonCapacity_cycleGraph_{n}_ge
#print axioms ShannonBounds.CapCert{name}.tight
"""
    out = os.path.join(HERE, "out")
    os.makedirs(out, exist_ok=True)
    if neg:
        os.makedirs(os.path.join(HERE, "neg"), exist_ok=True)
        p = os.path.join(HERE, "neg", f"Cert{name}neg.lean")
        open(p, "w").write(cert.replace(f"namespace {ns}", f"namespace {ns}neg").replace(f"end {ns}", f"end {ns}neg"))
        return p
    open(os.path.join(out, f"Cert{name}.lean"), "w").write(cert)
    open(os.path.join(out, f"CapCert{name}.lean"), "w").write(cap)
    info = dict(schedule=os.path.relpath(sched_path, HERE), n=n, nodes=len(nodes),
                tails=[nd["J"] for nd in nodes if nd["kind"] == "tail"], E=E, d=d, dim=dim,
                eT=eT, digits=len(str(M)), a=a, decimal=decstr(a), M_sha_prefix=str(M)[:30])
    json.dump(info, open(os.path.join(out, f"{name}.json"), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    prev = None
    for x in sys.argv:
        if x.startswith("--prev="):
            v, lab = x[7:].split(":", 1)
            prev = (v, lab)
    gen(sys.argv[1], sys.argv[2], neg="--neg" in sys.argv, prev=prev)
