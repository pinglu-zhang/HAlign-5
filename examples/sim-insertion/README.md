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
        --keep-length --consensus-num 1 \
        -o /tmp/sim.single.fasta
```

Output: **600 columns**, 5 records. Every query is forced back onto `refA`'s
600 columns, so the 30 bp and 21 bp insertions are gone.

### 2. Multi-reference — insertions are kept

```bash
halign5 -i examples/sim-insertion/queries.fasta \
        -r examples/sim-insertion/refs.aligned.fasta -a \
        --min-profile-references 2 --max-profile-references 3 \
        --consensus-num 1 \
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

## Why consensus-num 1 is needed

With `--keep-length` off and few queries, HAlign-5 takes a **fast path**: when
the number of input records is `<= --consensus-num` (default 1000) it writes
the reference through without aligning the queries. Setting
`--consensus-num 1` forces the full alignment path. This matters for every
small example, including the real-data one in
[`../covid/`](../covid/).

The two runs only differ in the reference set, so the extra 51 columns in the
second run (651 vs 600) are exactly INS1 + INS2 surfacing in the output.

## Reproducing the synthetic data

```bash
python3 make_data.py
```

The generator is seeded, so the files are reproducible byte for byte.
