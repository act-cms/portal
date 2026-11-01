## At a glance

| | |
|---|---|
| **Runtime** | CPU. |
| **Wall clock** | Under 2 minutes, including the MAFFT install. Budget 75–90 minutes of class time. |
| **Network** | `apt-get install mafft` from the Ubuntu archive. No other downloads. |
| **Prerequisites** | None technical. Students need the idea of a scoring matrix, which Section 2 supplies. |
| **Produces** | `data/foxp_homologs.fasta`, `data/foxp_expanded.fasta`, `data/foxp_aligned.fasta`, `manifests/lab1_3a_lockfile.json` |
| **Quiz items** | 6, in three blocks |

> **Read the "Known issues" section before you teach this one.** The sequence dataset in the
> notebook is mislabelled, and the problem propagates into the trees and into the narrative
> about why branches have zero length. There is a drop-in replacement at the end of this
> guide. Everything else in the notebook is sound.

## What this notebook is for

Three ideas, in a deliberate order. First, that homology is a hypothesis you argue for, not a
percentage you measure — identity, similarity and homology are three different words and
students use them interchangeably until stopped. Second, that an alignment score is a function
of the scoring model, so the "best" alignment moves when you change the matrix or the gap
penalty. Third, that distance methods and character methods answer the same question with
different information, and can disagree.

The sensitivity table in Section 2 is the heart of the session and the part students remember.

## Before class

Run it once. The only installation risk is `apt-get install -qq -y mafft`, which occasionally
stalls on an Ubuntu mirror; if that happens the alignment cell catches the failure and writes a
stored reference alignment instead, printing a notice, and the rest of the notebook runs
normally. Check which branch you got — the printed alignment width tells you (MAFFT gives 97
columns for this input; the stored fallback gives 99).

## Section-by-section

### Section 1 — vocabulary

Pure markdown, then a quiz. Worth defending the class time: get them to say out loud that two
sequences at 22% identity over 35 residues are in the twilight zone, and that "22% identical"
is a measurement while "homologous" is an inference about shared ancestry.

### Section 2 — pairwise scoring and the sensitivity sweep

```
Self-alignment score of 'ACDEFG' (BLOSUM62): 36.0 (Expected: 36.0)
Divergent alignment score 'ACDEFG' vs 'WWWWWW': -13.0
```

Then the sweep, which is the cell to dwell on:

| Matrix | Gap open | Score |
|---|---|---|
| BLOSUM62 | −5 | 47.0 |
| BLOSUM62 | −10 | 42.0 |
| BLOSUM62 | −15 | 37.0 |
| BLOSUM62 | −20 | 32.0 |
| PAM250 | −5 | 49.0 |
| PAM250 | −10 | 44.0 |
| PAM250 | −15 | 39.0 |
| PAM250 | −20 | 34.0 |

The score falls by exactly 5 for every 5 units of gap-open penalty under both matrices, which
means the optimal alignment contains exactly one gap and never changes topology across this
range. That is a nice, concrete thing to notice: a sensitivity sweep that produces a straight
line is telling you the alignment is *robust*, not that the parameter does not matter. Ask what
you would expect to see if the optimal path did flip — a kink, not a slope.

### Sections 3 and 3.5 — the dataset

Eight 97-residue sequences are written to `data/foxp_homologs.fasta` and de-duplicated:

```
Total raw sequences loaded: 8
Sequences remaining after exact de-duplication: 5
Collapsed records: ['FOXP1_HUMAN', 'FOXP3_HUMAN', 'FOXP_DROME', 'FOXA1_HUMAN', 'FOXO1_HUMAN']
```

Four records collapse to one because they are the same string. See "Known issues" — this is
where the trouble is.

### Section 4 — MSA and conservation

MAFFT if present, stored alignment otherwise, then a per-column conservation score and a
viridis heatmap. The ten fully-conserved columns it reports (88, 94, 95, 71, 69, 87, 32, 34,
46, 44) include the two arginines of the recognition helix and the invariant tryptophan, which
is the right biology even though the sequences are the wrong proteins.

Make them read the heatmap properly: the dark bands are *not* "unimportant", they are
positions where substitution is tolerated, which is itself evidence about function.

### Section 5 — two tree-building paradigms

Neighbour-joining from a BLOSUM62 distance matrix, then maximum parsimony seeded with the NJ
tree and refined by NNI search. Expected terminal set is all 8 taxa in both.

