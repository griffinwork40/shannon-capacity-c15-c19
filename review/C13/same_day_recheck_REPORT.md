# C13 v1.1 pre-publish gate: same-day recheck (2026-10-01, fetches about 20:53–21:10Z)

**VERDICT: FIX-WORDING.** The novelty and credit story stand. Nothing at or above
6.302927046770772 other than Protti's own bound was found. Protti's work is described correctly
in substance. Before publishing, make the exact edits in §B and §C below. One sentence is
inaccurate (note.md: "his refines BPZ's schedule locally"). One factual line is stale ("HEAD …
changes documentation only"). The search-limits text is now out of date. A credit to Itty et al.
for the C13 base set is missing.

Raw evidence is in `evidence/`, and the fetch time is in `evidence/fetch_time.txt` (20:53:26Z).
Fresh clones are in `/tmp/c13_recheck/{protti,bpz}`.

## A. Same-day recheck

**A1. Protti** (`evidence/protti_lsremote.txt`, `protti_log.txt`, `*protti*_{issues,pulls,releases,repo}.json`, `protti_events.txt`)
* Refs are unchanged:
  * HEAD and main are at 6a0235f.
  * The two codex/* branches equal PR #1 and PR #2, both closed and merged 2026-09-09.
  * Tags are v0.1.0–v0.5.0, and v0.5.0^{} = dfaef37.
* There are no commits after 6a0235f. pushed_at is 2026-09-09T22:47Z.
* Releases: the newest is v0.5.0.
* Issues and PRs: only #1 and #2, both his own, both closed, neither about a new bound.
* Forks: 0. His public events stop on 2026-09-09. His other repos are not about Shannon capacity.
* `C13R8D522.lean` is byte-identical at dfaef37 and 6a0235f (sha256 06fb80a1…, `protti_C13R8D522_sha256.txt`).
* **Correction to prior lane:** dfaef37→6a0235f is *not* docs-only and does not have "no .lean
  files". It adds two diagnostic Lean scripts,
  `diagnostics/olean-paths-2026-09-09/{InspectModule,NormalizeLintPaths}.lean`
  (`protti_lean_diff_since_tag.txt`). Neither touches any bound. The only README bound text
  changed is a link (`protti_diff_stat_tag_to_head.txt`).

**A2. BPZ** (`bpz_lsremote.txt`, `bpz_log.txt`, `spectra-research_*`)
* HEAD and main = aa21eeb; there is no other branch. pushed_at is 2026-08-10.
* 0 issues, 0 PRs, 0 releases.
* There is one fork, xyz2606 (Gao). Its branch `refined-c7-bound` is C7 only; last push
  2026-08-08 (`bpz_fork_xyz2606.txt`).
* There are no third-party C13, C15 or C19 claims.

**A3. arXiv** (`arxiv_2607.29681.xml`, `arxiv_q_*.xml`)
* 2607.29681 is v1 only (published = updated = 2026-07-31). `/abs/2607.29681v2` returns 404.
* API searches covered "Shannon capacity", "odd cycles", strong product + independence, Shannon
  capacity + cycle, C13 + capacity, and zero-error capacity, newest first. The only relevant
  papers are the known ones:
  * 2607.21517 (IRCR);
  * 2607.27869 (Gao);
  * 2607.29681 (BPZ);
  * 2608.30273 (Tandon, C7);
  * 2608.06573 (Sason).
* Nothing new since the earlier check. Semantic Scholar still lists one citation of 2607.29681
  (Tandon; `s2_citations.json`).

**A4. Tao board** (`teorth/optimizationproblems`; `tao_9a_commits.txt`, `tao_9a.md`, `tao_open_prs.txt`, `tao_issues_since_aug.json`)
* The last commit to `constants/9a.md` is 3fcd485 (2026-09-06).
* Its C13 entry only cites BPZ v1: "Θ(C13) ≥ 6.302455083464…" (line 56).
* There are 10 open PRs, none about Shannon capacity or C13/C15/C19. Issues and PRs since August
  that mention Shannon are #168 and #174 (closed, C7 only).

**A5. GitHub search** (`gh_repo_search.txt`, `gh_code_search.txt`, `gh_extra_search.txt`)
* Repo searches found only known repos:
  * BPZ, Protti, IRCR (Itty), Tandon (C7), xyz2606 (C7);
  * aoktyabrev/shannon (C7 only);
  * vibemathing (C7);
  * our own c15-c19.
* Code search for "6.302927" and "6.30292" returned only unrelated numeric data files.

**A6. Other sources**
* A general web search (Exa) worked in this session, unlike the earlier lane. Three queries found
  nothing new.
* VibeMathed's odd-cycle records page (sitemap lastmod today) still lists C13 at BPZ v1
  6.302455083464 (`vibemathed_records_extract.txt`). Protti has a C11 entry there, not C13.
* Exact recheck (`exact_compare_recheck.txt`):
  * M in the patch equals M_C13.txt.
  * M and N both have 418 digits, and M > N.
  * M − N has 412 digits (4.7204e411), and M/N − 1 = 2.0555e-6.
  * Roots: 6.30292707158978611…, gain 2.4819e-8.
  * All numbers in the drafts check out (3.42e-7 over BPZ, 3.9e-9 in log, <1/10 of Protti's step).

## B. Typed cells: verified against Protti's sources

**What Protti's construction does:**
* It keeps BPZ's C13^6 base, the seven-family relation, the schedule
  (a3…a9, b2…b17, c12, x34, x36; K3a on (x34, x36, b17)), the tables T2b/T3c, the terminal code
  K3a and dimension 522 (README.md:25; R8 PROOF.md §4–5; SEARCH_LEDGER "No seed mutation, table
  mutation, child permutation, reassembly, terminal replacement").
* It refines the 7 letters into 58 (family, mask) "type" letters.
* It adds guarded augmentations at three nodes:
  * c12 → A, reference code {BAB, BBV};
  * x34 and x36 → N, code {BBA, BBH, BVB, VAB, VBH, VHB}.
* In Lean it uses compiled typed tables over `C11R6Base.Ty`/`typedSep` (C13R8D522.lean:4–16).

**What ours does:**
* `certC13.patch` uses only BPZ's 7-letter `Letter`/`Letter.sep`, `Substitutions.S2b` (32 nodes)
  and `Substitutions.S3c` (17 nodes), 49 nodes in total. It uses `TerminalCodes.K3a` on
  n17/n37/n48 with exponents 34/36/17, and the BaseC13 base sizes.
* Atom Rf is `reindex Letter.sigma` from BPZ's `Reindex.lean`. That is a stock BPZ gadget, though
  BPZ's CertC13 itself does not use it.
* There is no `Ty`, no typed table and no new table or code; the only `Code` line is an alias of
  K3a.
* **"No typed cells, only a different schedule" is confirmed.**

**Draft sentences checked:**

| draft sentence | status |
|---|---|
| RELEASE_NOTES: "Protti's construction adds typed cells to BPZ's own schedule; ours uses no typed cells, only a different schedule." | accurate |
| RELEASE_NOTES: "It improved the value 6.302926729310108 … aa21eeb" | accurate |
| note §8 and README Prior bounds: "keeps BPZ's base and schedule and adds guarded typed cells at three nodes" | accurate (matches his README:25) |
| BPZ email: "which itself improves your aa21eeb value" | accurate |
| Protti email: "Your typed cells and our schedule are different kinds of change" | accurate |

**Wording edits:**
1. **note_C13_section.md** (inaccurate: he does not change the schedule)
   * Current: "his refines BPZ's schedule locally, ours replaces the schedule."
   * Replace with: "his keeps BPZ's schedule and enlarges families at three of its nodes with
     guarded typed cells; ours replaces the schedule."
2. **README "plain language"** (loose wording)
   * Current: "combined in a different order"
   * Replace with: "combined according to a different substitution schedule"
   * Optional: change "by adding typed cells to BPZ's construction" to "by adding guarded typed
     cells at three nodes of BPZ's construction".

## C. Other wording, overclaim and attribution fixes

3. **note §8 "Novelty check"** (stale/inaccurate)
   * Current: "Protti's HEAD after `v0.5.0` changes documentation only"
   * Replace with: "Protti's HEAD after `v0.5.0` adds only documentation and two build-diagnostic
     Lean scripts; `C13R8D522.lean` is unchanged"
   * Make the same fix in README Prior bounds, which says "changes documentation only".
4. **Search-limits text**, in RELEASE_NOTES, note §8 and README "Literature check".
   * "No general web search engine was available" is no longer true.
   * Replace with: "A same-day recheck at about 21:00Z on 2026-10-01 (GitHub refs, issues, PRs
     and forks; arXiv API; Tao's page and PRs; a general web search) found nothing new.
     Arxiv was searched by metadata only, and unpublished work cannot be excluded."
   * In README, change "after about 17:00Z" to "after about 21:00Z".
5. **Missing credit (attribution)**
   * The C13 README and RELEASE_NOTES call the base "BPZ's C13^6 base" and never mention Itty,
     Rosin, Carstensen and Reichman or Gao.
   * The 62530-element C13^6 base size is IRCR's (arXiv:2607.21517). BPZ's paper starts C13 from
     profile (62530, …), and BPZ's README credits Gao and IRCR for the method. (BPZ's Sraw set is
     not literally IRCR's set: the overlap is 676 words, `base_vs_ircr.txt`. Isomorphism was not
     checked.)
   * Add to README "What is new" and to RELEASE_NOTES: "BPZ's C13 base is a port system on an
     independent set of size 62530 in C13^⊠6, the size first found by Itty, Rosin, Carstensen and
     Reichman (arXiv:2607.21517); BPZ's method builds on Gao (arXiv:2607.27869) and on Itty et al."
6. **email_BPZ_followup**
   * The greeting "Dear Jeroen, Sven and Pjotr" addresses Buys, but the thread goes only to
     Zuiddam with Polak in cc.
   * Either cc Buys if an address exists, or write "Dear Jeroen and Sven (and Pjotr, via this
     forward)".
7. **Optional:** note table, BPZ v1 row: fill the dimension cell with 432 (BPZ v1 §C13).

There is no wrong BPZ name anywhere. Every draft uses Buys, Polak and Zuiddam or Buys-Polak-Zuiddam.

## Not checked
* No Lean build was run. I relied on the logged runs.
* I did not check private correspondence, or whether a Protti contact email exists.
* Arxiv full text was not searched.
* VibeMathed was checked only through raw HTML, because the headless browser was unavailable.
* I did not check whether BPZ's and IRCR's C13^6 sets are isomorphic.
* Model names in the AI disclosure were not checked.
