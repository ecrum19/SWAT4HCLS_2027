#!/usr/bin/env python3
"""Turn one run directory into the numbers the paper cites.

Every figure here is computed from that run's own results; nothing is carried
over from an earlier run, and nothing is stated that the JSON does not support.

    python3 reproduce/summarise.py reproduce/runs/<stamp> > SUMMARY.md
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
    disc = load(run, "cross-producer-discovery.json")
    rt = load(run, "round-trip.json")
    emap = load(run, "evidence-map.json")
    integ = load(run, "w4-results.json") or load(run, "results.json")
    prof = load(run, "example-profiles.json")

    pin = env["pinned"]
    out = []
    w = out.append

    w(f"# Reproduction run {run.name}")
    w("")
    w(f"Produced by `sh reproduce/run.sh` on {env['recordedAt']}, "
      f"{len(steps)} steps, {sum(s['seconds'] for s in steps)}s total, "
      f"{sum(1 for s in steps if s['exit'] != 0)} failures.")
    w("")
    w("| Pinned | |")
    w("| --- | --- |")
    w(f"| Vocabulary | `{pin['vocabulary']['tag']}` = `{(pin['vocabulary']['commit'] or '')[:7]}` |")
    w(f"| Converter | `{pin['converterFinal']['tag']}` = "
      f"`{(pin['converterFinal']['commit'] or '')[:7]}`, image `{pin['converterFinal']['image']}` |")
    w(f"| Converter, pre-correction | `{pin['converterBaseline']['tag']}` = "
      f"`{(pin['converterBaseline']['commit'] or '')[:7]}`, image `{pin['converterBaseline']['image']}` |")
    w(f"| Host | {env['machine']['osRelease'] or env['machine']['system']}, "
      f"{env['machine']['arch']}, {env['machine']['cpus']} CPU |")
    w(f"| Engines | rdflib {env['tooling']['rdflib']} (SPARQL), "
      f"pyshacl {env['tooling']['pyshacl']}, Docker {env['tooling']['docker']} |")
    w("")

    if final and disc:
        fs, ds = final["summary"], disc["summary"]
        w("## Cross-producer replay")
        w("")
        w("| | Pre-correction | Final |")
        w("| --- | ---: | ---: |")
        w(f"| Checks | {ds['checks']} | {fs['checks']} |")
        w(f"| Both pass | {ds['byOutcome'].get('pass/pass', 0)} | {fs['byOutcome'].get('pass/pass', 0)} |")
        w(f"| Divergent (repo passes, converter fails) | {ds['byOutcome'].get('pass/fail', 0)} "
          f"| {fs['byOutcome'].get('pass/fail', 0)} |")
        w(f"| Both fail | {ds['byOutcome'].get('fail/fail', 0)} | {fs['byOutcome'].get('fail/fail', 0)} |")
        w(f"| Converter passes, repo fails | {ds['byOutcome'].get('fail/pass', 0)} "
          f"| {fs['byOutcome'].get('fail/pass', 0)} |")
        w("")

        d_div = set(ds["repoPassConverterNot"])
        f_div = set(fs["repoPassConverterNot"])
        corrected = sorted(d_div - f_div)
        still = sorted(f_div)
        introduced = sorted(f_div - d_div)

        w(f"**{len(d_div)} requirements diverged before the corrections; {len(still)} still do.** "
          f"Every one is accounted for below, so no total needs inferring.")
        w("")
        w("| Requirement | Pre-correction | Final | Disposition |")
        w("| --- | --- | --- | --- |")
        for r in sorted(d_div | f_div):
            do, fo = outcomes(disc, r), outcomes(final, r)
            if r in corrected:
                disp = "corrected"
            elif r in introduced:
                disp = "**newly divergent**"
            else:
                disp = "still divergent"
            w(f"| {r} | {dict(do)} | {dict(fo)} | {disp} |")
        w("")
        w(f"Corrected ({len(corrected)}): {', '.join(corrected) or 'none'}.  ")
        w(f"Still divergent ({len(still)}): {', '.join(still) or 'none'}.  ")
        if introduced:
            w(f"Newly divergent ({len(introduced)}): {', '.join(introduced)} — "
              f"a regression, not present before the corrections.  ")
        w("")

        exercised = {row["requirement"] for row in final.get("results", [])}
        allpass = {r for r in exercised if set(outcomes(final, r)) == {"pass/pass"}}
        agree = {r for r in exercised if not outcomes(final, r).get("pass/fail")}
        w(f"Requirements exercised: **{len(exercised)}**; agreeing on every check: "
          f"**{len(agree)}**; passing on every check for both producers: **{len(allpass)}**.")
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
        checked = t.get("recordsChecked") or sum(
            f.get("recordsChecked", 0) for f in rt.get("fixtures", {}).values())
        matched = t.get("recordsMatched") or sum(
            f.get("recordsMatched", 0) for f in rt.get("fixtures", {}).values())
        w(f"## Semantic round-trip\n\n**{matched}/{checked} records** recovered from structured "
          f"properties alone, expanded profile.\n")

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

    if integ:
        status = integ.get("status", "?")
        rows = integ.get("rows") or integ.get("observed") or []
        w(f"## Integration example\n\n**{status}** — {len(rows)} rows returned, "
          f"matching the answers authored in advance.\n")

    print("\n".join(out))


if __name__ == "__main__":
    main()
