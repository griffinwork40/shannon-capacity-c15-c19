# New lower bounds for the Shannon capacity of the 15-cycle and the 19-cycle, checked in Lean

**In plain language.** Picture a communication channel whose symbols sit in a ring, where each
symbol can be mistaken for its two neighbours. Its *Shannon capacity* is the number of symbols
per use that can effectively be sent with zero chance of confusion, once long code words are
allowed. For rings of 15 and 19 symbols nobody knows the exact value. Researchers compete on
proving guaranteed lower bounds. In August 2026, Buys, Polak and Zuiddam (BPZ) proved
7.301628695930103 for 15 symbols and 9.357200030000796 for 19 symbols, and had the proofs
checked mechanically in the Lean proof assistant. We prove the larger bounds
**7.301635000991096** (15 symbols) and **9.357203012726939** (19 symbols), using BPZ's own Lean
framework and building blocks combined in a different order. A computer checks the proofs, so
you do not have to trust us. One command downloads BPZ's public code, adds our five files, has Lean
verify both results, and re-derives both numbers with an independent Python program. The improvements are small (about 6.3 millionths for 15 and about
3.0 millionths for 19), which is typical for this problem. They are still strict improvements on
the best published certified values we could find.

---

## Check it (one command)

Copy this directory anywhere (or unpack `dist/shannon-C15-C19-v1.0.tar.gz` of the release repository), then:

```sh
cd shannon-C15-C19 && sh check.sh --install-elan
```

That is all. Prerequisites: a POSIX shell, `git`, `curl`, `python3` (3.8 or newer, stdlib only),
`sha256sum` or `shasum`, about 8 GB of free disk, and network access to github.com and the Mathlib
build cache. Nothing else needs to be installed: `--install-elan` runs the official Lean installer
(elan) with `--no-modify-path` if `lake` is not already present, and elan then fetches the Lean
version pinned by BPZ (v4.32.2). If you already have elan, drop the flag. Use `--dir DIR` to choose
the work directory (default `./c15-c19-check`; it must not already contain a clone). The script never
deletes anything and never edits your shell profile. Expect 10 to 30 minutes, mostly downloading
Lean and the prebuilt Mathlib cache.

A passing run ends with:

```
ALL CHECKS PASSED (Lean 4 build + statements + axioms, and independent Python with exact BPZ controls)
  Theta(C15) >= 7.301635000991096   [ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge; BPZ: 7.301628695930103]
  Theta(C19) >= 9.357203012726939   [ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge; BPZ: 9.357200030000796]
```

and exit code 0. Any failure prints `CHECK FAILED: <reason>` and exits nonzero (exit 3 means only
that `lake` was not found and `--install-elan` was not given).

### What the script does

0. Checks the SHA-256 of every bundle file (`certL2.patch` = `ee71e471…`, `eval_dag.py`, both schedules).
1. Clones BPZ's repository fresh and checks out commit `aa21eeb`.
2. Applies `certL2.patch`, checks the SHA-256 of the five new Lean files, and checks that the only
   change to any existing BPZ file is five added `import` lines.
3. **Python.** Runs `eval_dag.py` (stdlib only) on the fresh clone. It re-derives the substitution
   tables, terminal codes, separation relation and base family sizes from BPZ's Lean sources,
   must reproduce BPZ's own CertC15 (7.301628695930103) and CertC19 (9.357200030000796) exactly,
   evaluates `schedules/*.json`, and its `M` must equal the Lean literals `CertC15b.M` and
   `CertC19c.M` digit for digit (the script compares the digits with `cmp` and checks their SHA-256).
4. Finds `lake` (installing elan if asked) and checks it runs Lean 4.32.2.
5. `lake exe cache get` (prebuilt Mathlib), then `lake build ShannonBounds.CapCertC15b ShannonBounds.CapCertC19c`.
6. In a fresh Lean process, re-type-checks both theorem statements verbatim, prints
   `#print ShannonBounds.shannonCapacity`, and runs `#print axioms`; fails on `sorryAx` or on any
   axiom other than `propext`, `Classical.choice`, `Quot.sound` and `native_decide` auxiliaries.
