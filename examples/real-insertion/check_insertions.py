#!/usr/bin/env python3
"""Verify that a multi-reference panel keeps an insertion a single reference drops.

Reads the two alignments produced by the commands in this directory's README:

    single.fasta   aligned against Wuhan only (29,903 columns)
    multi.fasta    aligned against the 3-row panel (29,997 columns)

For each query it reports the ungapped length change against the input and how
many times the 12 bp insertion occurs.

Why occurrence counts instead of a boolean "insertion present" test:

1. The motif occurs twice in an insertion-carrying genome. TCATGCCGCTGT also
   sits around position 17.1 kb, so a query that carries the real hotspot
   insertion contains it twice. A bare `INSERTION in seq` check is therefore
   true even after the real insertion has been dropped -- it reports a false
   positive on the single-reference output.
2. Flanks may be mutated. Requiring a fixed left/right context would produce
   false negatives on queries whose neighbouring bases differ from the reference.

Counting occurrences gives an unambiguous signal:

    input 2  ->  single reference 1  (insertion dropped)
    input 2  ->  multi-reference  2  (insertion kept)

Column coordinates also differ between the two outputs (29,997 vs 29,903), so
nothing here slices a fixed column range.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

INSERTION = "TCATGCCGCTGT"


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    name, buf = None, []
    with path.open() as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if name is not None:
                    records[name] = "".join(buf)
                name, buf = line[1:].split()[0], []
            elif line:
                buf.append(line)
    if name is not None:
        records[name] = "".join(buf)
    return records


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent
    ap.add_argument("--queries", type=Path, default=here / "queries.fasta")
    ap.add_argument("--single", type=Path, default=here / "single.fasta")
    ap.add_argument("--multi", type=Path, default=here / "multi.fasta")
    args = ap.parse_args()

    for p in (args.queries, args.single, args.multi):
        if not p.is_file():
            print(f"ERROR: missing {p}", file=sys.stderr)
            print("  Run the commands in README.md first.", file=sys.stderr)
            return 2

    queries = read_fasta(args.queries)
    single = read_fasta(args.single)
    multi = read_fasta(args.multi)

    single_width = len(next(iter(single.values())))
    multi_width = len(next(iter(multi.values())))

    print(f"single reference : {single_width} columns, {len(single)} records")
    print(f"multi  reference : {multi_width} columns, {len(multi)} records")
    print(f"insertion        : {INSERTION} ({len(INSERTION)} bp)")
    print()
    print(f"{'query':<20}{'input':>7}{'single':>8}{'diff':>6}{'n':>3}"
          f"{'multi':>8}{'diff':>6}{'n':>3}   verdict")
    print("-" * 76)

    failures = []
    for name, seq in queries.items():
        truth_len = len(seq.replace("-", ""))
        truth_n = seq.replace("-", "").count(INSERTION)

        if name not in single or name not in multi:
            failures.append(f"{name}: missing from an output")
            continue

        s_seq = single[name].replace("-", "")
        m_seq = multi[name].replace("-", "")
        s_n = s_seq.count(INSERTION)
        m_n = m_seq.count(INSERTION)

        verdict = "OK" if (s_n < truth_n and m_n == truth_n) else "FAIL"
        print(f"{name:<20}{truth_len:>7}{len(s_seq):>8}{len(s_seq) - truth_len:>+6}"
              f"{s_n:>3}{len(m_seq):>8}{len(m_seq) - truth_len:>+6}{m_n:>3}   {verdict}")

        if s_n >= truth_n:
            failures.append(f"{name}: single reference kept the insertion "
                            f"({s_n} occurrences, input had {truth_n})")
        if m_n != truth_n:
            failures.append(f"{name}: multi-reference lost the insertion "
                            f"({m_n} occurrences, input had {truth_n})")

    print()
    if failures:
        for f in failures:
            print(f"FAIL  {f}", file=sys.stderr)
        return 1

    print(f"PASS  {len(queries)}/{len(queries)} queries: the single reference dropped "
          f"the {len(INSERTION)} bp insertion, the panel kept it.")
    print(f"      alignment width {single_width} (single) vs {multi_width} (panel)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
