# Lane R3: independent exact review of the C15 and C19 DAG schedules

**Verdicts:** C15 `7.301635000991096` at p = 3424: **CONFIRMED**. C19 `9.357203012726939` at p = 14800: **CONFIRMED**.
Both are exact integer arithmetic inside BPZ's framework. I did not run `lake build` on the L2 Lean files.

## Rerun (stdlib only, about 2 s)

    cd discovery-2026-09
    nice -n 10 python3 lanes/R3_review/eval_dag.py data/bpz lanes/O_opt/best_C15_A_ref.json lanes/O_opt/best_C19_C_ref.json \
        --lean lanes/L2_lean/out/CertC15b.lean lanes/L2_lean/out/CertC19c.lean | tee lanes/R3_review/run.log
    cd lanes/R3_review && nice -n 10 python3 neg_control.py ../../data/bpz | tee neg_control.log

Outputs: `run.log`, `neg_control.log`, `M_C15.txt`, `M_C19.txt` (the exact M values).
Not read: any code under lanes/O_opt, L2_lean, L_lean or G_c19_baseline. I read only the two JSONs, the L2 `out/*.lean` files and `DagTail.lean`.

## What is parsed and re-checked from BPZ Lean (data/bpz)
* `Letter.sep` (PortRealisation.lean:37): 22 ordered pairs, symmetric and irreflexive. `Letter.sigma` (Reindex.lean) = (A D)(H V). It preserves sep.
* All 10 tables `S2a..S3h` pass my own hin + hcross check (Layered.lean:89). All 3 codes are pairwise separated (Layered.lean:379).
* **Base, recomputed from raw words** (BaseC{n}Data `Iraw/Xraw/pairsRaw/portsRaw`, C_n^4 closed-neighbour conflict). I re-checked I and X for independence and checked every RichPortSystem field (Lift.lean:97): ports in I, ep_parent, alt not in I, private, ep_conflict, alt injective, both transversals independent, and hsep. Recomputed families (PortRealisation `fam`): C15 (2839,2833,6,3,3,3,3), C19 (7664,7661,3,2,2,2,2). Both equal `w0`.
* `Rf` = base reindexed by sigma, with weights w(sigma a) (`w_reindex`). For C15 it swaps A=6 and D=3.
* d = 4 is read from `CapCertC{n}` `strongPower_mul_iso`. Then p = 4E.

## Positive controls (exact)
| cert | node literals | M == Lean M | p | digits | root |
|---|---|---|---|---|---|
| CertC15 | 23/23 match | yes | 3664 | 3164 | 7.301628695930103 = README |
| CertC19 | 16/16 match | yes | 11856 | 11514 | 9.357200030000796 = README |
| CertC7 (uses Rf + S2a) | 8/8 match | yes | 500 | 257 | 3.258827985920007 = README |

## Schedules
JSON format, inferred and then confirmed against the L2 Lean: `[S, c1, c2(, c3)]` is a multiSubst node. `["tail", start, S, 0, "ww", n]` is `DagTail.tailIter S start R1 R1 n`. Atoms are `R1` and `Rf`. Exponents add up.

| | C15 (best_C15_A_ref) | C19 (best_C19_C_ref) |
|---|---|---|
| tables used | S2a, S3e, S3f, S3g (+Rf) | S3a, S3e, S3f, S3g |
| distinct nodes / tails | 20 / 63, 3, 5, 19 (+ one n=0 no-op) | 26 / 265, 193, 153, 52, 177, 68, 230, 80 (+ one n=0) |
| eT, E | (314,147,169,226), 856 | (1245,713,793,949), 3700 |
| p = 4E | 3424 | 14800 |
| digits(M) | 2957 | 14373 |
| sha256(M_Cn.txt) | 541b2c97...f702b | c8404604...be08 |
| trunc15 root | **7.301635000991096** | **9.357203012726939** |

For both: a^p <= M*10^(15p) < (a+1)^p holds exactly.

## Comparison with the L2 Lean files
* `CertC15b.M` and `CertC19c.M` literals equal my M **digit for digit**.
* I re-evaluated the Lean `Sizes` DAG independently (node2/node3/tailW). It gives the same M.
* For every node, the `Rn*` realisation uses the same S, the same children, the same `en*` exponents and the same declared `strongPower G k` as its `sn*` size. Each `tailIter` call has the same arguments as its `tailW`. `eT`, `terminalChildren` and E in `bound` are consistent. No structural problems found.
* In `CapCertC15b`/`CapCertC19c`: d = 4, E = 856/3700, the `tight` exponents and decimals equal mine.

## Negative controls (neg_control.log)
The checker rejects each of these: a corrupted table, a corrupted code, a sigma that breaks sep, the C15 schedule with one tail shortened by one, and the C15 schedule with its Rf replaced by R1. The last two give M different from the Lean literal.

## Caveats
* The C15 bound uses Rf. This is legitimate: BPZ's CertC7 uses the same `reindex Letter.sigma` construction, and my control reproduces it.
* The JSON `float_rate` values (7.30163381, 9.35720281) are below the exact roots. They are optimiser floats, not used in the claim.
* The C15b.json field `M_sha_prefix` is actually the decimal prefix of M, not a sha.
* I did not compile the Lean. My confirmation is the exact arithmetic plus a structural reading of the Lean files.
