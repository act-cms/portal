## At a glance

| | |
|---|---|
| **Runtime** | CPU. Do not request a GPU; it buys nothing here and the queue wait is wasted class time. |
| **Wall clock** | Two to four minutes, most of it the package install. Budget 75–90 minutes of class time. |
| **Network** | Needs RCSB. Pulls `6ane.pdb`, `6ane.cif` and `1y26.pdb` from `files.rcsb.org`. |
| **Prerequisites** | None beyond basic Python syntax. This is the entry point to the sequence. |
| **Produces** | `data/6ane.pdb`, `data/6ane.cif`, `data/1y26.pdb`, `manifests/lab1_0_lockfile.json` |
| **Quiz items** | 7, in three blocks |

## What this notebook is for

This is the on-ramp. Everything downstream — minimization, solvation, dynamics, docking,
structure prediction — reads the same PETase crystal structure, so the point of this session
is to make students fluent in the file before they ever hand it to a simulation engine.

Three skills carry forward, and they are the ones I actually assess:

1. Reading a PDB file as a *stream of fixed-column records*, not as a magic object.
2. Holding two residue numbering systems in their head at once without mixing them up.
3. Computing a physical property (net charge) from first principles rather than calling a
   library function and trusting the number.

The enzyme is PETase from *Ideonella sakaiensis*, PDB `6ANE` — a real, 2.02 Å structure of a
real enzyme that depolymerises PET plastic. The RNA thread at the end uses the *add* adenine
riboswitch, PDB `1Y26`. Both recur in later sessions, so it is worth naming them properly now.

## Before class

Open the notebook, set **Runtime → Change runtime type → CPU**, then **Runtime → Run all**
and watch it finish. I do this the morning of, because the only thing that reliably breaks is
the RCSB download, and if that is down I want to know before thirty students find out.

If RCSB is unreachable, the cells print a notice and continue, but every later cell fails.
The fix is to upload the three files by hand into `data/` and re-run from Section 1.

One housekeeping note for the students: Colab runs on a disposable virtual machine. If the
session disconnects, `data/` is gone and they must start from the top. Say this out loud
before they start, not after someone loses an hour.

## Section-by-section

### Section 0 — environment

A single `pip install` cell pinning Biopython 1.83, jupyterquiz 2.8.1, py3Dmol 2.1.0 and
gemmi 0.6.5, plus a `COURSE_SEED = 42`. Takes about 40 seconds. Nothing to teach here, but
do point out that the pins are deliberate: an unpinned notebook is an unreproducible notebook.

### Section 1 — the shell, and why columns matter

Downloads `6ANE` and then interrogates it with `wc`, `grep` and `awk`. The numbers students
should see:

```
6869   lines in the file
5808   ATOM records
 475   HETATM records
 789   ATOM records matching " CA "
 474   HOH waters
```

Then a gemmi pass over the mmCIF version pulls the refinement metadata: resolution 2.02 Å,
R-work 0.177, R-free 0.217, space group C 2 2 2₁.

Two things are worth stopping on. First, `grep " CA "` works only because the PDB format is
column-fixed, and it would break on a calcium ion (`CA` as an element). Ask them why the
spaces are inside the quotes. Second — and this is the good one — **789 does not equal the
787 residues the next section reports**. The two extra alpha-carbons are the alternate
conformers in chains B and C. I let them find that discrepancy themselves in Section 2 rather
than pre-empting it here.

The `awk` cell slices columns by field number. On `6ANE` it behaves, but tell them that
field-splitting on whitespace is fragile for PDB files in general: when a coordinate column
runs together with its neighbour, `$5` silently becomes the wrong thing. That is the argument
for the column-slicing parser they write in Section 2.

### Section 2 — a parser, written by hand

An `Atom` class slicing by character position, then a nested dictionary of
chain → residue → atoms. Expected output:

```
Parsed 6283 total atoms from 6ANE.
Chain A: 262 amino acid residues resolved.
Chain B: 264 amino acid residues resolved.
Chain C: 261 amino acid residues resolved.
Total residues exhibiting conformational heterogeneity (altLocs): 2
  Chain B, Residue #158 has alternate conformers: ['A', 'B']
  Chain C, Residue #158 has alternate conformers: ['A', 'B']
```

Residue 158 is the tryptophan. It is the only residue in the whole structure modelled in two
conformations, and it is the catalytically interesting one — the aromatic clamp that stacks
against the terephthalate ring of the substrate. The crystallographers saw it in two positions
because it genuinely moves. That is not a coincidence to skip past; it is the single best
example in this course of experimental data carrying dynamic information.

### Section 3 — net charge and the titration curve

Henderson–Hasselbalch over a standard pKa table, applied residue by residue to chain A.

```
PETase Chain A sequence length: 262 amino acids
Calculated Net Charge at physiological pH 7.40: +6.288 e
Calculated Isoelectric Point (pI): 9.72
```

A positive number surprises people — "it's a hydrolase, shouldn't it be acidic?" — so have the
answer ready: chain A carries 13 Arg and 7 Lys against 9 Asp and 4 Glu. Count them on the
board if you have time; it takes a minute and it makes the number concrete.

