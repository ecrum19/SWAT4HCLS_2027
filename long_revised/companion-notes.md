# Companion notes for the shortened manuscript

These notes preserve supporting detail that was cut from a shorter version of the manuscript.

## RQ1: source audit and declaration registries

The audit partitions the five VCF specification sources into **344 section intervals**, from which **1,134 passage-level assertions** were authored. Assertions are classified as targeted (149: at least one linked case and no recorded test gap), partial (154: linked cases with a recorded gap), or untested (831: no case). This classification records the presence of tests, not their outcome, and is not the requirement-coverage score.

The assertions contain **385 distinct statements**, with 86 repeated verbatim across all five versions. A cited case must exist, share the assertion's version, name a linked requirement, and supply a query and expected answer. The original audit illustrates this distinction with a tested contig declaration, partially tested record position/identity/order, and an untested assembly/BKPTID relation.

The 94 requirements have 56 specific intent descriptions, 29 generic descriptions, and nine explicit unassessed markers. Test selection was influenced by availability of defensible specification examples; nine of 38 fixtures reproduce such examples byte for byte. The source audit therefore does not establish that the tested subset represents every difficult VCF interpretation problem.

The version registries contain **40, 40, 67, 78, and 122** explicit reserved definitions for VCF 4.1–4.5. The comparable Number/Type rows extracted from specification declarations and tables number **31, 31, 69, 79, and 123**, totaling **333**, all matching the registries. These populations differ: VCF 4.1 and 4.2 each also define 29 reserved keys in prose without Number and, for INFO, without Type. They are inventoried but not included in the comparable-row result. CNL/CNP illustrate a separate declaration–prose inconsistency: Number=G accompanies a description ordered by copy number.

