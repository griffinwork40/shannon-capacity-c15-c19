# Shannon capacity of C15 and C19: new lower bounds, checked in Lean

**In plain language.** Imagine sending messages over a channel whose symbols sit in a ring, where
each symbol can be mistaken for its two neighbours. The *Shannon capacity* of the ring is how much
information per symbol can be sent with zero chance of confusion when long code words are allowed.
For rings of 15 and 19 symbols (the cycle graphs C15 and C19) the exact value is unknown, and
researchers compete on proving guaranteed lower bounds. In August 2026 Buys, Polak and Zuiddam
(BPZ) proved the best known values and had a computer proof checker (Lean) confirm them. This
repository proves slightly larger lower bounds, **7.301635000991096** for C15 and
**9.357203012726939** for C19, using BPZ's own building blocks combined in a different order. The
proofs are checked by Lean, inside BPZ's own framework, so you do not have to trust us: one command
downloads BPZ's public code, adds five files, and has Lean verify both results. The gains are small
(about 6.3 millionths for C15 and 3.0 millionths for C19); they are still strict improvements on the
best certified values we could find.

## The two theorems (verbatim Lean statements)

```lean
theorem ShannonBounds.CapCertC15b.shannonCapacity_cycleGraph_15_ge :
    (7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15)
theorem ShannonBounds.CapCertC19c.shannonCapacity_cycleGraph_19_ge :
    (9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)
```

`shannonCapacity` is BPZ's definition (`ShannonBounds/Defs.lean`, unchanged); `cycleGraph` is
Mathlib's. Each bound is M^(1/p) truncated to 15 decimals for an explicit integer M ≤ α(C_n^⊠p):
p = 3424 (M has 2957 digits) for C15 and p = 14800 (M has 14373 digits) for C19. Lean also proves
that the truncation is exact.

## Prior bounds (quoted)

| n | BPZ Lean repo, commit `aa21eeb` (README row, verbatim) | BPZ paper arXiv:2607.29681 v1 (abstract) | this repository | gain |
|---|---|---|---|---|
| 15 | `\| 15 \| 7.301628695930103 \| 3664 \| 3164 \|` | Θ(C15) ≥ 7.301600534487… | **7.301635000991096** | 6.31·10⁻⁶ |
| 19 | `\| 19 \| 9.357200030000796 \| 11856 \| 11514 \|` | Θ(C19) ≥ 9.357192705918… | **9.357203012726939** | 2.98·10⁻⁶ |

Repository: https://github.com/spectra-research/shannon-capacity-lean, commit
`aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10, "Update the bounds"), still HEAD on
2026-10-01. The README columns are n, the bound, the power p and the number of digits of the
independent-set size. arXiv:2607.29681 had only version v1 (2026-07-31) on 2026-10-01; BPZ's README
says improved product trees "will appear in the next arXiv version".

## Check it (one command)

```sh
cd artifact && sh check.sh --install-elan
```

or unpack the release tarball (`dist/shannon-C15-C19-v1.0.tar.gz`, sha256 in `dist/SHA256`) and run
`cd shannon-C15-C19 && sh check.sh --install-elan`. Needs a POSIX shell, git, curl, python3 ≥ 3.8,
`sha256sum` or `shasum`, about 8 GB of disk and network access to github.com and the Mathlib cache.
Expect 10 to 30 minutes. A passing run ends with `ALL CHECKS PASSED` and exit code 0. The script
clones BPZ's repository at `aa21eeb`, applies `artifact/certL2.patch` (it only adds five files and
five import lines), runs an independent Python re-derivation (with BPZ's own certificates as
positive controls), builds with Lean 4.32.2 and Mathlib, re-checks both statements verbatim in a
fresh Lean process, and rejects `sorry` and any non-standard axiom. Details: `artifact/README.md`,
`artifact/ENVIRONMENT.md`. To check the file integrity of this repository:
`shasum -a 256 -c SHA256SUMS` (or `sha256sum -c SHA256SUMS`).

Without Lean (a few minutes; checks hashes, the patch and the independent Python re-derivation,
but not the Lean proof): `cd artifact && sh check.sh --python-only`.

## What is new, and what is not

* **New:** only the *substitution schedules* (the order in which BPZ's gadgets are combined),
  found by an automated search over BPZ's schedule space, and their Lean certificates. A small
  generic Lean helper (`DagTail.lean`) keeps the certificates compact.
* **Not new:** the framework, substitution tables, terminal codes and Lean infrastructure (BPZ,
  building on Gao and on Itty, Rosin, Carstensen and Reichman); the base independent sets
  (Baumert, McEliece, Rodemich, Rumsey, Stanley and Taylor 1971; Codenotti, Gerace and Resta 2003;
  De Boer, Buys and Zuiddam). No new mathematical method is claimed. The schedules are not claimed
  to be optimal. These are lower bounds only; the Lovász upper bounds (about 7.417 and 9.435) are
  far away.
* **Novelty caveat:** our literature search (2026-10-01, `review/novelty/`) found nothing at or
  above these values, but it could not cover Google Scholar or unpublished work, and BPZ have
  announced improved trees for their next arXiv version.

## Trust base

The same as for every BPZ certificate: the Lean 4 kernel (v4.32.2), Mathlib at BPZ's pinned
revision, and **`native_decide`** (large finite checks are run as compiled code and not re-checked
by the kernel). `#print axioms` on each theorem lists `propext`, `Classical.choice`, `Quot.sound`
and 40 `native_decide` auxiliary axioms, and no `sorryAx`. The only new native checks are the value
of M (`stepM`) and the decimal step. The schedule search, the generator and the Python evaluator are
**not** part of the trust base.

