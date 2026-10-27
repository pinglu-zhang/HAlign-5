#!/usr/bin/env python3
"""Extract the real-insertion demo data from the HAlign-4 insertion experiment.

Source (not shipped with the repository, ~1.8 GB):
    result-new/data/insertion/
        lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta

That file is a multi-reference alignment produced for the paper's insertion
analysis: 63,380 rows over 29,997 columns, with the Wuhan reference occupying
29,903 bases. Its insertion hotspot `between_ref_21608_21609` carries a 12 bp
insertion, TCATGCCGCTGT, in 631 Pango lineages (see
`insertion/results/*.lineage_reference_insertions.tsv`).

This script selects:

  refs.aligned.fasta   Wuhan + two lineages that carry the insertion, all
                       29,997 columns (a valid pre-aligned panel for `-a`)
  wuhan.fasta          Wuhan ungapped (29,903) for the single-reference run
  queries.fasta        five real isolates from lineages that carry the
                       insertion, named by lineage only

Every emitted query really does carry the insertion: selection is by inspecting
the alignment columns, not by trusting the lineage label. Within one lineage
only some isolates carry the 12 bp (e.g. PQ.2: 5,542 of 7,788), so a name-based
pick would produce a demo where some queries silently lack the insertion.

Usage:
    python3 make_data.py --source /path/to/lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Insertion hotspot `between_ref_21608_21609`: 0-based half-open slice of the
# 12 insertion columns in the 29,997-column alignment.
INS_START = 21611
INS_END = 21623
INSERTION = "TCATGCCGCTGT"
LEFT_FLANK = "TAGTCAGTGTG"
RIGHT_FLANK = "TTAATCT"

PANEL_LINEAGES = ("PQ.2", "XFG.3.4.1")
QUERY_LINEAGES = ("PQ.4", "XFG.5.1", "XFG.1.1", "PQ.1", "XFG.3.1")
MAX_QUERIES = 5

OUT_DIR = Path(__file__).resolve().parent


def read_fasta(path: Path):
    """Yield (header, sequence) for each record; sequence may contain gaps."""
    name, buf = None, []
    with path.open() as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(buf)
                name, buf = line[1:], []
            elif line:
                buf.append(line)
    if name is not None:
        yield name, "".join(buf)


def lineage_of(header: str) -> str | None:
    if "|lineage=" not in header:
        return None
    return header.split("|lineage=", 1)[1].split("|", 1)[0]


def carries_insertion(seq: str) -> bool:
    """True when this row carries the *full* 12 bp insertion at the hotspot.

    Within one lineage only a fraction of isolates carry all 12 bp; the rest have
    a single T or a run of Ns at the same site. Requiring the complete motif keeps
    the demo honest: every emitted query really has the full insertion.
    """
    return seq[INS_START:INS_END].replace("-", "") == INSERTION


def write_fasta(path: Path, records) -> None:
    with path.open("w") as handle:
        for name, seq in records:
            handle.write(f">{name}\n")
            for i in range(0, len(seq), 70):
                handle.write(seq[i:i + 70] + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, type=Path,
                    help="lineage-period.*.halign4-multi.fasta from the insertion experiment")
    args = ap.parse_args()

    src = args.source.expanduser()
    if not src.is_file():
        print(f"ERROR: source alignment not found: {src}", file=sys.stderr)
        print("  Expected the HAlign-4 insertion experiment alignment (~1.8 GB),",
              file=sys.stderr)
        print("  e.g. result-new/data/insertion/"
              "lineage-period.2025Q1-Q4_2026Q1.halign4-multi.fasta",
              file=sys.stderr)
        return 2

    wuhan = None
    panel: dict[str, str] = {}
    queries: list[tuple[str, str]] = []
    width = None

    for header, seq in read_fasta(src):
        if width is None:
            width = len(seq)
        elif len(seq) != width:
            if len(seq) != 29997:      # tolerate a final truncated record
                raise SystemExit(f"unexpected record width {len(seq)} in {src}")

        if header.lower().startswith("nc_045512.2"):
            if wuhan is None:
                wuhan = seq
            continue

        lineage = lineage_of(header)
        if lineage is None or not carries_insertion(seq):
            continue

        if lineage in PANEL_LINEAGES and lineage not in panel:
            panel[lineage] = seq
            continue

        if lineage in QUERY_LINEAGES and len(queries) < MAX_QUERIES:
            queries.append((lineage, seq))

        if wuhan and len(panel) == len(PANEL_LINEAGES) and len(queries) >= MAX_QUERIES:
            break

    problems = []
    if wuhan is None:
        problems.append("Wuhan reference (NC_045512.2) not found")
    missing_panel = [l for l in PANEL_LINEAGES if l not in panel]
    if missing_panel:
        problems.append(f"panel lineages without an insertion-carrying record: {missing_panel}")
    if len(queries) < MAX_QUERIES:
        problems.append(f"only {len(queries)} insertion-carrying queries found "
                        f"(wanted {MAX_QUERIES}) from {QUERY_LINEAGES}")
    if problems:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        return 2

    # ---- write outputs -----------------------------------------------------
    write_fasta(OUT_DIR / "refs.aligned.fasta",
                [("NC_045512.2", wuhan)] + [(k, v) for k, v in panel.items()])
    write_fasta(OUT_DIR / "wuhan.fasta", [("NC_045512.2", wuhan.replace("-", ""))])

    seen: dict[str, int] = {}
    named = []
    for lineage, seq in queries:
        seen[lineage] = seen.get(lineage, 0) + 1
        named.append((f"{lineage}_isolate{seen[lineage]}", seq))
    write_fasta(OUT_DIR / "queries.fasta", named)

    # ---- assertions --------------------------------------------------------
    panel_width = len(wuhan)
    if not all(len(v) == panel_width for v in panel.values()):
        raise SystemExit("panel rows are not all the same length (not a valid MSA)")
    # The reference must be gap-only at the hotspot. Checking the columns (not a
    # substring search) matters: the 12 bp motif also occurs once elsewhere in
    # the genome, so `INSERTION in wuhan` would be true for unrelated reasons.
    if wuhan[INS_START:INS_END].replace("-", ""):
        raise SystemExit(
            f"reference has bases in hotspot columns {INS_START}-{INS_END - 1}: "
            f"{wuhan[INS_START:INS_END]!r} (expected all gaps)")

    print(f"source        : {src}")
    print(f"panel width   : {panel_width}")
    print(f"Wuhan ungapped: {len(wuhan.replace('-', ''))}")
    print(f"hotspot       : columns {INS_START}-{INS_END - 1} ({INSERTION}, {len(INSERTION)} bp)")
    print()
    for name, seq in named:
        assert carries_insertion(seq), f"{name} lost the insertion during extraction"
        print(f"  {name:<20} ungapped={len(seq.replace('-', '')):>6} "
              f"hotspot={seq[INS_START:INS_END]}")
    print()
    print(f"wrote: refs.aligned.fasta (1 + {len(panel)} refs), wuhan.fasta, "
          f"queries.fasta ({len(named)} queries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
