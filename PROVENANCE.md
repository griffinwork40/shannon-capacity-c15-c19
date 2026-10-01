# Provenance

This repository is a curated public release, made with a fresh git history. The working
research repository (all lanes, intermediate attempts, failed experiments and machine-specific
logs) is private. This file links every released file to it, so the release can be audited
against the research history on request. The mathematical content was not changed for release.

## Research repository

Private git repository `discovery-2026-09`. Release prepared from commit `0e211a679d78eaff82834de640c3c7e2c2a9d517`.

| research tag | tag object | commit | meaning |
|---|---|---|---|
| `c15-c19-artifact-v1` | `c575cffdb5676ee62c588b8f6faeba444ef53be5` | `88383df194fee625d412f33a603a5f5f22aca563` | sealed bundle (patch `ee71e471…`: attribution headers only) |
| `c15-c19-record-v1` | `7c2dff031122d5be3cf14cdfe2f7c0f4d37cbc96` | `5737f31a6afb08c579c042b5c03991fe3d703057` | C15 and C19 certificates (original patch `68001af1…`) |
| `c19-record-v1` | `5e61cd643558b3fadcb159a49c8f730615932d93` | `86c62d942537d5ae009e3deff08133941d969702` | first Lean-certified C19 bound (9.357202700233073, superseded) |

The theorems, the `M` literals and the schedules are identical across `c15-c19-record-v1`,
`c15-c19-artifact-v1` and this release. Between the first two only the comment header of the five
added Lean files changed (it had wrongly named BPZ as authors). The release adds
`check.sh --python-only`, which only skips steps.

## Sessions and AI models

Work was done by the autonomous agent runtime agent-afk (github.com/griffinwork40/agent-afk):

* Attempt 1 (2026-09-30, C7/C9 and baseline work, the fixed checker `method/verifier/verify.py`):
  session `2f73e6bc-5f46-49b8-bf4d-8b6451572665`, coordinator `claude-opus-5-5`.
* Attempt 2 (2026-10-01, the C15/C19 result, verification, packaging):
  session `c69cb5b2-7e4d-431c-905e-0821bf90f5b8`, coordinator `claude-opus-5-5`. Subagents used the
  aliases opus, sonnet and haiku, which agent-afk resolves to `claude-opus-5-5`, `claude-sonnet-4-6`
  and `claude-haiku-4-5-20251001`.
* OpenAI ChatGPT wrote the original brief and suggested the verification/disclosure plan
  (outside agent-afk).

Every human input is logged in `HUMAN_INPUT.md`. Session transcripts and trace files are kept
privately and can be shared with reviewers on request.

## File map (release file -> research file at the commit above)

