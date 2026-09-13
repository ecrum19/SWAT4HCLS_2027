#!/bin/sh
# W4 reproduction. Run from the repository root on a machine with Docker.
#
#   sh w4/run.sh <vcf-core-vocabulary checkout> <VCF-RDFizer checkout> <workdir>
#
# Converts the pinned fixture, then checks the integration query against the
# answers authored in w4/expected.json. Exits non-zero if they differ.
set -e
VOCAB="${1:?path to a vcf-core-vocabulary checkout}"
RDFIZER="${2:?path to a VCF-RDFizer checkout}"
WORK="${3:-./w4-run}"
IMAGE="${IMAGE:-ecrum19/vcf-rdfizer}"
TAG="${TAG:-latest}"
PYTHON="${PYTHON:-python3}"

FIXTURE="$VOCAB/coverage/methodology/fixtures/local-alleles-v4.5.vcf"
mkdir -p "$WORK/in"
cp "$FIXTURE" "$WORK/in/"

# Expanded profile: the per-sample value items the query walks exist only there.
"$PYTHON" "$RDFIZER/vcf_rdfizer.py" -m full -i "$WORK/in/local-alleles-v4.5.vcf" \
  --sample-representation expanded --representations none --rdf-compression none \
  --no-progress -I "$IMAGE" -v "$TAG" -o "$WORK/out"

"$PYTHON" w4/check.py "$WORK/out/local-alleles-v4.5/local-alleles-v4.5.nt.gz"
