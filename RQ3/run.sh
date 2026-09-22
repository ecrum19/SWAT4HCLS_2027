#!/usr/bin/env bash
# RQ3 -- run the integration case study end to end.
#
#     sh RQ3/run.sh [workdir]
#
# Needs: git, docker, python3 with rdflib. No local checkout of anything: the
# vocabulary and the converter are fetched from GitHub at the tags below, and
# the container image is pulled by digest.
#
# VCF file -> VCF Core graph -> join to a flagged-alteration snapshot -> SPARQL
# -> answers checked against expectations authored before the query ran.
#
# Output lands in RQ3/results/:
#
#     integration.json  the observed rows, the expected rows and the comparison
#     check.txt         what the check printed
#     run.json          machine, toolchain and the exact versions used
set -euo pipefail

VOCAB_REPO="https://github.com/ecrum19/vcf-core-vocabulary.git"
VOCAB_TAG="v2.1.3"

RDFIZER_REPO="https://github.com/ecrum19/VCF-RDFizer.git"
CONVERTER_TAG="v3.0.3"
CONVERTER_IMAGE="ecrum19/vcf-rdfizer"
CONVERTER_DIGEST="sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a"

# The fixture the case study runs on. It exercises VCF 4.5 local alleles, which
# is what makes the answer depend on interpreting Number=LR correctly.
FIXTURE="local-alleles-v4.5"
# Expanded profile only: the query walks per-sample value resources, which the
# condensed profile stores as vectors instead.
PROFILE="expanded"

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
WORK="${1:-$HERE/work}"
# Pinned checkouts are shared by every RQ script and cached at the repository
# root, so running RQ1 then RQ2 then RQ3 fetches each repository once rather
# than once per question. The tag is part of the directory name: bumping a pin
# fetches a fresh checkout instead of silently reusing the old one.
ARTIFACTS="${ARTIFACTS:-$REPO/.artifacts}"
VOCAB="$ARTIFACTS/vcf-core-vocabulary-$VOCAB_TAG"
RDFIZER="$ARTIFACTS/VCF-RDFizer-$CONVERTER_TAG"
OUT="$HERE/results"
PYTHON="${PYTHON:-python3}"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

mkdir -p "$WORK" "$OUT" "$ARTIFACTS"

# ------------------------------------------------------------------ fetch ----
say "Fetching pinned artifacts"
[ -d "$VOCAB/.git" ]   || git clone --quiet --depth 1 --branch "$VOCAB_TAG"     "$VOCAB_REPO"   "$VOCAB"
[ -d "$RDFIZER/.git" ] || git clone --quiet --depth 1 --branch "$CONVERTER_TAG" "$RDFIZER_REPO" "$RDFIZER"
docker pull --quiet "$CONVERTER_IMAGE@$CONVERTER_DIGEST" > /dev/null
docker tag "$CONVERTER_IMAGE@$CONVERTER_DIGEST" "rq3-vcf-rdfizer:$CONVERTER_TAG" > /dev/null
printf '  vocabulary %s at %s\n' "$VOCAB_TAG"     "$(git -C "$VOCAB"   rev-parse --short HEAD)"
printf '  converter  %s at %s\n' "$CONVERTER_TAG" "$(git -C "$RDFIZER" rev-parse --short HEAD)"

# -------------------------------------------------------------- conversion ---
GRAPH="$WORK/converted/$PROFILE/$FIXTURE/$FIXTURE.nt.gz"
if [ ! -f "$GRAPH" ]; then
  say "Converting $FIXTURE.vcf ($PROFILE profile)"
  mkdir -p "$WORK/in"
  cp "$VOCAB/coverage/methodology/fixtures/$FIXTURE.vcf" "$WORK/in/"
  "$PYTHON" "$RDFIZER/vcf_rdfizer.py" -m full -i "$WORK/in/$FIXTURE.vcf" \
    --sample-representation "$PROFILE" --representations none --rdf-compression none \
    --no-progress --quiet -I rq3-vcf-rdfizer -v "$CONVERTER_TAG" -o "$WORK/converted/$PROFILE"
else
  say "Reusing the converted graph already in $WORK"
fi
cp "$GRAPH" "$OUT/$FIXTURE.nt.gz"

# ------------------------------------------------------------------- check ---
say "Joining the annotations and checking the answers"
RESULTS_DIR="$OUT" "$PYTHON" "$HERE/check.py" "$GRAPH" | tee "$OUT/check.txt"

# ------------------------------------------------------------- provenance ----
"$PYTHON" - "$VOCAB_TAG" "$(git -C "$VOCAB" rev-parse HEAD)" \
             "$CONVERTER_TAG" "$(git -C "$RDFIZER" rev-parse HEAD)" \
             "$CONVERTER_IMAGE@$CONVERTER_DIGEST" "$FIXTURE" "$PROFILE" <<'PY' > "$OUT/run.json"
import datetime, json, platform, sys

vtag, vcommit, ctag, ccommit, cimage, fixture, profile = sys.argv[1:8]

def pkg(name):
    try:
        import importlib.metadata as md
        return md.version(name)
    except Exception:
        return None

json.dump({
    "ranAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "machine": {"system": platform.platform(), "arch": platform.machine()},
    "tooling": {"python": platform.python_version(), "rdflib": pkg("rdflib")},
    "pinned": {
        "vocabulary": {"repository": "https://github.com/ecrum19/vcf-core-vocabulary",
                       "tag": vtag, "commit": vcommit},
        "converter": {"repository": "https://github.com/ecrum19/VCF-RDFizer",
                      "tag": ctag, "commit": ccommit, "image": cimage},
    },
    "case": {"fixture": f"coverage/methodology/fixtures/{fixture}.vcf",
             "sampleProfile": profile,
             "annotations": "inputs/annotations.ttl (synthetic, labelled as such in the file)"},
}, sys.stdout, indent=1, sort_keys=True)
print()
PY

say "Done"
printf 'Results: %s\n' "$OUT"
