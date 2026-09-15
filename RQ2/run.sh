#!/usr/bin/env bash

# Needs: git, docker, python3 (with rdflib), ~2 GB disk, ~20 minutes.
# Everything else -- the vocabulary, the converter, the container images -- is
# fetched at a pinned revision or digest. Nothing depends on the machine that
# produced the published numbers.
#
# Output lands in RQ2/runs/<UTC timestamp>/:
#
#     env.json      what this machine is, and what was pinned
#     steps.jsonl   every command run, with exit code and duration
#     logs/         stdout+stderr of each step
#     graphs/       the converted RDF each result was computed from
#     results/      the JSON each analysis wrote
#     SUMMARY.md    the headline numbers, ready to read
set -euo pipefail

# ---------------------------------------------------------------- pins --------
VOCAB_REPO="https://github.com/ecrum19/vcf-core-vocabulary.git"
VOCAB_TAG="v2.1.2"

RDFIZER_REPO="https://github.com/ecrum19/VCF-RDFizer.git"

# The converter is a wrapper revision plus the image it drives, pinned by digest
# so a moved tag cannot change what runs.
CONVERTER_TAG="v3.0.3"
CONVERTER_IMAGE="ecrum19/vcf-rdfizer"
CONVERTER_DIGEST="sha256:31f1361b6d66591a43e706caeba7c079f498a6ae69d9d279effa82d26beaf57a"

# Fixtures are not listed here. They are derived below from the assessment's own
# cases.json, so every fixture the assessment tests is replayed against the
# converter. A hand-kept list silently narrows the comparison as the assessment
# grows, which is what happened before: ten of the thirty-eight were replayed
# and the omission was invisible in the reported figures.
PROFILES="expanded condensed"

# ------------------------------------------------------------- layout --------
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
WORK="${1:-$HERE/work}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="$HERE/runs/$STAMP"

mkdir -p "$WORK" "$RUN"/{logs,results,graphs}
STEPS="$RUN/steps.jsonl"
: > "$STEPS"

PYTHON="${PYTHON:-python3}"

