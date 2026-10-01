# Slightly improved lower bounds for the Shannon capacity of C15 and C19, formalised in the Buys–Polak–Zuiddam Lean framework

**Author:** Griffin Long

**Status:** DRAFT, not submitted or posted anywhere. Dated 2026-10-01.

## Abstract

We prove Θ(C15) ≥ 7.301635000991096 and Θ(C19) ≥ 9.357203012726939. The best values we could
find were 7.301628695930103 and 9.357200030000796, both in the Lean repository of Buys, Polak and
Zuiddam (BPZ) at commit `aa21eeb`. Our values improve on these by about 6.3·10⁻⁶ and 3.0·10⁻⁶.
Every ingredient is BPZ's: the base port systems in C_n^⊠4, the substitution tables, the terminal
code and the Lean framework. Only the substitution schedules are new. They were found by an
automated search over BPZ's schedule space, run by the AI agent agent-afk. Both bounds are Lean 4
theorems, delivered as a patch that only adds files to BPZ's repository. The trust base is the
same as BPZ's, including `native_decide`. One command reproduces the check from a fresh clone.

## 1. Previous bounds

The Shannon capacity is Θ(G) = sup_d α(G^⊠d)^{1/d}. For odd cycles C_n with n ≥ 7 its value is
unknown.

**BPZ Lean repository.** github.com/spectra-research/shannon-capacity-lean, commit
`aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10, "Update the bounds"). This was still
HEAD on 2026-10-01. Its README table reads:

> `| 15 | 7.301628695930103 | 3664 | 3164 |`
> `| 19 | 9.357200030000796 | 11856 | 11514 |`

The columns are n, the bound, the power p, and the number of digits of α. `ShannonBounds/Main.lean`
states both as theorems.

**BPZ paper.** arXiv:2607.29681 v1 (2026-07-31), which is the only version. Its abstract gives
"Θ(C15) ≥ 7.301600534487 . . ., Θ(C19) ≥ 9.357192705918 . . .", obtained in C15^⊠4096 and
C19^⊠16384 by iterating Gao's ⋆-product of valid tuples. The repository README says that for
C15, C19, C21 and C23 it contains "improved product trees that will appear in the next arXiv
version".

**Other sources.** Itty, Rosin, Carstensen and Reichman (arXiv:2607.21517 v2) prove
Θ(C15) > 7.301399 and give nothing for C19. Gao's fork of the BPZ repository has the older BPZ
values. For C19, the bound before 2026 was the classical one of Baumert et al. (1971), as listed
in BPZ v1 Table 1. We did not find a C15 or C19 bound newer than `aa21eeb` (Section 6).

## 2. New bounds

**Theorem.** Θ(C15) ≥ 7.301635000991096 and Θ(C19) ≥ 9.357203012726939.

Both are verbatim Lean statements:

```lean
theorem ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge :
    (7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15)
theorem ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge :
    (9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)
