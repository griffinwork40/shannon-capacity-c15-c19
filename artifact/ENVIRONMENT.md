# Environment and provenance of the check

## Pinned inputs (all verified by `check.sh` on every run)

| item | value |
|---|---|
| BPZ repository | https://github.com/spectra-research/shannon-capacity-lean |
| BPZ commit | `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10 11:10:00 +0200, "Update the bounds") |
| Lean | `leanprover/lean4:v4.32.2` (from BPZ `lean-toolchain`; `Lake version 5.0.0-src+f3b06c7 (Lean version 4.32.2)`) |
| Mathlib | `905b95818eb32af7874a58b427f50c1711a5e96c` (BPZ `lake-manifest.json`, inputRev `v4.32.2`) |
| other Lake deps (`lake-manifest.json`) | plausible `e12c1910`, LeanSearchClient `c5d5b8fe`, importGraph `7e9612bf`, proofwidgets `6e311e2a`, aesop `a7dbf0c6`, Qq `38d591e7`, batteries `023ce7d6`, Cli `88679d08` |
| elan (installer used by `--install-elan`) | official `elan-init.sh` from `raw.githubusercontent.com/leanprover/elan/master`; installed version on the passing runs: `elan 4.2.4 (227caca13 2026-08-25)` |

## Bundle files (sha256)

| file | sha256 |
|---|---|
| `certL2.patch` | `ee71e47141d59484fd77b7e9e096d0e1ad900d2553ffcaea8ce5377034ce448e` |
| `check.sh` | `4cec675928b6740139e0eed570358559ecc5052e7d85312bce34b606d80ddfb5` (v1.0; adds `--python-only`; the clean-room runs listed below used `2a79c4ac…`, which differs only by that flag, and v1.0 itself was re-run in a clean room before release) |
| `eval_dag.py` | `72d1b07af3a9e7d4a628112936d2047c8e99869fe169a603c0b4a7cccef442f3` |
| `schedules/best_C15_A_ref.json` | `6a37e3c9dd8170ca10d6d184ea5e76a25af1b29a23f10f69f7b8a9535113ff35` |
| `schedules/best_C19_C_ref.json` | `df340f3f1cdd6eace681e7d7e10801a151bde6c3837e12816d82d2b1c2948b92` |

Files created by the patch: `DagTail.lean f277d0b7…`, `CertC15b.lean fd76961f…`,
`CapCertC15b.lean 45b3b426…`, `CertC19c.lean c1d8209e…`, `CapCertC19c.lean d5d08a91…` (full hashes in
`check.sh`).

Revision note (2026-10-01, after the red-team review `../review/red_team/REPORT.md`): the five added Lean files
originally carried BPZ's copyright/author header; they now say they were contributed by Griffin
Long with agent-afk as an addition to BPZ's framework. Only those header comment lines changed
(the mathematics, M literals and theorem statements are byte-identical apart from lines 2-4), so
`certL2.patch` changed from `68001af1…` (commit 5737f31, tag c15-c19-record-v1) to `ee71e471…`.
`check.sh` also gained a step that rejects `axiom`, `unsafe`, `opaque`, `implemented_by`,
`extern`, `csimp`, macro/syntax/elab and `#eval` in the added files. sha256 of the decimal digits of `M` (= Lean literal = Python value):
C15 `34e07ce861947b8cac30ca45a5d74cfc1b15ff100c4dcdb88923735ca5d3ad33` (2957 digits),
C19 `ac85cbc50fb67faa4766e5f8426fe98552c29f8d6fc54165fc3c1cdebfa8203d` (14373 digits).

## Research repository (where the result was produced)

| ref | tag object | commit |
|---|---|---|
| `c15-c19-record-v1` | `7c2dff031122d5be3cf14cdfe2f7c0f4d37cbc96` | `5737f31a6afb08c579c042b5c03991fe3d703057` (2026-10-01 00:40:27 -0400, C15 + C19 record, `certL2.patch`) |
| `c19-record-v1` | `5e61cd643558b3fadcb159a49c8f730615932d93` | `86c62d942537d5ae009e3deff08133941d969702` (2026-09-30 23:42:02 -0400, first C19 record, CapCertC19b) |

Both are annotated tags (tagger Griffin Long). The bundle files `certL2.patch`, `eval_dag.py` and
`schedules/*.json` are byte-identical to `artifacts/C15_C19c/certL2.patch`,
`artifacts/C15_C19c/eval_dag.py` (= `lanes/R3_review/eval_dag.py`) and
`lanes/O_opt/best_C15_A_ref.json`, `lanes/O_opt/best_C19_C_ref.json` at commit `5737f31`.

## Tarball

A tarball of this directory (packed as `shannon-C15-C19/...`) is kept in the release repository at
`dist/shannon-C15-C19-v1.0.tar.gz`; its sha256 is in `dist/SHA256` next to it (a file
cannot contain the hash of an archive that contains it).

## Machines on which the check passed

| date (UTC) | machine | OS | state before the run | script | result |
|---|---|---|---|---|---|
| 2026-10-01 11:17:34 to 11:32:58 | desk box (same machine) | Ubuntu 24.04.4 LTS | **clean room, stricter**: fresh `HOME` (empty dir, so no `~/.elan`, no `~/.cache/mathlib`, no git config); only this bundle copied in | this bundle (revised patch `ee71e471…`, check.sh `2a79c4ac…`), `HOME=<empty dir> sh check.sh --install-elan` | **ALL CHECKS PASSED, exit 0**. Log: `check_run_desk_linux.log` |
| 2026-10-01 10:25:55 to 10:41:44 | desk box, AMD Ryzen 3 3200G (4 cores), 5.7 GB RAM | Ubuntu 24.04.4 LTS, Linux 6.8.0-142-generic x86_64; git 2.43.0, Python 3.12.3 | **clean room**: no elan, no Lean, no `~/.cache/mathlib`; only this bundle directory copied in | this bundle, `sh check.sh --install-elan` | **ALL CHECKS PASSED, exit 0** (build of the new modules 423 s; whole run 16 min), with the original patch `68001af1…`. Its log was replaced by the stricter rerun above. |
| 2026-10-01 04:33:40 | MacBook, Apple M4 Pro | macOS 27.0.1 (Darwin arm64) | elan + Lean installed, Mathlib cache warm | predecessor `artifacts/C15_C19c/check.sh` (same Lean steps, no Python step) | ALL CHECKS PASSED, exit 0 (build 51 s). Log: `../logs/check_run_laptop.log` |
| 2026-10-01 10:25 | same MacBook | macOS 27.0.1, `/usr/bin/python3` 3.9.6 | `PATH=/usr/bin:/bin`, no lake reachable | this bundle | steps 0 to 3 (bundle hashes, fresh clone, patch, Python) passed; stopped at step 4 with exit 3 (no lake), as designed. Lean was deliberately not rerun on this machine. |
| 2026-10-01 ~00:39 (local) | Mac mini M4, 16 GB | macOS 27.0 (26A428) | fresh GitHub clone at aa21eeb, elan 4.2.4 | manual `lake build` of CapCertC15b / CapCertC19c (lane M) | Build completed successfully. Logs: `../logs/mac_mini_build_c15b.log`, `../logs/mac_mini_build_c19c.log` |

Note from the clean-room run: `lake exe cache get` first tried the `mathlib4-master` cache bucket,
found nothing there for this revision, and then downloaded all 8639 files from the main bucket
(about 2 minutes at 150 KB/s to 4 MB/s). This is normal Mathlib cache behaviour, not an error.
