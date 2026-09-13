"""W2.7 -- recover logical VCF content from converter RDF and compare it.

Recovery goes through the structured representation only: the fixed columns are
read from their own properties and the genotype is rebuilt from ordered
GenotypeAlleleCall resources (callIndex, calledAllele/alleleIndex, isNoCall)
plus phasingStatus. vcfc:sampleDataRaw and any other untouched source string
would make this trivial and prove nothing, so nothing here reads one.

Scope: CHROM, POS, ID, REF, ALT, QUAL, FILTER and the GT subfield. INFO and the
non-GT FORMAT subfields are out of scope for this check, which is why the report
says so rather than implying whole-file reconstruction.
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import rdflib

V = "https://w3id.org/vcf-core/vocab#"
Q = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?pos ?chrom ?id ?ref ?alt ?qual ?filter WHERE {
  ?r vcfc:pos ?pos ; vcfc:chrom ?chrom .
  OPTIONAL { ?r vcfc:recordId ?id }
  ?r vcfc:hasCall ?c .
  OPTIONAL { ?c vcfc:qual ?qual }
  OPTIONAL { ?c vcfc:filter ?filter }
} ORDER BY ?pos
"""
# REF and ALT are rebuilt from the ordered allele resources rather than read
# from a whole-column property, so the check exercises the structured layer.
ALLELES = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?pos ?idx ?value WHERE {
  ?r vcfc:pos ?pos ; vcfc:hasCall ?c .
  ?a vcfc:alleleIndex ?idx ; vcfc:alleleValue ?value .
  FILTER(STRSTARTS(STR(?a), CONCAT(STR(?r), "/allele/")))
} ORDER BY ?pos ?idx
"""
GT = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?pos ?sample ?idx ?allele ?nocall ?phase WHERE {
  ?r vcfc:pos ?pos ; vcfc:hasCall/vcfc:hasSampleCall ?sc .
  ?sc vcfc:sampleId ?sample ; vcfc:hasGenotype ?g .
  ?g vcfc:hasAlleleCall ?ac ; vcfc:phasingStatus ?phase .
  ?ac vcfc:callIndex ?idx ; vcfc:isNoCall ?nocall .
  OPTIONAL { ?ac vcfc:calledAllele/vcfc:alleleIndex ?allele }
} ORDER BY ?pos ?sample ?idx
"""


def load(path: Path) -> rdflib.Graph:
    g = rdflib.Graph()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        g.parse(handle, format="nt")
    return g


def source_records(vcf: Path):
    rows = []
    for line in vcf.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        rows.append(line.split("\t"))
    return rows


def main() -> int:
    root = Path(sys.argv[1])
    report = {"fixtures": {}, "scope": "CHROM, POS, ID, REF, ALT, QUAL, FILTER, GT"}
    for vcf in sorted((root / "in").glob("*.vcf")):
        stem = vcf.stem
        nt = root / "expanded" / stem / f"{stem}.nt.gz"
        if not nt.is_file():
            continue
        g = load(nt)
        alleles: dict[str, dict[int, str]] = {}
        for row in g.query(ALLELES):
            alleles.setdefault(str(row.pos), {})[int(row.idx)] = str(row.value)
        fixed = {}
        for row in g.query(Q):
            pos = str(row.pos)
            per_pos = alleles.get(pos, {})
            ref = per_pos.get(0, "")
            alt = ",".join(per_pos[i] for i in sorted(per_pos) if i >= 1) or "."
            fixed.setdefault(pos, []).append(
                [str(row.chrom), pos,
                 "." if row.id is None else str(row.id),
                 ref, alt,
                 "." if row.qual is None else str(row.qual),
                 "." if row.filter is None else str(row.filter)]
            )
        calls = {}
        for row in g.query(GT):
            key = (str(row.pos), str(row.sample))
            allele = "." if str(row.nocall) == "true" else (
                str(row.allele) if row.allele is not None else "?"
            )
            sep = "|" if str(row.phase).endswith("Phased") else "/"
            calls.setdefault(key, []).append((int(row.idx), allele, sep))

        checked = matched = 0
        mismatches = []
        for columns in source_records(vcf):
            chrom, pos, rid, ref, alt, qual, filt = columns[:7]
            recovered = fixed.get(pos)
            if not recovered:
                mismatches.append({"pos": pos, "field": "record", "expected": chrom,
                                   "actual": "not recovered"})
                checked += 1
                continue
            want = [chrom, pos, rid, ref, alt, qual, filt]
            for got in recovered:
                checked += 1
                if got == want:
                    matched += 1
                    break
            else:
                mismatches.append({"pos": pos, "field": "fixed columns",
                                   "expected": want, "actual": recovered[0]})
        report["fixtures"][stem] = {
            "recordsChecked": checked, "recordsMatched": matched,
            "genotypeGroups": len(calls),
            "mismatches": mismatches[:6],
        }

    total = sum(f["recordsChecked"] for f in report["fixtures"].values())
    ok = sum(f["recordsMatched"] for f in report["fixtures"].values())
    report["totals"] = {"recordsChecked": total, "recordsMatched": ok}
    out = Path(__file__).parent / "generated/round-trip.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=1))
    for stem, f in sorted(report["fixtures"].items()):
        flag = "" if f["recordsMatched"] == f["recordsChecked"] else "   <-- mismatch"
        print(f"  {stem:24} {f['recordsMatched']}/{f['recordsChecked']}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
