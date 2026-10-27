# HAlign-5

[![Downloads](https://anaconda.org/malab/halign5/badges/downloads.svg)](https://anaconda.org/malab/halign5)
[![License](https://anaconda.org/malab/halign5/badges/license.svg)](https://anaconda.org/malab/halign5)
[![Platforms](https://anaconda.org/malab/halign5/badges/platforms.svg)](https://anaconda.org/malab/halign5)
[![Last commit](https://img.shields.io/github/last-commit/pinglu-zhang/HAlign-5)](https://github.com/pinglu-zhang/HAlign-5/commits/main)

[HAlign 4: A New Strategy for Rapidly Aligning Millions of Sequences.](https://doi.org/10.1093/bioinformatics/btae718)

Documentation:

- Detailed usage & examples: [`docs/usage.md`](docs/usage.md)
- **Runnable examples**: [`docs/examples.md`](docs/examples.md)
- Source install & dependencies: [`docs/install.md`](docs/install.md)
- Tests: [`docs/test.md`](docs/test.md)

---

## Install (Conda)

Conda is the recommended installation method for end users:

```bash
conda install -c malab halign5
```

The `malab` channel currently hosts **v1.0.0**; the source in this repository
reports `VERSION 2.0.0`. To run the examples against the checked-out source,
build from source instead (see [`docs/install.md`](docs/install.md)).

Verify:

```bash
halign5 --version
halign5 -h
```

Source installation: see [`docs/install.md`](docs/install.md).

---

## Quick start

The repository includes small datasets under `test/data/` which are perfect for a first run.

Minimal example:

```bash
halign5 \
  -i test/data/mt1x.fasta.gz \
  -o mt1x.out.fasta
```

### See multi-reference keep insertions

With a single reference and `--keep-length`, the output is pinned to that
reference's columns, so insertions relative to it cannot be represented. With a
pre-aligned reference panel, the panel's columns already include the insertions,
so they survive. Two bundled examples make the difference visible:

```bash
# single reference: 600 columns, insertions cannot be represented
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refA.fasta \
        --keep-length -o /tmp/sim.single.fasta

# multi-reference: 651 columns, insertions kept
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refs.aligned.fasta -a \
        --keep-length -o /tmp/sim.multi.fasta
```

Real SARS-CoV-2 data (13 aligned references + 19 Pango lineages) is in
[`examples/covid/`](examples/covid/). Walkthrough: [`docs/examples.md`](docs/examples.md).

### Real insertions

[`examples/real-insertion/`](examples/real-insertion/) runs the same comparison
on SARS-CoV-2 genomes from the project's insertion experiment, where a genuine
12 bp insertion sits between reference positions 21608 and 21609:

- single Wuhan reference, `--keep-length` → **29,903 columns**, every query 13 bp shorter, insertion dropped
- 3-row reference panel, `-a --keep-length` → **29,997 columns**, every query lossless, insertion kept

`check_insertions.py` in that directory verifies the result.

---

## Parameters (overview)

The most important parameters are:

- `-i/--input`: input FASTA (required)
- `-o/--output`: output aligned FASTA (required)
- `-w/--workdir`: working directory (optional; default: `<output-dir>/tmp-<random>`)
- `--msa-tool`: MSA method (keyword: `minipoa`/`mafft`/`clustalo`, or a custom template)
- `-r/--reference`: provide a reference/center FASTA (optional)
- `-a/--reference-aligned`: treat `-r/--reference` as a pre-aligned reference MSA and strip gaps internally
- `--reference-msa`: compatibility option for a pre-aligned reference MSA; can also be used without `-r`
- `--score-matrix`: provide a DNA5 scoring matrix file (see `score.example.tsv`)
- `--minimizer-size`, `--minimizer-window`, `--consensus-num`, `--sketch-size`, `--sketch-kmer-size`, `--batch-size`: algorithm sizing controls
- `--gap-open`, `--gap-extend`: control gap open/extension penalties
- `--min-profile-references`, `--max-profile-references`, `--min-profile-reference-similarity`: mash-based reference profile selection controls
- `-k/--keep-length`: keep reference length coordinate rules
- `--auto-strand`, `--insertion-merge`, `--insertions-output`, `--no-reference-output`, `--save-workdir`, `--enable-wfa`: optional workflow/output controls

For the full parameter list and detailed examples, see [`docs/usage.md`](docs/usage.md).

---

## Tests

See [`docs/test.md`](docs/test.md) for how to run tests under the `test/` directory.

---

## Citation

If you use HAlign-5 in academic work, please cite:

HAlign 4: a new strategy for rapidly aligning millions of sequences. Bioinformatics, 2024, 40(12): btae718. https://doi.org/10.1093/bioinformatics/btae718