```
FOXO1_HUMAN   basal outgroup   branch 0.4746
FOXA1_HUMAN   basal outgroup   branch 0.1440
FOXP3_HUMAN   ingroup          branch 0.1934
FOXP_DROME    ingroup          branch 0.0495
FOXP1/2/4, Foxp2_MOUSE          branch 0.0000
```

**The two trees come out byte-identical.** Not similar — identical, down to the branch lengths
in the Newick strings, because the parsimony search starts from the NJ topology and NNI finds
no improving rearrangement on five distinct sequences. A student who diffs the two Newick
strings, which is the obvious thing to do, will find no difference at all and conclude the
methods are the same. Get ahead of that: the honest statement is that on a dataset this small
and this clean, the two criteria agree, and agreement between independent methods is a result
worth having. Then point out that the exercise cannot demonstrate disagreement, and that
disagreement is what the methods are actually interesting for.

### Section 6 — Newick export

Writes both topologies to disk for the maximum-likelihood session. **That session is not part
of this online set.** The notebook refers to it by name in the prose and in the second report
question. Either cut the reference or tell students the handoff file is for later.

## Known issues in this version

### The sequences are not FoxP

Every record in `FOXP_DATASET_FASTA` begins `KPPYSY`. The real FoxP forkhead domain begins
`RPPFTY`; `KPPYSY` is the FoxA signature. I aligned the record labelled `FOXP1_HUMAN` against
the genuine UniProt domains:

| Record in notebook | vs real FOXA1 forkhead | vs real FOXP1 forkhead |
|---|---|---|
| `FOXP1_HUMAN` | **72.9%** identical | 42.4% identical |
| `FOXP_DROME` | 67.7% | 44.7% |
| `FOXA1_HUMAN` (the "outgroup") | 69.5% | 45.9% |

So the ingroup is FoxA-like, and the designated FoxA outgroup is only 67.7% away from it —
closer than a real outgroup should be, because everything in the file is drawn from the same
family. The tree is internally consistent and biologically mislabelled.

### The zero-length branches are an artefact, and the explanation given is wrong

`FOXP1_HUMAN`, `FOXP2_HUMAN`, `FOXP4_HUMAN` and `Foxp2_MOUSE` are the *same 97 characters*.
They have zero-length branches because they are copies of one another, not because of
purifying selection. The markdown attributes the collapse to "intense evolutionary constraint"
on the recognition helix, which the data does not show.

The real numbers are better than the invented ones, which is the frustrating part. In the
genuine forkhead domain, human FOXP1/FOXP2/FOXP4 are **86.8–87.9%** identical — close, but
easily resolved. FOXP3 is the divergent paralogue at 71.9–78.7%. And human FOXP2 versus mouse
Foxp2 across the forkhead domain is **100.0% identical**, which is real biology and gives you a
genuine zero-length branch to explain. Replace the data and the story gets stronger.

### Section 3.5 promises something it never does

The markdown argues that widening the window to a multi-domain alignment resolves the polytomy.
The cell writes `data/foxp_expanded.fasta` and **nothing ever reads it again**. Worse, the three
FoxP records in that expanded file are also identical to each other, so even if it were loaded
the polytomy would survive. Either delete the section or finish it.

### Dangling cross-references

The prose and report question 2 refer to the maximum-likelihood notebook, which is not in this
online set. Report question 1 refers back to the foundations and databases sessions, which are.

## A drop-in replacement dataset

I built these from the real UniProt records, anchoring every window on the human FOXP2
fork-head domain (O15409, residues 504–594) so the windows are directly comparable. Paste over
`FOXP_DATASET_FASTA` in Section 3; nothing else in the notebook needs to change.

