## At a glance

| | |
|---|---|
| **Runtime** | CPU. |
| **Wall clock** | Under 2 minutes of compute. Budget 75 minutes of class time. |
| **Network** | Live UniProt REST call, with a cached payload as fallback. Nothing else is fetched. |
| **Prerequisites** | The foundations session. Students should already know the 27-residue numbering offset. |
| **Produces** | `manifests/lab1_1_lockfile.json` |
| **Quiz items** | 6, in three blocks |

## What this notebook is for

Two halves that do not look related and are. The first is database literacy: hit UniProt over
REST, parse the JSON, and discover that the annotation carries a numbering system which does
not match the coordinate file anyone will hand you. The second is quantitative enzymology:
fit Michaelis–Menten parameters by non-linear regression, then discriminate inhibition
mechanisms by global fitting rather than by eyeballing a Lineweaver–Burk plot.

The thread that joins them is that both halves are about *provenance*. Where did this number
come from, what does it describe, and does it mean what the label says? I teach the session
with that question in front, because the notebook contains at least one place where the
answer is no — see "Known issues" below, and consider using it deliberately.

## Before class

Run it end to end once. It is fast. The two things to check are that UniProt responds (if it
does not, the cell prints a notice and falls back to a cached copy, and the session still
works) and that you have replaced the placeholder NCBI e-mail address — the notebook ships
with `Entrez.email = "student_training@university.edu"`, which is not a real mailbox. NCBI's
usage policy asks for a working address so they can contact you before blocking an IP, and
the whole class will be coming from a narrow range of Google addresses.

## Section-by-section

### Section 1 — the four-class monomer table

A dictionary of representative monomers (alanine, aspartate, lysine, histidine, AMP,
palmitate, glucose) with charge at pH 7.4, hydrogen-bond donor and acceptor counts, and a
hydrophobicity flag. Seven rows, no computation to speak of.

It looks trivial and it is the right place to slow down. The quiz immediately afterwards asks
why free AMP carries about −2 while an internal nucleotide in a strand carries −1, and most
students have never been asked to think about a phosphodiester as *two esterified oxygens
that are no longer ionisable*. Draw it.

### Section 2 — UniProt, and the numbering contract again

```
UniProt ID: A0A0K8P6T7
Protein Name: Poly(ethylene terephthalate) hydrolase
Organism: Piscinibacter sakaiensis
Sequence Length: 290 amino acids

Annotated Signal Peptide: Residues 1 to 27 (cleaved upon secretion)
Mature functional protein starts at UniProt residue 28

Annotated Catalytic Sites in UniProt:
  UniProt #160 (Deposited PDB #133): Nucleophile
  UniProt #206 (Deposited PDB #179): Charge relay system
  UniProt #237 (Deposited PDB #210): Charge relay system
```

Note the organism. The notebook's prose says *Ideonella sakaiensis*, which is how the 2016
paper named it and how everyone still says it; UniProt now returns **Piscinibacter
sakaiensis** after a taxonomic reclassification. Students will spot the mismatch and ask. The
answer is that both refer to the same organism and the literature has not caught up — which
is a better lesson about databases than anything I could have scripted.

This section states the numbering relationship correctly: UniProt 160 is the nucleophile,
deposited residue 133 is the same atom. If you taught the foundations session first, note that
it labels the same two columns "mature" and "deposited", which is the wrong way round. Here
it is right. Use this version.

### Section 3 — sliding windows

Kyte–Doolittle hydrophobicity over the 263-residue mature sequence, window 9:

```
Mature PETase sequence length: 263 aa
Hydrophobicity: Min = -2.20, Max = 2.17, Mean = -0.27
```

Then the same machinery applied to GC content in an RNA. Expect `Riboswitch Length: 67 nt`,
base counts A 17 / C 17 / G 17 / U 16, overall GC 0.507.

Two points I make here. The window size is a smoothing parameter, not a property of the
protein: window 9 is conventional for spotting transmembrane helices and window 19 will erase
everything short. And the edge handling in this implementation truncates rather than pads, so
the first and last four values are averages over fewer residues. Ask what that does to the
ends of the plot.

### Sections 4 and 5 — kinetics and inhibition

Non-linear least squares on two substrates, then a global fit across five substrate
concentrations at four inhibitor concentrations to choose between competitive and
non-competitive models.

```
p-NP-butyrate:  Vmax 8.28 ± 0.03 uM/min   Km 0.283 mM   kcat 165.6 /min   kcat/Km 586.3
BHET:           Vmax 6.67 ± 0.04 uM/min   Km 1.275 mM   kcat 133.4 /min   kcat/Km 104.6
  -> 5.60-fold catalytic preference for p-NP-butyrate

Competitive     SSE = 0.0535   Vmax 9.84, Km 0.61 mM, Ki 0.50 mM
Non-competitive SSE = 3.8766   Vmax 11.20, Km 0.99 mM, Ki 2.37 mM
```

