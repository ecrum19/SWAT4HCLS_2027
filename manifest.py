#!/usr/bin/env python3
"""Emit the reproduction manifest for every recorded result.

One place a reader can check what produced each figure in the paper: the pinned
artifacts and their commits, the specification revisions and their hashes, the
fixture hashes, the query and validation engines with their versions and
inference settings, and the command that regenerates each result.

  python3 manifest.py <vcf-core-vocabulary checkout> <VCF-RDFizer checkout> [> MANIFEST.json]

Values that cannot be read from a checkout -- the container image digest and the
toolchain inside it -- are recorded in manifest-runtime.json beside this script,
written by hand from the run that produced the results, and merged in here.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

W2_FIXTURES = [
    "basic-v4.1", "basic-v4.2", "basic-v4.3", "basic-v4.4", "basic-v4.5",
    "header-audit-v4.5", "features-v4.5", "local-alleles-v4.5",
    "tandem-repeats-v4.4", "tandem-repeats-v4.5",
]

RESULTS = {
    "coverage inventory (104/104, 87 enforced)": {
        "paper": "Table 2, mechanism row",
        "command": "npm run coverage:report",
        "output": "stdout; coverage/vcf45-inventory/",
    },
    "specification-derived assessment (94 requirements, 210 cases)": {
        "paper": "Section 5.2, Table 2",
        "command": "npm run methodology:check -- --require-reviewed",
        "output": "coverage/methodology/generated/summary.json",
    },
    "evidence map, RQ/feature coverage and duplicate pass (465 distinct)": {
        "paper": "Section 5.2",
        "command": "python3 w2/evidence-map.py <vocab> w2/generated/cross-producer.json",
        "output": "w2/generated/evidence-map.json",
    },
    "cross-producer replay, final (572 checks, 508 both-pass)": {
        "paper": "Section 5.3, Table 2",
        "command": "sh w2/convert-fixtures.sh <outdir> && python3 w2/cross-producer.py <outdir>",
        "output": "w2/generated/cross-producer.json",
    },
    "cross-producer replay, discovery run (pre-correction converter)": {
        "paper": "Section 5.3, the 15 initially divergent requirements",
        "command": "convert with the pre-correction converter, then python3 w2/cross-producer.py <outdir>",
        "output": "w2/generated/cross-producer-discovery.json",
    },
    "semantic round-trip (35/35 records)": {
        "paper": "Section 5.3, Table 2",
        "command": "python3 w2/round-trip.py <outdir>",
        "output": "w2/generated/round-trip.json",
    },
    "integration example (2 rows, 3 exclusions)": {
        "paper": "Section 5.5",
        "command": "sh w4/run.sh <vocab> <rdfizer> <workdir>",
        "output": "w4/generated/w4-results.json",
    },
    "profile example figures (242/168 triples, 93/80 terms)": {
        "paper": "Section 5.4",
        "command": "python3 w5/measure.py <expanded.nt.gz> <condensed.nt.gz> <vocab> v2.1.2",
        "output": "w5/generated/example-profiles.json",
    },
}


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True).stdout.strip()


def release_tag(repo):
    """The tag whose content matches the checkout.

    Both repositories squash-merge into main, so the released tag sits on a
    commit that is not an ancestor of the branch that produced it even when the
    trees are byte-identical. Matching on tree makes the answer correct either
    way; the commit is reported separately.
    """
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    for tag in git(repo, "tag", "--sort=-v:refname").split():
        if git(repo, "rev-parse", f"{tag}^{{tree}}") == tree:
            return tag, "exact content match"
    described = git(repo, "describe", "--tags") or None
    return described, "no tag matches this tree; nearest ancestor tag shown"


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    vocab, rdfizer = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    here = pathlib.Path(__file__).parent

    specs = json.loads((vocab / "coverage/methodology/sources.lock.json").read_text())

    out = {
        "artifacts": {
            "vcf-core-vocabulary": {
                "version": json.loads((vocab / "package.json").read_text())["version"],
                "tag": release_tag(vocab)[0],
                "tagResolution": release_tag(vocab)[1],
                "commit": git(vocab, "rev-parse", "HEAD"),
                "repository": "https://github.com/ecrum19/vcf-core-vocabulary",
            },
            "VCF-RDFizer": {
                "tag": release_tag(rdfizer)[0],
                "tagResolution": release_tag(rdfizer)[1],
                "commit": git(rdfizer, "rev-parse", "HEAD"),
                "repository": "https://github.com/ecrum19/VCF-RDFizer",
            },
        },
        "specifications": {
            v: {"source": d["source"], "sha256": d["sha256"]}
            for v, d in sorted(specs["versions"].items())
        },
        "specificationsRetrieved": specs.get("provenance"),
        "fixtures": {
            f: sha256(vocab / f"coverage/methodology/fixtures/{f}.vcf")
            for f in W2_FIXTURES
        },
        "results": RESULTS,
    }

    runtime = here / "manifest-runtime.json"
    if runtime.exists():
        out["runtime"] = json.loads(runtime.read_text())

    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
