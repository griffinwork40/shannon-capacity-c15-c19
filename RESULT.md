# Result of discovery attempt 2 (2026-10-01)

*Public edition for the release repository. Paths are relative to this repository unless marked
"research repository" (private; see `PROVENANCE.md`). Mathematical content is unchanged.*

**In plain words.** The Shannon capacity of a graph is the most information per symbol that can
be sent over a noisy channel without any chance of confusion. For odd cycles C_n with n >= 7 it
is unknown. The best lower bounds come from very large explicit independent sets. In July and
August 2026, Buys, Polak and Zuiddam (BPZ) published record lower bounds for several odd cycles,
proved in Lean (a proof checker). agent-afk found better bounds for C15 and C19. It reused BPZ's
own building blocks and assembled them with a better recipe (substitution schedule). The new
proofs are checked by the same proof checker, in BPZ's own framework, and anyone can rerun the
check with one command.

| n | prior best (quoted) | new, Lean-certified | package |
|---|---|---|---|
| 19 | 9.357200030000796 (BPZ Lean repo README, row n=19, commit aa21eeb, 2026-08-10) | **9.357203012726939** (CapCertC19c); also 9.357202700233073 (CapCertC19b) | `artifact/` (C19b: research repository `artifacts/C19/`) |
| 15 | 7.301628695930103 (BPZ Lean repo README, row n=15, commit aa21eeb) | **7.301635000991096** (CapCertC15b) | `artifact/` |

BPZ README quote: "| 15 | 7.301628695930103 | 3664 | 3164 |" and "| 19 | 9.357200030000796 | 11856 | 11514 |"
(github.com/spectra-research/shannon-capacity-lean). The paper arXiv:2607.29681 v1 states weaker
values (C19: 9.357192705918...).

## How to check (no trust in us required)
* **Canonical bundle: `artifact/`** (self-contained; see its README.md and ENVIRONMENT.md; also
  packed as `dist/shannon-C15-C19-v1.0.tar.gz`). `cd artifact && sh check.sh --install-elan` does
  the Lean check and the independent Python check from a fresh clone of BPZ's repo. It clones
  BPZ's public repo at aa21eeb, checks and applies `certL2.patch` (it only adds files and import
  lines), builds with Lean 4.32.2 + Mathlib, re-checks both theorem statements, and rejects
  `sorry` and any axiom other than the standard ones and `native_decide`. It passed in a clean
  room (Linux box with no Lean, no caches, fresh HOME).
* Older packages (research repository only, kept there for history): `artifacts/C15_C19c/`
  (predecessor checker for the same two certificates, Lean only) and `artifacts/C19/` (first C19
  certificate CapCertC19b, Θ(C19) ≥ 9.357202700233073).
* Theorem statements (verbatim):
  `(9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)` and
  `(7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15)`.
* Trust base: the Lean kernel plus `native_decide` (the compiler evaluates large-integer facts).
  BPZ's own certificates have the same trust base.

## Verification performed (PLAYBOOK section 8)
1. Fixed checker: Lean builds in BPZ's framework (laptop). Negative control: replacing M by M+1
   makes Lean reject the file (`logs/laptop_build_neg_C15b.log`; research repository
   `lanes/L_lean/build_negative.log` for the earlier C19b certificate).
2. Independent checkers: stdlib Python evaluators written by reviewer lanes that did not read the
   search code (research repository lanes/R_review; `review/independent_evaluator/REPORT.md`). They reproduce BPZ's own CertC15/CertC19 exactly
   as positive controls, and their M equals the Lean literal M digit for digit.
3. Second machine: a fresh GitHub clone on a Mac mini builds all three certificates
   (`review/second_machine/REPORT.md`, `logs/mac_mini_build_c15b.log`, `logs/mac_mini_build_c19c.log`).
4. One-command check: ALL CHECKS PASSED in a clean room (Linux, empty HOME: no Lean, no caches;
   `logs/check_run_desk_linux.log`). An earlier laptop run used the predecessor script, which had
   the same Lean steps but no Python step (`logs/check_run_laptop.log`).
