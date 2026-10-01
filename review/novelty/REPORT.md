# Lane N2: Novelty search for Theta(C15) >= 7.301635000991096 and Theta(C19) >= 9.357203012726939
Date of search: 2026-10-01 (all queries run 2026-10-01, roughly 10:00 to 11:30 UTC).
Raw logs: `query_log.txt` (73 lines, one line per query with result counts) and `raw/` (87 files: API responses, READMEs, pages).

## VERDICT: NO KILL FOUND

No source found anywhere states a bound >= our values for C15 or C19. The best public bounds for both
cycles are still the BPZ Lean repo HEAD aa21eeb (pushed 2026-08-10). Nothing published, deposited or
pushed after 2026-08-10 improves C15 or C19.

| n | Our bound | Best public bound found | Source, date | Our margin |
|---|---|---|---|---|
| 15 | 7.301635000991096 | **7.301628695930103** (p=3664) | BPZ README table, github.com/spectra-research/shannon-capacity-lean @aa21eeb, 2026-08-10. Quote: `\| 15 \| 7.301628695930103 \| 3664 \| 3164 \|` | +6.305e-6 |
| 19 | 9.357203012726939 | **9.357200030000796** (p=11856) | same README, same commit. Quote: `\| 19 \| 9.357200030000796 \| 11856 \| 11514 \|` | +2.983e-6 |

Next-best public bounds (all weaker):
- BPZ arXiv:2607.29681v1 (2026-07-31), abstract: "Θ(C_{15})≥7.301600534487…, Θ(C_{19})≥9.357192705918…". No v2 exists (the v2 URL returns 404).
- Gao fork xyz2606/shannon-capacity-lean, README (2026-08-08): "| 15 | 7.301600548493336 | 4000 |", "| 19 | 9.357192717365020 | 16944 |". These are BPZ's values before aa21eeb. The fork's only extra content is C7.
- IRCR arXiv:2607.21517v2 (2026-07-30): "Θ(C_{15})≥8076974^{1/8}>7.301399". No C19.
- BPZ v1 Table 1 gives the prior C19 bound as 9.3571200 [BMR+71].

## Sources searched (counts are in query_log.txt)
1. **arXiv API**: 7 queries, all sorted by submittedDate. `"Shannon capacity" AND (cycle|cycles|odd)` gave 14 results, 3 since 2026-06-01. `"Shannon capacity"` gave 280 results, 16 since 2026-06-01. Also searched: zero-error, strong product, abs:"odd cycles", ti:Shannon capacity, and strong powers. I checked abs pages and probed v2/v3 URLs: 29681 has v1 only, 27869 v1 only, 21517 v1 and v2, 30273 v1 only. The listing pages math.CO, cs.IT, cs.DM and math.IT (new and recent) had nothing relevant. The arXiv web search returned the same 16 IDs.
2. **Citations**: Semantic Scholar found 1, 2, 3 and 0 citing papers for the four IDs. The only new one is 2609.17773, a Ramsey paper that is irrelevant. S2 bulk search found nothing new. OpenAlex lists all 4 works with cited_by=0. OpenAlex search since 2026-06 (121, 4662 and 49128 hits) surfaced only Zenodo deposits about C7.
3. **Zenodo** (not covered by lane N): 79 results for "Shannon capacity". The relevant ones all concern C7: Stavriianov 2026-09-12, Θ(C7) ≥ 3.258834362237710794 and α(C7^6) ≥ 1129; Oktiabrev 2026-09-26, a private-pairs negative result.
4. **GitHub**:
   - BPZ repo: 1 branch, 0 tags, 0 releases, 3 commits, 0 issues, 0 PRs, 1 fork.
   - The fork (xyz2606, Gao) has a `refined-c7-bound` branch whose diff touches only C7 files.
   - Protti repo: 3 branches and 5 tags (v0.1 to v0.5), all about C11/C13, 0 forks.
   - Repo search: 10 queries (61 hits for "shannon capacity"). Code search: 22 queries (e.g. "cycleGraph 19" 30 hits, "Theta(C19)" 0, BaseC19Data 1). Issue search: 6 queries. Commit search: 5 queries.
   - Other repos examined: aoktyabrev/shannon, Ratatosk32/*, tandonravi/*, nathanielitty/*, wustep/maths, vibemathing, ScientistsLastExam #34. All of these are C7, C11/C13, or benchmark work only.
5. **Authors**: Zuiddam's page lists his talks since August (CWI 8 Sep, AI4Science 23 Sep, LAB42 8 Oct, KWG 23 Oct) with no new numbers. Tandon's site was updated 2026-10-01 but does not mention Shannon. The jzuiddam GitHub has nothing new.
6. **Community**:
   - Wikipedia: the current revision has no 2026 bounds. Two edits citing BPZ (09-07 and 09-30) were reverted, and neither gave C15/C19 numbers.
   - teorth/optimizationproblems 9a (C7 page) cites the BPZ v1 values. u00dxk2/bounds-ledger mirrors it.
   - VibeMathed dataset (2 MB): the odd-cycle entry uses BPZ v1 values.
   - MathOverflow, math.SE and cstheory via the StackExchange API: nothing since 2026-06.
   - OEIS: 6 queries, nothing relevant.
7. **AI announcements**: 6 Exa web searches (AlphaEvolve, OpenAI, DeepMind, X/Twitter). The DeepMind AlphaEvolve repos contain no Shannon-capacity content. The Google AlphaEvolve TCS blog covers MAX-4-CUT, not Shannon capacity. The AI-Math-Contributions list has only the 2023 FunSearch entry.

## Inaccessible
- Lean Zulip API (needs authentication); I relied on Exa search of the public archive instead.
- Google Scholar.
- X/Twitter directly; I relied on Exa only.
- Gao's Google Site (JavaScript-only; Playwright is missing).
- svenpolak.nl (returned 500), pjotrbuys.nl and jzuiddam.com (DNS failure), nathanielitty.com (403).
- Full arXiv PDFs. I read the HTML versions of 29681 and 30273 instead.

## Residual risk (low to moderate)
- BPZ's README says the C15/C19 trees "will appear in the next arXiv version". A BPZ v2, or an unpushed BPZ branch, could appear with stronger trees at any time. This is the main risk.
- The method is public (Tandon's heterogeneous refinement, Stavriianov's tree search). Applying it to C15/C19 is an obvious next step, so parallel unpublished work is plausible.
- Search indexes lag by days. GitHub code search covers default branches only.
- Our margins are tiny (about 3e-6 and 6e-6), so any refinement by others would likely surpass them.
