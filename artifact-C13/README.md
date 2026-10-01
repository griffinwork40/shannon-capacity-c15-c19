# A new lower bound for the Shannon capacity of the 13-cycle, checked in Lean

**In plain language.** Picture a communication channel whose symbols sit in a ring, where each
symbol can be mistaken for its two neighbours. Its *Shannon capacity* is the number of symbols
per use that can effectively be sent with zero chance of confusion, once long code words are
allowed. For a ring of 13 symbols nobody knows the exact value, and researchers compete on
proving guaranteed lower bounds. In August 2026, Buys, Polak and Zuiddam (BPZ) proved
6.302926729310108 and had the proof checked in the Lean proof assistant. In September 2026,
Matthew Protti improved this to 6.302927046770772, also checked in Lean, by adding guarded typed
cells at three nodes of BPZ's construction. We prove the slightly larger bound **6.302927071589786**, using only BPZ's own
Lean framework and building blocks, combined according to a different substitution schedule. A computer checks the proof,
so you do not have to trust us. One command downloads BPZ's public code, adds our four files, has
Lean verify the result, re-derives the number with an independent Python program, and compares it
exactly with Protti's published integer. The improvement over Protti is tiny (about 2.5 hundred
millionths), smaller than the gains in our v1.0 release. It is still a strict improvement on the
best certified value we could find.

---

## Check it (one command)

Copy this directory anywhere (or unpack the release asset `shannon-C13-v1.1.tar.gz`), then:

```sh
cd shannon-C13 && sh check.sh --install-elan
```

Prerequisites: a POSIX shell, `git`, `curl`, `python3` (3.8 or newer, stdlib only), `sha256sum`
or `shasum`, about 8 GB of free disk, and network access to github.com and the Mathlib build
cache. `--install-elan` runs the official Lean installer (elan) with `--no-modify-path` if `lake`
is not already present; elan then fetches the Lean version pinned by BPZ (v4.32.2). If you already
have elan, drop the flag. Use `--dir DIR` to choose the work directory (default `./c13-check`; it
must not already contain a clone). The script never deletes anything and never edits your shell
profile. Expect 10 to 30 minutes, mostly downloading Lean and the prebuilt Mathlib cache.

A passing run ends with:

```
ALL CHECKS PASSED (Lean 4 build + statement + axioms, independent Python with exact BPZ controls, exact comparison with Protti v0.5.0)
  Theta(C13) >= 6.302927071589786   [ShannonBounds.CapCertC13b.shannonCapacity_cycleGraph_13_ge; prior: Protti 6.302927046770772, BPZ 6.302926729310108]
```

and exit code 0. Any failure prints `CHECK FAILED: <reason>` and exits nonzero (exit 3 means only
that `lake` was not found and `--install-elan` was not given). Without Lean:
`sh check.sh --python-only` runs steps 0 to 3b; it is not a substitute for the Lean check, which
is the proof.

### What the script does

0. Checks the SHA-256 of every bundle file (`certC13.patch` = `7fde38bc…`, `eval_c13.py`,
   `compare_protti.py`, the schedule).
1. Clones BPZ's repository fresh and checks out commit `aa21eeb`.
2. Applies `certC13.patch`, checks the SHA-256 of the four new Lean files, checks that the only
   change to any existing BPZ file is four added `import` lines, and rejects `axiom`, `unsafe`,
   `opaque`, `implemented_by`, `extern`, `csimp`, macro/syntax/elab, `run_cmd`, `#eval` and
   `initialize` in the added files.
3. **Python.** Runs `eval_c13.py` (stdlib only) on the fresh clone. It re-derives the substitution
   tables, terminal codes and separation relation from BPZ's Lean sources, must reproduce BPZ's
   own CertC13 (6.302926729310108), CertC15, CertC19 and CertC7 exactly as positive controls,
   evaluates `schedules/best_C13_SA1.json`, and its `M` must equal the Lean literal `CertC13b.M`
   digit for digit (compared with `cmp`, plus a SHA-256 of the digits).
3b. **Exact comparison with the prior bound.** Clones Protti's repository, checks that tag
   `v0.5.0` is commit `dfaef37`, reads the literal `N` from
   `shannon_checked_release/source/ShannonBounds/C13R8D522.lean` (after checking that its
   theorem statements are as expected), and checks `M^522 > N^522` with exact integers. Both
   constructions live in dimension 522, so this is the same as `M > N`.
4. Finds `lake` (installing elan if asked) and checks it runs Lean 4.32.2.
5. `lake exe cache get` (prebuilt Mathlib), then `lake build ShannonBounds.CapCertC13b`.
6. In a fresh Lean process, re-type-checks the theorem statement verbatim and the comparison
   `improves_1`, prints `#print ShannonBounds.shannonCapacity`, and runs `#print axioms`; fails on
   `sorryAx` or on any axiom other than `propext`, `Classical.choice`, `Quot.sound` and
   `native_decide` auxiliaries.
7. Greps all Lean sources for `sorry` / `admit`.

