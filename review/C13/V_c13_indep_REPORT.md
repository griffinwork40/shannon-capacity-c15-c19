# V_c13_indep: independent verification of the claim Θ(C13) ≥ 6.302927071589786

Date: 2026-10-01. Machine: laptop only. Nothing outside `lanes/V_c13_indep/` was modified.

## Scope change
Partway through, the coordinator narrowed this lane to **task 4 only**. Tasks 1–3 had been
confirmed by the other session's reviewer (`discovery-2026-09/review/C13_independent/REPORT.md`).
My partial work on tasks 1–3 was already finished when the instruction arrived. It is kept here as
supporting evidence. I ran no Lean builds.

| Task | Verdict | Evidence |
|---|---|---|
| 1. Base family sizes | CONFIRMED (supporting) | `base_recompute.py` → `base_recompute.out` |
| 2. Own evaluator reproduces M | CONFIRMED (supporting) | `my_eval.py`, `run_eval.py` → `run_eval.out` |
| 3. Exact M vs Protti N | CONFIRMED (supporting) | `run_eval.out` (`protti` block) |
| 4. Literature recheck | **CONFIRMED (no larger C13 bound found), with stated search limits** | `lit/` |

### Task 1 (supporting)
Raw syndrome lists exist in BPZ `BaseC13Data.lean`: Sraw, SXraw, SPraw, SAraw and pairRep. I
expanded them over all 13^6 words in NumPy and checked every RichPortSystem condition by brute force:
* I and X are independent;
* the ports lie inside I;
* each alternative conflicts with its own parent and with no other word of I (private);
* alternatives are injective, and both transversals are independent;
* the footprints are disjoint.

The resulting sizes are (N, d, L, η) = (62530, 1014, 62530, 60502), with |X_c| = 1014, matching the
BPZ v1 paper profile.

### Task 2 (supporting)
I wrote my own evaluator from the rules in BPZ `Layered.lean` (`w_multiSubst`, `card_multiCodeSet`)
and `Reindex.lean`. It parses the S2b, S3c and K3a tables from the raw Lean literals and re-checks
their admissibility independently.
* **Positive control:** it reproduces BPZ's CertC13.M exactly and the root 6.302926729310108 at
  p = 522.
* **Our schedule:** it gives M = M_C13.txt = CertC13b.M, 418 digits, sha256 cac3a5bd…0914fba.

### Task 3 (supporting)
M > N exactly. The 30-digit roots are:
* ours: 6.302927071589786110170913803164
* Protti: 6.302927046770772321964462956570

**Typo in the T_c13 report:** M − N ≈ 4.72e**411** (412 digits), not 4.72e414 as written in
T_c13/REPORT.md. The relative gain is still 2.06e-6.

## Task 4: literature recheck (fetched 2026-10-01 with curl and the GitHub API; raw files in `lit/`)

**Protti, github.com/matthewprotti/c11-shannon-capacity-lower-bound**
* `git ls-remote` shows tags v0.1.0–v0.5.0 only. v0.5.0 points to dfaef37e60e5 (2026-09-09T17:47Z).
* HEAD is 6a0235fab88c (2026-09-09T22:47Z), 4 commits ahead of v0.5.0. The compare API shows those
  commits touch docs, diagnostics and reviews only, with no .lean files.
* Releases API: the newest release is v0.5.0 (published 2026-09-09T17:49Z).
* The main README still states "Theta(C13) >= 6.302927046770772 in dimension 522".
* No activity after 2026-09-09.

**BPZ, github.com/spectra-research/shannon-capacity-lean**
* HEAD is aa21eeb (2026-08-10), and that is the only branch.
* README C13 row: `| 13 | 6.302926729310108 | 522 | 418 |`.

**arXiv 2607.29681**
* The abs page lists only [v1], Fri 31 Jul 2026.
* `https://arxiv.org/abs/2607.29681v2` returns HTTP 404.
* The API also reports v1 only. Its C13 value is 6.302455083464.

**arXiv search**
* API query "Shannon capacity", newest first, returned results through 2026-09-28. Relevant hits:
  * 2607.21517v2 (IRCR): C13 ≥ 6.300109.
  * 2607.27869 (Gao): C7 only.
  * 2608.30273 (Tandon, 2026-08-31): C7 only, 3.25883262.
  * 2608.06573v5 (Sason): lexicographic products, no C13 bound.
* Query "odd cycles" AND capacity found nothing new.
* The math.CO and cs.IT "recent" listings (25 Sep–1 Oct 2026, 363 and 145 titles) have no Shannon,
  odd-cycle or strong-product capacity paper.
* Semantic Scholar shows exactly one citation of 2607.29681: Tandon, C7 only.

**Tao, teorth/optimizationproblems constants/9a.md**
* Last commit 3fcd485d9414 (2026-09-06).
* The page lists C7 bounds up to Tandon's 3.25883262. For C13 it only mentions BPZ v1: "Θ(C13) ≥
  6.302455083464…".
* Recent issues and PRs mentioning Shannon (#168, #174, #198) contain no C13 value.
* The bounds-ledger mirror (u00dxk2) of 9a.md is identical.

**GitHub repository search**
* Queries for Shannon capacity / odd cycle / Lean found only these: BPZ, Protti, IRCR (last push
  2026-07-30), Gao, Tandon (C7), Zuiddam's other Lean repositories, and our own
  griffinwork40/shannon-capacity-c15-c19.
* None of them contains a C13 bound above 6.302927046770772.

**Conclusion:** I found no C13 lower bound ≥ 6.302927046770772 other than Protti's own. Protti's
v0.5.0 remains the prior record, and the claimed 6.302927071589786 exceeds it.

**Limits:**
* There was no general web search engine: Exa/web_scrape failed on this machine.
* arXiv was searched by metadata (title and abstract), not full text.
* Private or unpublished work, and anything posted after the fetches (about 12:50–13:10 EDT
  2026-10-01), cannot be excluded.
