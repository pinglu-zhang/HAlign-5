# Examples

Three runnable examples, all using data that ships with this repository:

| example | what it shows | time |
|---|---|---|
| [`examples/sim-insertion/`](../examples/sim-insertion/) | why a **multi-reference** panel keeps insertions that a single reference throws away | seconds |
| [`examples/real-insertion/`](../examples/real-insertion/) | the same effect on **real SARS-CoV-2** genomes: a genuine 12 bp insertion, dropped by one reference and kept by a panel | seconds |
| [`examples/covid/`](../examples/covid/) | the multi-reference workflow on **real SARS-CoV-2** genomes (13 references, 19 lineages) | seconds |

Build first ([`install.md`](install.md)); all commands below are run from the
repository root and assume `halign5` is on your `PATH`.

---

## 1. Multi-reference keeps insertions (synthetic)

This is the shortest path to seeing what distinguishes multi-reference mode.

**Single reference** — `--keep-length` pins the output to the 600 columns of
`refA`, so a query's insertion relative to it has nowhere to go:

```bash
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refA.fasta \
        --keep-length \
        -o /tmp/sim.single.fasta
```

Output: **600 columns**, 5 records.

**Multi-reference** — the pre-aligned panel's 651 columns already contain the
insertions, so they survive into the output:

```bash
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refs.aligned.fasta -a \
        --keep-length \
        -o /tmp/sim.multi.fasta
```

Output: **651 columns**, 7 records.

The contrast is driven by the reference set, not by `--keep-length` itself:
without the flag, the single-reference run would also grow to 651 columns for
these queries. Both runs use the flag so that each is pinned to its own
reference framework and the only difference left is the panel.

Per-query result (ungapped length / insertions kept):

| query | single | multi | meaning |
|---|---:|---:|---|
| `q_cladeB_1` | 600 | 630 | 30 bp INS1 kept |
| `q_cladeB_2` | 600 | 630 | 30 bp INS1 kept |
| `q_cladeC_1` | 600 | 651 | INS1 + 21 bp INS2 kept |
| `q_outgroup_A` | 600 | 600 | correctly receives no extra columns |

Full walkthrough and a self-check script: [`examples/sim-insertion/README.md`](../examples/sim-insertion/README.md).

---

## 2. Real SARS-CoV-2 data (multi-reference)

Decompress the bundled xz files:

```bash
xz -dc examples/covid/covid-refs.aligned.fasta.xz > /tmp/refs.aligned.fasta
xz -dc examples/covid/covid-lineages.fasta.xz     > /tmp/lineages.fasta
```

Align 19 Pango lineage consensus genomes against a 13-genome aligned panel:

```bash
halign5 -i /tmp/lineages.fasta \
        -r /tmp/refs.aligned.fasta -a \
        --keep-length \
        -o /tmp/covid.multi.fasta
```

Output: **32 records** (13 references + 19 queries), **29903 columns**.

What this dataset demonstrates is the real workflow — Mash-based reference
selection, profile alignment, shared coordinate projection. It does **not**
demonstrate insertion retention: these references differ by substitutions and
deletions, so the alignment does not grow. See [`examples/covid/README.md`](../examples/covid/README.md)
for that discussion.

---

## 3. Real insertion retention

[`examples/real-insertion/`](../examples/real-insertion/) shows the effect from
section 1 on real genomes instead of synthetic ones. It comes from the project's
own insertion experiment, where a genuine 12 bp insertion (`TCATGCCGCTGT`) sits
between reference positions 21608 and 21609 in 631 Pango lineages.

```bash
xz -dc examples/real-insertion/refs.aligned.fasta.xz > /tmp/real.refs.aligned.fasta
xz -dc examples/real-insertion/wuhan.fasta.xz         > /tmp/real.wuhan.fasta
xz -dc examples/real-insertion/queries.fasta.xz       > /tmp/real.queries.fasta

# single reference: 29,903 columns, insertion dropped
halign5 -i /tmp/real.queries.fasta -r /tmp/real.wuhan.fasta \
        --keep-length -o /tmp/real.single.fasta

# three-row panel: 29,997 columns, insertion kept
halign5 -i /tmp/real.queries.fasta -r /tmp/real.refs.aligned.fasta -a \
        --keep-length -o /tmp/real.multi.fasta

python3 examples/real-insertion/check_insertions.py
```

Output: all five queries lose 13 bp with the single reference and are restored
exactly by the panel. See [`examples/real-insertion/README.md`](../examples/real-insertion/README.md).

---

## Two things that trip people up

### `.xz` is not supported as input

HAlign-5 reads plain FASTA and gzip. Decompress xz/bzip2 first, and pass a
regular file — pipes and `/dev/stdin` are rejected:

```bash
xz -dc data.fasta.xz > data.fasta        # then -i data.fasta
```

### Small inputs and the fast path

When `--keep-length` is **off** and the number of input records is at most
`--consensus-num` (default 1000), HAlign-5 takes a fast path that aligns the
reference on its own and writes it through **without aligning the queries**. A
4-query dataset would come out as just the reference records.

All examples here pass `--keep-length`, and the fast-path condition explicitly
requires `keep_length == false`, so they never enter it. If you drop
`--keep-length` on a small dataset, pass `--consensus-num 1` to force the full
alignment path — otherwise the queries silently vanish from the output.

### `--insertions-output` positions are not genome coordinates

The insertion TSV (`query_id`, `ref_id`, `ref_slot`, `ref_pos_1based_after`,
`insertion_length`, `insertion_sequence`) is useful for extracting insertion
sequences, but `ref_pos_1based_after` is currently populated from the reference
slot index and duplicates `ref_slot`. Rely on `insertion_length` and
`insertion_sequence`.

---

## Data provenance

- Synthetic sequences in `examples/sim-insertion/` are generated by
  `make_data.py` (seeded, reproducible), and are not derived from any real
  genome.
- Pango lineage consensus sequences in `examples/covid/` come from
  <https://github.com/corneliusroemer/pango-sequences>. They are consensus
  genomes, not individual GISAID records.
- Genomes in `examples/real-insertion/` are extracted from the project's
  HAlign-4 insertion experiment
  (`result-new/data/insertion/lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta`)
  and are named by lineage rather than by isolate accession. The underlying
  sequences originate from GISAID; we gratefully acknowledge the GISAID
  contributors and submitting laboratories. `make_data.py` in that directory
  documents the exact extraction.
