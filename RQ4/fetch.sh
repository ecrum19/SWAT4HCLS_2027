#!/usr/bin/env bash
# RQ4 -- re-fetch the four inspected artifacts and record what came back.
#
#     sh RQ4/fetch.sh [workdir]
#
# RQ4 is a reading exercise, not an executed test: the verdicts in EXPERIMENT.md
# come from a person inspecting four published artifacts. This script exists so
# that inspection can be audited. It retrieves the same four artifacts and writes
# a SHA-256 for each, so a reader can confirm they are looking at what we looked
# at -- or see that an artifact has changed since.
#
# It checks nothing and scores nothing. A changed digest is information, not a
# failure, which is why this never exits non-zero on a mismatch.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-$HERE/work}"
OUT="$HERE/artifacts"
mkdir -p "$WORK" "$OUT"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# GVO serves plain HTTP only; an https:// attempt fails, which is worth keeping
# in the record because it is why an earlier inspection could not read it.
fetch() {  # fetch <name> <url> [accept header]
  local name="$1" url="$2" accept="${3:-}"
  local dest="$WORK/$name"
  if [ -n "$accept" ]; then
    curl -sSL -m 60 -H "Accept: $accept" -o "$dest" "$url"
  else
    curl -sSL -m 60 -o "$dest" "$url"
  fi
  local rc=$? size digest
  size=$(wc -c < "$dest" 2>/dev/null | tr -d ' ')
  digest=$(shasum -a 256 "$dest" 2>/dev/null | cut -d' ' -f1)
  printf '  %-12s %-7s %8s bytes  %s\n' "$name" \
    "$([ "$rc" -eq 0 ] && echo ok || echo FAILED)" "${size:-0}" "${digest:0:16}"
  printf '%s\t%s\t%s\t%s\n' "$name" "$url" "${size:-0}" "${digest:-none}" >> "$OUT/digests.tsv"
}

say "Retrieving the four inspected artifacts"
: > "$OUT/digests.tsv"
printf 'artifact\turl\tbytes\tsha256\n' > "$OUT/digests.tsv"

fetch gfvo.xml \
  "https://raw.githubusercontent.com/BioInterchange/Ontologies/master/gfvo.xml"
fetch hero.ttl \
  "https://hereditary.dei.unipd.it/ontology/genomics/schema/hero_genomics.ttl"
fetch gvo.ttl \
  "http://genome-variation.org/resource/gvo" "text/turtle"
fetch vcf2rdf-terms.json \
  "https://api.github.com/repos/diegopenhanut/vcf-resources/git/trees/HEAD?recursive=1"

say "Recorded"
printf 'Digests: %s\n' "$OUT/digests.tsv"
printf 'Copies:  %s\n' "$WORK"