| release file | research file | sha256 (release) | status |
|---|---|---|---|
| `HUMAN_INPUT.md` | `HUMAN_INPUT.md` | `8058391848689d98…` | edited for release (see Redactions) |
| `RESULT.md` | `RESULT.md` | `0518edb29644c7a7…` | edited for release (see Redactions) |
| `artifact/ENVIRONMENT.md` | `artifacts/shannon-C15-C19/ENVIRONMENT.md` | `607bb24ab1fb6b78…` | edited for release (see Redactions) |
| `artifact/README.md` | `artifacts/shannon-C15-C19/README.md` | `af93d25cf6e0c338…` | edited for release (see Redactions) |
| `artifact/certL2.patch` | `artifacts/shannon-C15-C19/certL2.patch` | `ee71e47141d59484…` | identical |
| `artifact/check.sh` | `artifacts/shannon-C15-C19/check.sh` | `4cec675928b67401…` | identical |
| `artifact/check_run_desk_linux.log` | `artifacts/shannon-C15-C19/check_run_desk_linux.log` | `69576d98cebcbd07…` | identical |
| `artifact/eval_dag.py` | `artifacts/shannon-C15-C19/eval_dag.py` | `72d1b07af3a9e7d4…` | identical |
| `artifact/schedules/best_C15_A_ref.json` | `artifacts/shannon-C15-C19/schedules/best_C15_A_ref.json` | `6a37e3c9dd8170ca…` | identical |
| `artifact/schedules/best_C19_C_ref.json` | `artifacts/shannon-C15-C19/schedules/best_C19_C_ref.json` | `df340f3f1cdd6eac…` | identical |
| `logs/check_run_desk_linux.log` | `artifacts/shannon-C15-C19/check_run_desk_linux.log` | `69576d98cebcbd07…` | identical |
| `logs/check_run_laptop.log` | `artifacts/C15_C19c/check_run_laptop.log` | `9e1d5a98228422a2…` | identical |
| `logs/laptop_build_neg_C15b.log` | `lanes/L2_lean/logs/build_neg_C15b.log` | `fac0e44dff60f7a8…` | identical |
| `logs/mac_mini_build_c15b.log` | `lanes/M_mini/l2/build_c15b.log` | `efa22dc3e4b0fcb8…` | identical |
| `logs/mac_mini_build_c19c.log` | `lanes/M_mini/l2/build_c19c.log` | `4c66284979f36dbd…` | identical |
| `method/lanes/L2_lean/gen_dag.py` | `lanes/L2_lean/gen_dag.py` | `341a972382630e9a…` | identical |
| `method/lanes/O_opt/certs.py` | `lanes/O_opt/certs.py` | `bb5ade4414620efa…` | identical |
| `method/lanes/O_opt/exact_eval.py` | `lanes/O_opt/exact_eval.py` | `94a0c194d4d1cb94…` | identical |
| `method/lanes/O_opt/lean_parse.py` | `lanes/O_opt/lean_parse.py` | `ba75c79091e6fc3a…` | identical |
| `method/lanes/O_opt/recursion.py` | `lanes/O_opt/recursion.py` | `b20ed3283edb49c6…` | identical |
| `method/lanes/O_opt/search.py` | `lanes/O_opt/search.py` | `f338641e464ea324…` | identical |
| `method/lanes/O_opt/search2.py` | `lanes/O_opt/search2.py` | `0dd94130edba492e…` | identical |
| `method/lanes/O_opt/worker.sh` | `lanes/O_opt/worker.sh` | `21aad00ffcb10ee7…` | identical |
| `method/search_logs/exact_C15_A.log` | `lanes/O_opt/logs/exact_C15_A.log` | `e61bcb1d1f0ac780…` | identical |
| `method/search_logs/exact_C19_C.log` | `lanes/O_opt/logs/exact_C19_C.log` | `89cf3fe2b500eebb…` | identical |
| `method/search_logs/search_C19_C.log` | `lanes/O_opt/logs/search_C19_C.log` | `7e4f96cc31a37cb5…` | identical |
| `method/verifier/verify.py` | `verifier/verify.py` | `f1e5d592b334fea4…` | identical |
| `paper/note.md` | `paper/note.md` | `41e3e1a3bfddd317…` | identical |
| `paper/note.pdf` | `paper/note.pdf` | `70fbd4743d8d0e58…` | identical |
| `paper/note.tex` | `paper/note.tex` | `9705a35c1d0aa25d…` | identical |
| `review/independent_evaluator/REPORT.md` | `lanes/R3_review/REPORT.md` | `9a2ee31681f50090…` | identical |
| `review/novelty/REPORT.md` | `lanes/N2_novelty/REPORT.md` | `9c05f92034c3d734…` | identical |
| `review/novelty/query_log.txt` | `lanes/N2_novelty/query_log.txt` | `22a195b0d55295a5…` | identical |
| `review/red_team/REPORT.md` | `lanes/K_kill/REPORT.md` | `101ec7d4c3b1f958…` | identical |
| `review/second_machine/REPORT.md` | `lanes/M_mini/REPORT.md` | `0350e31a3b4aae22…` | edited for release (see Redactions) |

