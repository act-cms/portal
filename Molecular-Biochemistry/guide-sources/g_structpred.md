## At a glance

| | |
|---|---|
| **Runtime** | CPU. Everything here is NumPy — no GPU, no model download, nothing to queue for. |
| **Wall clock** | About a minute, nearly all of it the package install. Budget 90 minutes of class time — this is a reading-and-discussion session with code attached. |
| **Network** | RCSB, for `6ane.pdb`. |
| **Prerequisites** | Comfort with matrices and indices. No deep-learning background needed. |
| **Produces** | `manifests/lab4_1_lockfile.json` |
| **Quiz items** | 4, in two blocks |

> **This notebook does not run AlphaFold.** No model is downloaded, no MSA is built, no
> structure is predicted. Sections 1 and 2 are correct, self-contained implementations of two
> AlphaFold2 *operations* in NumPy, and they are worth teaching. Sections 3 to 5 take the
> `6ANE` crystal coordinates, add Gaussian noise, call the result "the AlphaFold2 prediction",
> and then congratulate it on agreeing with the crystal structure. The code comments say so
> plainly; the printed output does not. Decide how you want to handle that before the session,
> because it is the only place in this set where a student could leave with a false belief
> about what a method can do.

## What this notebook is for

The architecture, honestly: how evolutionary information in an MSA becomes a pairwise
geometric hypothesis, and how that hypothesis becomes coordinates. Plus the confidence metrics,
which are the part students will actually use when they download a model from the AlphaFold
database and have to decide whether to trust it.

## Section-by-section

### Section 1 — Evoformer operations in NumPy

```
MSA Input Tensor:           (20, 15, 32)   (N_seq=20, L=15, channels=32)
Outer Product Mean Update:  (15, 15, 16)
Triangular Multiplicative:  (15, 15, 16)
Mean Triangular Magnitude:  0.5011
```

Two operations, both implemented correctly. The outer product mean is the channel through
which coevolution reaches the pair representation — a column pair that varies together in the
MSA produces a large entry at (i, j). The triangular update is the geometric consistency
constraint: if i is close to k and k is close to j, then d(i,j) is bounded, and updating every
pair using every third residue enforces that.

The tensor shapes are the lesson. Have students say out loud what each axis means before the
cell runs. The step from "an alignment" to "an L×L×c tensor" is the conceptual jump of the
whole session.

### Section 2 — Invariant Point Attention

A `RigidFrameSE3` class and a point-affinity calculation, then the key test:

```
Original IPA Point Affinity:    -15.845245
Transformed IPA Point Affinity: -15.845245
Absolute Difference:            4.44e-14
```

This is the best cell in the notebook. Rotate and translate the entire molecule and the
attention weight does not change, to machine precision. That is not a coincidence or an
approximation — it is a structural property of computing distances between points expressed in
local frames. Ask the class why a network would need this property rather than learning it,
and you get a real discussion about inductive bias and data efficiency.

### Section 3 — pLDDT and PAE

The confidence material is correct and well explained. pLDDT is a per-residue estimate of
local accuracy, calibrated against lDDT; PAE is a pairwise estimate of how wrong the position
of residue j would be if you aligned on residue i. The off-diagonal block interpretation —
high pLDDT in both domains with high inter-domain PAE means confident domains in an uncertain
relative orientation — is the single most useful thing in this session and it is the subject
of quiz question 3.

What the student sees:

```
Mean Whole-Chain pLDDT:           90.84 (High Quality Prediction)
Very High Confidence (pLDDT > 90): 87.0% of residues
Confident (70 <= pLDDT < 90):      13.0% of residues
Low Confidence (pLDDT < 70):        0.0% of residues
```

Those numbers are constructed, not predicted. The cell sets a baseline of 92.5, ramps the
first 15 and last 10 residues down into the 70s, drops an eight-residue surface loop near position 140 to 78, and adds
Gaussian jitter. It is a reasonable-looking profile for a rigid α/β hydrolase and it is a
drawing, not a measurement. The PAE matrix is likewise derived from the crystal Cα distances.

I have no objection to a synthetic profile for teaching how to *read* pLDDT — you need a
plausible curve and you do not need a GPU to get one. The objection is to the word
"Prediction" in the heading.

### Section 4 — "validation" against the crystal structure

```
=== AlphaFold2 Prediction vs. Experimental Ground Truth (6ANE) ===
Total C-alpha Atoms Evaluated:     262
Whole-Chain Backbone C-alpha RMSD: 1.016 Å (Sub-1.5 Å Atomic Accuracy!)
Catalytic Ser160 (133) Alignment Error: 0.808 Å
Catalytic Asp206 (179) Alignment Error: 0.766 Å
Catalytic His237 (210) Alignment Error: 0.948 Å
Aromatic Clamp Trp185 (158) Error:      0.933 Å
Conclusion: The catalytic active-site triad is predicted with atomic-level fidelity (<0.6 Å error).
```

