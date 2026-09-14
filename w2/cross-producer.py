"""Do the methodology's own queries still answer over converter-produced RDF?

The coverage assessment builds its witnesses with the vocabulary repository's
own materializer (`scripts/vcf_examples.py`, reached through
`from vcf_examples import materialize` in assess.py). VCF-RDFizer is a separate
program. Both target VCF Core, but nothing has checked that a query and expected
answer written against one also holds over the other.

This replays each case's query and independently authored expected answer over
both producers' graphs and reports where they agree. It does not re-derive any
expected answer: the oracle is the one already reviewed and accepted in
coverage/methodology/inputs/cases.json.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import rdflib
from rdflib import Graph

# The vocabulary checkout supplies the fixtures, queries and reviewed expected
# answers. Override with VCF_CORE_VOCAB when it is not beside this repository.
VOCAB = Path(os.environ.get(
    "VCF_CORE_VOCAB",
    Path(__file__).resolve().parent.parent.parent / "vcf-rdfizer-vocabulary"))
if not (VOCAB / "coverage/methodology/inputs/cases.json").exists():
    raise SystemExit(
        f"no vocabulary checkout at {VOCAB}; set VCF_CORE_VOCAB to one")
METHOD = VOCAB / "coverage/methodology"
PROFILES = ("expanded", "condensed")

# assess.py's rule: a structural query may not decode a compound literal.
DECODERS = re.compile(r"\b(REPLACE|SUBSTR|STRBEFORE|STRAFTER)\s*\(", re.I)


def encoded(row):
    return json.dumps(row)


def answers(graph: Graph, query: str):
    return sorted(
        [[str(v) if v is not None else None for v in row] for row in graph.query(query)],
        key=encoded,
    )


def normalize(rows):
    """Compare answer *values*, not the IRIs the two producers happen to mint.

    Both producers use a file:// base, but they name intermediate resources
    differently (#call/1/... versus #record/1/...). A query that projects an
    IRI would otherwise disagree for a reason that carries no meaning. Literal
    answers -- which is what every expected answer in cases.json is made of --
    are compared verbatim.
    """
    def strip(v):
        if v is None:
            return None
        # Both producers mint fragment IRIs, under different bases:
        # file://basic-v4.1.vcf#call/1 versus urn:vcf-coverage:basic-v4.1:expanded#call/1.
        # Keep the fragment, which is the part that carries meaning.
        if "#" in v and re.match(r"^(file://|urn:|https?://)", v):
            return "#" + v.split("#", 1)[1]
        return v

    return sorted([[strip(v) for v in row] for row in rows], key=encoded)


def load(path: Path) -> Graph | None:
    """Read one witness. The converter always gzips its N-Triples output."""
    g = Graph()
    if path.is_file():
        g.parse(str(path), format="nt")
        return g
    packed = path.with_suffix(path.suffix + ".gz")
    if packed.is_file():
        import gzip

        with gzip.open(packed, "rt", encoding="utf-8") as handle:
            g.parse(handle, format="nt")
        return g
    return None


def main() -> int:
    converted_root = Path(sys.argv[1])
    cases = json.loads((METHOD / "inputs/cases.json").read_text())
    subset = sorted({p.stem for p in (converted_root / "in").glob("*.vcf")})
    graphs: dict[tuple[str, str], Graph | None] = {}

    def graph_for(producer: str, stem: str, profile: str):
        key = (producer, f"{stem}-{profile}")
        if key not in graphs:
            if producer == "repo":
                path = METHOD / f"generated/witnesses/{stem}-{profile}.nt"
            else:
                path = converted_root / profile / stem / f"{stem}.nt"
            graphs[key] = load(path)
        return graphs[key]

    results = []
    for case in cases:
        stem = Path(case["fixture"]).stem
        if stem not in subset:
            continue
        for axis in ("preservation", "structure"):
            spec = case.get(axis)
            if not spec:
                continue
            for profile in PROFILES:
                entry = spec.get("both") or spec.get(profile)
                if not entry:
                    continue
                query = (METHOD / entry["query"]).read_text()
                if axis == "structure" and DECODERS.search(query):
                    continue
                expected = normalize(entry["expected"])
                row = {
                    "case": case["id"], "requirement": case["requirement"],
                    "version": case["version"], "fixture": stem,
                    "axis": axis, "profile": profile,
                    "query": entry["query"],
                }
                for producer in ("repo", "converter"):
                    g = graph_for(producer, stem, profile)
                    if g is None:
                        row[producer] = "no-witness"
                        continue
                    try:
                        got = normalize(answers(g, query))
                    except Exception as error:  # a query the graph cannot answer
                        row[producer] = "query-error"
                        row.setdefault("errors", {})[producer] = str(error)[:200]
                        continue
                    row[producer] = "pass" if got == expected else "fail"
                    if row[producer] == "fail" and producer == "converter":
                        row["converterAnswer"] = got[:4]
                        row["expectedAnswer"] = expected[:4]
                results.append(row)

    agree = sum(1 for r in results if r["repo"] == r["converter"])
    both_pass = sum(1 for r in results if r["repo"] == r["converter"] == "pass")
    repo_only = sorted(
        {r["requirement"] for r in results if r["repo"] == "pass" and r["converter"] != "pass"}
    )
    converter_only = sorted(
        {r["requirement"] for r in results if r["converter"] == "pass" and r["repo"] != "pass"}
    )
    summary = {
        "fixtures": subset,
        "checks": len(results),
        "agree": agree,
        "bothPass": both_pass,
        "repoPassConverterNot": repo_only,
        "converterPassRepoNot": converter_only,
        "byOutcome": {},
    }
    for r in results:
        key = f"{r['repo']}/{r['converter']}"
        summary["byOutcome"][key] = summary["byOutcome"].get(key, 0) + 1

    # A second positional argument names the output file, so one run cannot
    # overwrite another's results.
    name = sys.argv[2] if len(sys.argv) > 2 else "cross-producer.json"
    out = Path(os.environ.get("RESULTS_DIR", Path(__file__).parent / "generated"))
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_text(
        json.dumps({"summary": summary, "results": results}, indent=1, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