```

Here `shannonCapacity` is BPZ's definition in `Defs.lean`, unchanged, and `cycleGraph` is
Mathlib's.

| n | p | digits of M | new bound | BPZ `aa21eeb` | gain | BPZ v1 paper |
|---|---|---|---|---|---|---|
| 15 | 3424 | 2957 | 7.301635000991096 | 7.301628695930103 (p = 3664) | 6.31·10⁻⁶ | 7.301600534487 |
| 19 | 14800 | 14373 | 9.357203012726939 | 9.357200030000796 (p = 11856) | 2.98·10⁻⁶ | 9.357192705918 |

Each bound comes from an explicit integer M with M ≤ α(C_n^⊠p), proved in Lean as
`alpha_strongPower_ge`. The decimal is M^{1/p} truncated to 15 places. Lean proves that the
truncation is exact (`tight`: a^p ≤ M·10^{15p} < (a+1)^p, where a is the 16-digit integer).

## 3. The construction, in BPZ's framework

We follow the notation of BPZ's Lean files `PortRealisation.lean`, `Layered.lean`,
`Reindex.lean`, `Substitutions.lean` and `TerminalCodes.lean`. This is the framework of the
repository. It generalises the valid-tuple ⋆-product of the v1 paper.

**Separation system.** BPZ use the alphabet {B, N, A, D, O, H, V} with the symmetric,
irreflexive relation `Letter.sep` (`PortRealisation.lean:37`). A *realisation* in a graph G
assigns to each letter a an independent set P_a, such that P_a and P_b are separated whenever
sep(a, b) holds. The *weight* of a is w_a = |P_a|.

**Base.** For each n ∈ {15, 19}, BPZ give a `RichPortSystem` (I, ports, ep, side, X) in
G4 = C_n^⊠4 (`BaseC15.lean`, `BaseC19.lean`). Its seven families form a realisation R1 with
weights:

* C15: (B, N, A, D, O, H, V) = (2839, 2833, 6, 3, 3, 3, 3), from the 2842-set of De Boer, Buys
  and Zuiddam.
* C19: (7664, 7661, 3, 2, 2, 2, 2), from the 7666-set of Baumert et al. and Codenotti, Gerace
  and Resta.

`Rf` is R1 reindexed by BPZ's σ = (A D)(H V) (`Reindex.lean`). For C15 this swaps the A and D
weights 6 and 3.

**Substitution.** An admissible table S of arity q (`Layered.lean:89`, `Subst`) assigns to each
letter a set of words T(a) ⊆ {B,…,V}^q. A node S(c_1,…,c_q) applies BPZ's
`Realisation.multiSubst` to children of exponents e_i. It is a realisation in G4^⊠(Σe_i), with
weights

  w_a = Σ_{x ∈ T(a)} Π_i w^{(i)}_{x_i}   (`w_multiSubst`).

We use only five of BPZ's tables: S2a (20 words), S3a (58), S3e (53), S3f (47) and S3g (47).

**Terminal code.** For BPZ's 57-word code K4b (`TerminalCodes.lean`) applied to four nodes,
`le_indepNum_multiCode` gives an independent set of size
M = Σ_{x∈K4b} Π_{i=1}^{4} w^{(i)}_{x_i} in G4^⊠E, with E = Σ e_i. So p = 4E.

**Tails.** For a start node y_0, write J × [y ← S3g(y, R1, R1)] for the J-fold iteration
y_{k+1} = S3g(y_k, R1, R1). Each step raises the exponent by 2.

**Schedules.** Both schedules are DAGs. A shared sub-schedule is computed once.

* **C15** (`CertC15b`) has 20 nodes. A tower of S3f/S3e nodes reaches exponent 27. One S2a(R1, Rf)
  node is used. Four tails, of lengths 63, 3, 5 and 19, are merged back through S3g. K4b is
  applied to nodes of exponents (314, 147, 169, 226), so E = 856 and p = 3424. BPZ's `CertC15`
  has 23 nodes, uses S3e/S3f/S3g with K4b, and has E = 916 and p = 3664.
* **C19** (`CertC19c`) has 26 nodes. An S3f tower reaches exponent 81. Two shoulder nodes,
  S3a(n3, n2, R1) and S3e(n3, n2, R1), each have exponent 109. Four branches follow. Each branch
  merges a tail from the S3a node with a tail from the S3e node, of lengths (265, 193),
  (153, 52), (177, 68) and (230, 80). Each branch is then closed by S3g with the tower nodes or
  R1. K4b is applied to exponents (1245, 713, 793, 949), so E = 3700 and p = 14800. BPZ's
  `CertC19` uses S3f/S3g/S3d with K4b on four copies of an exponent-741 node, so E = 2964 and
  p = 11856.

The appendix gives both schedules in full. The machine-readable versions are
`schedules/best_C15_A_ref.json` and `schedules/best_C19_C_ref.json`. They are identical to
`lanes/O_opt/best_C15_A_ref.json` and `best_C19_C_ref.json`, with sha256 `6a37e3c9…` and
`df340f3f…`.

**Lean encoding.** The patch adds `DagTail.lean`, a generic helper. It defines `tailIter` by
structural recursion on J and proves `w_tailIter` by induction. These proofs use ordinary tactics,
not `native_decide`, and use only `multiSubst` and `w_multiSubst` from BPZ's `Layered.lean`.
No node size is written as a literal. Each node's size record is computed from its children's.
The single literal M is checked against the terminal sum by one `native_decide` (`stepM`).

## 4. Verification

1. **Lean certificate, as a patch on BPZ.** `certL2.patch` (sha256 `ee71e471…ce448e`) applies to
   `aa21eeb`. It adds `DagTail`, `CertC15b`, `CapCertC15b`, `CertC19c` and `CapCertC19c`, plus
   five import lines in `ShannonBounds.lean`. It changes no BPZ proof, and BPZ's own C15 and C19
   theorems still build alongside ours. We used Lean 4.32.2 and Mathlib `905b9581…`, both as
   pinned by BPZ.
2. **Axioms.** `#print axioms` on each main theorem lists `propext`, `Classical.choice`,
   `Quot.sound` and 40 `native_decide` auxiliary axioms, with no `sorryAx`. Compared with BPZ's
   certificates, the only new native checks are `stepM` (the value of M) and the decimal step.
   The rest are BPZ's own checks of the base data, the tables S2a/S3a/S3e/S3f/S3g and K4b.
   **Trust base:** as in BPZ, the Lean kernel plus the compiled evaluation behind `native_decide`.
