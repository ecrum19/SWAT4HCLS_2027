#!/usr/bin/env python3
"""Recover everything round-trip.py leaves out, and compare it with the source.

round-trip.py covers the fixed columns and the genotype. This covers the rest of
the file: every header line, every INFO entry, and every non-GT FORMAT subfield.

Recovery is structural. A multi-valued field is rebuilt from its ordered value
items (valueIndex + itemValue) and joined with commas; a flag is recognised by
fieldValueBoolean with no lexical value; anything else uses the field's own
fieldValue. vcfc:infoRaw and vcfc:sampleDataRaw hold whole source columns and are
never read -- using them would make this trivial and prove nothing.

    python3 field-round-trip.py <converted root>

Writes field-round-trip.json to RESULTS_DIR.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from pathlib import Path

import rdflib

# One row per (record, field). ?owner distinguishes an INFO entry, which hangs off
# the call, from a FORMAT value, which hangs off a sample call.
INFO = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?pos ?key ?value ?flag ?item ?itemIndex WHERE {
  ?r vcfc:pos ?pos ; vcfc:hasCall ?c .
  ?c vcfc:hasInfoValue ?f .
  ?f vcfc:declaredBy/vcfc:fieldId ?key .
  OPTIONAL { ?f vcfc:fieldValue ?value }
  OPTIONAL { ?f vcfc:fieldValueBoolean ?flag }
  OPTIONAL { ?f vcfc:hasValueItem ?vi . ?vi vcfc:valueIndex ?itemIndex ; vcfc:itemValue ?item }
}
"""

# Header lines carry their key, their verbatim right-hand side, and their source
# position, so a header round-trip is a line-for-line comparison in order.
HEADERS = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?lineIndex ?key ?value WHERE {
  ?h a vcfc:VCFHeader ; vcfc:hasHeaderLine ?l .
  ?l vcfc:lineIndex ?lineIndex ; vcfc:headerKey ?key .
  OPTIONAL { ?l vcfc:headerValue ?value }
} ORDER BY ?lineIndex
"""

FORMAT = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?pos ?sample ?key ?value ?item ?itemIndex WHERE {
  ?r vcfc:pos ?pos ; vcfc:hasCall/vcfc:hasSampleCall ?sc .
  ?sc vcfc:sampleId ?sample ; vcfc:hasFormatValue ?f .
  ?f vcfc:declaredBy/vcfc:fieldId ?key .
  OPTIONAL { ?f vcfc:fieldValue ?value }
  OPTIONAL { ?f vcfc:hasValueItem ?vi . ?vi vcfc:valueIndex ?itemIndex ; vcfc:itemValue ?item }
}
"""


def load(path: Path) -> rdflib.Graph:
    g = rdflib.Graph()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        g.parse(handle, format="nt")
    return g


def collect(graph, query, key_fields):
    """Group result rows into {key: {'value':…, 'flag':…, 'items':{index: value}}}."""
    out: dict[tuple, dict] = {}
    for row in graph.query(query):
        key = tuple(str(getattr(row, f)) for f in key_fields)
        entry = out.setdefault(key, {"value": None, "flag": None, "items": {}})
        if row.value is not None:
            entry["value"] = str(row.value)
        if getattr(row, "flag", None) is not None:
            entry["flag"] = str(row.flag)
        # NB: row.index would resolve to tuple.index, not the SPARQL variable.
        if row.item is not None and row.itemIndex is not None:
            entry["items"][int(row.itemIndex)] = str(row.item)
    return out


def rebuild(entry):
    """The source form of one field value, from the structured layer only."""
    if entry is None:
        return None
    if entry["items"]:
        return ",".join(entry["items"][i] for i in sorted(entry["items"]))
    if entry["value"] is not None:
        return entry["value"]
    if entry["flag"] is not None:          # an INFO flag has no lexical value
        return "<flag>"
    return None


