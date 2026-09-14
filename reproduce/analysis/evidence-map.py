#!/usr/bin/env python3
"""W2.1 — map the existing methodology evidence to RQ1-RQ3 and the W1 features,
find duplicate checks, and report untested requirements.

Reads only pinned inputs; derives nothing from converter output.

  python3 w2/evidence-map.py <vcf-core-vocabulary checkout> [w2/generated/cross-producer.json]
"""
import json, sys, collections, pathlib

# --- Curated mapping, requirement -> W1 features. Authored by hand from the
# --- requirement questions; listed here so it can be audited and corrected.
FEATURES = {
    "F1 file identity":        "R01 R02 R05 R06 R34 R55 R56 R58 R59 R62 R65",
    "F2 header declarations":  "R03 R04 R34 R35 R36 R51 R52 R53 R57 R59 R61 R65",
    "F3 version distinction":  "R01 R22 R27 R28 R29 R30 R31 R33 R38 R45 R46 R49 R50 R54 R59 R64 R65"
                               " R69 R71 R72 R74 R75 R76 R79 R80 R82 R83 R84 R85 R86 R87 R88 R89 R91 R94",
    "F4 ordered alleles":      "R10 R23 R24 R25 R53 R54 R64 R90",
    "F5 genotype structure":   "R19 R20 R28 R37 R49 R70 R81 R82",
    "F6 per-sample FORMAT":    "R17 R18 R21 R29 R30 R60 R68",
    "F7 allele-dependent":     "R16 R33 R38 R44 R67 R73 R74 R77 R83 R84 R91",
    "F8 missingness":          "R11 R12 R19 R21 R26 R40 R45 R64 R66 R87 R91",
}
# F9 (profile choice) is not a per-requirement feature: every case is executed in
# both sample profiles, so the profile axis carries it.

def rqs(req, feat_of):
    """RQ assignment rules, applied uniformly. A requirement may serve several."""
    out = ["RQ1"]                                     # every requirement asks whether
                                                      # a construct's meaning survives
    versioned = len(req["versions"]) < 5 or "version" in req["question"].lower()
    if versioned:
        out.append("RQ2")                             # version-specific behaviour
    if feat_of[req["id"]] & {"F1 file identity", "F2 header declarations",
                             "F6 per-sample FORMAT", "F7 allele-dependent"}:
        out.append("RQ3")                             # the provenance chain an
    return out                                        # integration query traverses

def main():
    voc = pathlib.Path(sys.argv[1])
    inp = voc / "coverage/methodology/inputs"
    reqs = json.loads((inp / "requirements.json").read_text())
    cases = json.loads((inp / "cases.json").read_text())

    feat_of = collections.defaultdict(set)
    for f, ids in FEATURES.items():
        for r in ids.split():
            feat_of[r].add(f)

    by_req = collections.defaultdict(list)
    for c in cases:
        by_req[c["requirement"]].append(c)

    # ---- RQ / feature coverage -------------------------------------------------
    rq_rows = collections.defaultdict(lambda: {"requirements": set(), "tested": set()})
    feat_rows = collections.defaultdict(lambda: {"requirements": set(), "tested": set()})
    for r in reqs:
        tested = bool(by_req[r["id"]])
        for q in rqs(r, feat_of):
            rq_rows[q]["requirements"].add(r["id"])
            if tested: rq_rows[q]["tested"].add(r["id"])
        for f in feat_of[r["id"]] or {"(unmapped)"}:
            feat_rows[f]["requirements"].add(r["id"])
            if tested: feat_rows[f]["tested"].add(r["id"])

    # ---- Duplicate-check pass --------------------------------------------------
    # (a) a case whose two axes run the identical query against the identical
    #     expected answer -- the second execution establishes nothing new.
    axis_dupes, by_signature = [], collections.defaultdict(list)
    for c in cases:
        pres, struct = c.get("preservation") or {}, c.get("structure") or {}
        if pres and pres == struct:
            axis_dupes.append(c["id"])
        for axis in ("preservation", "structure"):
            for profile, spec in (c.get(axis) or {}).items():
                sig = (spec.get("query"), json.dumps(spec.get("expected"), sort_keys=True),
                       c["fixture"])
                by_signature[sig].append(f'{c["id"]}:{axis}:{profile}')
    # (b) the same query+expected+fixture reached from more than one case.
    cross_dupes = {"|".join(k[:1]) + " @ " + k[2]: sorted({e.split(":")[0] for e in v})
                   for k, v in by_signature.items()
                   if len({e.split(":")[0] for e in v}) > 1}
    # (c) how much of the nominal execution count is a re-run of an identical check.
    nominal, distinct = 0, set()
    for c in cases:
        for axis in ("preservation", "structure"):
            for profile, spec in (c.get(axis) or {}).items():
                for pr in (("expanded", "condensed") if profile == "both" else (profile,)):
                    nominal += 1
                    distinct.add((c["id"], spec.get("query"),
                                  json.dumps(spec.get("expected"), sort_keys=True),
                                  c["fixture"], pr))

    # ---- Gaps ------------------------------------------------------------------
    untested = sorted(r["id"] for r in reqs if not by_req[r["id"]])
    per_version = collections.defaultdict(lambda: {"applicable": 0, "tested": 0})
    for r in reqs:
        have = {c["version"] for c in by_req[r["id"]]}
        for v in r["versions"]:
            per_version[v]["applicable"] += 1
            if v in have: per_version[v]["tested"] += 1

    out = {
        "requirements": len(reqs), "cases": len(cases),
        "rq": {k: {"requirements": len(v["requirements"]), "tested": len(v["tested"]),
                   "untested": sorted(v["requirements"] - v["tested"])}
               for k, v in sorted(rq_rows.items())},
        "features": {k: {"requirements": len(v["requirements"]), "tested": len(v["tested"]),
                         "untested": sorted(v["requirements"] - v["tested"])}
                     for k, v in sorted(feat_rows.items())},
        "duplicates": {
            "casesWithIdenticalAxes": len(axis_dupes),
            "casesWithIdenticalAxesIds": axis_dupes,
            "signaturesSharedAcrossCases": len(cross_dupes),
            "nominalExecutions": nominal,
            "distinctExecutions": len(distinct),
            "redundantExecutions": nominal - len(distinct),
        },
        "gaps": {"untestedRequirements": untested,
                 "perVersion": {k: v for k, v in sorted(per_version.items())}},
    }
    if len(sys.argv) > 2:                    # optional: executed cross-producer status
        xp = json.loads(pathlib.Path(sys.argv[2]).read_text())
        ex = collections.defaultdict(lambda: collections.Counter())
        for row in xp["results"]:
            ex[row["requirement"]][f'{row["repo"]}/{row["converter"]}'] += 1
        out["executed"] = {"checks": xp["summary"]["checks"],
                           "requirementsExercised": len(ex),
                           "divergent": xp["summary"]["repoPassConverterNot"]}
    print(json.dumps(out, indent=1, sort_keys=True))

if __name__ == "__main__":
    main()