Three separate problems in six lines.

**The "prediction" is the answer plus noise.** `ca_pred_coords = ca_coords_exp.copy()`, then
`rng.normal(0, 0.45)` on core residues and `rng.normal(0, 1.25)` on low-confidence ones. The
1.016 Å RMSD is the magnitude of the noise that was just added — for the core, 0.45 × √3 ≈
0.78 Å by construction. The Kabsch superposition is correctly implemented and is measuring
nothing.

**The conclusion contradicts the numbers directly above it.** It claims errors below 0.6 Å.
The four values printed are 0.808, 0.766, 0.948 and 0.933 Å. Every one exceeds the threshold
in the sentence. A student who reads carefully will catch this, and they should.

**The triad indices are off by one.** `triad_indices_0based = [132, 178, 209, 157]` assumes the
chain starts at residue 1. Chain A of `6ANE` starts at residue **2**, so index 132 is residue
134 — a methionine. I checked all four: the code reads Met134, Ser180, Ser211 and Asp159
instead of Ser133, Asp179, His210 and Trp158. The correct indices are `[131, 177, 208, 156]`.
Since the "errors" are isotropic noise this changes nothing numerically, which is precisely
why nobody noticed. The identical bug is in the molecular-dynamics notebook, from the same
cause.

**How I would teach it.** Do not delete the section. Run it, let them read the triumphant
output, then show them the three lines that generate the "prediction" and ask what the RMSD
actually measured. It is a five-minute inoculation against believing validation statistics
without checking what was compared to what, and that habit is worth more than the section
was going to teach anyway. Then show a real validation: AlphaFold DB has a model for this
protein, and comparing it to `6ANE` yourself takes a few lines and gives an honest number.

### Section 5 — rendering confidence

py3Dmol with the standard AlphaFold colour scheme (blue >90, cyan 70–90, yellow 50–70,
orange <50) painted into the B-factor column. Correct, and a good habit — storing a
per-residue scalar in the B-factor field is how every structural biology tool expects to
receive it.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Why triangular updates | The triangle inequality: d(i,j) ≤ d(i,k) + d(k,j), so pair entries must be mutually consistent across all triplets |
| 2 | What the outer product mean does | Carries per-column covariation from the MSA representation into the pair representation |
| 3 | High pLDDT, high inter-domain PAE | Both domains individually accurate; their relative orientation is uncertain or genuinely flexible |
| 4 | pLDDT < 50 | Read as likely intrinsic disorder, not as a badly folded domain |

All four are correct and none depends on the synthetic data. Question 3 is the one I would put
on an exam.

## Known issues in this version

- **No AlphaFold is run.** The "prediction" is the crystal structure plus Gaussian noise.
- **The Section 4 conclusion (<0.6 Å) contradicts its own printed values** (0.766–0.948 Å).
- **"Sub-1.5 Å Atomic Accuracy!"** describes injected noise.
- **pLDDT and PAE are drawn, not predicted.** Fine for teaching interpretation; the heading
  should say so.
- **`triad_indices_0based` is off by one** — use `[131, 177, 208, 156]`.
- **Report question 1 cannot be answered with this notebook.** It asks students to vary
  ColabFold's `max_msa` and observe the effect on pLDDT. There is no ColabFold here. Either
  point them at the public ColabFold notebook — Mirdita et al. 2022, which does run on a free
  Colab GPU — or rewrite the question.

## Report questions

Question 1 needs the real ColabFold notebook, as noted. If you keep it, the expected finding
is a monotone collapse: PETase is a well-covered family, so at `max_msa = 512:1024` the core
is above 90, and by the time you are down to a handful of sequences the model loses the fold
and pLDDT falls into the 40s and 50s. Students should report the depth at which it breaks,
not just that it breaks.

Question 2, on MSA subsampling to recover alternative conformations, is a genuinely current
topic and a good discussion prompt. The expected line of argument is that a deep MSA encodes
the dominant conformer, and that deliberately shallow, resampled MSAs let the network land in
other basins.

## Further reading I hand out

- Jumper et al., *Nature* 596:583 (2021). `10.1038/s41586-021-03819-2` — AlphaFold2; the IPA and Evoformer sections are implemented from this.
- Mirdita et al., *Nat Methods* 19:679 (2022). `10.1038/s41592-022-01488-1` — ColabFold.
- Varadi et al., *Nucleic Acids Res* 50:D439 (2022). `10.1093/nar/gkab1061` — the AlphaFold database.
- Tunyasuvunakool et al., *Nature* 596:590 (2021). `10.1038/s41586-021-03828-1` — proteome-scale accuracy, and where the pLDDT bands come from.
- Kabsch, *Acta Crystallogr A* 32:922 (1976). `10.1107/S0567739476001873` — the superposition algorithm in Section 4.