Knobs: `LEAN_NUM_THREADS` (default 4), `NICE` (default 5). Machines, OSes, versions and dates of
passing runs: `ENVIRONMENT.md`. Full log of the clean-room run: `check_run_desk_linux.log`.

## Theorem (verbatim)

`ShannonBounds/CapCertC13b.lean`:

```lean
/-- **`Theta (cycleGraph 13) >= 6.302927071589786`**. -/
theorem shannonCapacity_cycleGraph_13_ge :
    (6.302927071589786 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 13)
```

Full name: `ShannonBounds.CapCertC13b.shannonCapacity_cycleGraph_13_ge`. `shannonCapacity` is
BPZ's definition in `ShannonBounds/Defs.lean`, unchanged: `⨆ n, α(G^⊠(n+1))^(1/(n+1))`, where `α`
is the independence number and `⊠` is the strong product. `cycleGraph` is Mathlib's definition.
These are the same objects BPZ's `Main.lean` uses.

The same file also proves (p = 522, M has 418 digits):
* `alpha_strongPower_ge : M ≤ α(C13^⊠522)`, where `M` is the explicit integer literal `CertC13b.M`;
* `shannonCapacity_Cyc_ge : M^(1/522) ≤ Θ(C13)`, the exact form;
* `tight : a^522 ≤ M·10^(15·522) < (a+1)^522` with `a = 6302927071589786`, so the decimal is the
  exact truncation of `M^(1/522)` to 15 places;
* `improves : (6.302926729310108 : ℝ) < 6.302927071589786` (BPZ) and
  `improves_1 : (6.302927046770772 : ℝ) < 6.302927071589786` (Protti).

## Prior bounds

* **Protti**, https://github.com/matthewprotti/c11-shannon-capacity-lower-bound, tag `v0.5.0` =
  commit `dfaef37e60e55c55b1744d9badd1f26c5364c7d5` (2026-09-09), file
  `shannon_checked_release/source/ShannonBounds/C13R8D522.lean`:
  `alpha_ge : N ≤ (strongPower (SimpleGraph.cycleGraph 13) 522).indepNum` and
  `capacity_lower : (6.302927046770772 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 13)`.
  Default-branch HEAD `6a0235f` (same day) adds only documentation and two build-diagnostic Lean
  scripts; `C13R8D522.lean` is unchanged. His construction keeps
  BPZ's base and schedule and adds guarded typed cells at three nodes.
* **BPZ Lean repository**, https://github.com/spectra-research/shannon-capacity-lean, commit
  `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10), README row
  `| 13 | 6.302926729310108 | 522 | 418 |`.
* **BPZ paper**, arXiv:2607.29681 v1 (the only version), states Θ(C13) ≥ 6.302455083464.

**Exact comparison.** Our `M` and Protti's `N` both have 418 digits and live in the same
dimension 522. `M − N ≈ 4.7204·10⁴¹¹` and `M/N − 1 ≈ 2.06·10⁻⁶`, so the rate gain is about
2.48·10⁻⁸ (6.30292707158978611… against 6.30292704677077232…).

**Literature check, 2026-10-01** (research repo `lanes/V_c13_indep/REPORT.md`): GitHub API and
`git ls-remote` for Protti and BPZ, arXiv abstract pages, API and recent math.CO / cs.IT listings,
Semantic Scholar citations of 2607.29681, and Tao's optimization-constants page. No C13 bound at
or above 6.302927046770772 other than Protti's was found. A same-day recheck at about 21:00Z on
2026-10-01 (GitHub refs, issues, PRs and forks; the arXiv API; Tao's page and its PRs; a general
web search) found nothing new. Limits: arXiv was searched by metadata only, and private or
unpublished work, or anything posted after about 21:00Z on 2026-10-01, cannot be excluded.

## What is new

Only the *substitution schedule* is new. The base independent sets, the substitution tables
(S2b, S3c), the terminal code K3a, the reindexing `sigma` and the Lean framework are BPZ's, used
unchanged; the C13^⊠6 base and its family sizes are exactly those of BPZ's `CertC13`. The schedule
was found by simulated annealing over BPZ's schedule space, scored exactly (research repo lane O,
`lanes/O_opt/best_C13_SA1.json`; copy in `schedules/`). It is a DAG of 49 distinct nodes, with
terminal code K3a applied to nodes of exponents (34, 36, 17), so E = 87 in C13^⊠6 and dimension
p = 522, the same dimension as BPZ and Protti. The full schedule is written out in the header
comment of `CertC13b.lean`. Unlike Protti's construction, it uses no typed cells.

Credit for the ingredients: BPZ's C13 base is a port system on an independent set of size 62530 in
C13^⊠6, the size first found by Itty, Rosin, Carstensen and Reichman (arXiv:2607.21517); BPZ's
method builds on Gao (arXiv:2607.27869) and on Itty et al.

The patch adds `ShannonBounds/{DagTail,DagCode3,CertC13b,CapCertC13b}.lean` and four import lines
in `ShannonBounds.lean`. `DagTail.lean` is byte-identical to the one in the v1.0 C15/C19 patch
(sha256 `f277d0b7…`). `DagCode3.lean` adds `code3` / `sum_code3`, the arity-3 analogues of
`DagTail.code4` / `sum_code4`. Node sizes are never literals: each node carries a `Sizes` value
computed from its children's, and the single literal `M` is checked by one `native_decide`
(`CertC13b.stepM`). The patch modifies no existing BPZ proof, and BPZ's own C13 theorem still
builds next to the new one.

`certC13.patch` and the v1.0 `certL2.patch` are alternatives, not a stack: both create
`DagTail.lean`, so each applies on its own to a clean `aa21eeb`, but not one after the other.

## Trust base

The same as for every BPZ certificate (and Protti's numerical ones):
* the Lean 4 kernel (v4.32.2) and Mathlib at the pinned revision;
* **`native_decide`**: the finite checks run as compiled code with GMP-backed `Nat` arithmetic and
  are not re-checked by the kernel. `#print axioms` lists `propext`, `Classical.choice`,
  `Quot.sound` and 47 `…._native.native_decide.ax_*` auxiliary axioms, and no `sorryAx`. The new
  files add native axioms only in `CertC13b.stepM` (the value of `M`) and in the capacity theorem
  (the decimal step); all others come from BPZ's BaseC13 checks, the tables S2b and S3c, and the
  code K3a.
