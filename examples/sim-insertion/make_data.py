#!/usr/bin/env python3
"""Regenerate the synthetic data for the multi-reference insertion demo.

The output is deterministic (fixed seeds), so re-running this reproduces
refA.fasta, refs.aligned.fasta and queries.fasta byte for byte.

Layout:
  refA            no insertion
  refB            INS1 at reference position 200
  refC            INS1 at 200 and INS2 at 420
  queries         members of those clades, with 1-2 random SNVs each

The panel is written as a real alignment: every row is the same length, and a
reference that lacks an insertion carries gap columns at that site. That is
what `-a` validates and what multi-reference mode consumes.
"""

from __future__ import annotations

import random
from pathlib import Path

SEED = 20240516
LENGTH = 600
INS1 = "TTAGCCGGATCCGTAAGGCTTACCGATGCA"   # 30 bp, at reference position 200
INS2 = "GGTCAACTGACCTAGGCTTAA"             # 21 bp, at reference position 420
INS_SITES = {200: INS1, 420: INS2}
CARRY = {"refA": set(), "refB": {1}, "refC": {1, 2}}

OUT = Path(__file__).resolve().parent


def write_fasta(path: Path, records: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for name, seq in records:
            fh.write(f">{name}\n")
            for i in range(0, len(seq), 70):
                fh.write(seq[i:i + 70] + "\n")


def mutate(seq: str, n: int, rng: random.Random) -> str:
    s = list(seq)
    for pos in rng.sample(range(len(s)), n):
        s[pos] = rng.choice([b for b in "ACGT" if b != s[pos]])
    return "".join(s)


def main() -> None:
    rng = random.Random(SEED)
    base = "".join(rng.choice("ACGT") for _ in range(LENGTH))

    # Build the panel column by column so all rows stay aligned.
    rows: dict[str, list[str]] = {name: [] for name in CARRY}
    for i in range(LENGTH):
        if i in INS_SITES:
            which = 1 if i == 200 else 2
            ins = INS_SITES[i]
            for name in rows:
                rows[name].append(ins if which in CARRY[name] else "-" * len(ins))
        for name in rows:
            rows[name].append(base[i])
    panel = {name: "".join(cols) for name, cols in rows.items()}

    write_fasta(OUT / "refs.aligned.fasta", [(n, panel[n]) for n in ("refA", "refB", "refC")])
    write_fasta(OUT / "refA.fasta", [("refA", base)])

    # Queries: few SNVs so the reference choice is unambiguous and the demo is
    # stable regardless of the profile-reference settings.
    qrng = random.Random(7)
    q_b1 = mutate(base[:200], 1, qrng) + INS1 + mutate(base[200:], 1, qrng)
    q_b2 = mutate(base[:200], 2, qrng) + INS1 + mutate(base[200:], 1, qrng)
    q_c = (mutate(base[:200], 1, qrng) + INS1
           + mutate(base[200:420], 1, qrng) + INS2 + mutate(base[420:], 1, qrng))
    q_a = mutate(base, 2, qrng)

    write_fasta(OUT / "queries.fasta", [
        ("q_cladeB_1", q_b1),
        ("q_cladeB_2", q_b2),
        ("q_cladeC_1", q_c),
        ("q_outgroup_A", q_a),
    ])

    print(f"panel columns : {len(panel['refA'])}")
    print(f"ungapped      : refA={len(base)} refB={len(base) + len(INS1)} "
          f"refC={len(base) + len(INS1) + len(INS2)}")
    print(f"queries       : B1={len(q_b1)} B2={len(q_b2)} C={len(q_c)} A={len(q_a)}")


if __name__ == "__main__":
    main()
