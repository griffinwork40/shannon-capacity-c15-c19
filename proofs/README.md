# proofs/: the five Lean files

These files are **additions to BPZ's Lean repository**,
https://github.com/spectra-research/shannon-capacity-lean at commit
`aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65`. They do not build on their own: they import BPZ's
`ShannonBounds` framework (and Mathlib), and belong in its `ShannonBounds/` directory.

They are provided here for reading. They are byte-identical to the files that
`../artifact/certL2.patch` creates when applied to a clean checkout of `aa21eeb` (verified for this
release by applying the patch to a pristine copy and comparing sha256). `check.sh` pins the same
hashes.

| file | sha256 | contents |
|---|---|---|
| `DagTail.lean` | `f277d0b7695904f6339f760e6c37a51b40654d2b546e61d657bf268153efe147` | generic helper: `tailIter` (J-fold tail) and its size lemma `w_tailIter`, proved by induction without `native_decide` |
| `CertC15b.lean` | `fd76961fc9d9ebf1d45b1d8f824250e37bd0f94701d694cf97a39779322ae9b9` | the C15 schedule (20 nodes), `M` (2957 digits), `alpha_strongPower_ge` |
| `CapCertC15b.lean` | `45b3b426ed9ee29ec553cfad72e9bcca7b7393bbe4fe01dd791872e07d435e6d` | `shannonCapacity_cycleGraph_15_ge : (7.301635000991096 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 15)` |
| `CertC19c.lean` | `c1d8209e7e628bc7556303f90c2c912fa68ba7c313f501ab2c1ce9246833b4ba` | the C19 schedule (26 nodes), `M` (14373 digits), `alpha_strongPower_ge` |
| `CapCertC19c.lean` | `d5d08a91559d8e5f93bfcaadb067f208a8bdc65d10e992018f6ab7e6c44f95b9` | `shannonCapacity_cycleGraph_19_ge : (9.357203012726939 : ℝ) ≤ shannonCapacity (SimpleGraph.cycleGraph 19)` |

The patch also adds five `import` lines to BPZ's `ShannonBounds.lean` and changes nothing else.

To build them by hand instead of with `check.sh`:

```sh
git clone https://github.com/spectra-research/shannon-capacity-lean
cd shannon-capacity-lean && git checkout aa21eeb12b75b0413d3fa9fb4208b5d0bf2c4d65
git apply /path/to/artifact/certL2.patch     # or copy these five files into ShannonBounds/
lake exe cache get
lake build ShannonBounds.CapCertC15b ShannonBounds.CapCertC19c
```

Licence: Apache-2.0, as BPZ's repository. The file headers state that they were contributed by
Griffin Long with the AI agent agent-afk, as an addition to BPZ's framework, and that BPZ did not
write them.
