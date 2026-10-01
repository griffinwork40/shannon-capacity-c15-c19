# method/: how the schedules were found and turned into Lean

**None of this is part of the trust base.** A schedule is just data. The Lean build in
`../artifact/check.sh` (and, independently, `../artifact/eval_dag.py`) checks the result whatever
produced it. This directory is here so the search can be inspected and rerun.

The files are byte-identical copies of the research-repository files listed in
`../PROVENANCE.md` (paths kept: `lanes/O_opt/`, `lanes/L2_lean/`, `verifier/`). Nothing was
edited, so the relative-path assumptions below are those of the research repository.

| file | role |
|---|---|
| `lanes/O_opt/search2.py` | beam search over BPZ schedule DAGs (float scoring; BPZ tables, codes and reindexing only); produced both winning schedules |
| `lanes/O_opt/exact_eval.py` | local refinement of tail lengths (`--refine`, writes `*_ref.json`) and exact integer evaluation |
| `lanes/O_opt/worker.sh` | the job driver actually used: `search2.py N 12 8 EMAX MAXNODES TAG 420`, then `exact_eval.py best_TAG.json --refine` |
| `lanes/O_opt/certs.py`, `lean_parse.py`, `recursion.py`, `search.py` | parsers of BPZ's Lean sources, the exact recursion, and helpers imported by the above |
| `verifier/verify.py` | stdlib helper imported by `recursion.py` |
| `lanes/L2_lean/gen_dag.py` | turns a schedule JSON into `CertC*.lean` / `CapCertC*.lean` |
| `search_logs/` | the original logs of the two winning jobs (`exact_C15_A.log`, `search_C19_C.log`, `exact_C19_C.log`) |

## Path assumptions (left unchanged on purpose)

* `lean_parse.py` reads BPZ's Lean sources from `$BPZ_REPO` if set, else from
  `../../data/bpz/ShannonBounds` relative to `lanes/O_opt/`. Set
  `BPZ_REPO=/path/to/shannon-capacity-lean/ShannonBounds` (a checkout of BPZ at `aa21eeb`).
* `recursion.py` and `certs.py` add `../../verifier` to `sys.path`; `gen_dag.py` imports from
  `../O_opt`. Keep the directory layout of this folder.
* The driver uses `$PY` (default `../../.venv/bin/python`). Python 3.11+ (uses
  `sys.set_int_max_str_digits`) with NumPy for the search; the exact evaluator is stdlib-only.
* Outputs are written next to the scripts (`best_TAG.json`, `best_TAG_ref.json`, `logs/`).

## Rerun

```sh
git clone https://github.com/spectra-research/shannon-capacity-lean bpz
git -C bpz checkout aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65
cd method/lanes/O_opt
export BPZ_REPO=$PWD/../../../bpz/ShannonBounds PY=python3   # python3 with numpy
sh worker.sh "15 916 100000 C15_A"      # C15: about 1 min; writes best_C15_A_ref.json
sh worker.sh "19 11856 600 C19_C"       # C19: a few minutes; writes best_C19_C_ref.json
cd ../L2_lean
python3 gen_dag.py ../O_opt/best_C15_A_ref.json C15b      # writes out/CertC15b.lean, out/CapCertC15b.lean
python3 gen_dag.py ../O_opt/best_C19_C_ref.json C19c --prev=9.357202700233073:'CapCertC19b (lane L)'
```

What to expect (checked on 2026-10-01 on the laptop, see the release-build report):

* `worker.sh "15 916 100000 C15_A"` and `worker.sh "19 11856 600 C19_C"` reproduced
  `best_C15_A_ref.json` (sha256 `6a37e3c9…`) and `best_C19_C_ref.json` (sha256 `df340f3f…`)
  byte for byte, identical to `../artifact/schedules/`. The beam search is deterministic (no
  random seed), but it has a wall-clock limit (420 s inside `search2.py`, 540 s in `worker.sh`), so
  a much slower machine could stop earlier with a different schedule. On the laptop C15 took about
  1 minute and C19 about 2 minutes.
* `gen_dag.py` on the two shipped schedules regenerates the four certificate files exactly,
  **except lines 2 to 4** (the header comment): the generator still writes BPZ's copyright and
  author header, which was replaced by hand with the "Contributed in 2026 by Griffin Long, with
  the AI agent agent-afk …" header after the red-team review (see `../artifact/ENVIRONMENT.md`).
  `DagTail.lean` was written by hand and received the same header change.
* The search also needs BPZ's own `CertC15.lean` / `CertC19.lean` (it seeds from them), which is
  why a BPZ checkout is required.

Other search code from the research repository (simulated annealing, exploratory scripts, and
the jobs for C7, C11, C13, C23 that gave no certified gain) is not included, because it did not
produce the published schedules.