```
>FOXP1_HUMAN forkhead domain          (Q9H334, 465-555)
RPPFTYASLIRQAILESPEKQLTLNEIYNWFTRMFAYFRRNAATWKNAVRHNLSLHKCFVRVENVKGAVWTVDEVEFQKRRPQKISGNPSL
>FOXP2_HUMAN forkhead domain          (O15409, 504-594)
RPPFTYATLIRQAIMESSDRQLTLNEIYSWFTRTFAYFRRNAATWKNAVRHNLSLHKCFVRVENVKGAVWTVDEVEYQKRRSQKITGSPTL
>FOXP4_HUMAN forkhead domain          (Q8IVH2, 467-559)
RPPFTYASLIRQAILETPDRQLTLNEIYNWFTRMFAYFRRNTATWKNAVRHNLSLHKCFVRVENVKGAVWTVDEREYQKRRPPKMTGSPTL
>FOXP3_HUMAN forkhead domain          (Q9BZS1, 337-423)
RPPFTYATLIRWAILEAPEKQRTLNEIYHWFTRMFAFFRNHPATWKNAIRHNLSLHKCFVRVESEKGAVWTVDELEFRKKRSQRPSRCSNP
>Foxp2_MOUSE forkhead domain          (P58463, 503-593)
RPPFTYATLIRQAIMESSDRQLTLNEIYSWFTRTFAYFRRNAATWKNAVRHNLSLHKCFVRVENVKGAVWTVDEVEYQKRRSQKITGSPTL
>FOXP_DROME forkhead domain           (Q9VH87, 328-401)
RPPFTYASLIRQAIIDSPDKQLTLNEIYNWFQNTFCYFRRNAATWKNAVRHNLSLHKCFMRVENVKGAVWTVDEIEFYKRRPQRTAGIGNN
>FOXA1_HUMAN forkhead domain          (P55317, 169-260)
KPPYSYISLITMAIQQAPSKMLTLSEIYQWIMDLFPYYRQNQQRWQNSIRHSLSFNDCFVKVARSPDKPGKGSYWTLHPDSGNMFENGCYLRRQKR
>FOXO1_HUMAN forkhead domain          (Q12778, 159-235)
WGNLSYADLITKAIESSAEKRLTLSQIYEWMVKSVPYFKDKGDSNSSAGWKNSIRHNLSLHSKFIRVQNEGTGKSSWWMLNPEGGKSGKSPRRRAA
```

What changes in the narrative if you use these:

- Paralogue identity is **~87%**, not 100%. The polytomy among FOXP1/2/4 disappears and the
  tree resolves — which is the outcome Section 3.5 claims and never delivers.
- Human FOXP2 and mouse Foxp2 remain **100% identical** in this domain. That is the zero-length
  branch, and now it is real. It is also a good question: why would roughly 90 million years
  of divergence leave a 91-residue domain untouched?
- The outgroups become genuinely distant: FOXA1 at 41.0–47.5%, FOXO1 at 36.4–42.5%.
- *Drosophila* FoxP sits at 67.0–81.3% from the vertebrate FoxP group, so it is an ingroup
  member, not an outgroup. The notebook already treats it correctly.
- Note that FOXA1 carries `RHSLS`, not the FoxP `RHNLS`. Do not describe `RHNLS` as universal
  across the forkhead superfamily — it is a FoxP marker, and that is precisely what makes the
  outgroup comparison informative.
- One bonus: FOXP2 R553H, the variant segregating in the KE family with developmental verbal
  dyspraxia, is residue 50 of the FOXP2 window above — the arginine of `RHNLS`. With the real
  sequence you can point at it in the alignment.

## Quiz answer key

| # | Topic | Correct answer |
|---|---|---|
| 1 | 22% identity over 35 residues | Twilight zone; similarity alone is not evidence of homology |
| 2 | FOXP1/FOXP2 vs human/mouse FOXP2 | Paralogues; orthologues |
| 3 | BLOSUM45 vs BLOSUM80 | BLOSUM45 clusters at ≥45% identity, so divergent substitutions dominate |
| 4 | Why affine gaps | One indel event of n residues is one mutation, so penalise opening heavily and extension lightly |
| 5 | NJ limitation vs parsimony | NJ compresses the alignment to pairwise distances and discards column-level character states |
| 6 | Why an outgroup | Tree algorithms return unrooted topologies; the outgroup places the root and gives time a direction |

All six remain correct with the replacement dataset. Question 2 is about FOXP1 and FOXP2 as
concepts, not about the strings in the file, so it survives either way.

## Further reading I hand out

- Henikoff & Henikoff, *PNAS* 89:10915 (1992). `10.1073/pnas.89.22.10915` — BLOSUM.
- Saitou & Nei, *Mol Biol Evol* 4:406 (1987). `10.1093/oxfordjournals.molbev.a040454` — neighbour-joining.
- Katoh & Standley, *Mol Biol Evol* 30:772 (2013). `10.1093/molbev/mst010` — MAFFT 7.
- Cock et al., *Bioinformatics* 25:1422 (2009). `10.1093/bioinformatics/btp163` — Biopython.
