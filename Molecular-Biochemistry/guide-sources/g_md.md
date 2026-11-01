## At a glance

| | |
|---|---|
| **Runtime** | CPU is adequate. A GPU runtime helps if you lengthen the simulation, which you may want to. |
| **Wall clock** | Three to four minutes; the equilibration cell alone is ~110 seconds on two CPU threads. Budget 90 minutes of class time. |
| **Network** | RCSB, for `6ane.pdb`. |
| **Prerequisites** | The solvation session. This notebook rebuilds the solvated system if it cannot find one, so it also stands alone. |
| **Produces** | `data/6ane_solvated_minimized.pdb`, `data/petase_micro_traj.dcd`, `manifests/lab2_2_lockfile.json` |
| **Quiz items** | 4, in two blocks |

> **Say this at the start and again at the end: the trajectory is 2 picoseconds long.**
> Everything the notebook computes from it — RMSD convergence, RMSF, radius of gyration — is
> computed from ten frames spanning two trillionths of a second. The analysis code is correct
> and the numbers are real, but they are not evidence about protein dynamics, and the notebook
> labels some of them as though they were. Details below.

## What this notebook is for

Integration, ensembles, and trajectory analysis. By the end students should be able to say why
the timestep is 2 fs and not 10, what a thermostat actually does to the equations of motion,
and how to read RMSD, RMSF and Rg plots — including what each one cannot tell you.

## Section-by-section

### Section 1 — integrators, compared honestly

A one-dimensional harmonic oscillator integrated with explicit Euler and with velocity Verlet:

```
Velocity-Verlet Energy Drift: 2.7707e-03 kcal/mol
Euler Energy Drift:           61.24 kcal/mol
```

Four orders of magnitude, in fifteen lines of Python. This is the cleanest demonstration in
the whole course and I spend real time on it. The point is not that Euler is inaccurate — it
is that Euler is *systematically* wrong in one direction, pumping energy in forever, while
Verlet's error oscillates and stays bounded. Symplectic is not a synonym for accurate.

Then the 2 fs argument: a C–H stretch has a period near 10 fs, you need several steps per
oscillation, and constraining those bonds with SHAKE or LINCS removes the fastest motion so
you can double the step. Make them do the arithmetic rather than memorising "2 fs".

### Section 2 — ensembles

Markdown only, no code. NVE, NVT with Langevin, NPT with a Monte Carlo barostat. Short, and
the quiz immediately before it covers the integration material, so this is a good place to
stop for questions.

### Section 3 — the equilibration pipeline

If `data/6ane_solvated_minimized.pdb` is missing — which it will be, because each notebook runs
in its own Colab session — the cell rebuilds the solvated system from scratch. That rebuild is
most of the 110 seconds. Then:

```
Starting Phase 1: NVT Thermalization (500 steps = 1.0 ps micro-run)...
  NVT Completed: Temperature = 196.78 K

Starting Phase 2: NPT Density Relaxation & Trajectory Recording (1000 steps = 2.0 ps)...
  Final Periodic Box Volume: 282.972 nm³
```

**Stop at 196.78 K.** The thermostat target is 300 K and after 1 ps of Langevin coupling at
1 ps⁻¹ the system has reached two thirds of it. That is exactly what the physics predicts — a
friction coefficient of 1 ps⁻¹ means the characteristic relaxation time is about 1 ps, so one
time constant gets you roughly 63% of the way — and the notebook prints it under the heading
"NVT Completed" with no comment.

I turn this into the question of the session: *is this system equilibrated?* The answer is
plainly no, and every number downstream inherits that. A real protocol would run 100 ps of NVT
with position restraints, then 1 ns of NPT, before recording anything. If you have a GPU
runtime and twenty spare minutes, raising `simulation_nvt.step(500)` to `step(50000)` and
`simulation_npt.step(1000)` to `step(250000)` gives a 500 ps trajectory and genuinely different
plots. I recommend doing it once as a demo so they see what converged output looks like.

### Section 4 — trajectory analysis

```
MDAnalysis Loaded: 10 recorded frames, 262 CA atoms.
  Final Backbone CA RMSD:     0.644 Å (Stable plateau)
  Mean Radius of Gyration Rg: 16.497 Å (Compact native fold)
  Mean Backbone RMSF:         0.428 Å
```

"Stable plateau" describes an RMSD curve with ten points over 2 ps. It has not plateaued; it
has not had time to go anywhere. Flag the phrase when you reach it. The Rg figure is fine —
16.5 Å is a sensible radius of gyration for a 262-residue α/β hydrolase, and it is the one
number here that a 2 ps window can legitimately report, because Rg is an instantaneous
property rather than a converged average.

