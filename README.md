# HAlign-5

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CMakeLists.txt)
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

With a single reference, insertions relative to that reference are discarded.
With a pre-aligned reference panel, they are kept. Two bundled examples make
the difference visible:

```bash
# single reference: 600 columns, insertions lost
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refA.fasta \
        --keep-length --consensus-num 1 -o /tmp/sim.single.fasta

# multi-reference: 651 columns, insertions kept
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refs.aligned.fasta -a \
        --min-profile-references 2 --max-profile-references 3 \
        --consensus-num 1 -o /tmp/sim.multi.fasta
```

Real SARS-CoV-2 data (13 aligned references + 19 Pango lineages) is in
[`examples/covid/`](examples/covid/). Walkthrough: [`docs/examples.md`](docs/examples.md).

---

## Limitations

- **Insertions relative to the reference are dropped in keep-length mode.**
  With `-k/--keep-length`, columns that would introduce gaps into a reference
  are removed, so insertions relative to the reference coordinate system
  disappear from the output. Without `--keep-length` they are retained in the
  aligned FASTA (see [`examples/sim-insertion/`](examples/sim-insertion/),
  where the same queries come out 600 columns with `--keep-length` and 651
  without). Multi-reference panels also keep the insertions that the panel
  itself contains.
- **`--insertions-output` position column is not a genome coordinate.** The TSV
  reports `query_id`, `ref_id`, `ref_slot`, `ref_pos_1based_after`,
  `insertion_length` and `insertion_sequence`, but `ref_pos_1based_after` is
  currently filled from the reference slot index rather than a nucleotide
  position, so it duplicates `ref_slot`. Treat the insertion sequence and
  length as the authoritative fields until this is fixed.
- **External MSA tools are required.** The consensus/insertion alignment step
  calls an external tool (`minipoa` by default; `mafft` and `clustalo` are also
  supported).
- **Small inputs may take a fast path.** When `--keep-length` is off and the
  input has at most `--consensus-num` records (default 1000), the reference is
  written through without aligning the queries. Pass `--consensus-num 1` to
  force the full alignment path on small datasets.
- **Compressed input is limited to gzip.** xz/bzip2 files must be decompressed
  first, and input must be a regular file (pipes and `/dev/stdin` are rejected).

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
