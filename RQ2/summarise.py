#!/usr/bin/env python3
"""Turn one run directory into the numbers the paper cites.

Every figure here is computed from that run's own results; nothing is carried
over from an earlier run, and nothing is stated that the JSON does not support.

    python3 RQ2/summarise.py RQ2/runs/<stamp> > SUMMARY.md
"""
import collections
import json
import pathlib
import sys


def load(run, name):
    p = run / "results" / name
    return json.loads(p.read_text()) if p.exists() else None


def outcomes(js, requirement=None):
    c = collections.Counter()
    for row in js.get("results", []):
        if requirement is None or row["requirement"] == requirement:
            c[f'{row["repo"]}/{row["converter"]}'] += 1
    return c


def main():
    run = pathlib.Path(sys.argv[1])
    env = json.loads((run / "env.json").read_text())
    steps = [json.loads(l) for l in (run / "steps.jsonl").read_text().splitlines() if l.strip()]

    final = load(run, "cross-producer.json")
    rt = load(run, "round-trip.json")
    frt = load(run, "field-round-trip.json")
    emap = load(run, "evidence-map.json")
    prof = load(run, "example-profiles.json")

    pin = env["pinned"]
    out = []
    w = out.append

    w(f"# Reproduction run {run.name}")
    w("")
    w(f"Produced by `sh RQ2/run.sh` on {env['recordedAt']}, "
      f"{len(steps)} steps, {sum(s['seconds'] for s in steps)}s total, "
      f"{sum(1 for s in steps if s['exit'] != 0)} failures.")
    w("")
    w("| Pinned | |")
    w("| --- | --- |")
    w(f"| Vocabulary | `{pin['vocabulary']['tag']}` = `{(pin['vocabulary']['commit'] or '')[:7]}` |")
    w(f"| Converter | `{pin['converter']['tag']}` = "
      f"`{(pin['converter']['commit'] or '')[:7]}`, image `{pin['converter']['image']}` |")
    w(f"| Host | {env['machine']['osRelease'] or env['machine']['system']}, "
      f"{env['machine']['arch']}, {env['machine']['cpus']} CPU |")
    w(f"| Engines | rdflib {env['tooling']['rdflib']} (SPARQL), "
      f"pyshacl {env['tooling']['pyshacl']}, Docker {env['tooling']['docker']} |")
    w("")

    if final:
        fs = final["summary"]
        by = fs["byOutcome"]
        w("## Cross-producer replay")
        w("")
        w(f"The vocabulary's own materializer and the converter were run over the same "
          f"{len(fs['fixtures'])} fixtures in both sample profiles, and every applicable case "
          f"replayed against the reviewed expected answers.")
        w("")
        w("| Outcome | Checks |")
        w("| --- | ---: |")
        w(f"| Both pass | {by.get('pass/pass', 0)} |")
        w(f"| Repo passes, converter fails | {by.get('pass/fail', 0)} |")
        w(f"| Both fail | {by.get('fail/fail', 0)} |")
        w(f"| Converter passes, repo fails | {by.get('fail/pass', 0)} |")
        w(f"| **Total** | **{fs['checks']}** |")
        w("")

        exercised = {row["requirement"] for row in final.get("results", [])}
        allpass = {r for r in exercised if set(outcomes(final, r)) == {"pass/pass"}}
        agree = {r for r in exercised if not outcomes(final, r).get("pass/fail")}
        divergent = sorted(fs["repoPassConverterNot"])
        w(f"Requirements exercised: **{len(exercised)}**; agreeing on every check: "
          f"**{len(agree)}**; passing on every check for both producers: **{len(allpass)}**.")
        w("")
        w(f"**{len(divergent)} requirements diverge**, on {by.get('pass/fail', 0)} checks:")
        w("")
        w("| Requirement | Outcomes |")
        w("| --- | --- |")
        for r in divergent:
            w(f"| {r} | {dict(outcomes(final, r))} |")
        w("")

        # Profile agreement, computed from this run only.
        byk = collections.defaultdict(dict)
        for row in final.get("results", []):
            k = (row["requirement"], row["version"], row["axis"], row["case"])
            byk[k][row["profile"]] = (row["repo"], row["converter"])
        pairs = [v for v in byk.values() if {"expanded", "condensed"} <= set(v)]
        same = sum(1 for v in pairs if v["expanded"] == v["condensed"])
        disagree_reqs = sorted({k[0] for k, v in byk.items()
                                if {"expanded", "condensed"} <= set(v)
                                and v["expanded"] != v["condensed"]})
        w(f"**Sample profiles** return the same outcome on **{same} of {len(pairs)}** comparable "
          f"checks. The {len(pairs) - same} disagreements fall on {len(disagree_reqs)} "
          f"requirements: {', '.join(disagree_reqs)}.")
        w("")

    if rt:
        t = rt.get("totals", rt)
        checked, matched = t.get("recordsChecked", 0), t.get("recordsMatched", 0)
        gt_checked, gt_matched = t.get("genotypesChecked", 0), t.get("genotypesMatched", 0)
        w("## Semantic round-trip")
        w("")
        w(f"Rebuilt from structured properties alone, expanded profile: "
          f"**{matched}/{checked} records** (CHROM, POS, ID, REF, ALT, QUAL, FILTER) and "
          f"**{gt_matched}/{gt_checked} sample genotypes**.")
        if rt.get("normalisation"):
            w("")
            w(f"_{rt['normalisation']}_")
        if frt:
            ft = frt.get("totals", {})
            w("")
            w(f"Every header line, recovered by source line number and compared on key "
              f"and value: **{ft.get('headerLinesMatched', 0)}/"
              f"{ft.get('headerLinesChecked', 0)} lines**.")
            w("")
            w(f"Every INFO entry and non-GT FORMAT subfield, rebuilt from ordered value "
              f"items rather than from a preserved column: "
              f"**{ft.get('matched', 0)}/{ft.get('checked', 0)} values**.")
            fbad = {k: v for k, v in frt.get("fixtures", {}).items()
                    if v.get("matched") != v.get("checked")}
            if fbad:
                w("")
                for k, v in sorted(fbad.items()):
                    for m in v.get("mismatches", []):
                        w(f"- `{k}` {m['field']} at position {m['pos']}: "
                          f"expected `{m['expected']}`, got `{m['actual']}`")
        bad = {k: v for k, v in rt.get("fixtures", {}).items()
               if v.get("recordsMatched") != v.get("recordsChecked")
               or v.get("genotypesMatched") != v.get("genotypesChecked")}
        if bad:
            w("")
            w(f"Fixtures with a mismatch: {', '.join(sorted(bad))}.")
        w("")

    if emap:
        d = emap["duplicates"]
        w("## Assessment shape\n")
        w(f"{emap['requirements']} requirements, {emap['cases']} cases. "
          f"Nominal executions **{d['nominalExecutions']}**, of which "
          f"**{d['redundantExecutions']}** repeat an identical check, leaving "
          f"**{d['distinctExecutions']}** distinct. "
          f"Signatures shared across cases: {d['signaturesSharedAcrossCases']}.")
        w("")
        w("| | Requirements | Tested |")
        w("| --- | ---: | ---: |")
        for k, v in emap["rq"].items():
            w(f"| {k} | {v['requirements']} | {v['tested']} |")
        w("")

    if prof:
        w("## Section 5.4 profile figures\n")
        w("| Profile | Triples | Distinct VCF Core terms | Undeclared |")
        w("| --- | ---: | ---: | ---: |")
        for name in ("expanded", "condensed"):
            p = prof["profiles"][name]
            w(f"| {name} | {p['triples']} | {p['distinctTerms']} | {len(p['undeclared'])} |")
        w("")
        w(f"Declaredness checked against `{prof['declaredAt']}` "
          f"({prof['declaredNames']} declared local names).")
        w("")

    print("\n".join(out))


if __name__ == "__main__":
    main()
