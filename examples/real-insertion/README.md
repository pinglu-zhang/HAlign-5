# Real insertion: a 12 bp insertion a single reference cannot hold

A real-data companion to [`../sim-insertion/`](../sim-insertion/). The synthetic
example shows the mechanism; this one reproduces it on SARS-CoV-2 genomes taken
from the project's own insertion experiment, where the hotspot is a genuine
12 bp insertion (`TCATGCCGCTGT`) between reference positions 21608 and 21609.

**Result:** with a single Wuhan reference the insertion is dropped (13 bp
shorter); with a three-row reference panel it is kept, and the aligned sequence
is lossless.

## The data

All three files are xz-compressed; HAlign-5 reads plain FASTA and gzip only, so
decompress them first.

| file | contents |
|---|---|
| `refs.aligned.fasta.xz` | 3 pre-aligned references, **29,997 columns**: Wuhan plus `PQ.2` and `XFG.3.4.1`, both of which carry the insertion |
| `wuhan.fasta.xz` | Wuhan alone, ungapped (29,903 bp) — the single-reference control |
| `queries.fasta.xz` | 5 real isolates from `PQ.4`, `XFG.5.1`, `XFG.1.1`; every one carries the full 12 bp insertion |

The panel is a valid alignment (all rows the same length), which is what `-a`
validates. Wuhan occupies 29,903 of the 29,997 columns; the remaining columns
are the insertions that some lineages carry and others do not.

### Provenance

Extracted from the HAlign-4 insertion experiment,

```
result-new/data/insertion/lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta
```

whose hotspot table (`insertion/results/...lineage_reference_insertions.tsv`)
lists this 12 bp insertion across 631 Pango lineages. Sequence identifiers were
replaced with lineage names for these files. The underlying genome sequences
originate from GISAID; we gratefully acknowledge the GISAID contributors and
the submitting laboratories.

## Run it

From the repository root, after [`docs/install.md`](../../docs/install.md):

```bash
xz -dc examples/real-insertion/refs.aligned.fasta.xz > /tmp/real.refs.aligned.fasta
xz -dc examples/real-insertion/wuhan.fasta.xz         > /tmp/real.wuhan.fasta
xz -dc examples/real-insertion/queries.fasta.xz       > /tmp/real.queries.fasta
```

### 1. Single reference — the insertion is dropped

```bash
halign5 -i /tmp/real.queries.fasta \
        -r /tmp/real.wuhan.fasta \
        --keep-length \
        -o /tmp/real.single.fasta
```

Expect **6 records** (Wuhan + 5 queries) of **29,903 columns**. Every query is
13 bp shorter than its input: the 12 bp insertion plus one adjacent base.

### 2. Multi-reference — the insertion is kept

```bash
halign5 -i /tmp/real.queries.fasta \
        -r /tmp/real.refs.aligned.fasta -a \
        --keep-length \
        -o /tmp/real.multi.fasta
```

Expect **8 records** (3 references + 5 queries) of **29,997 columns**. Every
query comes back at its original length, insertion intact.

### 3. Check it

```bash
python3 examples/real-insertion/check_insertions.py \
  --queries /tmp/real.queries.fasta \
  --single  /tmp/real.single.fasta \
  --multi   /tmp/real.multi.fasta
```

Measured output:

```
single reference : 29903 columns, 6 records
multi  reference : 29997 columns, 8 records
insertion        : TCATGCCGCTGT (12 bp)

query                 input  single  diff  n   multi  diff  n   verdict
----------------------------------------------------------------------------
PQ.4_isolate1         29838   29825   -13  1   29838    +0  2   OK
PQ.4_isolate2         29762   29749   -13  1   29762    +0  2   OK
XFG.5.1_isolate1      29775   29762   -13  1   29775    +0  2   OK
XFG.1.1_isolate1      29706   29693   -13  1   29706    +0  2   OK
PQ.4_isolate3         29772   29759   -13  1   29772    +0  2   OK

PASS  5/5 queries: the single reference dropped the 12 bp insertion, the panel kept it.
```

The `n` column counts occurrences of the 12 bp motif. It is 2 in the input
because `TCATGCCGCTGT` also occurs once near position 17.1 kb, unrelated to this
hotspot. A sequence that has lost the real insertion therefore still contains one
copy — which is exactly why the check counts rather than testing presence. A
plain `grep TCATGCCGCTGT` on the single-reference output would wrongly suggest
the insertion survived.

## Why `--keep-length` matters here

`--keep-length` pins the output to the reference's column framework. That is what
makes the difference visible:

| reference | without `--keep-length` | with `--keep-length` |
|---|---:|---:|
| Wuhan alone | grows for the queries | **29,903**, insertion dropped |
| 3-row panel | 29,997 | **29,997**, insertion kept |

Without the flag the single-reference run can open new columns for the
insertions, so both modes would keep them and there would be nothing to compare.

## Regenerating the data

`make_data.py` rebuilds the three files from the original 1.8 GB alignment:

```bash
python3 examples/real-insertion/make_data.py \
  --source /path/to/lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta
```

It selects rows by inspecting the hotspot columns rather than trusting the
lineage label: within a single lineage only a fraction of isolates carry all
12 bp (for `PQ.2`, 5,542 of 7,788; the rest carry a single `T`), so a name-based
pick would silently produce queries without the insertion.