* the two definitions in the statement (BPZ's `shannonCapacity`, Mathlib's `cycleGraph`).

Negative control, done during development (research repo `lanes/T_c13/logs/build_neg_C13b.log`):
with `M+1` in place of `M`, Lean rejects the file at `stepM`.

Independent (non-Lean) reproduction, step 3: `eval_c13.py` is the v1.0 evaluator `eval_dag.py`
(written by a reviewer lane that did not read the search or generator code) extended to the C13
base and arity-3 codes by the lane that also wrote the generator. For C13 it reads the base family
sizes from the Lean-proved statements in BPZ's `BaseC13.lean` rather than from raw words. Two
further independent re-derivations were done outside this bundle: a reviewer with the search code
withheld wrote a new evaluator that reproduces BPZ's CertC7, C11, C13, C15, C19 and C23 and our
`M` digit for digit (`review/C13_independent/REPORT.md`), and a second lane re-derived the BaseC13
family sizes by brute force over all 13⁶ words (`lanes/V_c13_indep/REPORT.md`). The Lean check does
not depend on any of them.

## What is NOT claimed

* Not the value of Θ(C13). This is a lower bound only; the Lovász bound (about 6.4) is far away.
* Not a new mathematical method. The method, framework, base sets, tables and code are BPZ's. The
  contribution is a better schedule and its certificate.
* Not a large gain: about 2.5·10⁻⁸ over Protti, about 3.4·10⁻⁷ over BPZ's repository value.
* Not kernel-only. As with BPZ, `native_decide` is trusted.
* Not an optimal schedule, and not a combination with Protti's typed cells (which might well
  improve it further).
* No claim of novelty against sources we could not search. BPZ, Protti or others may hold
  stronger unpublished bounds.

## Provenance

Paths of the form `lanes/...` and `review/...` refer to the research repository. They are records
of how the result was found; none of them is needed to run the check.

This result was produced by **agent-afk**, an autonomous coding agent built by Griffin Long,
running parallel "lanes" as subagents on a laptop and two lab machines. The agent found the
schedule (lane O), generated and certified the Lean files and the checker (lane T_c13), ran the
independent reviews (review/C13_independent, lanes/V_c13_indep) and assembled this package (lane
C13_release). Every human input is logged in `HUMAN_INPUT.md` in the research repository. No human
supplied mathematical content, the schedule, or code.

## Licence

BPZ's repository is released under the **Apache License 2.0**. The four new Lean files state that
they were contributed by Griffin Long with agent-afk as an addition to BPZ's framework, which BPZ
did not write, under Apache-2.0. The patch, `check.sh`, `eval_c13.py` and `compare_protti.py` are
offered under Apache-2.0 as well. Protti's repository is Apache-2.0; this bundle does not include
any of his files, it only clones his public tag to read one integer.

## Files

| file | what |
|---|---|
| `check.sh` | the one-command checker (POSIX sh; macOS and Linux) |
| `certC13.patch` | adds `DagTail.lean`, `DagCode3.lean`, `CertC13b.lean`, `CapCertC13b.lean` and 4 import lines to BPZ `aa21eeb` (sha256 `7fde38bcb178fb747be18bb9deb63f303225c2cc0b7e1d566281ad47fb301138`) |
| `eval_c13.py` | stdlib-only Python evaluator (v1.0 `eval_dag.py` extended to C13) |
| `compare_protti.py` | exact integer comparison with Protti's `C13R8D522.N` |
| `schedules/best_C13_SA1.json` | the substitution schedule (input to `eval_c13.py`) |
| `ENVIRONMENT.md` | versions, commits, hashes, machines on which the check passed |
| `check_run_desk_linux.log` | full log of the Linux clean-room run |
