#!/usr/bin/env python3
"""Assert that every statistic quoted in the SWAT4HCLS 2027 manuscript still
matches ``coverage/curated/generated/report.json``.

The manuscript quotes concrete counts. This check fails if the artifacts move
and the prose does not, so a published figure cannot go stale unnoticed.
Run ``npm run coverage:report`` first; ``npm run validate`` does both.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REPORT = ROOT / "coverage/curated/generated/report.json"
PAPER = ROOT / "SWAT4HCLS_2027" / "main.tex"


def main() -> int:
    if not REPORT.exists():
        print("coverage-report.json missing; run: npm run coverage:report", file=sys.stderr)
        return 1
    report = json.loads(REPORT.read_text())
    tex = PAPER.read_text()

    cov = report["coverage"]["logicalModel"]
    ser = report["coverage"]["serialization"]
    voc = report["vocabulary"]["byKind"]
    ext = report["externalVocabularies"]
    maps = report["mappings"]
    asserted = maps["asserted"]
    third = maps["thirdParty"]
    req = report["coverage"]["representation"]
    keys = report["reservedKeys"]
    shapes = report["shaclProfiles"]
    portable = shapes["vcf-core-vocabulary.shacl.ttl"]

    expected: list[tuple[str, str]] = [
        ("construct total", str(cov["constructs"])),
        ("constructs fully covered", str(cov["full"])),
        # The manuscript may state the ratio or "all N entries"; accept either.
        ("full coverage claim", [f"{cov['fullPercent']}\\%", f"all {cov['full']} logical-model entries"]),
        ("declared terms", str(report["vocabulary"]["declaredTerms"])),
        ("classes", f"{voc['class']} classes"),
        ("object properties", f"{voc['objectProperty']} object properties"),
        ("datatype properties", f"{voc['datatypeProperty']} datatype properties"),
        ("named individuals", f"{voc['namedIndividual']} named individuals"),
        ("reserved declarations", f"{keys['current']['total']} reserved key declarations"),
        ("reserved split", f"{keys['current']['info']} INFO and {keys['current']['format']} FORMAT"),
        ("portable node shapes", f"{portable['nodeShapes']} node shapes"),
        ("portable property shapes", f"{portable['propertyShapes']} property shapes"),
        ("sparql rules", f"{shapes['vcf-core-vocabulary-sparql.shacl.ttl']['sparqlConstraints']} cross-resource"),
        ("consistency rules", f"{shapes['vcf-core-consistency.shacl.ttl']['sparqlConstraints']} rules relating raw tokens"),
        ("validated fixtures", f"accepts {report['validation']['fixtures']} fixtures"),
        ("serialization fixtures", f"{ser['fixturesPassed']} of {ser['fixturesChecked']} satisfy"),
        ("enforced constructs", f"{cov['axesHeld']['enforced']} of {cov['constructs']} are enforced"),
        # The alignment layer. Curated in SSSOM; the Turtle module is generated.
        ("asserted alignments", f"{asserted['mappings']} mappings"),
        ("alignment subjects", f"{asserted['distinctSubjects']} of its own terms"),
        ("alignment objects", f"{asserted['distinctObjects']} external terms"),
        ("alignments also inline", f"{asserted['alsoInlineInOntology']} of the "
                                   f"{asserted['mappings']} mappings are additionally asserted inline"),
        ("alignments module-only", f"the remaining {asserted['moduleOnly']}"),
        ("alignment confidences", f"{asserted['withConfidence']} of the {asserted['mappings']} mappings "
                                  f"carry an explicit confidence"),
        ("third-party mappings", f"{third['mappings']} third-party mappings"),
        # Counts from the separate information-requirement assessment.
        ("registered requirements", f"{req['requirements']} source-anchored information requirements"),
        ("representation cases", f"{req['cases']} version-specific cases"),
        ("pending reviews", f"{req['pendingReviews']} review decisions"),
        ("matching declarations", f"{req['declarations']['exact']} of {req['declarations']['rows']} explicit source rows"),
    ]
    for predicate, label in (("skos:exactMatch", "exactMatch"), ("skos:closeMatch", "closeMatch"),
                             ("skos:relatedMatch", "relatedMatch"), ("skos:narrowMatch", "narrowMatch")):
        expected.append((f"alignment predicate: {label}",
                         f"{asserted['byPredicate'][predicate]} \\term{{{label}}}"))
    for vocab, name in (("gvo", "GVO"), ("hero", "HERO"), ("vrs", "GA4GH VRS 2.0"),
                        ("gfvo", "GFVO"), ("med2rdf", "Med2RDF")):
        expected.append((f"alignment table row: {name}",
                         f"{name} & {asserted['byTarget'][vocab]} &"))
    for source, name in (("hero", "HERO"), ("med2rdf", "Med2RDF"),
                         ("gigwa", "Gigwa"), ("sembeacon", "SemBeacon")):
        expected.append((f"third-party set: {name}",
                         f"{name}~({third['bySet'][source]})"))
    for entry in req["byVersion"]:
        value = entry["structure"]["demonstrated"]
        expected.append((f"structural demonstrations {entry['version']} {entry['profile']}",
                         f"({entry['version']},{value})"))
        expected.append((f"registered denominator {entry['version']}",
                         f"({entry['version']},{entry['denominator']})"))
    # Figure 3(a) plots the per-area evidence tiers. Its axis abbreviates the
    # inventory's area names, so the bar coordinates are matched against the
    # abbreviation the figure actually uses.
    axis_labels = {
        "File and header structure": "File and header",
        "Field declaration attributes": "Field declarations",
        "Type and arity value sets": "Type and arity",
        "Lexical and encoding rules": "Lexical rules",
        "Fixed fields and allele structure": "Fixed fields",
        "FORMAT and genotype": "FORMAT and genotype",
        "Structural variation, repeats, gVCF": "SV/repeats/gVCF",
    }
    for area in cov["byArea"]:
        label = axis_labels[area["area"]]
        for tier, count in area["evidenceTiers"].items():
            expected.append((f"evidence bar: {area['area']} / {tier}", f"({count},{label})"))
    for prefix, count in (("SO", "so"), ("ChEBI", "chebi"), ("VRS", "vrs"),
                          ("HERO-Genomics", "hero"), ("FALDO", "faldo"), ("GENO", "geno")):
        expected.append((f"{prefix} alignment count",
                         f"{prefix}~({ext['alignmentTargets']['byVocabulary'][count]})"))

    # The per-area construct counts are quoted in the text and plotted as the
    # stacked-bar totals in Figure 3(a); both are checked below.
    expected.append(("per-area construct sizes",
                     ", ".join(str(area["constructs"]) for area in cov["byArea"][:-1])
                     + f" and {cov['byArea'][-1]['constructs']}"))

    def present(value):
        options = value if isinstance(value, list) else [value]
        return any(option in tex for option in options)

    missing = [(label, text) for label, text in expected if not present(text)]
    if missing:
        print("Manuscript figures no longer match the generated report:", file=sys.stderr)
        for label, text in missing:
            print(f"  {label}: expected to find {text!r} in main.tex", file=sys.stderr)
        return 1
    print(f"Manuscript figures: {len(expected)} checked, all match coverage/curated/generated/report.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
