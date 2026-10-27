# Why multi-reference keeps insertions

A 10-second demonstration that a **single** reference throws away insertions
relative to itself, while a **multi-reference** panel keeps them.

All sequences here are synthetic and deliberately tiny, so the effect is
visible at a glance.

## The data

```
refA.fasta            single reference, 600 bp, no insertions
refs.aligned.fasta    pre-aligned panel, 3 references, 651 columns
queries.fasta         4 query sequences
```

The panel encodes two clades:

| reference | INS1 (30 bp @ 200) | INS2 (21 bp @ 420) | ungapped |
|---|:--:|:--:|---:|
| `refA` | — | — | 600 |
| `refB` | yes | — | 630 |
| `refC` | yes | yes | 651 |

`refA` has gap columns where `refB`/`refC` carry the insertions, and every
panel row is exactly 651 columns long (that is what "pre-aligned" means, and
what `-a` validates).

The queries belong to those clades: `q_cladeB_1`/`q_cladeB_2` carry INS1,
`q_cladeC_1` carries INS1+INS2, and `q_outgroup_A` carries neither.

## Run it

Build first (see [`docs/install.md`](../../docs/install.md)), then from the
repository root:

### 1. Single reference — insertions are lost

```bash
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refA.fasta \
        --keep-length \
        -o /tmp/sim.single.fasta
```

Output: **600 columns**, 5 records. Every query is forced back onto `refA`'s
600 columns, so the 30 bp and 21 bp insertions are gone.

### 2. Multi-reference — insertions are kept

```bash
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refs.aligned.fasta -a \
        --keep-length \
        -o /tmp/sim.multi.fasta
```

Output: **651 columns**, 7 records.

## Check the result yourself

```bash
echo "single columns: $(head -2 /tmp/sim.single.fasta | tail -1 | tr -d '\n' | wc -c)"
echo "multi columns : $(head -2 /tmp/sim.multi.fasta  | tail -1 | tr -d '\n' | wc -c)"
```

For each record, report its ungapped length and whether each insertion
survived. Checking whole sequences (not `grep` on lines) matters, because the
insertion is split across 70-character line breaks:

```bash
python3 - <<'EOF'
INS1 = "TTAGCCGGATCCGTAAGGCTTACCGATGCA"
INS2 = "GGTCAACTGACCTAGGCTTAA"

def read(path):
    d, name, buf = {}, None, []
    for line in open(path):
        line = line.rstrip()
        if line.startswith(">"):
            if name:
                d[name] = "".join(buf)
            name = line[1:].split()[0]; buf = []
        elif line:
            buf.append(line)
    if name:
        d[name] = "".join(buf)
    return d

for tag, path in (("single", "/tmp/sim.single.fasta"),
                  ("multi",  "/tmp/sim.multi.fasta")):
    d = read(path)
    print(f"[{tag}] {len(next(iter(d.values())))} columns, {len(d)} records")
    for k, v in sorted(d.items()):
        u = v.replace("-", "")
        print(f"   {k:<14} ungapped={len(u):>4} "
              f"INS1={'YES' if INS1 in u else 'no '} "
              f"INS2={'YES' if INS2 in u else 'no'}")
EOF
```

Expected (verified):

| query | single | multi | meaning |
|---|---:|---:|---|
| `q_cladeB_1` | 600 | 630 | INS1 kept |
| `q_cladeB_2` | 600 | 630 | INS1 kept |
| `q_cladeC_1` | 600 | 651 | INS1+INS2 kept |
| `q_outgroup_A` | 600 | 600 | correctly gets no extra columns |

## Why both commands pass --keep-length

Two independent reasons.

**1. It creates the contrast.** The two runs differ only in the reference set,
so they must be compared under the same mode. With `--keep-length` the
single-reference run is pinned to `refA`'s 600 columns and drops the
insertions, while the multi-reference run is pinned to the panel's 651 columns
and keeps them. Without `--keep-length` the single-reference run would itself
grow to 651 to make room for the insertions, and the 600-vs-651 contrast would
vanish — the difference you are meant to see comes from the reference panel,
not from the flag.

**2. It keeps the commands short.** HAlign-5 has a **fast path** when
`--keep-length` is **off** and the input has at most `--consensus-num` records
(default 1000): it aligns the reference on its own and writes that through,
without aligning any query. On this 4-query dataset that fast path would return
only the 3 reference sequences in 70 columns. The condition explicitly requires
`keep_length == false`, so passing `--keep-length` skips it and both commands
run the full alignment path with no extra flags.

If you drop `--keep-length`, keep the queries from disappearing by passing
`--consensus-num 1` — see the real-data example in [`../covid/`](../covid/),
which has a note on this.

Measured widths for this dataset:

| reference set | no `--keep-length` | `--keep-length` |
|---|---:|---:|
| `refA.fasta` (single) | 651 | **600** |
| `refs.aligned.fasta` (panel) | 651 | 651 |

## Reproducing the synthetic data

```bash
python3 make_data.py
```

The generator is seeded, so the files are reproducible byte for byte.
