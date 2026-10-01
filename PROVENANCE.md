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
