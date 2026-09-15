#!/usr/bin/env bash
# Re-run the two coverage assessments behind RQ1.
#
#     sh RQ1/run.sh [workdir]
#
# Needs: git, python3 with rdflib. No npm, and no local copy of the vocabulary --
# it is cloned from GitHub at the pinned tag below.
#
# Why it runs inside the clone rather than here: assess.py fingerprints its
# inputs by path relative to the vocabulary repository root, and the recorded
# human review acceptances are keyed to those fingerprints. Running the copies
# in this directory from a different root would report every requirement as
# unreviewed, which would be an artefact of where the files sit, not a finding.
# So the clone is what executes, and this directory is what you read.
#
# The copies here are checked against the clone before anything runs, so drift
# between the two is reported rather than discovered later.
set -euo pipefail

VOCAB_REPO="https://github.com/ecrum19/vcf-core-vocabulary.git"
VOCAB_TAG="v2.1.2"

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
WORK="${1:-$HERE/work}"
# Pinned checkouts are shared by every RQ script and cached at the repository
# root, so running RQ1 then RQ2 then RQ3 fetches each repository once rather
# than once per question. The tag is part of the directory name: bumping a pin
# fetches a fresh checkout instead of silently reusing the old one.
ARTIFACTS="${ARTIFACTS:-$REPO/.artifacts}"
VOCAB="$ARTIFACTS/vcf-core-vocabulary-$VOCAB_TAG"
OUT="$HERE/results"
PYTHON="${PYTHON:-python3}"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

mkdir -p "$WORK" "$OUT" "$ARTIFACTS"

# ------------------------------------------------------------------ fetch ----
say "Fetching $VOCAB_TAG from GitHub"
if [ ! -d "$VOCAB/.git" ]; then
  git clone --quiet --depth 1 --branch "$VOCAB_TAG" "$VOCAB_REPO" "$VOCAB"
fi
printf '  %s at %s\n' "$VOCAB_TAG" "$(git -C "$VOCAB" rev-parse --short HEAD)"

# ------------------------------------------------------------- drift check ---
# Every file duplicated here must be byte-identical to the pinned tag. If one is
# not, the copy is stale and the numbers below would not describe it.
say "Checking the copies in this directory against the tag"
drift=0
while IFS= read -r rel; do
  mine="$HERE/$rel"
  theirs="$VOCAB/coverage/$rel"
  [ -f "$theirs" ] || { printf '  missing upstream: %s\n' "$rel"; drift=1; continue; }
  cmp -s "$mine" "$theirs" || { printf '  differs: %s\n' "$rel"; drift=1; }
done < <(cd "$HERE" && find methodology vcf45-inventory -type f \
           -not -path '*/generated/*' -not -name '.DS_Store' | sort)
if [ "$drift" -ne 0 ]; then
  printf '\n\033[31mThe copies here no longer match %s. Re-copy them before trusting a run.\033[0m\n' "$VOCAB_TAG" >&2
  exit 1
fi
printf '  all copies match\n'

# --------------------------------------------------------------- assessments -
say "Specification-derived assessment (94 requirements)"
(cd "$VOCAB" && "$PYTHON" coverage/methodology/scripts/assess.py check --require-reviewed) \
  | tee "$OUT/methodology-check.txt"

say "Curated VCF 4.5 inventory (104 constructs)"
(cd "$VOCAB" && "$PYTHON" coverage/vcf45-inventory/check_serialization.py) \
  | tee "$OUT/serialization.txt"
(cd "$VOCAB" && "$PYTHON" coverage/vcf45-inventory/report.py) \
  | tee "$OUT/inventory-report.txt"

# ------------------------------------------------------------------ collect --
say "Collecting results"
for f in summary.json provenance.json review-queue.json; do
  cp "$VOCAB/coverage/methodology/generated/$f" "$OUT/$f" 2>/dev/null || true
done
cp "$VOCAB/coverage/vcf45-inventory/generated/report.json"        "$OUT/inventory-report.json" 2>/dev/null || true
cp "$VOCAB/coverage/vcf45-inventory/generated/serialization.json" "$OUT/serialization.json"    2>/dev/null || true

"$PYTHON" - "$OUT" "$VOCAB_TAG" "$(git -C "$VOCAB" rev-parse HEAD)" <<'PY' > "$OUT/run.json"
import datetime, json, platform, subprocess, sys

out, tag, commit = sys.argv[1:4]

def pkg(name):
    try:
        import importlib.metadata as md
        return md.version(name)
    except Exception:
        return None

json.dump({
    "ranAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "vocabulary": {"repository": "https://github.com/ecrum19/vcf-core-vocabulary",
                   "tag": tag, "commit": commit},
    "machine": {"system": platform.platform(), "arch": platform.machine()},
    "tooling": {"python": platform.python_version(), "rdflib": pkg("rdflib"),
                "pyshacl": pkg("pyshacl")},
}, sys.stdout, indent=1, sort_keys=True)
print()
PY

say "Done"
printf 'Results: %s\n' "$OUT"