5. Literature re-check (research repository lanes/N_novelty/REPORT.md, 2026-09-30): BPZ HEAD is still aa21eeb, and
   arXiv 2607.29681 is still v1. The only newer work found (M. Protti's repo, 2026-09-09) covers
   C11 and C13 only. No C15 or C19 bound newer than BPZ was found. Not accessible: Google
   Scholar. Unpublished work cannot be ruled out.

## Adversarial review and novelty search (2026-10-01)
* Red team (`review/red_team/REPORT.md`), told only to kill the result: SURVIVES on theorem
  statement, trust holes, patch scope, precision, and dominated baseline. The supremum rates of
  the tail families used are below BPZ's finite bounds, and BPZ states no asymptotic bound. Fixes
  applied: the added Lean files no longer carry BPZ author headers, and check.sh now rejects
  `axiom`/`unsafe`/`implemented_by`/`extern`/macros in the added files (the red team had shown
  that a spoofed axiom named like a native_decide axiom would have passed the old filter).
* Novelty search (`review/novelty/REPORT.md`: arXiv API, Semantic Scholar, OpenAlex, Zenodo,
  GitHub incl. forks/issues/branches, author pages, Wikipedia, MathOverflow, OEIS, AI-lab
  announcements): nothing at or above our bounds. Main residual risk: BPZ's README says improved
  product trees "will appear in the next arXiv version".
* Not yet done: reproduction by an external mathematician. Draft note: `paper/note.md`. An email to BPZ is drafted
  in the research repository (NOT SENT).

## What is new, and what is not
* New: the substitution schedules (towers, plus long tails merged in several branches), found by
  an automated search (research repository lanes/G_c19_baseline and lanes/O_opt; the scripts
  that produced the two winning schedules are in `method/`) over BPZ's existing tables, codes and
  base sets. A generic Lean tail-iteration lemma (DagTail.lean) keeps the certificates small.
* Not new: the base sets, the tables, and the framework (BPZ; Baumert et al. 1971; Codenotti,
  Gerace and Resta 2003; Polak-Schrijver). The gains are small (C19 +3.0e-6, C15 +6.3e-6), and
  they mainly show that BPZ's schedule space was not exhausted.
* Side fact: alpha(C19^4) = 7666 exactly (the BPZ base is maximum). The upper bound is
  floor(19 * floor(19 * floor(19*9/2)/2)/2) = 7666 (research repository lanes/G_c19_baseline/check_base.log). So no
  larger base set exists in C19^4. A different 7666-set with a better port system (more private
  pairs, or a different X) could still change the starting family sizes; that was not explored.
* Exhaustive or empirical statements: none are claimed. The results are proofs.

## What failed or was dropped
* C17 (attempt-2 primary target): killed before any search. A classical code gives
  17^(3/4) > sqrt(68) (research repository HANDOFF_attempt2.md).
* C7, C23: no gain from BPZ's rules (research repository lanes/O_opt). C7 stays below Tandon's 3.258832620353266.
* C11, C13: float-only leads from lane O. C13 6.3029270716 may exceed Protti's 6.302927046770772,
  but it has not been exactly evaluated or certified (open lead).
* Moonshot (second 367-set of C7^5): the Lane F model was audited and found SOUND
  (research repository lanes/F_audit/REPORT.md), but it only rules out small neighbourhoods. No new search was run.

## Provenance
The agent (agent-afk, Claude Opus coordinator, session c69cb5b2-7e4d-431c-905e-0821bf90f5b8)
chose the lanes and built the search, the evaluators and the Lean certificates. Human input is
listed in HUMAN_INPUT.md: the goal statement, `/gather`, a resume after a usage limit, and "whatever u
think is best proceed". BPZ's work, data and Lean framework are the foundation. Research-repository commits and tags:
see `PROVENANCE.md`.
