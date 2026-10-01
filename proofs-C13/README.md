# proofs-C13/: the Lean files of the C13 certificate (v1.1)

These files are **additions to BPZ's Lean repository**,
https://github.com/spectra-research/shannon-capacity-lean at commit
`aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65`. They do not build on their own: they import BPZ's
`ShannonBounds` framework (and Mathlib), and belong in its `ShannonBounds/` directory.

They are provided here for reading. They are byte-identical to the files that
`../artifact-C13/certC13.patch` creates when applied to a clean checkout of `aa21eeb` (verified for
this release by applying the patch to a pristine GitHub clone and comparing sha256). `check.sh`
pins the same hashes.

The patch creates four files. The fourth, `DagTail.lean`, is byte-identical to `../proofs/DagTail.lean`
(sha256 `f277d0b7695904f6339f760e6c37a51b40654d2b546e61d657bf268153efe147`) and is not repeated here.

| file | sha256 | contents |
|---|---|---|
| `DagCode3.lean` | `fa3f760ff74d11f870728d1f5b5a2bb37de149ab9525d7986f6d131e60763377` | generic helper: `code3` and its size lemma `sum_code3`, the arity-3 analogues of `DagTail.code4` / `sum_code4` |
| `CertC13b.lean` | `cffbb8ab757a7f8d2d7b4b8cfa6d3597431e77b725f39f87d6a9768946e22564` | the C13 schedule (49 nodes, terminal code K3a on exponents 34, 36, 17), `M` (418 digits), `stepM`, `bound` |
| `CapCertC13b.lean` | `5c5558263bf78fde7d54d191eb0e58611ad38997a334b4959dacfa97dd77ea6a` | `alpha_strongPower_ge : M ≤ α(C13^⊠522)`, `shannonCapacity_cycleGraph_13_ge : (6.302927071589786 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 13)`, `tight`, `improves`, `improves_1` |

The patch also adds four `import` lines to BPZ's `ShannonBounds.lean` and changes nothing else.
It is an alternative to `../artifact/certL2.patch` (the v1.0 C15/C19 patch), not a stack on it:
both create `DagTail.lean`, so each applies on its own to a clean `aa21eeb`.

To build them by hand instead of with `check.sh`:

```sh
git clone https://github.com/spectra-research/shannon-capacity-lean
cd shannon-capacity-lean && git checkout aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65
git apply /path/to/artifact-C13/certC13.patch   # or copy these three files and ../proofs/DagTail.lean into ShannonBounds/
lake exe cache get
lake build ShannonBounds.CapCertC13b
```

Licence: Apache-2.0, as BPZ's repository. The file headers state that they were contributed by
Griffin Long with the AI agent agent-afk, as an addition to BPZ's framework, and that BPZ did not
write them.
