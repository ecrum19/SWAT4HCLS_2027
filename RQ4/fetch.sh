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

# VCF2RDF publishes one HTML page per term on GitHub Pages. What we record is
# those pages' public URLs -- each opens in a browser -- rather than the git tree
# listing recorded previously, which named blob SHAs a reader cannot resolve.
# The tree API is still used to ENUMERATE the pages, because the published index
# does not link to them; it is a means of enumeration, not the evidence itself.
VCF2RDF_BASE="https://diegopenhanut.github.io/vcf-resources/v4_2"
VCF2RDF_TREE="https://api.github.com/repos/diegopenhanut/vcf-resources/git/trees/HEAD?recursive=1"

fetch_vcf2rdf() {
  local list="$OUT/vcf2rdf-terms.tsv" tree="$WORK/vcf2rdf-tree.json"
  local pages="$WORK/vcf2rdf-pages" term url code size digest n=0 ok=0

  mkdir -p "$pages"
  curl -sSL -m 60 -o "$tree" "$VCF2RDF_TREE"

  # A term page is v4_2/<TERM>/index.html. v4_2/index.html is the section
  # landing page, not a term, and is counted separately below.
  python3 -c "
import json, sys
tree = json.load(open(sys.argv[1]))['tree']
for e in tree:
    p = e['path']
    if (e['type'] == 'blob' and p.startswith('v4_2/')
            and p.endswith('/index.html') and p.count('/') == 2):
        print(p.split('/')[1])
" "$tree" | sort > "$pages/terms.txt"

  printf 'term\turl\thttp\tbytes\tsha256\n' > "$list"
  while IFS= read -r term; do
    url="$VCF2RDF_BASE/$term/"
    code=$(curl -sSL -m 30 -o "$pages/$term.html" -w '%{http_code}' "$url")
    size=$(wc -c < "$pages/$term.html" 2>/dev/null | tr -d ' ')
    digest=$(shasum -a 256 "$pages/$term.html" 2>/dev/null | cut -d' ' -f1)
    printf '%s\t%s\t%s\t%s\t%s\n' "$term" "$url" "$code" "${size:-0}" "${digest:-none}" >> "$list"
    n=$((n + 1)); [ "$code" = "200" ] && ok=$((ok + 1))
  done < "$pages/terms.txt"

  printf '  %-12s %-7s %8s pages  %s resolved (HTTP 200)\n' \
    "vcf2rdf" "$([ "$n" -gt 0 ] && echo ok || echo FAILED)" "$n" "$ok"

  # One row in the shared record, so the four-artifact table stays complete. The
  # digest is over the listing, so any change to a term page, or to the set of
  # pages, changes it.
  digest=$(shasum -a 256 "$list" 2>/dev/null | cut -d' ' -f1)
  size=$(wc -c < "$list" | tr -d ' ')
  printf '%s\t%s\t%s\t%s\n' "vcf2rdf-terms.tsv" "$VCF2RDF_BASE/" "${size:-0}" "${digest:-none}" >> "$OUT/digests.tsv"
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
fetch_vcf2rdf

say "Recorded"
printf 'Digests: %s\n' "$OUT/digests.tsv"
printf 'Copies:  %s\n' "$WORK"