Files with no research counterpart (written for the release): `README.md`, `PROVENANCE.md`,
`LICENSE` (Apache-2.0 text, as in BPZ's repository), `NOTICE`, `CITATION.cff`, `.gitignore`,
`method/README.md`, `proofs/README.md`, `tools/make_dist.py`, `SHA256SUMS`, `dist/*`.
`proofs/*.lean` are exactly the five files that `artifact/certL2.patch` creates in BPZ's repository
at `aa21eeb` (checked by applying the patch to a fresh GitHub clone). `dist/` is produced from
`artifact/` by `tools/make_dist.py`, deterministically.

## Redactions and edits for release

* `HUMAN_INPUT.md`: an ssh host alias was removed from the hardware line.
* `review/second_machine/REPORT.md`: a local hostname replaced by "Mac mini".
* `artifact/ENVIRONMENT.md`: a hostname and a copy command removed; research-repo paths replaced by
  release paths; the `check.sh` hash updated for `--python-only`.
* `artifact/README.md`, `RESULT.md`: research-repo paths replaced by release paths; one date
  clarified; one log described accurately.
* `paper/note.*`: as in the research repository at the commit above (bibliography verified against
  zbMATH, Crossref and arXiv; release URL inserted).
* Logs are verbatim. They contain the local username in paths (`/Users/griffinlong`,
  `/home/griffinlong`); no IP addresses, hostnames with network details, keys or tokens.
* Not released: attempt-1 lanes, scraped web pages from the novelty search (only the report and
  query log are included), copies of third-party papers, and BPZ's repository itself (it is cloned
  from GitHub by `check.sh`).

## v1.1 (2026-10-01): C13

v1.1 adds files and edits the top-level documents; every v1.0 file under `artifact/`, `proofs/`,
`dist/shannon-C15-C19-v1.0.tar.gz` and `dist/SHA256` is unchanged. The v1.1 material was prepared
from research-repository commit `85621eb29985397fdbbfe61bcc0b387066c2353a` (C13 release material,
same-day recheck); the C13 certificate itself was first committed in
`bd805fe651fb804e39baf64eb7ace1558b962894` (lane T_c13). Sessions: the C13 work ran in attempt 3
(coordinator session `86e5b329…`) and a parallel session (`9676a00d…`, which built the release
bundle and ran the recheck), both with coordinator `claude-opus-5-5`.