### The catalytic-site table, which has an indexing bug

```
                   Residue  PDB Index  CA RMSF (Å)            Stability
0     Ser160 (Nucleophile)        133       0.4496  Rigid Core (<0.8 Å)
1            Asp206 (Acid)        179       0.5115  Rigid Core (<0.8 Å)
2            His237 (Base)        210       0.3891  Rigid Core (<0.8 Å)
3  Trp185 (Aromatic Clamp)        158       0.4703  Rigid Core (<0.8 Å)
```

The code is `val = float(rmsf_vals[r_idx - 1])`. That subtracts one to convert a residue number
into a zero-based array index, which would be right if the trajectory were numbered from 1.
It is not. Chain A of `6ANE` is numbered **2 to 263**, and when OpenMM writes the solvated
system out it renumbers everything from 1 — so the residue at array position `r_idx - 1` is one
past the one you wanted. I checked each row against the trajectory file:

| Table says | Array index used | Residue actually read |
|---|---|---|
| Ser133 | 132 | **Met** |
| Asp179 | 178 | **Ser** |
| His210 | 209 | **Ser** |
| Trp158 | 157 | **Asp** |

The correct index is `r_idx - 2`. With that change the four residues are the serine, aspartate,
histidine and tryptophan you wanted.

Here is the part worth telling the students: **the conclusion survives the fix.** With correct
indexing the triad sits at 0.24–0.25 Å, around the tenth percentile of the per-residue RMSF
distribution, so "exceptionally low" is true — the notebook simply arrived at it by reading
four neighbouring residues that happened to be rigid too. Trp158, correctly indexed, comes out
mid-pack rather than rigid, which is the more interesting result given it is the mobile clamp
with two conformers in the crystal. Make them fix the index and re-run; it takes one character
and it changes a sentence of the interpretation.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Why Δt ≈ 2 fs | C–H stretches have ~10 fs periods; stability needs several steps per period, and constraining X–H bonds buys the factor of two |
| 2 | What "symplectic" means | Preserves phase-space volume and time-reversibility, so energy error stays bounded rather than drifting |
| 3 | RMSD vs RMSF | RMSD is global and time-resolved against a reference; RMSF is per-residue and averaged over time |
| 4 | Why restrain heavy atoms during heating | Newly placed waters carry clashes and voids; restraints stop that energy from deforming the crystal fold during thermalisation |

All four are correct. Note that question 4 describes position restraints during NVT heating —
good practice, and something this notebook's pipeline does not actually do. If a student asks
whether the code matches the quiz, the honest answer is no, and that is a fair criticism of the
protocol rather than of the question.

## Known issues in this version

- **`rmsf_vals[r_idx - 1]` is off by one residue**, as above. One-character fix: `r_idx - 2`.
- **196.78 K is reported as a completed thermalisation** to 300 K.
- **"Stable plateau"** for a 2 ps, 10-frame RMSD trace.
- **"Exceptionally low RMSF"** happens to be true, but not for the residues printed, and not
  defensible from 10 frames regardless.
- **Unquoted `openmm>=8.2.0`** in the pip line — the shell treats it as a redirection, so the
  floor is not enforced and a file named `=8.2.0` appears. Quote it.
- The prose refers to the triad throughout as Ser160/Asp206/His237 (UniProt numbering) while
  the code selects 133/179/210 (coordinate numbering). Both are correct; make sure students
  know they are the same atoms.

## Report questions

Both are substantial and both require a longer trajectory to mean anything — say so when you
assign them. The hydrogen-bond occupancy question over 10 frames can only return a multiple of
10%, which is not an occupancy measurement. Either extend the simulation as part of the
assignment or grade the method rather than the number.

The cross-correlation matrix question has the same problem in a worse form: a DCCM estimated
from 10 frames of a 262-residue protein is almost entirely noise, since you are estimating a
262×262 covariance from ten samples. That is itself a result worth writing up, and I would
accept a report that demonstrates it.

## Further reading I hand out

- Eastman et al., *PLoS Comput Biol* 13:e1005659 (2017). `10.1371/journal.pcbi.1005659` — OpenMM 7.
- Michaud-Agrawal et al., *J Comput Chem* 32:2319 (2011). `10.1002/jcc.21787` — MDAnalysis.
- Ryckaert, Ciccotti & Berendsen, *J Comput Phys* 23:327 (1977). `10.1016/0021-9991(77)90098-5` — SHAKE.
- Maier et al., *J Chem Theory Comput* 11:3696 (2015). `10.1021/acs.jctc.5b00255` — ff14SB.
