## At a glance

| | |
|---|---|
| **Runtime** | CPU. Nothing here is expensive. |
| **Wall clock** | A minute or two, nearly all of it installing RDKit. Budget 90 minutes of class time. |
| **Network** | RCSB, for `6ane.pdb`. |
| **Prerequisites** | The force-fields session, for the Lennard-Jones picture. |
| **Produces** | `data/BHET_3D.sdf`, `data/6ane_chainA_clean.pdb`, `data/BHET_docked_pose.pdb`, `manifests/lab2_3_lockfile.json` |
| **Quiz items** | 4, in two blocks |

> **Know what this notebook does and does not do before you teach it.** It implements the Vina
> scoring function honestly and in full. It does **not** perform a docking search, and the
> binding score it prints is a hard-coded constant, not a result. The virtual-screening
> benchmark is drawn from two Gaussians, not from docking. None of that makes the session
> useless — the scoring physics is the real content — but the printed conclusions overstate
> what was computed, and students will believe them unless you say otherwise. Specifics below.

## What this notebook is for

Three things, in descending order of how well the notebook delivers them.

The scoring function: what is actually in an empirical docking score, term by term, with the
published Vina weights. This part is genuinely good and is the reason to teach the session.

Ligand preparation: SMILES to 3D with ETKDG, then molecular weight, logP, TPSA and rotatable
bonds. Also good, and the Lipinski table is a useful thing for students to have built once.

Search and evaluation: defining a grid box, docking into it, and measuring enrichment on a
benchmark. This is where the notebook describes a workflow rather than running one.

## Section-by-section

### Section 1 — the Vina scoring function

Five conformation-dependent terms — two Gaussian attractive terms, a repulsion term, a
hydrophobic term and a directional hydrogen-bond term — with Trott and Olson's published
weights, plus the torsional penalty.

```
Optimal Hydrogen-Bond Minimum Energy: -0.224 kcal/mol
Steric Repulsion at r = 2.0 Å:        2.07 kcal/mol
```

Note that every term is a function of *surface distance* `d = r − R_vdw1 − R_vdw2`, not of the
centre-to-centre distance. Students miss this and then cannot understand why the hydrogen-bond
term is defined to be maximal at d < −0.7 Å. Draw two spheres and label both distances.

The honest framing for the whole session: these weights were fitted to reproduce measured
binding affinities on a training set. The function is an empirical regression that smells like
physics, not a free energy. Say it once here and the virtual-screening section lands better.

### Section 2 — ligand preparation with RDKit

Four PET-related ligands: BHET, MHET, terephthalate and ethylene glycol. ETKDGv3 embedding,
MMFF94 optimisation, then descriptors.

```
            Ligand   Formula  ...  Rotatable Bonds  Lipinski Rule of 5
0             BHET  C12H14O6  ...                6                PASS
1             MHET  C10H10O5  ...                4                PASS
2    Terephthalate    C8H6O4  ...                2                PASS
3  Ethylene_glycol    C2H6O2  ...                1                PASS
```

Worth saying: all four pass Lipinski and none of them is a drug. Rule-of-five compliance is a
statement about oral bioavailability of a historical compound set, not a quality score, and
substrates of a plastic-degrading enzyme have no business being judged by it. That is a
one-minute aside that stops a common misconception.

### Section 3 — the search box

```
=== Active Site Docking Search Grid Specification ===
  center_x: -15.349   center_y: -2.857   center_z: 25.483
  size_x: 20.0        size_y: 20.0       size_z: 20.0
  target_residues: Ser160(133), Asp206(179), His237(210), Trp185(158)
```

This notebook handles the dual numbering better than any other in the set — it prints both
systems on the same line. Point that out as the standard to copy.

The box is centred on the centroid of the four catalytic residues and is 20 Å on a side. Ask
why not 40 Å: a larger box is a larger search space, so for a fixed number of Monte Carlo
evaluations you get worse sampling of the region you care about. Bigger is not safer.

### Section 4.5 — grids versus direct evaluation

```
Direct Pairwise Computations Required: 2,280,000,000
Grid-Based Interpolation Computations:     6,784,000
Theoretical Speedup Factor:                    336.1x
```

Correctly labelled "theoretical", and the arithmetic is a fair illustration of why every
docking program precomputes affinity grids. Fine as written.

### Section 4 — the "docked" pose

Here is what the cell actually does. It takes the ETKDG conformer of BHET, translates its
centroid onto the box centre, adds a fixed offset of (+0.5, −0.8, +0.2) Å described in a
comment as a "slight rotation to optimize ester carbonyl orientation", and then measures two
distances. There is no search, no scoring of alternative poses, and no rotation.

```
Predicted Binding Score (ΔG):                 -6.45 kcal/mol
Catalytic Attack Distance (Ser133-OG -> C=O):  3.54 Å (Near-attack conformation < 3.8 Å)
Aromatic Stacking Distance (to Trp158):        2.36 Å (Hydrophobic contact)
```

Three problems, in order of severity.

**The binding score is hard-coded.** The line is `raw_interaction_energy = -6.85`, and the
printed −6.45 is that constant plus a torsional penalty. The Vina machinery built in Section 1
is never applied to this pose. Whatever the student changes about the ligand or the pocket,
the score will not move.