7. Greps all Lean sources for `sorry` / `admit`.

Knobs: `LEAN_NUM_THREADS` (default 4), `NICE` (default 5). Machines, OSes, versions and dates of
passing runs: `ENVIRONMENT.md`. Full logs of passing runs: `check_run_*.log`.

## Theorems (verbatim)

`ShannonBounds/CapCertC15b.lean`:

```lean
/-- **`Theta (cycleGraph 15) >= 7.301635000991096`**. -/
theorem shannonCapacity_cycleGraph_15_ge :
    (7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15)
```

`ShannonBounds/CapCertC19c.lean`:

```lean
/-- **`Theta (cycleGraph 19) >= 9.357203012726939`**. -/
theorem shannonCapacity_cycleGraph_19_ge :
    (9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)
```

Full names: `ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge` and
`ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge`. `shannonCapacity` is BPZ's
definition in `ShannonBounds/Defs.lean`, unchanged: `⨆ n, α(G^⊠(n+1))^(1/(n+1))`, where `α` is
the independence number and `⊠` is the strong product. `cycleGraph` is Mathlib's definition.
These are the same objects BPZ's `Main.lean` uses.

The same files also prove, for each cycle (`(n, p, digits of M)` = `(15, 3424, 2957)` and
`(19, 14800, 14373)`):
* `alpha_strongPower_ge : M ≤ α(C_n^⊠p)`, where `M` is an explicit integer literal
  (`CertC15b.M`, `CertC19c.M`);
* `shannonCapacity_Cyc_ge : M^(1/p) ≤ Θ(C_n)`, the exact form;
* `tight : a^p ≤ M·10^(15·p) < (a+1)^p` with `a = 7301635000991096` resp. `9357203012726939`,
  which shows that each decimal is the exact truncation of `M^(1/p)` to 15 places;
* `improves`: `(7.301628695930103 : ℝ) < 7.301635000991096` and
  `(9.357200030000796 : ℝ) < 9.357203012726939`; for C19 also `improves_1`:
  `(9.357202700233073 : ℝ) < 9.357203012726939`.

## Prior bounds

