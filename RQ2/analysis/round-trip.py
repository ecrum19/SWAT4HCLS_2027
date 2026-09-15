"""Recover logical VCF content from converter RDF and compare it with the source.

Recovery goes through the structured representation only. The fixed columns are
read from their own properties, REF and ALT are rebuilt from ordered allele
resources, and each sample genotype is rebuilt from ordered GenotypeAlleleCall
resources (callIndex, calledAllele/alleleIndex, isNoCall, phaseIndicator).
vcfc:sampleDataRaw and vcfc:genotypeString are untouched source strings that
would make this trivial and prove nothing, so nothing here reads either.

Scope: CHROM, POS, ID, REF, ALT, QUAL, FILTER, and the GT subfield of every
sample column. INFO and the non-GT FORMAT subfields are out of scope, which the
report states rather than implying whole-file reconstruction.

One deliberate normalisation, and the reason for it. VCF 4.4 onwards allows a
genotype to be written with a leading phase indicator: "|0|1" and "0|1" describe
the same phasing. The vocabulary records that distinction as lexical, not
semantic -- vcfc:phaseIndicator carries "the effective first indicator when
omitted in the source", and only genotypeString preserves whether it was written
out. Reproducing the leading character would therefore require reading the raw
string this check exists to avoid. So the comparison is against the source
genotype with any leading indicator removed, and a genotype that differs only by
that character counts as recovered. Everything else -- allele order, missing
calls, ploidy, and the phased/unphased indicator between every pair -- must match
exactly.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from pathlib import Path

import rdflib

V = "https://w3id.org/vcf-core/vocab#"
Q = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?r ?pos ?chrom ?id ?ref ?alt ?qual ?filter WHERE {
  ?r vcfc:pos ?pos ; vcfc:chrom ?chrom .
  OPTIONAL { ?r vcfc:recordId ?id }
  ?r vcfc:hasCall ?c .
  OPTIONAL { ?c vcfc:qual ?qual }
  OPTIONAL { ?c vcfc:filter ?filter }
} ORDER BY ?pos
"""
# REF and ALT are rebuilt from the ordered allele resources rather than read
# from a whole-column property, so the check exercises the structured layer.
# The record reaches its alleles through hasReferenceAllele and hasAltAllele --
# declared relationships -- rather than by matching the shape of their IRIs.
ALLELES = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?r ?pos ?idx ?value WHERE {
  ?r vcfc:pos ?pos .
  { ?r vcfc:hasReferenceAllele ?a } UNION { ?r vcfc:hasAltAllele ?a }
  ?a vcfc:alleleIndex ?idx ; vcfc:alleleValue ?value .
} ORDER BY ?pos ?idx
"""
# The separator before allele i is that call's own phaseIndicator, which is what
# lets a mixed genotype such as 0|1/2 be rebuilt. phasingStatus is the fallback
# for a producer that does not emit per-call indicators.
GT = """
PREFIX vcfc: <https://w3id.org/vcf-core/vocab#>
SELECT ?r ?pos ?sample ?idx ?allele ?nocall ?phase ?indicator WHERE {
  ?r vcfc:pos ?pos ; vcfc:hasCall/vcfc:hasSampleCall ?sc .
  ?sc vcfc:sampleId ?sample ; vcfc:hasGenotype ?g .
  ?g vcfc:hasAlleleCall ?ac ; vcfc:phasingStatus ?phase .
  ?ac vcfc:callIndex ?idx ; vcfc:isNoCall ?nocall .
  OPTIONAL { ?ac vcfc:calledAllele/vcfc:alleleIndex ?allele }
  OPTIONAL { ?ac vcfc:phaseIndicator ?indicator }
} ORDER BY ?pos ?sample ?idx
"""


def effective(gt: str) -> str:
    """The source genotype without a leading phase indicator. See the module docstring."""
    return gt[1:] if gt[:1] in ("|", "/") else gt


def rebuild(calls) -> str:
    """One genotype, from ordered allele calls. calls: [(idx, allele, indicator)]."""
    parts = []
    for position, (_, allele, indicator) in enumerate(sorted(calls)):
        if position:
            parts.append(indicator)
        parts.append(allele)
    return "".join(parts)


def load(path: Path) -> rdflib.Graph:
    g = rdflib.Graph()
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        g.parse(handle, format="nt")
    return g


def source_records(vcf: Path):
    """Data lines, plus the sample names from the #CHROM header line."""
    rows, samples = [], []
    for line in vcf.read_text(encoding="utf-8").splitlines():
        if line.startswith("#CHROM"):
            samples = line.split("\t")[9:]
            continue
        if line.startswith("#") or not line.strip():
            continue
        rows.append(line.split("\t"))
    return rows, samples


def source_genotypes(columns, samples):
    """{sample: effective GT} for one data line, empty when the line declares no GT."""
    if len(columns) < 10 or not samples:
        return {}
    keys = columns[8].split(":")
    if "GT" not in keys:
        return {}
    slot = keys.index("GT")
    out = {}
    for name, cell in zip(samples, columns[9:]):
        # A trailing FORMAT field may be dropped; a cell of "." drops all of them.
        fields = cell.split(":")
        if cell == "." or slot >= len(fields):
            continue
        out[name] = effective(fields[slot])
    return out