say()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[31mFAILED: %s\033[0m\n' "$*" >&2; exit 1; }

# step <name> <command...> -- runs it, logs it, records timing and exit code.
step() {
  local name="$1"; shift
  local log="$RUN/logs/$name.log"
  local started ended rc
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local t0=$SECONDS
  printf '  %-34s ' "$name"
  if "$@" >"$log" 2>&1; then rc=0; else rc=$?; fi
  ended="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local secs=$((SECONDS - t0))
  "$PYTHON" - "$name" "$started" "$ended" "$secs" "$rc" "$log" "$@" <<'PY' >> "$STEPS"
import json, sys
name, started, ended, secs, rc, log, *cmd = sys.argv[1:]
print(json.dumps({"step": name, "started": started, "ended": ended,
                  "seconds": int(secs), "exit": int(rc),
                  "log": log.split("/runs/", 1)[-1],
                  "command": cmd}, sort_keys=True))
PY
  if [ "$rc" -eq 0 ]; then printf 'ok   %3ss\n' "$secs"
  else printf 'FAIL %3ss  (see %s)\n' "$secs" "$log"; fail "$name"; fi
}

# ------------------------------------------------------ pinned checkouts ------
say "Fetching pinned artifacts into $WORK"

clone_at() {  # clone_at <repo> <tag> <dir>
  [ -d "$3/.git" ] || git clone --quiet --depth 1 --branch "$2" "$1" "$3"
  git -C "$3" rev-parse HEAD > /dev/null
}

step vocab-checkout   clone_at "$VOCAB_REPO"   "$VOCAB_TAG"     "$WORK/vocab"
step rdfizer-checkout clone_at "$RDFIZER_REPO" "$CONVERTER_TAG" "$WORK/rdfizer"
step image-pull       docker pull --quiet "$CONVERTER_IMAGE@$CONVERTER_DIGEST"

# Tag the pulled digest so the wrapper, which takes image+version, can find it.
docker tag "$CONVERTER_IMAGE@$CONVERTER_DIGEST" "reproduce-vcf-rdfizer:$CONVERTER_TAG" >/dev/null

VOCAB="$WORK/vocab"
FIXDIR="$VOCAB/coverage/methodology/fixtures"

# Every fixture any case refers to, in a stable order.
FIXTURES="$("$PYTHON" - "$VOCAB" <<'PY'
import json, pathlib, sys
cases = json.loads((pathlib.Path(sys.argv[1]) /
                    "coverage/methodology/inputs/cases.json").read_text())
print(" ".join(sorted({pathlib.Path(c["fixture"]).stem for c in cases})))
PY
)"
printf '  %s fixtures referenced by the assessment\n' "$(printf '%s' "$FIXTURES" | wc -w | tr -d ' ')"

# ------------------------------------------------------------ environment -----
say "Recording the environment"
"$PYTHON" - "$RUN" "$WORK" "$VOCAB_TAG" "$CONVERTER_TAG" \
             "$CONVERTER_IMAGE@$CONVERTER_DIGEST" <<'PY' > "$RUN/env.json"
import json, os, platform, subprocess, sys, datetime

run, work, vtag, ctag, cimg = sys.argv[1:6]

def sh(*c):
    try:
        return subprocess.run(c, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return None

def git(repo, *a):
    return sh("git", "-C", repo, *a)

def pkg(name):
    try:
        import importlib.metadata as md
        return md.version(name)
    except Exception:
        return None

env = {
    "recordedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "machine": {
        "hostname": platform.node(),
        "system": f"{platform.system()} {platform.release()}",
        "platform": platform.platform(),
        "arch": platform.machine(),
        "cpus": os.cpu_count(),
        "osRelease": (sh("sh", "-c", "grep PRETTY_NAME /etc/os-release | cut -d= -f2-") or "").strip('"'),
        "memoryGB": (lambda m: round(int(m) / 1048576) if m and m.isdigit() else None)(
            (sh("sh", "-c", "grep MemTotal /proc/meminfo | awk '{print $2}'") or "")),
    },
    "tooling": {
        "python": platform.python_version(),
        "rdflib": pkg("rdflib"),
        "pyshacl": pkg("pyshacl"),
        "docker": sh("docker", "version", "--format", "{{.Server.Version}}"),
        "git": (sh("git", "--version") or "").replace("git version ", ""),
    },
    "pinned": {
        "vocabulary": {
            "repository": "https://github.com/ecrum19/vcf-core-vocabulary",
            "tag": vtag,
            "commit": git(os.path.join(work, "vocab"), "rev-parse", "HEAD"),
        },
        "converter": {
            "repository": "https://github.com/ecrum19/VCF-RDFizer",
            "tag": ctag,
            "commit": git(os.path.join(work, "rdfizer"), "rev-parse", "HEAD"),
            "image": cimg,
        },
    },
    "specifications": json.loads(
        open(os.path.join(work, "vocab", "coverage/methodology/sources.lock.json")).read()),
}
json.dump(env, sys.stdout, indent=1, sort_keys=True)
print()
PY

# ------------------------------------------------------------ conversions -----
convert_set() {
  local out="$WORK/converted"
  mkdir -p "$out/in"
  for f in $FIXTURES; do cp "$FIXDIR/$f.vcf" "$out/in/"; done
  for f in $FIXTURES; do
    for p in $PROFILES; do
      [ -f "$out/$p/$f/$f.nt.gz" ] && continue
      "$PYTHON" "$WORK/rdfizer/vcf_rdfizer.py" -m full -i "$out/in/$f.vcf" \
        --sample-representation "$p" --representations none --rdf-compression none \
        --no-progress --quiet -I reproduce-vcf-rdfizer -v "$CONVERTER_TAG" -o "$out/$p" \
        || return 1
    done
  done
}

say "Converting $(printf '%s' "$FIXTURES" | wc -w | tr -d ' ') fixtures x 2 profiles with $CONVERTER_TAG (this is the slow part)"
step convert convert_set

# ---------------------------------------------------------------- analyses ----
say "Running the analyses"
export VCF_CORE_VOCAB="$VOCAB"
export RESULTS_DIR="$RUN/results"

step cross-producer "$PYTHON" "$HERE/analysis/cross-producer.py" "$WORK/converted" cross-producer.json
step round-trip     "$PYTHON" "$HERE/analysis/round-trip.py"     "$WORK/converted"

step evidence-map sh -c \
  "\"$PYTHON\" \"$HERE/analysis/evidence-map.py\" \"$VOCAB\" \"$RUN/results/cross-producer.json\" \
   > \"$RUN/results/evidence-map.json\""

# The Section 5.4 profile figures use the paper's own single-record example.
mkdir -p "$WORK/example"
cp "$REPO/coverage/synthetic.vcf" "$WORK/example/"
for p in $PROFILES; do
  [ -f "$WORK/example/$p/synthetic/synthetic.nt.gz" ] && continue
  step "convert-example-$p" "$PYTHON" "$WORK/rdfizer/vcf_rdfizer.py" \
    -m full -i "$WORK/example/synthetic.vcf" --sample-representation "$p" \
    --representations none --rdf-compression none --no-progress --quiet \
    -I reproduce-vcf-rdfizer -v "$CONVERTER_TAG" -o "$WORK/example/$p"
done

step profile-figures sh -c \
  "\"$PYTHON\" \"$HERE/analysis/profile-figures.py\" \
     \"$WORK/example/expanded/synthetic/synthetic.nt.gz\" \
     \"$WORK/example/condensed/synthetic/synthetic.nt.gz\" \
     \"$VOCAB\" \"$VOCAB_TAG\" > \"$RUN/results/example-profiles.json\""

# ------------------------------------------------------------- collect --------
say "Collecting the graphs each result was computed from"
for p in $PROFILES; do
  mkdir -p "$RUN/graphs/$p"
  for f in $FIXTURES; do
    cp "$WORK/converted/$p/$f/$f.nt.gz" "$RUN/graphs/$p/$f.nt.gz"
  done
done
mkdir -p "$RUN/graphs/example"
for p in $PROFILES; do
  cp "$WORK/example/$p/synthetic/synthetic.nt.gz" "$RUN/graphs/example/$p.nt.gz"
done

# --------------------------------------------------------------- summary ------
"$PYTHON" "$HERE/summarise.py" "$RUN" > "$RUN/SUMMARY.md"

say "Done"
cat "$RUN/SUMMARY.md"
printf '\nFull run: %s\n' "$RUN"