* **BPZ Lean repository**: https://github.com/spectra-research/shannon-capacity-lean, commit
  `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10, "Update the bounds"). This was still the
  repository HEAD when last checked, on 2026-10-01. The README table rows read:
  > `| 15 | 7.301628695930103 | 3664 | 3164 |`
  >
  > `| 19 | 9.357200030000796 | 11856 | 11514 |`

  `ShannonBounds/Main.lean` states these as `shannonCapacity_cycleGraph_15_ge` and
  `shannonCapacity_cycleGraph_19_ge`.
* **BPZ paper**, arXiv:2607.29681 v1 (2026-07-31, the only version). The abstract states
  > "Θ(C15) ≥ 7.301600534487 . . ., Θ(C19) ≥ 9.357192705918 . . ."

  (https://arxiv.org/abs/2607.29681v1). The repository README says its bounds "are stronger than those in
  its first version", so the repository values above are the ones to beat.
* **Our own earlier C19 result**, research repository `artifacts/C19/` (`CapCertC19b`, not yet published; see `../PROVENANCE.md`):
  Θ(C19) ≥ 9.357202700233073. The new C19 bound exceeds it by about 3.1·10⁻⁷. The patch here is
  independent of `certC19b.patch`; it applies on its own to `aa21eeb`.
* **Literature check, 2026-09-30** (research repository `lanes/N_novelty/REPORT.md`; the later 2026-10-01 search is `../review/novelty/REPORT.md`). We searched GitHub, arXiv
  listings and the API, and Semantic Scholar citations of 2607.29681. For both C15 and C19 the
  best bound found is BPZ's `aa21eeb` value. Protti's repository (2026-09-09) covers only C11
  and C13. Tandon (arXiv:2608.30273) covers only C7. Google Scholar and paywalled venues were not
  searched.

## What is new

Only the *substitution schedules* are new. The base independent sets, the substitution tables,
the terminal codes and the Lean framework are all BPZ's, used unchanged. The schedules were found
by an automated search (lane O: simulated annealing over schedule DAGs, scored exactly) that uses
only BPZ's own substitution tables (S2a, S3a, S3e, S3f, S3g), terminal code K4b, the reindexing
`sigma`, and BPZ's base data. The schedules are in `schedules/` (byte-identical copies of `lanes/O_opt/best_C15_A_ref.json` and
`lanes/O_opt/best_C19_C_ref.json` in the research repository); the Lean files were generated from them by
`../method/lanes/L2_lean/gen_dag.py`, which re-evaluates `M` with its own evaluator and cross-checks it
against lane O's exact evaluator.

* **C15** (`CertC15b`): 20 distinct nodes, 4 of them iterated tails `y ↦ S3g(y, R1, R1)` of
  lengths 63, 3, 5 and 19; terminal code K4b on nodes of exponents (314, 147, 169, 226), so
  E = 856 in `G4 = C15^⊠4`, dimension p = 3424. (BPZ: 23 nodes, a 57-word code, p = 3664.)
* **C19** (`CertC19c`): 26 distinct nodes, 8 of them tails `y ↦ S3g(y, R1, R1)` of lengths 265,
  193, 153, 52, 177, 68, 230 and 80; terminal code K4b on nodes of exponents
  (1245, 713, 793, 949), so E = 3700 in `G4 = C19^⊠4`, dimension p = 14800. (BPZ: p = 11856;
  our CapCertC19b: one 415-step tail, p = 14576.)

The full schedules are written out in the header comment of each `Cert*.lean` file.

In Lean, a shared sub-schedule is defined once and reused. Each tail is one structural recursion
(`DagTail.tailIter`), and a kernel-checked induction (`DagTail.w_tailIter`, ordinary tactics, no
`native_decide`) ties its realisation to a size recursion. Node sizes are never written as
literals: each node carries a `Sizes` value computed from its children's, and the single literal
`M` is checked against the terminal sum by one `native_decide` (`stepM`). `DagTail.lean` is a
generic helper file; it uses only `Realisation.multiSubst` and `w_multiSubst` from BPZ's
`Layered.lean`.

The patch adds `ShannonBounds/{DagTail,CertC15b,CapCertC15b,CertC19c,CapCertC19c}.lean` plus five
import lines in `ShannonBounds.lean`. It modifies no existing BPZ proof, and BPZ's own C15 and
C19 theorems still build next to the new ones.

## Trust base

Trust is the same as for every BPZ certificate:
* the Lean 4 kernel (v4.32.2) and Mathlib at the pinned revision;
* **`native_decide`**: the finite checks are run as compiled code, with GMP-backed `Nat`
  arithmetic, and are not re-checked by the kernel. `#print axioms` lists, for each theorem,
  `propext`, `Classical.choice`, `Quot.sound` and 40 `…._native.native_decide.ax_*` auxiliary
  axioms, and no `sorryAx`. The new files add native axioms only in `CertC15b.stepM`,
  `CertC19c.stepM` (the value of `M`) and in the two capacity theorems (the decimal bracket).
  All others come from BPZ's own BaseC15 / BaseC19 checks, the tables S2a, S3a, S3e, S3f, S3g,
  and the code K4b.
* the two definitions in the statements (BPZ's `shannonCapacity`, Mathlib's `cycleGraph`).
  `#print ShannonBounds.shannonCapacity` is shown in the log for inspection.