The manuscript records specification example problems reported as [hts-specs#869](https://github.com/samtools/hts-specs/issues/869), [#870](https://github.com/samtools/hts-specs/issues/870) and [#871](https://github.com/samtools/hts-specs/issues/871), alongside the previously reported [#868](https://github.com/samtools/hts-specs/issues/868). These links identify the reports; their live resolution status was not rechecked for this shortening. Disputed interpretations left without tests remain in the coverage denominator.

For VCF 4.5, 40 requirements remain unassessed: 37 await fixtures and queries, R45 needs further interpretation, and R67–R68 require all reserved INFO/FORMAT keys to be covered. The 18 condensed-structure case failures affect 14 requirements; those counts must not be conflated. Across all versions, 41 of 94 requirements have no case.

The materializer emits 200 distinct vocabulary terms; the 79 queries reference 125 terms, leaving 81 emitted terms without a query reference. These inventories describe the assessed implementation and do not establish correctness for every term.

## RQ1: curated inventory

All 104 inventoried VCF 4.5 constructs have curated preservation and structure evidence. Enforcement evidence is present for 87, with less complete categories as follows:

| Category | With enforcement / inventoried |
| --- | ---: |
| File and header structure | 17/20 |
| Lexical and encoding rules | 6/7 |
| FORMAT and genotype | 16/21 |
| Structural variation, repeats, and gVCF | 8/16 |

Evidence types for the 104 classifications are queries (7), regression probes (23), shapes or decoded checks (62), and materialized fixtures (12). These are evidence categories behind curated judgments, not 104 executed retrieval tests. Separately, 17 fixtures pass the byte-level checks; this does not claim byte-for-byte reconstruction or BCF binary-layout coverage.

## RQ2: execution and comparison details

The evaluated converter is VCF-RDFizer 3.0.3, commit `be658a2`, using the container whose digest begins `sha256:31f1361b`; the authoritative pin and full digest are recorded in `../PINS.md`. It executes RML mappings through RMLStreamer, independently of the Python materializer's triple-construction code. Shared authorship remains a limitation.

All fixtures are selected from the case register and converted in both profiles. Materializer graphs are rebuilt during the run. Recorded witnesses act as a consistency guard; a discrepancy aborts the run instead of silently substituting stale graphs. Queries and expected answers are reused unchanged. Fragment-bearing resource IRIs are compared by fragment alone to accommodate different bases, which can hide an incorrect namespace.

Two scripts reconstruct logical source content:

- `../RQ2/analysis/round-trip.py` recovers CHROM, POS, ID, REF, ALT, QUAL, FILTER, and sample GT. Alleles are ordered through allele indices and values; genotype reconstruction uses ordered allele-call resources and per-call phase indicators.
- `../RQ2/analysis/field-round-trip.py` recovers headers by source line number, comparing key and verbatim value, and reconstructs INFO entries and non-GT FORMAT subfields from ordered value items.

Neither reconstruction uses the preserved-source properties `infoRaw`, `sampleDataRaw`, or `genotypeString`. Six perturbations were checked individually: changing a phase indicator, deleting an allele call, corrupting an INFO item, deleting a FORMAT value, altering a header value, and deleting a header line. Each produces one mismatch. Leading phase notation is normalized for VCF 4.4 onward; intervening phase, allele order, missing calls, and ploidy are still compared exactly. Condensed round-tripping is not evaluated because the required accessor is not emitted (R21).

For R27, the expanded materializer writes the empty LAA field and `fieldValue ""`; the converter writes its resource and declaration link without a value triple. The reconstructed cell is consequently `0/0:?:30:0`. Empty LAA means reference-only local alleles, so present-and-empty must remain distinguishable from present-without-value. The associated LAD value retains its allele link. The condensed query comparison also records a difference in empty-list encoding (`""` versus `"."`). These are complementary observations of the same requirement across the assessed representations.

An earlier comparison led to the local-allele association correction and eight further repairs. The pinned release additionally emits ID, FILTER, field-index, and per-allele phase-indicator accessors, and recognizes 30 base-modification aliases. This implementation history is separate from the 15 requirements with disagreements in the evaluated release.

The small worked example produces 242 expanded and 168 condensed triples, using 93 and 80 VCF Core terms respectively. All used terms resolve in release 2.1.2. The vocabulary's recorded validation run accepts 21 fixtures and includes a negative control, with 101 regression tests. These checks do not establish performance at cohort scale, complete support for all 467 declared terms, or every historical VCF version.

## RQ3: deterministic integration example

The input is `local-alleles-v4.5.vcf`, with four sites each represented locally and globally, one sample, and approximately 1,400 expanded triples. The local annotation snapshot is `../RQ3/inputs/annotations.ttl`, containing five invented flagged alterations. No shared identifier is created before the join.

The complete query compares all eight projected fields against expected answers authored before execution. The threshold is LAD >= 20, selected to distinguish the correct interpretation from a positional misreading. Depth comparisons are textual, so `"30"` and `"30.0"` differ. All returned rows must cite the actual input file, checked against the supplied path rather than graph-internal consistency alone.

The three exclusions are checked individually. ALT 1 is outside the sample's LAA subset for `chr1:1 G>A` and `chr1:2 A>C`; `chr1:3 C>G` is outside `LAA=3` and its positional value would also fall below threshold. The first two exclusions change under a positional misreading. These synthetic observations do not carry biological or clinical significance.

## RQ4: artifact and alignment detail

The inspection uses GFVO (`gfvo.xml`), HERO-Genomics (`hero_genomics.ttl`), GVO (versionInfo 2021-11-18), and 58 published VCF2RDF term pages. `../RQ4/fetch.sh` records artifact digests, with VCF2RDF pages recorded in `../RQ4/artifacts/vcf2rdf-terms.tsv`. Verdicts are human inspection judgments, not generated by the fetch script; no inter-rater assessment was performed.

GVO declares 48 classes, comprising a root and 47 variation types, together with 12 datatype properties and no object properties. Its mostly out-of-scope verdicts reflect this purpose. The missingness convention can preserve a literal dot, but does not itself distinguish that token from an absent triple.

The graded alignment set contains 57 `skos:exactMatch`, 40 `skos:closeMatch`, 16 `skos:relatedMatch`, and 10 `skos:narrowMatch` relationships, recorded in SSSOM. The majority are therefore not exact matches. They relate vocabulary terms and do not establish cross-file identity for variants, samples, or patients. The alignment files are available in the [VCF Core repository](https://github.com/ecrum19/vcf-core-vocabulary/tree/main/mappings).

## Reproduction and editorial scope

Each RQ has its own procedures and run scripts in the experimental repository. Runs preserve toolchain and machine descriptions, commands, exit codes, durations, logs, converted graphs, and results. Specification revisions and fixture sets are pinned; query execution uses rdflib 7.6.0. RQ1 executes scripts inside the pinned vocabulary checkout rather than potentially different working-tree copies.

The shortened manuscript does not rerun or alter the experiments. Repetition and development history were removed from the submission text, while the figures, numerical outcomes, scope boundaries, and principal counterexamples were retained. Reference entries, authorship, acknowledgments, and the AI disclosure were copied from the original manuscript. The revised bibliography substitutes `n.d.` for a missing GA4GH repository year that otherwise renders as `????`; no date was invented. The original-file hash manifest supports verification that the `long-paper/` versions have not changed.
