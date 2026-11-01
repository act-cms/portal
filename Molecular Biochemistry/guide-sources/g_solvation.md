## At a glance

| | |
|---|---|
| **Runtime** | CPU is fine here — about a minute. A GPU runtime is not needed. |
| **Wall clock** | Two to three minutes; the solvation and minimisation cell is ~50 seconds of it. Budget 75 minutes of class time. |
| **Network** | RCSB, for `6ane.pdb`. |
| **Prerequisites** | The force-fields session. Students should already have seen a minimisation. |
| **Produces** | `data/6ane_chainA_clean.pdb`, `data/6ane_solvated_minimized.pdb`, `manifests/lab2_1_lockfile.json` |
| **Quiz items** | 4, in two blocks |

## What this notebook is for

Everything that has to be true before you are allowed to press "run" on a molecular dynamics
simulation. Which water model, how much of it, in what shaped box, with which ions, and why
the total charge must be exactly zero.

It is the least glamorous session in the sequence and the one where careless work does the
most damage, because every error here is silent. A box that is too small does not crash; it
produces a protein quietly interacting with its own image. An unneutralised cell under PME
does not crash either; it applies a uniform background charge and gives you plausible, wrong
numbers.

Note that unlike the force-fields session, this one is fast — explicit solvent with PME and a
1 nm cutoff is O(N log N), so 27,775 atoms minimise in under a minute while 4,200 atoms in
cutoff-free implicit solvent took a quarter of an hour. That comparison is worth making out
loud; students assume bigger always means slower.

## Section-by-section

### Section 1 — water models

A comparison table for TIP3P, TIP4P-Ew and OPC: site count, geometry, charges, dipole moment.
No computation. The quiz that follows asks why a 4-site model puts the negative charge on a
massless dummy site, and the answer is about reproducing the quadrupole moment, not the
dipole — most students will guess dipole, so let them, then correct it.

Be clear about why the course uses TIP3P anyway: it is what Amber ff14SB was parameterised
against, and mixing a protein force field with a water model it was not fitted to is a real
error, not a stylistic choice.

### Section 2 — ion arithmetic

This is where the notebook's one substantive error lives, and it is a good one to teach with.

```
=== PETase (Protein Thread) Ion Accounting ===
  solute_net_charge: -2
  n_added_salt_pairs: 27
  total_Na_plus: 29
  total_Cl_minus: 27
```

The `-2` is hard-coded. **Chain A of 6ANE does not carry −2 e; it carries about +6.3 e at
pH 7.4.** That is not my opinion — it is what the foundations notebook computes from the same
sequence with Henderson–Hasselbalch (`+6.288 e`), and you can confirm it by counting formal
charges: 13 Arg and 7 Lys against 9 Asp and 4 Glu, so +7 before the histidines and termini are
accounted for.

The consequence is visible two sections later without changing a line of code. Section 4 calls
`modeller.addSolvent(..., neutralize=True)`, which computes the real charge itself and does the
right thing:

```
Table 2.2: Solvated System Inventory Breakdown
  Protein         262 residues    3,930 atoms
  Water (HOH)   7,981 molecules  23,943 atoms
  Sodium (NA)      22
  Chloride (CL)    29
```

So the hand calculation in Section 2 predicts **29 Na⁺ and 27 Cl⁻**, and the system OpenMM
actually builds has **22 Na⁺ and 29 Cl⁻**. Seven more chloride than sodium — which is the
charge of the protein, recovered independently by the software.

I would not patch this before teaching it. Put both tables on the screen, ask the class which
is right and how they could tell, and let them arrive at the sign error themselves. It is the
single best illustration in the course of why you check a number against a second source. If
you would rather fix it, change `net_charge=-2` to `net_charge=7` in the `calculate_exact_ion_counts`
call and the two tables agree.

The RNA half of the same cell is correct: `1Y26` has 71 nucleotides and therefore 70
phosphodiester charges, and the cell uses −70, giving 104 Na⁺ against 34 Cl⁻. Manning
condensation is introduced here — the idea that a fraction of the counter-ions are
territorially bound rather than freely diffusing — and it is worth the five minutes.

### Section 3 — box geometry

