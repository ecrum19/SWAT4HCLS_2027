"""Calculate the Section 3 statement counts for the expanded and condensed profiles.

The manuscript's scaling example (1,000 records across 2,500 samples) is too
large to materialize in memory, so it is calculated rather than measured:
small files are materialized with the pinned VCF Core materializer, the number
of statements per record, per sample column and per (record, sample) cell is
solved for exactly, and those counts are extrapolated. Linearity is checked on a
further file before extrapolating, so a non-linear producer fails loudly.

Every record copies line 9 of Listing 1 (two ALT alleles, one local allele) and
every sample carries S1's value from that line, using the FORMAT column
GT:LAA:LAD. The counts are statements, not bytes: each condensed vector literal
still holds one value per sample.

Needs rdflib and the vocabulary clone that RQ1/run.sh fetches into
.artifacts/; set ARTIFACTS to use another location.
"""
from pathlib import Path
import itertools
import os
import sys
import tempfile

VOCAB_TAG = "v2.1.3"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARTIFACTS = Path(os.environ.get("ARTIFACTS", REPO / ".artifacts"))
MATERIALIZER = ARTIFACTS / f"vcf-core-vocabulary-{VOCAB_TAG}" / "scripts"
if not (MATERIALIZER / "vcf_examples.py").exists():
    sys.exit(f"Materializer not found at {MATERIALIZER}; run `sh RQ1/run.sh` first to fetch {VOCAB_TAG}.")
sys.path.insert(0, str(MATERIALIZER))
from vcf_examples import materialize  # noqa: E402

RECORDS, SAMPLES = 1000, 2500
HEADER = """##fileformat=VCFv4.5
##reference=https://example.org/reference.fa
##contig=<ID=chr1,length=100000>
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=LAA,Number=.,Type=Integer,Description="Local ALT indices">
##FORMAT=<ID=LAD,Number=LR,Type=Integer,Description="Local read depths">
"""
SAMPLE_VALUE = "2/2:2:20,30"


def statements(records, samples, profile, workdir):
    path = workdir / f"r{records}-s{samples}.vcf"
    columns = "\t".join(f"S{i}" for i in range(1, samples + 1))
    lines = [f"chr1\t{pos}\t.\tG\tA,C\t.\t.\t.\tGT:LAA:LAD\t" + "\t".join([SAMPLE_VALUE] * samples)
             for pos in range(1, records + 1)]
    path.write_text(HEADER + f"#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{columns}\n"
                    + "\n".join(lines) + "\n")
    return len(materialize(path, profile))


def coefficients(profile, workdir):
    t = {(r, s): statements(r, s, profile, workdir) for r, s in itertools.product((1, 2), (1, 2))}
    cell = t[2, 2] - t[1, 2] - t[2, 1] + t[1, 1]
    record = t[2, 1] - t[1, 1] - cell
    sample = t[1, 2] - t[1, 1] - cell
    fixed = t[1, 1] - cell - record - sample
    predicted = fixed + 3 * record + 3 * sample + 9 * cell
    measured = statements(3, 3, profile, workdir)
    assert predicted == measured, f"{profile}: not linear ({predicted} predicted, {measured} measured)"
    return fixed, record, sample, cell


with tempfile.TemporaryDirectory() as tmp:
    print(f"VCF Core {VOCAB_TAG} materializer; {RECORDS:,} records x {SAMPLES:,} samples, FORMAT GT:LAA:LAD")
    for profile in ("expanded", "condensed"):
        fixed, record, sample, cell = coefficients(profile, Path(tmp))
        total = fixed + record * RECORDS + sample * SAMPLES + cell * RECORDS * SAMPLES
        print(f"{profile:9s} fixed={fixed} per-record={record} per-sample={sample} per-cell={cell}"
              f"  -> {total:,} statements ({total:.2e})")