Negative control, done during development (`../logs/laptop_build_neg_C15b.log`): with `M+1`
in place of `M` in the C15 certificate, Lean rejects the file ("Tactic `native_decide` evaluated
that the proposition … is false").

Independent (non-Lean) reproduction, step 3 of `check.sh`: `eval_dag.py` (stdlib-only Python, written by a reviewer
lane that did not read the search or generator code; `../review/independent_evaluator/REPORT.md`) re-derives the
tables, codes, separation relation and base family sizes from BPZ's Lean sources, reproduces
BPZ's own CertC15 (7.301628695930103) and CertC19 (9.357200030000796) exactly as positive
controls, and evaluates both new schedules to the same `M` as the Lean literals, digit for digit.
The Lean check does not depend on it.

## What is NOT claimed

* Not the values of Θ(C15) or Θ(C19). These are lower bounds only. The best upper bounds
  (Lovász theta, about 7.417 for C15 and 9.435 for C19) are far away.
* Not a new mathematical method. The method, framework, base sets, tables and codes are BPZ's
  (see arXiv:2607.29681 and their repo). The contribution is better schedules and their
  certificates.
* Not "previously thought impossible". The defensible claim is "not previously achieved (as far
  as our literature check found), found by an autonomous agent, and checkable without trusting
  us".
* Not kernel-only. As with BPZ, `native_decide` is trusted.
* Not optimal schedules. The search was bounded in time and total exponent; other schedules may
  do better.
* No claim of novelty against sources we could not search (Google Scholar, private preprints).
  BPZ may hold stronger unpublished bounds.

## Provenance

Paths of the form `lanes/...` below and above refer to the private research repository (tag
`c15-c19-record-v1`, see `ENVIRONMENT.md` and `../PROVENANCE.md`). They are records of how the result was found; none of
them is needed to run the check.

These results were produced by **agent-afk**, an autonomous coding agent built by Griffin Long,
running parallel "lanes" as subagents on a laptop and two lab machines. The agent built the
schedule search (lane O), the DAG certificate generator and Lean files (lane L2), the novelty
check (lane N), and this package (lane P2). Every human input is logged in `../HUMAN_INPUT.md` at
the repo root: the original goal, hardware, the lane-parallel workflow, approvals of the agent's
wave plans, and "continue"/"proceed" messages. No human supplied mathematical content, the
schedules, or code.

Research-repo commits (`git log`):
* `86c62d942537d5ae009e3deff08133941d969702` (2026-09-30 23:42 -0400): "Wave 2: Lean-certified
  Theta(C19) >= 9.357202700233073 …", which contains lane O's candidate C15/C19 schedules;
* `a0d1733`, `4ac6d23`, `506df30`: wave 1, HUMAN_INPUT approval, live-log start.

Lane L2 (`lanes/L2_lean/`: `PROGRESS.md`, `gen_dag.py`, `src/DagTail.lean`, `out/`, `logs/`),
the source schedule files `lanes/O_opt/best_C15_A_ref.json` / `best_C19_C_ref.json`, and this
package (`artifacts/C15_C19c/`) are committed together with RESULT.md. Lane L2 built both
certificates on the laptop (`lanes/L2_lean/logs/build_capcert_C15b_2.log`, `build_capcert_C19c.log`);
a second machine (Mac mini M4, fresh GitHub clone at aa21eeb) built both as well
(`../logs/mac_mini_build_c15b.log`, `../logs/mac_mini_build_c19c.log`).

## Licence

BPZ's repository is released under the **Apache License 2.0** (its `LICENSE`). The five new Lean
files keep BPZ's Apache-2.0 header, because they are adapted from BPZ's `CertC15.lean`,
`CertC19.lean`, `CapCertC15.lean` and `CapCertC19.lean` and use their framework. The patch and
`check.sh` are offered under Apache-2.0 as well.

## Files

| file | what |
|---|---|
| `check.sh` | the one-command checker (POSIX sh; macOS and Linux) |
| `certL2.patch` | adds `DagTail.lean`, `CertC15b.lean`, `CapCertC15b.lean`, `CertC19c.lean`, `CapCertC19c.lean` and 5 import lines to BPZ `aa21eeb` (sha256 `ee71e47141d59484fd77b7e9e096d0e1ad900d2553ffcaea8ce5377034ce448e`) |
| `eval_dag.py` | independent stdlib-only Python evaluator (lane R3), unchanged |
| `schedules/best_C15_A_ref.json`, `schedules/best_C19_C_ref.json` | the two substitution schedules (input to `eval_dag.py`) |
| `ENVIRONMENT.md` | versions, commits, tags, tarball hash, machines on which the check passed |
| `check_run_*.log` | full logs of passing runs |
