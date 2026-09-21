# HAlign-5

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CMakeLists.txt)
[![Last commit](https://img.shields.io/github/last-commit/pinglu-zhang/HAlign-5)](https://github.com/pinglu-zhang/HAlign-5/commits/main)

[HAlign 4: A New Strategy for Rapidly Aligning Millions of Sequences.](https://doi.org/10.1093/bioinformatics/btae718)

Documentation:

- Detailed usage & examples: [`docs/usage.md`](docs/usage.md)
- Source install & dependencies: [`docs/install.md`](docs/install.md)
- Tests: [`docs/test.md`](docs/test.md)

---

## Install (Conda)

Conda is the recommended installation method for end users.

> **Note:** the `halign5` package is not published on the `malab` channel yet.
> Until it is, install from source (see [`docs/install.md`](docs/install.md)).

```bash
conda install -c malab halign5
```

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