3. **Negative control.** We replaced M by M+1 in the C15 certificate. Lean then rejects the file:
   "Tactic `native_decide` evaluated that the proposition … is false".
4. **Independent re-derivation in Python.** `eval_dag.py` uses only the standard library. A
   separate agent lane wrote it without reading the search or generator code. It re-parses BPZ's
   Lean sources and re-checks:
   * the admissibility of all ten tables and three codes;
   * every `RichPortSystem` field;
   * the base weights.

   As positive controls, it reproduces BPZ's `CertC7`, `CertC15` and `CertC19` digit for digit.
   It also reproduces our two M values digit for digit. Its own negative controls (perturbed
   tables, codes, σ and schedules) are all rejected. The Lean check does not depend on this
   evaluator.
5. **Several machines.** The check passed on three machines:
   * an Apple M4 Pro laptop;
   * a Mac mini M4, from a fresh GitHub clone;
   * a clean-room Ubuntu 24.04 x86_64 desktop with no prior Lean or Mathlib. There the
     one-command bundle installed elan and passed on its first run (16 min).
6. **Red-team review.** An adversarial lane checked:
   * the theorem statements with explicit elaboration, with the supremum unfolded and the
     strong-product adjacency checked by `Iff.rfl`;
   * the patch scope;
   * for trust holes, finding no `implemented_by`, `extern`, `unsafe`, `opaque`, `axiom`,
     `macro` or `#eval`;
   * the exact truncation;
   * whether any limit proved by BPZ dominates our values.

   It found no mathematical flaw. Its remaining points are in Section 7.

## 5. Reproducibility

```sh
cd shannon-C15-C19 && sh check.sh --install-elan
```

The script:

* checks the hashes of the bundle files;
* clones BPZ's repository and checks out `aa21eeb`;
* applies the patch and confirms that it only adds files and import lines;
* runs the Python evaluator, including BPZ's certificates as controls;
* builds with `lake`;
* re-type-checks both statements verbatim in a fresh Lean process and prints their axioms;
* greps for `sorry` and `admit`.

It ends with `ALL CHECKS PASSED` (exit 0). It needs a POSIX shell, git, curl, python3 ≥ 3.8 and
about 8 GB of disk.

**Provenance.** The research repository has the annotated tag `c15-c19-record-v1` (tag object
`7c2dff03…`) on commit `5737f31a6afb08c579c042b5c03991fe3d703057`, which contains `certL2.patch`.
An earlier tag, `c19-record-v1` on `86c62d94…`, holds a first C19 certificate,
Θ(C19) ≥ 9.357202700233073, which the result here supersedes. The clean-room bundle directory
Public release: https://github.com/griffinwork40/shannon-capacity-c15-c19, tag `v1.0`, which
contains the bundle (`artifact/`), its tarball (`dist/`, with its SHA-256), the proof sources, the
logs, the review and novelty reports, and this note. The research repository itself (with the full
working history) is not public; `PROVENANCE.md` maps every released file to it by commit and hash.

