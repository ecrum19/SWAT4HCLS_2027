#!/bin/sh
# Convert the W2 fixture subset with VCF-RDFizer, both sample profiles.
# Outputs land in the scratchpad: they are large, regenerable, and not evidence
# on their own -- the evidence is cross-producer.py's comparison of them.
set -e
VOCAB=/Users/eliascrum/PhD_Things/vcf-rdfizer-vocabulary
RDFIZER=/Users/eliascrum/PhD_Things/vcf-rdfizer/vcf_rdfizer.py
OUT="$1"
FIXTURES="basic-v4.1 basic-v4.2 basic-v4.3 basic-v4.4 basic-v4.5 \
header-audit-v4.5 features-v4.5 local-alleles-v4.5 \
tandem-repeats-v4.4 tandem-repeats-v4.5"

mkdir -p "$OUT/in"
for f in $FIXTURES; do cp "$VOCAB/coverage/methodology/fixtures/$f.vcf" "$OUT/in/"; done

for f in $FIXTURES; do
  for profile in expanded condensed; do
    if [ -f "$OUT/$profile/$f/$f.nt.gz" ] || [ -f "$OUT/$profile/$f/$f.nt" ]; then echo "skip $f $profile"; continue; fi
    echo "=== $f $profile ==="
    python3 "$RDFIZER" -m full -i "$OUT/in/$f.vcf" \
      --sample-representation "$profile" --representations none \
      --rdf-compression none --no-progress -o "$OUT/$profile" >/dev/null 2>&1 \
      && echo "  ok" || echo "  FAILED $f $profile"
  done
done
echo "ALL DONE"