Histidine is the teaching point. At pH 7.4 with pKa 6.0 it is about 4% protonated, so it
contributes almost nothing to the net charge, yet it is the catalytic base. Charge and
chemistry are not the same question.

> **Carry this number forward.** `+6.29 e` is computed here from the sequence. The solvation
> notebook later in the sequence hard-codes `net_charge=-2` for the same chain and adds
> counter-ions on that basis. They cannot both be right, and this one is right. I flag it in
> that guide too; if you teach the two sessions back to back, make it an exercise rather than
> an erratum.

### Section 4 — rendering, and the numbering contract

py3Dmol renders chain A with the catalytic machinery highlighted, followed by a table mapping
the two numbering systems. This is the part students get wrong for the rest of the semester
if it is not nailed down here.

| Role | UniProt A0A0K8P6T7 | 6ANE coordinates |
|---|---|---|
| Nucleophile (Ser) | 160 | **133** |
| Electrostatic anchor (Asp) | 206 | **179** |
| General base (His) | 237 | **210** |
| Aromatic clamp (Trp) | 185 | **158** |

The offset is 27, the length of the cleaved signal peptide. I have verified every row of this
against the deposited coordinates: in `6ANE`, residue A133 is SER, A179 is ASP, A210 is HIS and
A158 is TRP. Residue A160, by contrast, is a different serine entirely, and A206 and A237 are
both asparagine. If a student selects residue 160 expecting the nucleophile, they get a
plausible-looking serine in the wrong place and no error message. Watch for it.

The notebook calls the 160/206/237 column "mature sequence numbering". That label is
backwards — 160 is the *precursor* (UniProt) number, and the deposited 133 is the mature
number, counting from the first residue after the signal peptide. The arithmetic in the cell
is correct; only the word is wrong. The databases session states it the right way round
("UniProt #160, deposited PDB #133"), so if you teach them in order, correct it here verbally
and the next session will reinforce the fix.

Chain A is numbered 2–263 in the coordinate file, not 1–262. Mention it. It is the root cause
of an off-by-two indexing error in the dynamics notebook later on.

### Section 5 — the RNA thread

Downloads `1Y26` and tabulates the adenine binding pocket. The ligand is `ADE 90` in chain X,
and the three bases listed in the table are genuine close contacts — I measured them:
U74 at 2.65 Å, U51 at 2.77 Å, U22 at 2.78 Å, closest heavy atom to ligand in each case.
U74 is the Watson–Crick discriminator that reads adenine over guanine, which is the detail the
docking session's report question comes back to.

### Section 6 — report questions

Two: a histidine-pKa sweep, and an altLoc hunt across chains B and C. Both are well posed and
both are answerable with code already in the notebook.

For the altLoc question, the answer is that the only alternate conformers in `6ANE` are at
residue 158 in chains B and C — so the honest finding is "almost none, and the one that exists
is functional, not surface noise". A student who reports that has done the work. A student who
reports a long list has a bug in their altLoc test, most likely treating the blank altLoc
field as a conformer label.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | ATOM vs HETATM | ATOM = standard polymer residues; HETATM = ligands, ions, waters |
| 2 | `grep " CA " \| wc -l` | Count of residues with a resolved alpha-carbon, across all chains |
| 3 | Occupancy 0.60, altLoc A | That atom sits in conformation A in ~60% of unit cells |
| 4 | His at pH 7.4 | pH is 1.4 units above its pKa, so it is ~96% neutral imidazole |
| 5 | Definition of pI | The pH at which summed positive and negative charges cancel |
| 6 | Trp185 "wobbling" clamp | π-stacks with terephthalate; modelled in alternate conformers |
| 7 | RNA polyanion | Each phosphodiester has an ionisable OH with pKa < 2, so −1 e per nucleotide |

Item 2 is the one I would quibble with as written. The literal output is 789, while the
structure holds 787 residues, because two residues contribute two CA records each. The answer
is right in spirit and off by two in fact. I treat the discrepancy as a discussion prompt
rather than fixing the question, but if you are grading strictly, say so in advance.

## Known issues in this version

- **"Mature" and "precursor" are swapped** in the Section 4 numbering note, as described
  above. Arithmetic fine, wording wrong.
- **789 vs 787 alpha-carbons.** Unremarked in the notebook. Good discussion, bad surprise.
- **The net charge disagrees with the solvation notebook** (+6.29 e here, `-2` hard-coded
  there). This one is correct.
- **No primary citation for `6ANE`.** It is Fecker et al., *Biophysical Journal* 114:1302–1312
  (2018), `10.1016/j.bpj.2018.02.005`. I give it to students when I introduce the structure.
- The py3Dmol viewers render nothing if the notebook is opened in anything other than Colab or
  classic Jupyter. Not a problem in Colab; worth knowing if a student emails you a screenshot
  of an empty box from VS Code.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: data/6ane.pdb` | Download cell skipped, or session restarted | Re-run from Section 1 |
| Empty 3D viewer | Not running in Colab, or output cleared | Re-run the render cell; use Colab |
| `ModuleNotFoundError: gemmi` | Section 0 not run | Run Section 0, then re-run the failing cell |
| Residue 160 is the wrong serine | Numbering mix-up | Coordinates use 133/179/210/158 |
| Everything gone after lunch | Colab VM recycled | Re-run all; it takes ~4 minutes |