## 6. How the schedules were found

The schedules came from an automated search inside BPZ's schedule grammar. The only atoms were
R1 and Rf, nodes S(c_1,…,c_q) for BPZ's tables, J-fold tails, and a terminal BPZ code. The search
had two stages:

* beam search and simulated annealing, scored in floating point, with the total exponent bounded
  by BPZ's;
* local refinement of tail lengths, followed by exact integer re-evaluation.

The search ran for minutes per job on ordinary machines, with no paid compute. It is not part of
the trust base. A schedule is just data, and Lean and the Python evaluator check it.

**Use of AI and software.** Griffin Long is the sole author. The computational work, the
certificates and the first draft of this note were produced by **agent-afk**, an open-source
autonomous agent runtime written by the author (github.com/griffinwork40/agent-afk). The agent
chose the target, wrote the schedule search, the Lean generator and certificates, both checkers
and the draft. AI systems are credited here rather than as authors.

AI models used through agent-afk (Anthropic):

* Claude Opus, model id `claude-opus-5-5`: coordinator of both working sessions (2026-09-30 and
  2026-10-01), and most subagent lanes (baseline reproduction, schedule search, Lean
  certification, independent review, red-team review, novelty search, packaging, drafting).
* Claude Sonnet, model id `claude-sonnet-4-6`: some lanes (an early literature check, the
  second-machine rerun, finishing an audit report, a repository status survey).
* Claude Haiku, model id `claude-haiku-4-5-20251001`: one read-only repository survey.

OpenAI ChatGPT wrote the original task brief given to the agent and, after the result was found,
suggested the verification and disclosure plan that was followed; it contributed no mathematical
content, code or schedules.

Software: Lean 4 (v4.32.2), Mathlib, Lake and elan; Python 3 (standard library only for the
checkers; NumPy in exploratory scripts); Google OR-Tools CP-SAT (an earlier, unsuccessful C7
search); LaTeX; Git and the GitHub CLI; Exa web search and the arXiv, Semantic Scholar, OpenAlex,
Zenodo and GitHub APIs for the literature search.

The author's inputs are logged in `HUMAN_INPUT.md`:

* a goal statement;
* hardware (three machines);
* a lane-parallel working style;
* approval of the agent's wave plans;
* "continue/proceed" messages;
* a forwarded plan for hardening and reporting the result;
* the decision to disclose, and review of this text.

No human supplied mathematical content, schedules or code. We report this to describe the
method, not as a claim about it. The search is a straightforward local search, and its success
mainly shows that BPZ's schedule space was not exhausted. The literature check covered arXiv
(API and listings), Semantic Scholar, OpenAlex, Zenodo, GitHub (repositories, code, issues,
forks), author pages, Wikipedia, MathOverflow and OEIS, up to 2026-10-01. It did not cover
Google Scholar, the Lean Zulip (we could only reach its public archive through web search), or
unpublished work.

## 7. Remarks: what is not new, and residual risks

**Not new.** Every ingredient is due to others:

* the framework, tables, terminal codes and Lean infrastructure (BPZ, building on Gao and on
  Itty–Rosin–Carstensen–Reichman);
* the base independent sets (Baumert, McEliece, Rodemich, Rumsey, Stanley and Taylor 1971;
  Codenotti, Gerace and Resta 2003; De Boer, Buys and Zuiddam).

We introduce no new method. `DagTail.lean` is a convenience for writing long tails compactly.

