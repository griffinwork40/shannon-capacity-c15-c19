# Environment and provenance of the check

## Pinned inputs (all verified by `check.sh` on every run)

| item | value |
|---|---|
| BPZ repository | https://github.com/spectra-research/shannon-capacity-lean |
| BPZ commit | `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65` (2026-08-10 11:10:00 +0200, "Update the bounds") |
| Protti repository (prior bound, read only) | https://github.com/matthewprotti/c11-shannon-capacity-lower-bound |
| Protti tag | `v0.5.0` = commit `dfaef37e60e55c55b1744d9badd1f26c5364c7d5` (2026-09-09); default-branch HEAD at the clean-room run: `6a0235fab88c49a2499d8fb8b9daa621909b24de` (since v0.5.0 only documentation and two build-diagnostic Lean scripts were added; `C13R8D522.lean` is unchanged) |
| Protti file read | `shannon_checked_release/source/ShannonBounds/C13R8D522.lean` (`def N`, `alpha_ge`, `capacity_lower`) |
| Lean | `leanprover/lean4:v4.32.2` (from BPZ `lean-toolchain`; `Lake version 5.0.0-src+f3b06c7 (Lean version 4.32.2)`) |
| Mathlib | `905b95818eb32af7874a58b427f50c1711a5e96c` (BPZ `lake-manifest.json`) |
| elan (installer used by `--install-elan`) | official `elan-init.sh` from `raw.githubusercontent.com/leanprover/elan/master`; installed version on the clean-room run: `elan 4.2.4 (227caca13 2026-08-25)` |

## Bundle files (sha256)

| file | sha256 |
|---|---|
| `certC13.patch` | `7fde38bcb178fb747be18bb9deb63f303225c2cc0b7e1d566281ad47fb301138` |
| `check.sh` | `cc8ac72a1a201e69234015fba15eac4ac0813d63f2061ed4e30ad6e5ee753bc4` |
| `eval_c13.py` | `4de5d55a0ea0005c932fb9aa1bfab3bde3059bd9143c9fc3db75f934ba4de4ec` |
| `compare_protti.py` | `790710c268b7b5f442d192d8d863cfd039cdf00b3066e2332826713d17c18381` |
| `schedules/best_C13_SA1.json` | `0843977febf93c1be1932e43a7e3cb34f382ec3b672f85e8ac9847d91eba7407` |

Files created by the patch: `DagTail.lean f277d0b7…` (byte-identical to the v1.0 C15/C19 patch),
`DagCode3.lean fa3f760f…`, `CertC13b.lean cffbb8ab…`, `CapCertC13b.lean 5c555826…` (full hashes in
`check.sh`). sha256 of the decimal digits of `M` (= Lean literal `CertC13b.M` = Python value, 418
digits): `cac3a5bdf4a4f34045c3a80c52bb1d651e5a0ff2a007b3f13efb6a9ab0914fba`.

## Research repository (where the result was produced)

The bundle files are byte-identical to these files in the research repository `discovery-2026-09`:
`lanes/T_c13/certC13.patch`, `lanes/T_c13/eval_c13.py`, `lanes/T_c13/compare_protti.py`,
`lanes/T_c13/schedules/best_C13_SA1.json` (= `lanes/O_opt/best_C13_SA1.json`). `check.sh` is
`lanes/T_c13/check_c13.sh` (sha256 `4ee1d034…`) with packaging edits only: the file name in its
help text, a licence line and the Mathlib revision in the log, and a closing hint after
`--python-only`. No check was removed or weakened. The `lanes/T_c13/` files are in research-repository commit
`bd805fe651fb804e39baf64eb7ace1558b962894`; this bundle is in commit
`85621eb29985397fdbbfe61bcc0b387066c2353a` (`lanes/C13_release/shannon-C13/`).

## Machines on which the check passed

| date (UTC) | machine | OS | state before the run | script | result |
|---|---|---|---|---|---|
| 2026-10-01 18:41:35 to 19:04:51 | desk box, AMD Ryzen 3 3200G (4 cores), 5.7 GB RAM | Ubuntu 24.04.4 LTS, Linux 6.8.0-142-generic x86_64; git 2.43.0, Python 3.12.3 | **clean room**: fresh `HOME` (empty directory, so no `~/.elan`, no `~/.cache/mathlib`, no git config), environment cleared with `env -i` except `HOME`, a system `PATH` and `LANG`; only this bundle copied in | this bundle (`check.sh cc8ac72a…`), `sh check.sh --install-elan` | **ALL CHECKS PASSED, exit 0, first attempt.** Whole run 1396 s (23 min 16 s); `lake build ShannonBounds.CapCertC13b` 665 s (BPZ modules from source, Mathlib from cache). Log: `check_run_desk_linux.log` |
| 2026-10-01 16:00:04 to 16:02:08 | Mac mini M4, 16 GB | macOS 27.0 (Darwin arm64); Python 3.9.6 | elan installed, Mathlib cache warm; fresh clones of BPZ and Protti | predecessor `check_c13.sh` (`4ee1d034…`; same checks) | ALL CHECKS PASSED, exit 0 (build 56 s). Research repo: `review/C13_second_machine/check_c13_mini.log` |
| 2026-10-01 15:25:55 to 15:28:18 | MacBook, Apple M4 Pro | macOS 27.0.1 (Darwin arm64); Python 3.14.5 | elan installed, Mathlib cache warm; fresh clones of BPZ and Protti | predecessor `check_c13.sh` (same checks) | ALL CHECKS PASSED, exit 0 (build 54 s). Research repo: `lanes/T_c13/logs/check_c13_fresh.log` |
| 2026-10-01 19:09:40 to 19:12:05 | same MacBook | macOS, `/usr/bin/python3` 3.9.6, `PATH=/usr/bin:/bin` | elan in `~/.elan` (not on PATH), Mathlib cache warm; bundle unpacked from a test build of the tarball (`make_dist_c13.py`, sha256 `bf9f7808…`, built before this ENVIRONMENT.md row was added, so the final tarball hash differs) | this bundle, `sh check.sh` | ALL CHECKS PASSED, exit 0 (build 56 s): the tarball path works. |
| 2026-10-01 18:39 | same MacBook | as above | no lake reachable | this bundle, `sh check.sh --python-only` | steps 0 to 3b passed, exit 0 |

Notes from the clean-room run:
* The desk box was also running a low-priority background search (nice 19). It was paused with
  `kill -STOP` for the duration of the check and resumed with `kill -CONT` afterwards, so the
  timings above are for an otherwise idle 4-core machine, apart from the network.
* As in v1.0, `lake exe cache get` first tried the `mathlib4-master` cache bucket, found nothing
  there for this revision, and then downloaded all 8639 files from the main bucket. This is normal
  Mathlib cache behaviour, not an error. In the copied log, carriage-return progress lines are
  reduced to their final state (the raw log is kept in the research repository as
  `lanes/C13_release/attempts/desk_attempt1_run.log`).
