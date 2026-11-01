## At a glance

| | |
|---|---|
| **Runtime** | CPU works, but see the timing note. A GPU runtime makes one cell about fifteen times faster. |
| **Wall clock** | **About 15–18 minutes on a CPU runtime**, almost all of it in one cell. Budget 90 minutes of class time. |
| **Network** | RCSB, for `6ane.pdb` and `1y26.pdb`. |
| **Prerequisites** | The foundations session. Students need to know the 133/179/210/158 numbering. |
| **Produces** | `data/6ane_chainA_clean.pdb`, `data/6ane_minimized.pdb`, `manifests/lab2_0_lockfile.json` |
| **Quiz items** | 3 — the thinnest assessment in the set. Plan to supplement. |

> **Timing, because it will catch you out.** Section 3 calls `simulation.minimizeEnergy()` on
> PETase chain A in OBC2 implicit solvent with no non-bonded cutoff. I timed it at **848
> seconds — just over fourteen minutes — on two CPU threads**, which is what a free Colab CPU
> runtime gives you. Nothing is wrong; implicit-solvent forces with no cutoff are O(N²) and
> there are about 4,200 atoms. Two options: set **Runtime → Change runtime type → T4 GPU**
> before you start, since `get_optimal_openmm_platform()` already prefers CUDA and the cell
> drops to a minute or two; or start the cell, let it run, and lecture through Section 1 while
> it works. I would not discover this live.

## What this notebook is for

The transition from *describing* structures to *computing* on them. Students have been reading
coordinates; now those coordinates acquire an energy, and the energy acquires a gradient.

I teach it as three claims. A force field is a specific functional form with fitted parameters,
not a law of nature. Minimisation finds a nearby local minimum, not the global one and not the
biologically relevant conformation. And the solvent model is not an optional detail — the last
section exists to show that the same structure is stable in implicit water and flies apart in
vacuum.

## Section-by-section

### Section 1 — the potential energy function

Markdown through the five terms, then a cell that plots Lennard-Jones and Coulomb curves.

```
Optimal Hydrogen-Bond Minimum Energy: -0.224 kcal/mol
Steric Repulsion at r = 2.0 Å:        2.07 kcal/mol
```

The LJ curve uses σ = 3.4 Å, so the minimum sits at 2^(1/6)·σ = **3.82 Å**. Put that number on
the board; it comes back in the next cell and again in the docking session. (Minor
inconsistency worth knowing about: the plotting cell uses ε = 0.086 kcal/mol and the minimiser
in Section 2 uses ε = 0.1. It changes the depth of the well, not its position.)

### Section 2 — steepest descent by hand

A 1-D steepest-descent walk out of a steric clash at r = 2.4 Å:

```
step      r      energy     force
   0   2.400   22.905    122.606
   4   2.568    9.447     49.175
  34   2.876    1.885     10.139
```

After 35 steps it has reached 2.88 Å and the minimum is at 3.82 Å. **It has not converged, and
the notebook does not say so.** That is the best teachable moment in the session, so do not
let it pass as a success story. Steepest descent is excellent at escaping a catastrophic
clash — look at the energy falling from 22.9 to 1.9 — and terrible at the last stretch into a
minimum, where the gradient is small and the steps become tiny. That is exactly why production
codes switch to L-BFGS, which is what the next section does. Ask them how many steps SD would
need; have them raise `max_steps` and find out.

### Section 3 — the real thing in OpenMM

Chain A is extracted, PDBFixer adds the missing C-terminal OXT (and is deliberately told *not*
to model missing loops, `fixer.missingResidues = {}` — a good decision, and worth explaining:
inventing unresolved loops would put fabricated coordinates into a structure the whole course
depends on). Then amber14-all with OBC2 implicit solvent, hydrogens added at pH 7.4, HBonds
constrained, and L-BFGS to a 10 kJ/mol/nm tolerance.

```
Initial Potential Energy:  -29,034.24 kJ/mol
Final Potential Energy:    -33,020.68 kJ/mol
Total Relieved:             -3,986.43 kJ/mol
```

Those are the numbers on a clean run. The absolute values mean nothing on their own — an
Amber potential energy has no zero point you can interpret — and students always ask whether
−33,000 is "good". The honest answer is that only the *difference* is interpretable, and only
against the same system with the same force field.

