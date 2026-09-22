"""Generate the RQ1 coverage figure from recorded results as PDF, SVG, and PNG."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE.parent / "figures"
data = json.loads((ROOT / "RQ1/results/summary.json").read_text())["byVersion"]
versions = sorted({r["version"] for r in data})
rows = []
for version in versions:
    expanded = next(r for r in data if r["version"] == version and r["profile"] == "expanded")
    condensed = next(r for r in data if r["version"] == version and r["profile"] == "condensed")
    assert expanded["denominator"] == condensed["denominator"]
    assert expanded["preservation"] == condensed["preservation"] == expanded["structure"]
    assert expanded["structure"]["not-demonstrated"] == expanded["structure"]["partial"] == 0
    assert condensed["structure"]["partial"] == 0
    both = condensed["structure"]["demonstrated"]
    expanded_only = expanded["structure"]["demonstrated"] - both
    unassessed = expanded["structure"]["unassessed"]
    assert condensed["structure"]["unassessed"] == unassessed
    assert expanded_only == condensed["structure"]["not-demonstrated"]
    assert both + expanded_only + unassessed == expanded["denominator"]
    rows.append((version, expanded["denominator"], both, expanded_only, unassessed))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "svg.fonttype": "none", "pdf.fonttype": 42})
blue, orange, grey = "#286581", "#EABD78", "#E4E7E9"
fig = plt.figure(figsize=(6.3, 2.35), facecolor="white")
ax = fig.add_axes((0.22, 0.248, 0.73, 0.519))
fig.legend(
    handles=[Patch(facecolor=blue), Patch(facecolor=orange, edgecolor="#986A30", hatch="///"), Patch(facecolor=grey)],
    labels=["Direct retrieval:\nboth profiles", "Direct retrieval:\nexpanded only", "Not assessed"],
    loc="upper left", bbox_to_anchor=(0.012, 0.933), ncol=3, frameon=False,
    fontsize=8.5, handlelength=1.8, columnspacing=3.0, borderaxespad=0,
)
for y, (version, total, *counts) in enumerate(rows):
    left = 0.0
    for count, color, hatch in zip(counts, (blue, orange, grey), (None, "///", None)):
        width = 100 * count / total
        ax.barh(y, width, left=left, height=0.64, color=color,
                edgecolor="#986A30" if hatch else "white", linewidth=0.5, hatch=hatch)
        ax.text(left + width / 2, y, str(count), ha="center", va="center", fontsize=9,
                color="white" if color == blue else "#20262B", weight="medium",
                bbox=dict(facecolor=color, edgecolor="none", pad=0.55) if hatch else None)
        left += width
ax.set_yticks(range(len(rows)), [f"VCF {v}  (n = {n})" for v, n, *_ in rows])
ax.set_ylim(len(rows) - 0.45, -0.55)
ax.set_xlim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.tick_params(axis="y", length=0, pad=8)
ax.tick_params(axis="x", length=3, color="#9AA2A8", labelsize=8)
for name, spine in ax.spines.items():
    spine.set_visible(name == "bottom")
ax.spines["bottom"].set_color("#9AA2A8")
ax.set_xlabel("Share of requirements applicable to each VCF version", fontsize=8.5, labelpad=5)
OUTPUT.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT / "requirement-coverage.pdf")
fig.savefig(OUTPUT / "requirement-coverage.svg")
fig.savefig(OUTPUT / "requirement-coverage.png", dpi=200)
plt.close(fig)
print("Verified (version, applicable, direct in both, direct in expanded only, unassessed):")
for row in rows:
    print(row)