**Size of the gain.** The gains are 6.3·10⁻⁶ for C15 and 3.0·10⁻⁶ for C19, or 8.6·10⁻⁷ and
3.2·10⁻⁷ in log Θ. For comparison, BPZ's repository improved on their v1 paper by
2.8·10⁻⁵ (C15) and 7.3·10⁻⁶ (C19). Our gains are about a fifth and two fifths of those steps. The Lovász bounds (7.4171 and 9.4348) remain far away. The schedules are not
claimed to be optimal, and further search within BPZ's grammar would probably improve them. A
side remark: the asymptotic rates of the families our tails use, and of BPZ-style homogeneous
towers, are below both BPZ's values and ours. These rates are 9.357148 and 7.301474 for the tail
family S3g(y, R1, R1), and 9.3571998 and 7.3016276 for the best homogeneous towers. So the gain
comes from finite mixing, not from a better limit.

**Residual risks a referee may raise.**

1. *Trust in `native_decide`.* Our certificate relies on the compiler, as BPZ's do. The kernel
   alone does not check the large-integer evaluations.
2. *Checker hardening (fixed).* The red-team review showed that an axiom declared by hand with a
   name matching `*._native.native_decide.ax_*` would have passed the axiom-name filter.
   `check.sh` now also rejects `axiom`, `unsafe`, `opaque`, `implemented_by`, `extern`, `csimp`,
   macros and `#eval` in the added files.
3. *Attribution in file headers (fixed).* The five new files initially inherited BPZ's copyright
   and author header. They now state that they were contributed by Griffin Long with agent-afk,
   as an addition to BPZ's framework, and that BPZ did not write them (Apache-2.0).
4. *Novelty.* BPZ have said improved trees will appear in their next arXiv version. Unpublished
   BPZ work, or other parallel work, could match or beat these bounds. Our search did not cover
   Google Scholar or private channels.
5. *Independence of verification.* The Python evaluator was written by another instance of the
   same AI system, not by an independent human. All three machines belong to one person. No
   external party has reproduced the result yet. An external reproduction is what the
   accompanying email requests.
6. *Interest.* Improvements in the sixth decimal from re-ordering known gadgets are of limited
   mathematical interest by themselves. The defensible contribution is the certified values plus
   a reproducible, fully mechanised workflow.

## Acknowledgements

We thank Pjotr Buys, Sven Polak and Jeroen Zuiddam for releasing their Lean framework openly.
This note would not exist without it. Their repository is under the Apache License 2.0. Our patch
is a derivative work and is offered under the same licence. The use of AI models and software is
described in the methodology section above.

## References