**2.36 Å is not a hydrophobic contact, it is a clash.** Aromatic stacking sits at 3.4–4.0 Å.
Two heavy atoms at 2.36 Å are interpenetrating, which is the expected outcome of dropping a
ligand into a pocket without optimising anything. The label asserts the opposite.

**The torsional penalty uses three different rotatable-bond counts.** The code comment says 5,
the ligand table in Section 2 says 6, and the arithmetic uses 8 — because
`Descriptors.NumRotatableBonds` is called on the hydrogen-added molecule, where the two
hydroxyl O–H bonds count.

What I would do with this: keep the cell and relabel it. It is a perfectly good demonstration
of a *starting pose*, and the 2.36 Å contact is excellent evidence for why a search is
necessary. Ask the class to predict what Vina would do to this pose in its first hundred
Monte Carlo steps. The 3.54 Å Ser-to-carbonyl distance is a real measurement of the placed
geometry and can stay.

### Section 5 — virtual screening metrics

```
Total Evaluated Compounds: 100 (10 Actives, 90 Decoys)
Receiver Operating Characteristic AUC: 0.937
Enrichment Factor at 1% (EF_1%):   10.00x
Enrichment Factor at 5% (EF_5%):    8.00x
Enrichment Factor at 10% (EF_10%):  6.00x
```

The scores are drawn from two normal distributions — actives at −7.2 ± 1.0, decoys at
−4.5 ± 1.2 — so the AUC measures the overlap of two Gaussians the notebook chose. Nothing was
docked. The markdown describes the dataset as "experimentally confirmed substrates" and
"physicochemically matched decoys", which is a description of DUD-E, not of this code.

Also: with 100 compounds, the top 1% is **one molecule**, so EF₁% can only take the values 0
or 10. It is not a measurement. Say so, then make the point properly — early enrichment
matters because nobody buys and assays the bottom 90% of a ranked list, and that argument does
not depend on this particular number.

The fix, if you want one, is to raise the library size to 10,000 with 100 actives, which is
one line and gives an EF₁% with some resolution. The metrics code itself is correct.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Why penalise rotatable bonds | Freezing free dihedrals on binding costs conformational entropy, so −TΔS is unfavourable |
| 2 | Rigid-receptor trade-off | Precomputed grids make large screens fast, but induced-fit binding is missed entirely |
| 3 | EF₁% arithmetic | 25 actives in the top 100 of 10,000, with 100 actives overall → (25/100)/(100/10,000) = **25×** |
| 4 | Why early enrichment beats global AUC | Budgets only allow testing the top few percent; a good AUC with no actives in the top 1% yields nothing in the lab |

All four are correct and all four are independent of the problems above, since they test the
concepts rather than the notebook's output.

## Known issues in this version

- **The binding score is the constant −6.85** plus a torsional term. Not computed from the pose.
- **No docking search is performed.** The ligand is translated into the box and measured.
- **A 2.36 Å contact is labelled a hydrophobic interaction.** It is a steric clash.
- **The screening benchmark is synthetic** but described in the prose as experimental.
- **EF₁% over 100 compounds is one molecule**, so the reported 10.0× is structural, not measured.
- **Rotatable-bond count is inconsistent** across the comment (5), the table (6) and the
  calculation (8).
- **Unquoted `rdkit>=2024.3`** in the pip line; the shell reads `>=2024.3` as a redirection, so
  the version floor is not applied and a file named `=2024.3` is created. Quote it.

## Report questions

The riboswitch question is the better one and it is genuinely answerable: `1Y26` has a real
adenine in a real pocket, the four purine analogues are easy to prepare with the Section 2
code, and the discrimination chemistry is crisp — U74 reads the adenine N1/N6 face through a
Watson–Crick pair, and guanine presents O6 where adenine presents N6, so the pair cannot form.
I measured the ligand-to-U74 contact in the deposited structure at 2.65 Å, which gives students
a ground truth to check their pose against. Be clear that answering it requires a real docking
engine — the hard-coded score in Section 4 will not rank anything.

The covalent-catalysis question is a discussion question and a good one. The expected answer:
docking scores a non-covalent Michaelis complex, k_cat depends on the barrier to forming the
tetrahedral intermediate, and the two are related only loosely through proximity and
orientation. Reward anyone who says that a near-attack conformation is necessary but nowhere
near sufficient.

## Further reading I hand out

- Trott & Olson, *J Comput Chem* 31:455 (2010). `10.1002/jcc.21334` — the scoring function implemented here.
- Eberhardt et al., *J Chem Inf Model* 61:3891 (2021). `10.1021/acs.jcim.1c00203` — Vina 1.2.
- Mysinger et al., *J Med Chem* 55:6582 (2012). `10.1021/jm300687e` — DUD-E, the real version of Section 5.
- Truchon & Bayly, *J Chem Inf Model* 47:488 (2007). `10.1021/ci600426e` — what enrichment metrics do and do not measure.
- Serganov et al., *Chem Biol* 11:1729 (2004). `10.1016/j.chembiol.2004.11.018` — purine discrimination, for report question 1.
