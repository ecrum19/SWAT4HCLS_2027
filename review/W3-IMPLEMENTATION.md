# W3 — Implementation evidence

Executed 2026-09-12 against VCF-RDFizer 3.0.2 and vcfcv 2.1.1. **Superseded in part on
2026-09-14**: the three issues below were fixed and released as `v3.0.3` (`be658a2`), and the
QUAL guidance as vcfcv `v2.1.2` (`3f06d18`). Figures here are the pre-fix state; the released
measurements are in [W5-MANUSCRIPT.md](W5-MANUSCRIPT.md).

Executed 2026-09-12. Every result below comes from a run on this machine; nothing is quoted
from documentation.

## W3.1 Exact release

| | Pin |
| --- | --- |
| Converter | VCF-RDFizer **3.0.2**, tag `v3.0.2` = `b8da2ed` (= `origin/main` tip) |
| Vocabulary | VCF Core **2.1.1**, tag `v2.1.1` = `dd139f9`; local tree byte-identical |
| Container | `ecrum19/vcf-rdfizer:latest` @ `sha256:389735…fe34b978` (arm64), index `sha256:e333f889…` |
| Host | macOS 26.6.2 arm64, Python 3.14.2, Docker 29.7.2 |

Two pinning hazards, both recorded rather than worked around:

- **No versioned image tags exist.** Docker Hub serves only `ecrum19/vcf-rdfizer:latest`;
  `3.0.2`, `3.0.1`, `3.0.0` and `2.1.0` all return nothing. The host CLI pins by git tag, but
  the containerised toolchain (Flink, RMLStreamer, hdtc, pycottas, Comunica, QLever, pyshacl,
  cyvcf2, bcftools) cannot be pinned at all. Cite the image digest above, not the tag.
- **The PATH-installed `vcf-rdfizer` is 1.0.0** and lacks the `validation`, `tsv`, `index` and
  `link` modes. Every command below runs `python3 vcf_rdfizer.py` from the pinned checkout.
  The delta from tag `v3.0.2` to the local tree is `conda-recipe/meta.yaml` only (+2 lines,
  packaging), so the tree is behaviourally the tag.

## W3.2 Emitted representation

Static: 148 VCF Core local names are constructed in the converter's Python; **all 148 are
declared in vcfcv 2.1.1**. The RML rules reference 65 names, all resolving except the
documented sentinel `vcfc:VCFVersionFile`, which the wrapper rewrites per input — confirmed in
the generated rules, where it became `vcfc:VCF45File` with zero sentinel occurrences left.

Emitted (`synthetic.vcf`, VCF 4.5, 1 record, 3 samples):

| | Expanded | Condensed |
| --- | ---: | ---: |
| Triples | 225 | 159 |
| Distinct VCF Core terms | 79 | 69 |
| Terms not declared in vcfcv 2.1.1 | **0** | **0** |

Profile shapes are the ones the vocabulary defines: expanded emits `SampleCall` ×3 and
`FormatFieldValue` ×6; condensed emits one `CohortCallMatrix` and two `FormatValueVector`.
Missing values carry the documented datatype — `"."^^vcfc:Null` on the absent DP, ID and INFO;
`preflight_missing_token_conformance` passed with zero plain-dot literals under
`--strict-conformance`. No-calls are structured, not just preserved: SAMPLE3's genotype has two
`GenotypeAlleleCall` resources with `isNoCall true` and no `calledAllele`.

## W3.3 Reproduction

```sh
python3 vcf_rdfizer.py -m full -i synthetic.vcf \
  --sample-representation expanded --representations none \
  --rdf-compression none -o out-expanded          # exit 0; repeat with condensed
```

Converter semantic validation (`-m validation`, Comunica): `comparisonStatus: PASS`, engine
agreement true, all preflights PASS, 225 parsed triples, 0 duplicates.

SHACL against the vocabulary's published shapes:

| Configuration | Expanded | Condensed |
| --- | --- | --- |
| `--shacl-shapes shacl/vcf-core-vocabulary.shacl.ttl` | **FAIL, 5 violations** | not run |
| Same shapes + `ont_graph` + `inference='rdfs'` (what `tests/validate_shacl.py` does) | conforms | conforms |
| `shacl/vcf-4.5.shacl.ttl`, same configuration | conforms | conforms |

The 5 violations are an artefact of the converter's SHACL configuration, not of the data. It
passes the shapes file alone, with no ontology graph and no inference, so `sh:class vcfc:Allele`
cannot see that `AltAllele`/`ReferenceAllele` are subclasses, and `sh:class
vcfc:RepresentationProfile` cannot see that `vcfc:ExpandedRepresentation` is one. Loading the
ontology the way the vocabulary's own test does makes the same graph conform.

## W3.4 Support boundary

VCF-RDFizer 3.0.2 emits the VCF Core namespace and, on this input, emits only terms declared in
vcfcv 2.1.1, in both sample profiles, conforming to the shared and VCF 4.5 shape profiles. That
is the established claim. It does **not** establish coverage of the other 388 declared terms,
of VCF 4.1–4.4, or of any larger or more irregular input. The converter declares no vocabulary
version, so the relationship is established only by the behaviour recorded here.

### Three issues for the converter — all fixed 2026-09-12

1. **`--shacl-shapes` reported false violations** against the vocabulary's own shapes. Fixed:
   the SHACL layer now loads the vocabulary with RDFS inference, via a new `--shacl-ontology`
   that defaults to the bundle beside the shapes in a vocabulary checkout. Verified directly
   on this graph: FAIL/5 without the ontology, PASS/0 with it.
2. **`docs/validation.md` named the retired `shacl/vcf-rdfizer-vocabulary.shacl.ttl`.** Fixed to
   `vcf-core-vocabulary.shacl.ttl`, with a paragraph explaining why the ontology is required.
3. **No typed FORMAT value accessors.** The typed-companion helper existed but was wired to
   INFO values only. Fixed: a single, non-missing Integer/Float FORMAT cell now also gains
   `vcfc:fieldValueInteger` / `vcfc:fieldValueDecimal`. Missing values and String fields
   correctly gain none.

Landed in `0b00b8f` on `main` (source) and [#11](https://github.com/ecrum19/VCF-RDFizer/pull/11)
(the matching fixture oracle). Full suite: 647 tests, OK.

**Still not done as of 2026-09-14:** `src/validation/` is baked into the image, and the newest
published image is 3.0.2, which predates these fixes, so it must be rebuilt before an
end-to-end `-m validation` run passes. Against the published image the
new graph reports `MISMATCH` with `extraRows: [{fieldValueInteger, 2}]`.

### Consequence for the manuscript

Listing~\ref{lst:depth}, the depth query, returned **no rows** against converter output before
the fix above: every hop resolved except the last, which asks for `vcfc:fieldValueInteger`. With
the fix it returns `SAMPLE1, 42` against real converter output, and the expanded graph goes from
225 to 227 triples, still with no undeclared terms and still conforming to both shape profiles.

The illustration counts remain hand-authored. The paper's "172 expanded and 149 condensed
triples" are the hand-authored files; the converter produces **225 and 159** for the same input,
because it also materialises allele resources and per-sample genotype and allele-call resources
that the illustration omits. Either the illustration is relabelled as hand-authored, or it is
regenerated from the converter and the query is rewritten against `vcfc:fieldValue` — a W4/W5
decision, not one W3 should make silently.