```
PETase Cartesian Spans: ΔX = 37.94 Å | ΔY = 44.82 Å | ΔZ = 46.62 Å
Maximum Solute Extent:  46.62 Å
Minimum Periodic Buffer: 2 x 10.0 Å = 20.0 Å
Required Cubic Box Side: 66.62 Å (6.66 nm)
Estimated Unit Cell Volume: 295,621 Å³
```

The rule being taught is that the buffer must exceed the non-bonded cutoff — 1.0 nm here — so
that no atom ever sees its own periodic image within the cutoff sphere. Make them state the
minimum image convention in their own words before you give them the number.

### Section 4 — build and relax

TIP3P, 1 nm padding, 150 mM NaCl, PME with a 1 nm cutoff, HBonds constrained, then L-BFGS
for 300 iterations:

```
Total Atoms in Periodic Unit Cell: 27,775
Total Residues: 8,294

Initial Potential Energy (clashing waters): -203,953.45 kJ/mol
Final Potential Energy (after relaxation):  -421,917.31 kJ/mol
Total Relieved:                             -217,963.87 kJ/mol
```

That energy drop is enormous compared with the ~4,000 kJ/mol the implicit-solvent run
relieved, and the reason is worth stating: almost all of it is water finding its own hydrogen-
bond network, not the protein relaxing. Ask what fraction of the 27,775 atoms belong to the
protein (3,930, about 14%) and the point makes itself.

### Section 5 — visual check

py3Dmol render of the solvated active site. Mostly a sanity check that the box is full and the
protein is not sitting against a wall.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Why a 4-site model uses a dummy M-site | Shifting the negative charge along the bisector reproduces the gas-to-liquid quadrupole moment, and so bulk density and dielectric constant |
| 2 | When GB implicit solvent is inappropriate | Whenever specific waters matter — bridging waters in an active site, dewetting in a buried cavity |
| 3 | 0.4 nm buffer | Violates the minimum image convention; the protein interacts with its own periodic image |
| 4 | Why the cell must be neutral under PME | The reciprocal-space sum diverges for a charged cell; the uniform neutralising background that suppresses it introduces artifactual forces |

All four are correct as written.

## Known issues in this version

- **`net_charge=-2` for PETase chain A is wrong** (it is ≈ +6.3 e). Discussed at length above.
  Nothing downstream is corrupted, because `addSolvent(neutralize=True)` does its own
  arithmetic — but the two printed tables contradict each other, and an attentive student will
  notice.
- **The ion cell assumes 9,850 waters** before the box is built; the real count is 7,981. The
  salt concentration that results is therefore a little higher than the nominal 150 mM. Minor,
  but if a student recomputes it they will find ~0.19 M, not 0.15 M.
- **Unquoted `openmm>=8.2.0` in the pip line.** The shell reads `>=8.2.0` as a redirection, so
  the version floor is not enforced and a file named `=8.2.0` is created. Quote it if you edit
  the notebook.
- **The riboswitch is discussed but never solvated.** Section 2 does the RNA ion arithmetic and
  the second report question asks students to build the system; the notebook itself only
  solvates the protein. Fine as an assignment, but do not describe the RNA system as having
  been built.

## Report questions

The rhombic dodecahedron question is a clean geometry exercise — the cell volume ratio is
1/√2 ≈ 0.707, so about 29% fewer waters and, to first order, about a 40% increase in ns/day
since cost scales with atom count. Accept any defensible estimate with the reasoning shown.

The Mg²⁺ question is the better one scientifically: 35 divalent ions replace 70 monovalent
ones for the same neutralisation, and the interesting part is where they sit. Students should
find Mg²⁺ coordinating non-bridging phosphate oxygens, often through a retained water shell
rather than directly. Point out that `1Y26` already contains five crystallographic Mg²⁺ ions,
so they have an experimental answer to check against — that is the whole exercise.

## Further reading I hand out

- Jorgensen et al., *J Chem Phys* 79:926 (1983). `10.1063/1.445869` — TIP3P.
- Essmann et al., *J Chem Phys* 103:8577 (1995). `10.1063/1.470117` — smooth particle mesh Ewald.
- Manning, *J Chem Phys* 51:924 (1969). `10.1063/1.1672157` — counter-ion condensation.
- Eastman et al., *PLoS Comput Biol* 13:e1005659 (2017). `10.1371/journal.pcbi.1005659` — OpenMM 7.
