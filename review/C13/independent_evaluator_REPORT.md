# Independent review: Theta(C13) >= 6.302927071589786

## Verdict: CONFIRMED

I wrote a new evaluator from BPZ's Lean definitions. The search and generation code was withheld from me, and I did not read the lane REPORT until my own numbers were finished. The evaluator reproduces the candidate's literal M digit for digit. As an exact integer, M is strictly larger than Protti's N in the same dimension (522). The patch is purely additive. I applied it to a fresh BPZ clone at aa21eeb, built it, and it type-checks the stated theorem with no sorry.

## 1. Evaluator and positive control
`bpz_eval.py` uses only the stdlib. It parses the Lean sources directly:
- `Substitutions.lean`, `TerminalCodes.lean`;
- each Cert file's `chX`, `RX := Realisation.multiSubst ...` and `terminalChildren` defs.

It applies `w_multiSubst` (a sum over the words of a product of the child weights) and `le_indepNum_multiCode`. It handles `R1` and `Rf = reindex sigma`, with sigma = (A D)(H V). It also checks the exponents against the `strongPower G k` annotations, and re-checks the admissibility of all 10 tables and the separation of all 3 codes against `Letter.sep`.

Positive control (`logs_eval.txt`), comparing the computed M with BPZ's literal M:
- CertC7: MATCH, 257 digits.
- CertC11: MATCH, 150 digits.
- CertC13: MATCH, 418 digits.
- CertC15: MATCH, 3164 digits.
- CertC19: MATCH, 11514 digits.
- CertC23: MATCH, 3206 digits.

All intermediate `wX` literals also match.

## 2. Base sizes
BaseC13.lean proves the following: `base_N = 62530`, `base_d = 1014`, `base_Xc_card c = 1014` (for both c), and `base_eta = 60502`. The last one is proved from `Xcard = 62530 - 2*1014`.

PortRealisation proves the family sizes:
- B = N - d
- N = eta
- A = |Xc false|
- D = |Xc true|
- O = H = V = d

So w0 = (61516, 60502, 1014, 1014, 1014, 1014, 1014). This equals the `w0` in CertC13b, and `exact_check.py` asserts it. `w0f` = sigma(w0), and that is asserted too.

CapCertC13b's `base_fam_card` is line-for-line BPZ's CapCertC13 proof, and it discharges exactly the hypothesis `hw` of `bound`. `Rf` uses BPZ's own `Realisation.reindex` with `Letter.sigma_sep`; BPZ's CertC7 does the same.

## 3. Values (`logs_exact.txt`, `logs_schedule.txt`)
- The M recomputed from CertC13b's DAG equals the Lean literal (418 digits, sha256 cac3a5bd…0914fba).
- Evaluating the JSON schedule tree separately gives the same M. The exponents are (34, 36, 17), so E = 87 and the dimension is 6·87 = 522.
- In all 49 nodes, the `sn` size arguments and subst names agree with the `chn` realisation children. That means `stepM` really refers to the realised nodes.
- Compared with Protti v0.5.0 (commit dfaef37), `C13R8D522.N`: **M > N**. M − N ≈ 4.72e411 [erratum 2026-10-01: originally written 4.72e414; recomputed exactly by afk:6 (lanes/V_c13_indep) and by the coordinator: 4.7204e411, both M and N have 418 digits; verdict unaffected], and the relative gap is ≈ 2.06e-6.
- The decimal is implied by M and is tight: 6302927071589786^522 ≤ M·10^(15·522) < 6302927071589787^522. A Fraction check gives the same result.
- 6.302927071589786 > 6.302927046770772 (Protti) and > 6.302926729310108 (BPZ).

## 4. Patch audit
- sha256 = 7fde38bc…01138. It contains 5 diffs: 4 new files, plus 4 import lines appended to ShannonBounds.lean, with no removed lines.
- No `axiom`, `unsafe`, `implemented_by`, `extern`, `macro`, `opaque`, `sorry`, `admit`, `instance`, `attribute` or notation appears in the added files.
- No added file redefines `shannonCapacity` or `cycleGraph`. The new namespaces are CertC13b, CapCertC13b and DagTail.
- DagTail.lean differs from the bpz_copy version only in its header comment.

## 5. Build (fresh aa21eeb clone + patch, laptop, battery 80% on AC)
`lake build ShannonBounds.CapCertC13b` exited 0 (`logs_build.txt`).

`#print axioms` on the theorem gives propext, Classical.choice, Quot.sound and 47 `native_decide` auxiliaries, all in BaseC13, Substitutions, TerminalCodes, CertC13b.stepM and the decimal step. sorryAx does not appear.

`#check` shows the type is `6.302927071589786 ≤ ShannonBounds.shannonCapacity (SimpleGraph.cycleGraph 13)`, and `#print` shows `shannonCapacity` is BPZ's ⨆ definition.

## Caveats and what I did not check
- The result trusts `native_decide`, i.e. the compiler, the same way BPZ's own certificates do.
- My Mathlib/.lake packages were cloned from L_lean/bpz_copy (same lake-manifest) instead of being fetched fresh.
- I did not run anything on a second machine.
- I did no literature search beyond Protti v0.5.0 and BPZ aa21eeb.
- I did not re-derive BaseC13 itself; Lean checked it.

## Comparison with the lane REPORT (read afterwards)
These all agree with the lane REPORT: the M sha, M > N, the relative gap of 2.06e-6, the patch sha, the axiom set (47 native_decide auxiliaries), and the one-file DagTail header difference. I found no discrepancy.