* [BMR+71] L. D. Baumert, R. J. McEliece, E. Rodemich, H. C. Rumsey Jr., R. Stanley, H. Taylor. A combinatorial packing problem. In *Computers in Algebra and Number Theory* (Proc. SIAM-AMS Sympos. Appl. Math., New York, 1970), SIAM-AMS Proc., Vol. IV, pp. 97–108. Amer. Math. Soc., Providence, RI, 1971. Zbl 0252.05016.
* [BPZ26] P. Buys, S. Polak, J. Zuiddam. Lean-verified lower bounds for the Shannon capacity of odd cycles. arXiv:2607.29681 (v1, 2026-07-31). Lean repository: github.com/spectra-research/shannon-capacity-lean, commit `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10).
* [CGR03] B. Codenotti, I. Gerace, G. Resta. Some remarks on the Shannon capacity of odd cycles. *Ars Combinatoria* 66 (2003) 243–257. Zbl 1073.05544.
* [dBBZ24] D. de Boer, P. Buys, J. Zuiddam. The asymptotic spectrum distance, graph limits, and the Shannon capacity. arXiv:2404.16763 (v1 2024, v2 2026).
* [Gao26] Y. Gao. A recursive construction improving the lower bound on the Shannon capacity of C7. arXiv:2607.27869 (2026).
* [IRCR26] N. Itty, C. D. Rosin, C. Carstensen, D. Reichman. Improved lower bounds for the Shannon capacity of odd cycles. arXiv:2607.21517 (v2, 2026).
* [Lov79] L. Lovász. On the Shannon capacity of a graph. *IEEE Trans. Inform. Theory* 25(1) (1979) 1–7. doi:10.1109/TIT.1979.1055985.
* [Sha56] C. E. Shannon. The zero error capacity of a noisy channel. *IRE Trans. Inform. Theory* 2(3) (1956) 8–19. doi:10.1109/TIT.1956.1056798.

## Appendix A. Schedules in full

The exponents are in brackets. R1 and Rf have exponent 1. Every exponent is in units of G4 = C_n^⊠4.

### C15 (`CertC15b`)

```
n0  = S3f(R1, R1, R1)                          [3]
n1  = S3e(R1, R1, R1)                          [3]
n2  = S3f(n0, n1, n0)                          [9]
n3  = S3f(n0, n0, n0)                          [9]
n4  = S3f(n2, n3, n3)                          [27]
n5  = S3g(n4, R1, n4)                          [55]
n6  = S2a(R1, Rf)                              [2]
n7  = S3f(n3, R1, n3)                          [19]
n8  = S3g(n5, n6, n7)                          [76]
n9  = 63 x [y <- S3g(y, R1, R1)] from y = n5   [181]
n10 = S3g(n5, R1, n9)                          [237]
n11 = S3g(n8, R1, n10)                         [314]
n12 = 3 x [y <- S3g(y, R1, R1)] from y = n5    [61]
n13 = S3g(n5, R1, n12)                         [117]
n14 = 5 x [y <- S3g(y, R1, R1)] from y = n13   [127]
n15 = S3g(n14, n7, R1)                         [147]
n16 = 19 x [y <- S3g(y, R1, R1)] from y = n5   [93]
n17 = S3g(n5, R1, n16)                         [149]
n18 = S3g(n17, n7, R1)                         [169]
n19 = S3g(n8, R1, n17)                         [226]
M   = K4b(n11, n15, n18, n19)                  E = 856, p = 3424
```

M has 2957 digits. It begins with 22412415576865115264 and ends with 79776353377970664416. The
sha256 of its decimal string is `34e07ce8…a5d3ad33`.

### C19 (`CertC19c`)

```
n0  = S3f(R1, R1, R1)                          [3]
n1  = S3f(n0, n0, n0)                          [9]
n2  = S3f(n1, n1, n1)                          [27]
n3  = S3f(n2, n2, n2)                          [81]
n4  = S3a(n3, n2, R1)                          [109]
n5  = 265 x [y <- S3g(y, R1, R1)] from y = n4  [639]
n6  = S3e(n3, n2, R1)                          [109]
n7  = 193 x [y <- S3g(y, R1, R1)] from y = n6  [495]
n8  = S3g(n5, R1, n7)                          [1135]
n9  = S3g(n8, R1, n3)                          [1217]
n10 = S3g(n9, R1, n2)                          [1245]
n11 = 153 x [y <- S3g(y, R1, R1)] from y = n4  [415]
n12 = 52 x [y <- S3g(y, R1, R1)] from y = n6   [213]
n13 = S3g(n11, R1, n12)                        [629]
n14 = S3g(n13, R1, n3)                         [711]
n15 = S3g(n14, R1, R1)                         [713]
n16 = 177 x [y <- S3g(y, R1, R1)] from y = n4  [463]
n17 = 68 x [y <- S3g(y, R1, R1)] from y = n6   [245]
n18 = S3g(n16, R1, n17)                        [709]
n19 = S3g(n18, R1, n3)                         [791]
n20 = S3g(n19, R1, R1)                         [793]
n21 = 230 x [y <- S3g(y, R1, R1)] from y = n4  [569]
n22 = 80 x [y <- S3g(y, R1, R1)] from y = n6   [269]
n23 = S3g(n21, R1, n22)                        [839]
n24 = S3g(n23, R1, n3)                         [921]
n25 = S3g(n24, R1, n2)                         [949]
M   = K4b(n10, n15, n20, n25)                  E = 3700, p = 14800
```

M has 14373 digits. It begins with 91531227246421702821 and ends with 35690099930718797824. The
sha256 of its decimal string is `ac85cbc5…bfa8203d`.