A seventy-fold difference in SSE is not a close call, and that is the pedagogical point: model
selection by fit quality is decisive here in a way that reading intercepts off a double-
reciprocal plot is not. The Lineweaver–Burk plot that follows is presented as a *diagnostic*,
after the fit, which is the right order. Say so explicitly, because most of them learned it as
the primary method in biochemistry.

Make sure they can state why kcat/Km, not kcat, is the specificity constant: at low substrate
it is the apparent second-order rate constant for free enzyme meeting free substrate, so it is
the quantity under selection in a cell where substrate is scarce.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | Free AMP vs internal nucleotide | Terminal monophosphate has two ionisable OH (pKa₂ ≈ 6.2); an internal residue has both oxygens esterified, leaving one |
| 2 | Glucose vs palmitate | Glucose neutral and hydrophilic; palmitate is amphipathic with a −1 carboxylate head |
| 3 | Which database for a new ncRNA | Rfam — families defined by covariance models |
| 4 | Primary vs secondary databases | Primary archive raw observations; secondary add curation and prediction |
| 5 | Km rises 0.4 → 1.8 mM, Vmax unchanged | Competitive inhibition |
| 6 | Why kcat/Km | It is the apparent second-order constant at sub-saturating substrate |

All six are sound as written.

## Known issues in this version

**The RNA sequence is the wrong riboswitch.** This is the one to deal with before you teach.
Section 3 says it is computing GC content for "the *add* A-riboswitch aptamer", the adenine
riboswitch from the foundations session (PDB `1Y26`). The 67-nucleotide string in the cell is
not that molecule. It is byte-for-byte the **xpt-pbuX guanine riboswitch aptamer domain** of
*B. subtilis* — I checked it against the deposited sequence for PDB `4FE5`, and it matches
exactly. The *add* adenine riboswitch in `1Y26` has a completely different sequence
(`CGCUUCAUAUAAUCCUAAUGAUAUGG...`, 71 modelled nucleotides, numbered 13–83).

Nothing downstream breaks — the GC calculation is correct arithmetic on a real riboswitch
aptamer — but the label is wrong, and a student who tries to map the GC track onto the `1Y26`
structure will get nonsense. Two honest fixes:

- Relabel it. Say it is the *xpt-pbuX* guanine riboswitch, cite Serganov et al., *Chem Biol*
  11:1729 (2004), `10.1016/j.chembiol.2004.11.018`, and point out that purine riboswitches
  come in adenine- and guanine-reading flavours distinguished by a single pyrimidine.
- Or swap in the `1Y26` sequence so the thread stays on one molecule.

I prefer the first. The contrast between the two aptamers is worth five minutes, and it turns
an erratum into content.

**The kinetics data has no source.** The cell is headed "Experimental PETase steady-state
kinetics data" but no paper is cited, and the numbers fit the model almost too well for
bench data. Treat them as teaching data and say so. If you want students to compare against
real measurements, the anchors are Yoshida et al., *Science* 351:1196 (2016),
`10.1126/science.aad6359`; Joo et al., *Nat Commun* 9:382 (2018),
`10.1038/s41467-018-02881-1`; and Austin et al., *PNAS* 115:E4350 (2018),
`10.1073/pnas.1718804115`.

**`Entrez.email` is a placeholder.** Replace it with your own address before the class runs.

**Organism name drift.** Covered above — narrative says *Ideonella*, live API says
*Piscinibacter*. Not an error so much as a thing to be ready for.

## Report questions

Two, both good. The uncompetitive-inhibition extension is a genuine coding exercise and the
expected finding is that uncompetitive fits this dataset badly — the point being that a third
model does not automatically beat two. The parallel-lines result in the double-reciprocal plot
follows from both slope and intercept being scaled by the same factor; make them derive that
rather than assert it.

The signal-peptide electrostatics question is answerable with the function from the foundations
session. Expect a near-neutral, strongly hydrophobic 27-mer with a modest positive patch at the
N-terminus — the classic n-h-c architecture of a Sec signal peptide.

## Further reading I hand out

- Yoshida et al., *Science* 351:1196 (2016). `10.1126/science.aad6359` — the original organism.
- Joo et al., *Nat Commun* 9:382 (2018). `10.1038/s41467-018-02881-1` — PETase mechanism.
- Kyte & Doolittle, *J Mol Biol* 157:105 (1982). `10.1016/0022-2836(82)90515-0` — the hydropathy scale.
- Serganov et al., *Chem Biol* 11:1729 (2004). `10.1016/j.chembiol.2004.11.018` — purine riboswitch discrimination.
- Cock et al., *Bioinformatics* 25:1422 (2009). `10.1093/bioinformatics/btp163` — Biopython.
