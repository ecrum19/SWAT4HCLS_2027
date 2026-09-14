#!/usr/bin/env python3
"""W5 — measure the manuscript's Section 5.4 figures from converter output.

Reports, per sample profile: triple count, distinct VCF Core terms used, and any
term not declared in the vocabulary release the paper cites. Declaredness is
checked against a git ref (default the v2.1.1 tag) rather than the working tree,
so an uncommitted ontology edit cannot flatter the result.

  python3 w5/measure.py <expanded.nt.gz> <condensed.nt.gz> <vcf-core-vocabulary checkout> [ref]

Convert first, from a VCF-RDFizer checkout, for each profile:

  python3 vcf_rdfizer.py -m full -i coverage/synthetic.vcf \\
    --sample-representation expanded --representations none \\
    --rdf-compression none -o out-expanded
"""
import gzip
import json
import pathlib
import re
import subprocess
import sys

NS = "https://w3id.org/vcf-core/vocab#"
TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
TRIPLE = re.compile(r"^(<[^>]*>|_:\S+)\s+(<[^>]*>)\s+(.*)\s\.$")


def read(path):
    """Return (triple count, terms used, predicates, rdf:type classes)."""
    triples = 0
    used, preds, classes = set(), set(), set()
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            triples += 1
            used |= {m for m in re.findall(rf"{re.escape(NS)}([A-Za-z0-9_]+)", line)}
            m = TRIPLE.match(line)
            if not m:
                continue
            _, p, o = m.groups()
            if p.startswith("<" + NS):
                preds.add(p[len(NS) + 1:-1])
            if p == TYPE and o.startswith("<" + NS):
                classes.add(o[len(NS) + 1:-1])
    return triples, used, preds, classes


def declared_at(vocab, ref):
    """Local names declared by the ontology modules at a git ref."""
    def git(*args):
        return subprocess.run(["git", "-C", str(vocab), *args],
                              capture_output=True, text=True, check=True).stdout

    names = set()
    for f in git("ls-tree", "-r", "--name-only", ref).split():
        if not (f.startswith("ontology/") and f.endswith(".ttl")):
            continue
        txt = git("show", f"{ref}:{f}")
        names |= set(re.findall(r"(?:^|\s)vcfc:([A-Za-z0-9_]+)\s+(?:a|rdf:type)\s", txt, re.M))
        names |= set(re.findall(r"^:([A-Za-z0-9_]+)\s+(?:a|rdf:type)\s", txt, re.M))
        names |= set(re.findall(rf"<{re.escape(NS)}([A-Za-z0-9_]+)>\s+(?:a|rdf:type)\s", txt))
    return names


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    expanded, condensed, vocab = sys.argv[1:4]
    ref = sys.argv[4] if len(sys.argv) > 4 else "v2.1.1"
    declared = declared_at(pathlib.Path(vocab), ref)

    out = {"declaredAt": ref, "declaredNames": len(declared), "profiles": {}}
    for name, path in (("expanded", expanded), ("condensed", condensed)):
        triples, used, preds, classes = read(path)
        out["profiles"][name] = {
            "triples": triples,
            "distinctTerms": len(used),
            "predicates": len(preds),
            "classes": len(classes),
            "undeclared": sorted(used - declared),
        }
    out["allDeclared"] = not any(p["undeclared"] for p in out["profiles"].values())
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0 if out["allDeclared"] else 1


if __name__ == "__main__":
    sys.exit(main())
