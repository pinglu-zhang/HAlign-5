# Real SARS-CoV-2 data: multi-reference alignment at scale

A small, real dataset for running HAlign-5 on SARS-CoV-2 with a
**pre-aligned multi-reference panel** instead of a single Wuhan genome.

Both files are xz-compressed because HAlign-5 itself only reads plain FASTA
(and gzip); see [Compression](#compression) below.

## The data

| file | contents | uncompressed |
|---|---|---|
| `covid-refs.aligned.fasta.xz` | 13 SARS-CoV-2 reference genomes, **pre-aligned** (every row 29903 columns, gaps included) | ~395 KB |
| `covid-lineages.fasta.xz` | 19 representative Pango lineage consensus genomes (A, B, B.1.1.7, B.1.351, B.1.617.2, BA.1, BA.2, BA.2.86, BA.5, JN.1, XBB.1.5, XFG, P.1, ...) | ~576 KB |

The panel is aligned, so it can be passed with `-a`; that flag validates that
all rows share the same length.

Lineage consensus sequences come from
<https://github.com/corneliusroemer/pango-sequences>. They are consensus
genomes, not individual GISAID records, and carry no sample metadata.

## Run it

### 1. Decompress

```bash
xz -dc examples/covid/covid-refs.aligned.fasta.xz    > /tmp/refs.aligned.fasta
xz -dc examples/covid/covid-lineages.fasta.xz        > /tmp/lineages.fasta
```

### 2. Multi-reference alignment

```bash
halign5 -i /tmp/lineages.fasta \
        -r /tmp/refs.aligned.fasta -a \
        --keep-length \
        -o /tmp/covid.multi.fasta
```

Expect **32 records** (13 references + 19 queries) of **29903 columns** each.

### 3. Compare against a single reference

Extract just Wuhan and drop the gaps, then align the same queries:

```bash
python3 - <<'EOF'
lines = open("/tmp/refs.aligned.fasta").read().split(">")
for rec in lines:
    if rec.startswith("NC_045512"):
        name, _, seq = rec.partition("\n")
        with open("/tmp/wuhan.fasta", "w") as fh:
            fh.write(">" + name.strip() + "\n" + seq.replace("\n", "").replace("-", "") + "\n")
EOF

halign5 -i /tmp/lineages.fasta -r /tmp/wuhan.fasta \
        --keep-length \
        -o /tmp/covid.single.fasta
```

Expect **20 records** (reference + 19 queries) of **29903 columns**.

## What this dataset does and does not show

It shows the **multi-reference workflow on real genomes**: several references
per query are selected by Mash similarity, queries are aligned against the
best-matching profile, and the results are projected into one shared
coordinate system.

It does **not** demonstrate insertion retention, because these 13 reference
genomes have no insertions relative to each other — the panel's 96 gap columns
are **deletions** in some lineages relative to Wuhan, not insertions. That is
why both runs above come out at 29903 columns and why `--insertions-output`
would produce only a header row on this data.

For a clean demonstration that insertions survive when the panel actually
contains them, use the synthetic example:
[`../sim-insertion/`](../sim-insertion/) (600 columns single-reference vs
651 multi-reference).

## Compression

HAlign-5 reads plain FASTA and gzip via zlib. It does **not** read xz/bzip2,
and it rejects non-regular files such as pipes and `/dev/stdin`
(`input is not a regular file`), so decompress to a real file first.

```bash
xz -dc covid-lineages.fasta.xz > lineages.fasta   # right
xz -dc covid-lineages.fasta.xz | halign5 -i /dev/stdin ...   # fails
```

## Why both commands pass --keep-length

`--keep-length` pins the output to the **reference MSA column framework**: the
alignment width is set by the reference panel, not by what the queries happen to
carry, and the panel's existing gap columns are preserved. Column numbers
therefore stay comparable across the whole panel.

It also keeps the commands short, because HAlign-5 has a fast path when
`--keep-length` is **off** and the input has at most `--consensus-num` records
(default 1000): the reference is aligned on its own and written through with no
queries. On this 19-query dataset that would return only the 13 references. The
fast-path condition explicitly requires `keep_length == false`, so passing
`--keep-length` avoids it without any extra flags.

If you need to drop `--keep-length`, pass `--consensus-num 1` so the queries
are still aligned — see
[`../sim-insertion/README.md`](../sim-insertion/README.md#why-both-commands-pass---keep-length).
