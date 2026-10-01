# Lane M: Mac Mini Rerun Report
**PLAYBOOK Section 8 — Independent Lean Certification, Second Machine**

---

## Machine

| Field | Value |
|---|---|
| Host | Mac mini (M4, 10 cores, 16 GB) |
| OS | macOS 27.0 (Build 26A428) |
| Lean toolchain | leanprover/lean4:v4.32.2 (per repo lean-toolchain) |
| elan | 4.2.4 (227caca13 2026-08-25), user-level install |
| Python | 3.9.6 (system) |
| Working dir | ~/c19_rerun/ (created fresh for this rerun) |
| Run date | 2026-09-30 (America/New_York) |

---

## Step-by-Step Results

### 1. elan install
User-level install via official script, `--no-modify-path --default-toolchain none`.
Result: `elan 4.2.4` installed to `~/.elan/bin/`.

### 2. Clone + checkout
```
git clone https://github.com/spectra-research/shannon-capacity-lean repo
git checkout aa21eeb
```
**HEAD SHA recorded:** `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65`

### 3. Patch application
**Patch SHA-256:** `6d60173a18459f12bf74cfde2d4d233dadcfd93ddba8b651c0f85f898c9717f8`

```
git apply --check ../certC19b.patch  -> OK
git apply ../certC19b.patch          -> OK
```

Files changed:
- `ShannonBounds.lean` (+2 lines: imports for CapCertC19b and CertC19b)
- `ShannonBounds/CapCertC19b.lean` (new, 88 lines)
- `ShannonBounds/CertC19b.lean` (new, large)

### 4. Build

`lake exe cache get`: downloaded 8639 mathlib .olean files (~8639/8639 = 100%).

`lake build ShannonBounds.CapCertC19b`: **Build completed successfully (2056 jobs).**
(Positive control `ShannonBounds.CapCertC19` skipped per playbook time guidance.)

### 5. Axioms check + sorry grep

Scratch file `axiom_check.lean`:
```lean
import ShannonBounds.CapCertC19b
#print axioms ShannonBounds.CapCertC19b.shannonCapacity_cycleGraph_19_ge
```
Run: `lake env lean axiom_check.lean` -> exit 0.

**Axiom list:** `propext`, `Classical.choice`, `Quot.sound`, plus `native_decide` kernels.
**`sorry` does NOT appear** in the axiom list.

Grep for `sorry` in `CapCertC19b.lean` and `CertC19b.lean`: **NO SORRY FOUND**.

### 6. Python independent checker

`eval_c19.py` (stdlib only, Lane R) run against the cloned repo's `ShannonBounds/` directory.
(Minor patch for Python 3.9 compat: `set_int_max_str_digits` wrapped in try/except; ROOT path hardcoded to `~/c19_rerun/repo/ShannonBounds`.)

**Exit code: 0**

Key output lines:
```
control root trunc15 = 9.357200030000796  (BPZ: 9.357200030000796) True
claim root trunc20 = 9.35720270023307379044
BPZ root trunc20 = 9.35720003000079613738
claim exceeds BPZ, exact witness r=9.35720003000079613739: True
decimal_le check a=9357202700233073 b=10^15: a^p <= M*b^p : True ; (a+1)^p > M*b^p : True
```

All node literals match Lean source (`True` for all 16 nodes).
All substitution tables admissible. All terminal codes pairwise separated.

---

## Timings (approximate)

| Step | Time |
|---|---|
| elan install | ~10 s |
| git clone + checkout | ~20 s |
| lake exe cache get | ~4 min |
| lake build ShannonBounds.CapCertC19b | ~60 s |
| lake env lean (axioms) | ~15 s |
| python eval_c19.py | ~5 s |

---

## Summary

**PASS**

- Repo cloned fresh from GitHub at commit `aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65`.
- Patch applied cleanly (sha256 `6d60173a...`).
- `lake build ShannonBounds.CapCertC19b` succeeded (2056 jobs, no errors).
- `#print axioms` shows only `propext / Classical.choice / Quot.sound / native_decide` kernels. **No `sorry`.**
- Grep of new files: **no `sorry`**.
- Python checker: all 16 substitution literals match, `decimal_le` bounds verified, exit 0.

The theorem `(9.357202700233073 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)` is Lean-certified at commit `aa21eeb` on an independent M4 Mac mini, with no sorry.