| release file | research file (at `85621eb`) | sha256 (release) | status |
|---|---|---|---|
| `artifact-C13/README.md` | `lanes/C13_release/shannon-C13/README.md` | `a2dea1371feccf0e…` | identical |
| `artifact-C13/ENVIRONMENT.md` | `lanes/C13_release/shannon-C13/ENVIRONMENT.md` | `573c4f9b7ebbb4ef…` | edited for release (see below) |
| `artifact-C13/certC13.patch` | `lanes/C13_release/shannon-C13/certC13.patch` = `lanes/T_c13/certC13.patch` | `7fde38bcb178fb74…` | identical |
| `artifact-C13/check.sh` | `lanes/C13_release/shannon-C13/check.sh` (packaging edits of `lanes/T_c13/check_c13.sh`, see `artifact-C13/ENVIRONMENT.md`) | `cc8ac72a1a201e69…` | identical |
| `artifact-C13/check_run_desk_linux.log` | `lanes/C13_release/shannon-C13/check_run_desk_linux.log` | `0216e49345c8219b…` | identical |
| `artifact-C13/compare_protti.py` | `lanes/C13_release/shannon-C13/compare_protti.py` = `lanes/T_c13/compare_protti.py` | `790710c268b7b5f4…` | identical |
| `artifact-C13/eval_c13.py` | `lanes/C13_release/shannon-C13/eval_c13.py` = `lanes/T_c13/eval_c13.py` | `4de5d55a0ea0005c…` | identical |
| `artifact-C13/schedules/best_C13_SA1.json` | `lanes/C13_release/shannon-C13/schedules/best_C13_SA1.json` = `lanes/O_opt/best_C13_SA1.json` | `0843977febf93c1b…` | identical |
| `proofs-C13/CertC13b.lean` | `lanes/T_c13/out/CertC13b.lean` | `cffbb8ab757a7f8d…` | identical |
| `proofs-C13/CapCertC13b.lean` | `lanes/T_c13/out/CapCertC13b.lean` | `5c5558263bf78fde…` | identical |
| `proofs-C13/DagCode3.lean` | `lanes/T_c13/lean/DagCode3.lean` | `fa3f760ff74d11f8…` | identical |
| `review/C13/independent_evaluator_REPORT.md` | `review/C13_independent/REPORT.md` | `c49dc5c808c22718…` | identical |
| `review/C13/V_c13_indep_REPORT.md` | `lanes/V_c13_indep/REPORT.md` | `d5892c1dd845aa01…` | identical |
| `review/C13/check_c13_mini.log` | `review/C13_second_machine/check_c13_mini.log` | `6e2edbc7653c73e1…` | identical |
| `review/C13/same_day_recheck_REPORT.md` | `lanes/C13_release/recheck/REPORT.md` | `b37445e92c3d9bf4…` | identical |
| `tools/make_dist_c13.py` | `lanes/C13_release/make_dist_c13.py` | `a698aa6ffa9618e1…` | identical |
| `HUMAN_INPUT.md` | `HUMAN_INPUT.md` | `79c690dcb4395e0d…` | edited for release (see below) |
| `paper/note.md`, `paper/note.tex` | `paper/note.*` (v1.0 text) + `lanes/C13_release/note_C13_section.md` | `ec9074edcf4c77b8…`, `8bf2d08acd10fa35…` | merged for v1.1 (see below) |
| `paper/note.pdf` | built from `paper/note.tex` | `2c2b67f3706af0ba…` | rebuilt (pdflatex, two passes) |
| `RESULT.md`, `README.md`, `CITATION.cff`, `PROVENANCE.md`, `.gitignore`, `SHA256SUMS` | — | — | written or extended for the release |
| `proofs-C13/README.md` | — | — | written for the release |
| `dist/v1.1/shannon-C13-v1.1.tar.gz`, `dist/v1.1/SHA256` | — | — | produced from `artifact-C13/` by `tools/make_dist_c13.py artifact-C13 dist/v1.1`, deterministically |

`proofs-C13/*.lean` are exactly the files that `artifact-C13/certC13.patch` creates in BPZ's
repository at `aa21eeb` (checked by applying the patch to a fresh GitHub clone); the fourth file
the patch creates, `DagTail.lean`, is byte-identical to `proofs/DagTail.lean`.

Redactions and edits for v1.1:

* `artifact-C13/ENVIRONMENT.md`: a hostname removed (as in v1.0); the stale remark that Protti's
  HEAD after `v0.5.0` changed "documentation only" corrected (it also adds two build-diagnostic
  Lean scripts; `C13R8D522.lean` is unchanged; see `review/C13/same_day_recheck_REPORT.md`); the
  "not yet committed" sentence replaced by the research commits above. This file is not
  hash-pinned by `check.sh`.
* `HUMAN_INPUT.md`: the ssh host alias removed (as in v1.0), and a third party's email address
  replaced by "(omitted here)".
* `paper/note.*`: Section 8 (C13) merged from `note_C13_section.md` with its draft comments
  removed, plus the edits that file listed (title, abstract sentence, status line, Section 5 bundle
  command, reference [Pro26], acknowledgement) and one sentence crediting Itty, Rosin, Carstensen
  and Reichman and Gao for the C13 base (from the same-day recheck).
* Logs are verbatim. As in v1.0, they contain the local username in paths (`/home/griffinlong`,
  `/Users/griffinlong`); no IP addresses, keys or tokens.
* The same-day recheck report refers to an `evidence/` directory and to temporary clones; these are
  kept in the research repository and are not released.