def source_headers(vcf: Path):
    """[(index, key, value)] for each ## line, in file order."""
    out = []
    # lineIndex in the graph is the file's own 1-based line number.
    for i, line in enumerate(vcf.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("##"):
            continue
        key, sep, value = line[2:].partition("=")
        out.append((i, key, value if sep else None))
    return out


def source_fields(vcf: Path):
    """[(pos, {info key: value}, {sample: {format key: value}})] from the file."""
    samples, rows = [], []
    for line in vcf.read_text(encoding="utf-8").splitlines():
        if line.startswith("#CHROM"):
            samples = line.split("\t")[9:]
            continue
        if line.startswith("#") or not line.strip():
            continue
        c = line.split("\t")
        info = {}
        if len(c) > 7 and c[7] not in (".", ""):
            for entry in c[7].split(";"):
                if not entry:
                    continue
                k, sep, v = entry.partition("=")
                info[k] = v if sep else "<flag>"
        fmt = {}
        if len(c) > 8 and samples:
            keys = c[8].split(":")
            for name, cell in zip(samples, c[9:]):
                if cell == ".":
                    continue
                fmt[name] = {k: v for k, v in zip(keys, cell.split(":")) if k != "GT"}
        rows.append((c[1], info, fmt))
    return rows


def main() -> int:
    root = Path(sys.argv[1])
    report = {
        "fixtures": {},
        "scope": "every header line, every INFO entry and every non-GT FORMAT subfield",
        "method": "Rebuilt from ordered value items where present, otherwise the "
                  "field's own value. infoRaw and sampleDataRaw are never read.",
    }
    for vcf in sorted((root / "in").glob("*.vcf")):
        stem = vcf.stem
        nt = root / "expanded" / stem / f"{stem}.nt.gz"
        if not nt.is_file():
            continue
        g = load(nt)
        info_graph = collect(g, INFO, ("pos", "key"))
        fmt_graph = collect(g, FORMAT, ("pos", "sample", "key"))

        # --- header lines -------------------------------------------------
        recovered_headers = {}
        for row in g.query(HEADERS):
            recovered_headers[int(row.lineIndex)] = (
                str(row.key), None if row.value is None else str(row.value))
        h_checked = h_matched = 0
        mismatches = []
        for index, key, value in source_headers(vcf):
            h_checked += 1
            got = recovered_headers.get(index)
            if got == (key, value):
                h_matched += 1
            else:
                mismatches.append({"line": index, "field": f"##{key}",
                                   "expected": value, "actual": (got or ("not recovered",))[-1]})

        # --- INFO and FORMAT values ----------------------------------------
        checked = matched = 0
        for pos, info, fmt in source_fields(vcf):
            for key, want in info.items():
                checked += 1
                got = rebuild(info_graph.get((pos, key)))
                if got == want:
                    matched += 1
                else:
                    mismatches.append({"pos": pos, "field": f"INFO/{key}",
                                       "expected": want, "actual": got or "not recovered"})
            for sample, fields in fmt.items():
                for key, want in fields.items():
                    checked += 1
                    got = rebuild(fmt_graph.get((pos, sample, key)))
                    if got == want:
                        matched += 1
                    else:
                        mismatches.append({"pos": pos, "field": f"FORMAT/{key}[{sample}]",
                                           "expected": want, "actual": got or "not recovered"})
        report["fixtures"][stem] = {
            "headerLinesChecked": h_checked, "headerLinesMatched": h_matched,
            "checked": checked, "matched": matched,
            "mismatches": mismatches[:8]}

    total = sum(f["checked"] for f in report["fixtures"].values())
    ok = sum(f["matched"] for f in report["fixtures"].values())
    h_total = sum(f["headerLinesChecked"] for f in report["fixtures"].values())
    h_ok = sum(f["headerLinesMatched"] for f in report["fixtures"].values())
    report["totals"] = {"checked": total, "matched": ok,
                        "headerLinesChecked": h_total, "headerLinesMatched": h_ok}

    out_dir = Path(os.environ.get("RESULTS_DIR", Path.cwd()))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "field-round-trip.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=1))
    for stem, f in sorted(report["fixtures"].items()):
        clean = (f["matched"] == f["checked"]
                 and f["headerLinesMatched"] == f["headerLinesChecked"])
        print(f"  {stem:24} headers {f['headerLinesMatched']}/{f['headerLinesChecked']}"
              f"   fields {f['matched']}/{f['checked']}"
              f"{'' if clean else '   <-- mismatch'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