def main() -> int:
    root = Path(sys.argv[1])
    report = {
        "fixtures": {},
        "scope": "CHROM, POS, ID, REF, ALT, QUAL, FILTER, and the GT subfield of every sample",
        "notInScope": "INFO and the non-GT FORMAT subfields",
        "normalisation": "A leading phase indicator is removed from the source genotype "
                         "before comparison: it is lexical, and only genotypeString -- an "
                         "untouched source string this check does not read -- records "
                         "whether it was written out.",
    }
    for vcf in sorted((root / "in").glob("*.vcf")):
        stem = vcf.stem
        nt = root / "expanded" / stem / f"{stem}.nt.gz"
        if not nt.is_file():
            continue
        g = load(nt)
        alleles: dict[str, dict[int, str]] = {}
        for row in g.query(ALLELES):
            alleles.setdefault(str(row.r), {})[int(row.idx)] = str(row.value)
        fixed = {}
        for row in g.query(Q):
            pos = str(row.pos)
            per_record = alleles.get(str(row.r), {})
            ref = per_record.get(0, "")
            alt = ",".join(per_record[i] for i in sorted(per_record) if i >= 1) or "."
            fixed.setdefault(pos, []).append(
                (str(row.r),
                 [str(row.chrom), pos,
                 "." if row.id is None else str(row.id),
                 ref, alt,
                 "." if row.qual is None else str(row.qual),
                 "." if row.filter is None else str(row.filter)])
            )
        calls = {}
        for row in g.query(GT):
            # Keyed by record identity, not position: a fixture may write the
            # same site twice, and those records have different genotypes.
            key = (str(row.r), str(row.sample))
            allele = "." if str(row.nocall) == "true" else (
                str(row.allele) if row.allele is not None else "?"
            )
            if row.indicator is not None:
                sep = str(row.indicator)
            else:  # producer emits no per-call indicator; fall back to the status
                sep = "|" if str(row.phase) == V + "Phased" else "/"
            calls.setdefault(key, []).append((int(row.idx), allele, sep))

        checked = matched = 0
        gt_checked = gt_matched = 0
        mismatches = []
        records, samples = source_records(vcf)
        claimed: set[str] = set()
        for columns in records:
            chrom, pos, rid, ref, alt, qual, filt = columns[:7]
            recovered = fixed.get(pos)
            if not recovered:
                mismatches.append({"pos": pos, "field": "record", "expected": chrom,
                                   "actual": "not recovered"})
                checked += 1
                continue
            want = [chrom, pos, rid, ref, alt, qual, filt]
            # Pair this source line with the graph record that carries the same
            # columns, so its genotypes are read from that record and not from a
            # different one at the same position. Each graph record is claimed
            # once.
            record_iri = None
            checked += 1
            for candidate_iri, got in recovered:
                if candidate_iri in claimed:
                    continue
                if got == want:
                    record_iri = candidate_iri
                    claimed.add(candidate_iri)
                    matched += 1
                    break
            if record_iri is None:
                mismatches.append({"pos": pos, "field": "fixed columns",
                                   "expected": want, "actual": recovered[0][1]})

            # Every sample genotype the source declares must be rebuilt from the
            # ordered allele calls alone.
            for name, want_gt in source_genotypes(columns, samples).items():
                gt_checked += 1
                got_gt = "" if record_iri is None else rebuild(
                    calls.get((record_iri, name), []))
                if got_gt == want_gt:
                    gt_matched += 1
                else:
                    mismatches.append({"pos": pos, "field": f"GT[{name}]",
                                       "expected": want_gt, "actual": got_gt or "not recovered"})
        report["fixtures"][stem] = {
            "recordsChecked": checked, "recordsMatched": matched,
            "genotypesChecked": gt_checked, "genotypesMatched": gt_matched,
            "mismatches": mismatches[:6],
        }

    total = sum(f["recordsChecked"] for f in report["fixtures"].values())
    ok = sum(f["recordsMatched"] for f in report["fixtures"].values())
    gt_total = sum(f["genotypesChecked"] for f in report["fixtures"].values())
    gt_ok = sum(f["genotypesMatched"] for f in report["fixtures"].values())
    report["totals"] = {"recordsChecked": total, "recordsMatched": ok,
                        "genotypesChecked": gt_total, "genotypesMatched": gt_ok}
    out_dir = Path(os.environ.get("RESULTS_DIR", Path.cwd()))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "round-trip.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report["totals"], indent=1))
    for stem, f in sorted(report["fixtures"].items()):
        clean = (f["recordsMatched"] == f["recordsChecked"]
                 and f["genotypesMatched"] == f["genotypesChecked"])
        print(f"  {stem:24} columns {f['recordsMatched']}/{f['recordsChecked']}"
              f"   GT {f['genotypesMatched']}/{f['genotypesChecked']}"
              f"{'' if clean else '   <-- mismatch'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