### Section 4 — did minimisation break the structure?

```
Global Backbone CA RMSD:  0.201 Å
Mean CA Displacement:     0.177 Å
Maximum CA Displacement:  0.618 Å

Ser160 (133)  0.1552 Å   PASS
Asp206 (179)  0.2663 Å   PASS
His237 (210)  0.1111 Å   PASS
Trp185 (158)  0.2488 Å   PASS
```

This is the quality-control habit I most want them to pick up: after any structural
manipulation, measure how far the structure moved and check that the functionally important
part moved least. A 0.2 Å global RMSD means the minimiser relieved local strain without
repacking anything, which is what you want before dynamics. If a student reports 2 Å, something
went wrong upstream — usually a protonation or a missing-atom problem.

### Section 5 — the RNA thread

Parses phosphorus atoms from `1Y26` and compares electrostatic repulsion in vacuum with
dielectric screening.

```
Total Phosphorus (P) Atoms Parsed: 70
Mean Adjacent P-P Distance:        6.05 Å
Repulsive Energy in Vacuum (ε=1):  54.93 kcal/mol
Repulsive Energy in Water (ε=78):   0.70 kcal/mol
```

A factor of 78 is a factor of 78, so the arithmetic is unsurprising — but the magnitude is the
point. 55 kcal/mol of unscreened repulsion along a 70-phosphate backbone is more than enough to
tear the fold apart, and it explains why the next session spends its time on counter-ions
rather than treating them as bookkeeping.

## Known issues in this version

- **The objectives promise vacuum minimisation**, and the notebook never does one. Only the
  implicit-solvent run is executed. It is the first report question, so this may be deliberate;
  just do not claim it has been demonstrated.
- **"Amber14-SB"** in the prose; the code loads `amber14-all.xml`, which contains ff14SB for
  protein plus parameters for nucleic acids, lipids and water. Not wrong, slightly loose.
- **Three quiz questions** for a 90-minute session. If you want more formative checks, the
  obvious additions are the position of the LJ minimum, why constraints on hydrogen bonds let
  you take a larger timestep, and what a 0.2 Å RMSD after minimisation tells you.
- **The pip line has a shell-quoting bug.** `!pip install -q openmm>=8.2.0 pdbfixer ...` is run
  through a shell, which reads `>=8.2.0` as an output redirection. The practical effects are
  that the version floor is not enforced (you get whatever OpenMM is current) and that a junk
  file literally named `=8.2.0` appears in the working directory. Quote it —
  `"openmm>=8.2.0"` — if you are editing the notebook anyway. The same bug is in the solvation
  and dynamics notebooks.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Why LJ explodes below ~2 Å | The (σ/r)¹² term models Pauli repulsion; r¹² in the denominator sends the energy to +∞ |
| 2 | Why Class I force fields cannot break bonds | Bonds are harmonic springs, so they stiffen without limit instead of dissociating |
| 3 | Unneutralised RNA in vacuum | Phosphate–phosphate repulsion overwhelms base pairing and stacking; the fold blows apart |

All three are correct as written.

## Report questions

The vacuum-versus-implicit comparison is the better of the two and directly repairs the gap in
the objectives. Expected finding: in vacuum, surface Asp and Lys side chains collapse inward to
form salt bridges that do not exist in solution, global CA RMSD rises several-fold, and the
final energy is not comparable between the two models because the Hamiltonians differ.

The trimer question is good but expensive — minimising all three chains is three times the
atom count and more than three times the O(N²) implicit-solvent cost. On a CPU runtime that is
well over an hour. Assign it only to students who will use a GPU runtime, and say so.

## Further reading I hand out

- Eastman et al., *PLoS Comput Biol* 13:e1005659 (2017). `10.1371/journal.pcbi.1005659` — OpenMM 7.
- Maier et al., *J Chem Theory Comput* 11:3696 (2015). `10.1021/acs.jctc.5b00255` — ff14SB.
- Onufriev, Bashford & Case, *Proteins* 55:383 (2004). `10.1002/prot.20033` — the OBC generalised Born model.
- Fecker et al., *Biophys J* 114:1302 (2018). `10.1016/j.bpj.2018.02.005` — the 6ANE structure itself.