## How this was made (AI and tools disclosure)

Author: **Griffin Long**. The computational work, the certificates, the checkers and the first
draft of the note were produced by **agent-afk**, an open-source autonomous agent runtime written
by the author (https://github.com/griffinwork40/agent-afk). The agent chose the target and wrote the
schedule search, the Lean generator and certificates, both checkers, and the draft. AI systems are
credited here, not as authors. Models used through agent-afk (Anthropic):

* Claude Opus, model id `claude-opus-5-5`: coordinator of both working sessions (2026-09-30 and
  2026-10-01) and most subagent lanes (baseline reproduction, schedule search, Lean certification,
  independent review, red-team review, novelty search, packaging, drafting);
* Claude Sonnet, model id `claude-sonnet-4-6`: some lanes (an early literature check, the
  second-machine rerun, finishing an audit report, a repository status survey);
* Claude Haiku, model id `claude-haiku-4-5-20251001`: one read-only repository survey.

OpenAI ChatGPT wrote the original task brief given to the agent and, after the result was found,
suggested the verification and disclosure plan that was followed; it contributed no mathematical
content, code or schedules. Every human input is logged in `HUMAN_INPUT.md`. No human supplied
mathematical content, schedules or code. Software: Lean 4, Mathlib, Lake, elan, Python 3, LaTeX,
Git. See `paper/note.md` (section 6) and `PROVENANCE.md`.

The independent Python evaluator was written by another instance of the same AI system, and all
three test machines belong to one person. **No external party has reproduced the result yet.**

## Layout

| path | contents |
|---|---|
| `artifact/` | the canonical, self-contained check bundle: `check.sh`, `certL2.patch`, `eval_dag.py`, `schedules/*.json`, `README.md`, `ENVIRONMENT.md`, clean-room log |
| `dist/` | `shannon-C15-C19-v1.0.tar.gz` (the bundle packed as `shannon-C15-C19/…`) and its `SHA256` |
| `proofs/` | the five Lean files created by the patch, for reading (see `proofs/README.md`) |
| `method/` | the generator and the schedule-search code (not part of the trust base; see `method/README.md`) |
| `review/` | red-team report, independent-evaluator report, novelty search report and query log, second-machine report |
| `logs/` | clean-room Linux log, laptop log, negative-control build log, Mac mini build logs |
| `paper/` | the note (`note.md`, `note.tex`, `note.pdf`); draft, not submitted |
| `RESULT.md` | summary of the result as recorded at the end of the work |
| `HUMAN_INPUT.md` | log of every human input |
| `PROVENANCE.md` | research-repository commits and tags, sessions, models, byte-identity table, redactions |
| `LICENSE`, `NOTICE` | Apache-2.0 (code and patch); CC BY 4.0 (paper text) |
| `tools/make_dist.py` | rebuilds `dist/` from `artifact/` byte for byte (deterministic tarball) |
| `CITATION.cff` | citation metadata |
| `SHA256SUMS` | sha256 of every tracked file except itself |

## Licence

Code, Lean files and the patch: Apache License 2.0 (`LICENSE`), the licence of BPZ's repository, of
which the patch is a derivative. Paper text in `paper/`: CC BY 4.0 (see `NOTICE`).

## How to cite

Griffin Long, *Slightly improved lower bounds for the Shannon capacity of C15 and C19, formalised in
the Buys–Polak–Zuiddam Lean framework*, version 1.0.0 (2026),
https://github.com/griffinwork40/shannon-capacity-c15-c19. Machine-readable: `CITATION.cff`.
Please also cite BPZ (arXiv:2607.29681 and their Lean repository), on whose work this rests.

## Contact

Please open an issue on the GitHub repository. Reproduction reports, positive or negative, are
very welcome.
