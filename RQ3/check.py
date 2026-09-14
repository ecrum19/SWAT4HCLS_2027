"""Run the integration query and compare it with the authored answers.

Compares identities, values and provenance, not row counts: a count match with
the wrong allele attached is exactly the failure this example exists to detect.
Also asserts that each excluded alteration really is absent, since two of them
are excluded only when Number=LR is resolved through the sample's local allele
set.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from pathlib import Path

import rdflib

HERE = Path(__file__).parent
INPUTS = HERE / "inputs"


def load_graph(rdf_path: Path, annotations: Path) -> rdflib.Graph:
    g = rdflib.Graph()
    opener = gzip.open if rdf_path.name.endswith(".gz") else open
    with opener(rdf_path, "rt", encoding="utf-8") as handle:
        g.parse(handle, format="nt")
    g.parse(str(annotations), format="turtle")
    return g


def main() -> int:
    rdf_path = Path(sys.argv[1])
    graph = load_graph(rdf_path, INPUTS / "annotations.ttl")
    query = (INPUTS / "local-allele-evidence.rq").read_text(encoding="utf-8")
    expected = json.loads((INPUTS / "expected.json").read_text(encoding="utf-8"))

    observed = []
    for row in graph.query(query):
        observed.append({
            "contig": str(row.contig), "position": int(row.position),
            "ref": str(row.ref), "alt": str(row.alt), "depth": str(row.depth),
            "sample": str(row.sample), "fieldId": str(row.fieldId),
            "number": str(row.number), "file": str(row.file),
        })
    observed.sort(key=lambda r: (r["position"], r["alt"]))

    fields = ("contig", "position", "ref", "alt", "depth", "sample", "fieldId", "number")
    want = [{k: r[k] for k in fields} for r in expected["expectedRows"]]
    got = [{k: r[k] for k in fields} for r in observed]

    problems = []
    if got != want:
        problems.append("rows differ")
    # Each excluded alteration must be absent, by identity not by count.
    for row in expected["excludedRows"]:
        hit = [r for r in observed
               if r["position"] == row["position"] and r["alt"] == row["alt"]]
        if hit:
            problems.append(
                f"excluded {row['contig']}:{row['position']} {row['ref']}>{row['alt']} "
                f"was returned with depth {hit[0]['depth']}"
            )
    # Provenance has to be recoverable, not merely present.
    for r in observed:
        if not r["file"].startswith("file://"):
            problems.append(f"row {r['position']} {r['alt']} has no source file")

    report = {
        "status": "PASS" if not problems else "FAIL",
        "rdf": str(rdf_path),
        "expectedRows": want,
        "observedRows": got,
        "provenance": [{"alt": r["alt"], "file": r["file"], "sample": r["sample"],
                        "declaredAs": f'{r["fieldId"]} Number={r["number"]}'}
                       for r in observed],
        "excludedConfirmed": [
            f'{r["contig"]}:{r["position"]} {r["ref"]}>{r["alt"]}'
            for r in expected["excludedRows"]
        ],
        "problems": problems,
    }
    out = Path(os.environ.get("RESULTS_DIR", Path.cwd()))
    out.mkdir(exist_ok=True)
    (out / "integration.json").write_text(json.dumps(report, indent=1) + "\n")

    print(f"Integration check: {report['status']}")
    print(f"  expected {len(want)} rows, observed {len(got)}")
    for r in got:
        print(f"    {r['contig']}:{r['position']} {r['ref']}>{r['alt']}  depth={r['depth']}"
              f"  sample={r['sample']}  via {r['fieldId']} Number={r['number']}")
    print(f"  excluded confirmed absent: {len(expected['excludedRows'])}")
    for p in problems:
        print(f"  PROBLEM: {p}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
