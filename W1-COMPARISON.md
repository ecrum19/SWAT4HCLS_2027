# W1 — Comparison with existing models

Completed 2026-09-12. Every verdict below names the artifact it rests on. Where an artifact
could not be inspected, the verdict is **Not established**, which is not a claim of absence.

## W1.1 Comparison set

Four models, all already discussed in the manuscript, chosen because each states a *different*
purpose for the same subject matter — which is what makes the contrast informative.

| Model | Pinned artifact inspected | Evidence quality |
| --- | --- | --- |
| **GFVO** | `gfvo.xml`, BioInterchange/Ontologies `master`, retrieved 2026-09-12 | ontology inspected |
| **HERO-Genomics** | `hero_genomics.ttl` v1.0, `hereditary.dei.unipd.it`, retrieved 2026-09-12 | ontology inspected |
| **GVO** | Kawashima et al., SWAT4HCLS 2023 (CEUR Vol-3415 paper-22) + the 39 `gvo:` terms curated in `mappings/vcf-core-alignments.sssom.tsv` | **paper + curated terms only** — `genome-variation.org` refused HTTPS, so the ontology file itself was not inspected |
| **VCF2RDF** | Penha et al., *Bioinformatics* 33(4):547–548, 2017 | **paper only** — the released artifact was not inspected |

GA4GH VRS is not scored. Its 15 curated alignments are all variation-shaped (`vrs:Allele`,
`vrs:SequenceLocation`, `vrs:CisPhasedBlock`, `vrs:Adjacency`, `vrs:CopyNumberChange`), and it
describes computable variation identity rather than a source file. Scoring it against
file-format features would manufacture a contrast that its authors never sought.

VCF Core is assessed under the same criteria, against `v2.1.1` (`dd139f9`).

## W1.2–W1.3 Features and what counts as support

The eight areas W0.3 prioritised, plus the declaration link. Each criterion is a retrieval
question, not a judgement of quality.

| # | Feature | Operational criterion |
| --- | --- | --- |
| F1 | File-scoped identity | A term denotes the VCF file, so a record traces to the file it came from. |
| F2 | Header declarations as resources | An INFO/FORMAT declaration's ID, Number, Type and Description are retrievable as data, not as a header string to re-parse. |
| F3 | Version distinction | A consumer can read which VCF version the file declares. |
| F4 | Ordered alleles | ALT allele *n* is addressable by index, so a GT integer resolves to an allele. |
| F5 | Genotype structure | Ploidy, ordered allele calls and phasing are separable. |
| F6 | Sample-specific FORMAT values | The value for (sample, field) is retrievable without splitting the `:`-joined cell. |
| F7 | Allele-dependent values | A `Number=A`/`R`/`G` list is associable with the allele each element belongs to. |
| F8 | Missingness | `.` is distinguishable from "not stated". |
| F9 | Representation-profile choice | A consumer can tell from the graph which sample encoding was used. |

## W1.5 Comparison

**E** explicitly represented · **C** representable with additional conventions · **S** outside
stated scope · **?** not established from the available artifacts

| | VCF Core 2.1.1 | GFVO | HERO 1.0 | GVO | VCF2RDF |
| --- | :-: | :-: | :-: | :-: | :-: |
| F1 file identity | **E** | **E** | **E** | **S** | **C** |
| F2 header declarations | **E** | **S** | **S** | **S** | **C** |
| F3 version | **E** | **S** | **S** | **S** | **C** |
| F4 ordered alleles | **E** | **C** | **C** | **?** | **C** |
| F5 genotype structure | **E** | **C** | **C** | **S** | **C** |
| F6 per-sample FORMAT | **E** | **C** | **C** | **S** | **C** |
| F7 allele-dependent values | **E** | **C** | **C** | **?** | **C** |
| F8 missingness | **E** | **S** | **C** | **?** | **C** |
| F9 profile choice | **E** | **S** | **S** | **S** | **S** |

### Evidence per verdict

**VCF Core** — every row rests on a declared term, verified present in the 2.1.1 bundle:
`VCFFile`; `INFOHeaderLine`/`FORMATHeaderLine` with `fieldNumber`/`fieldType`; `fileFormat`
plus the `VCF41File`–`VCF45File` gates; `alleleIndex`; `ploidy`, `callIndex`, `phasingStatus`;
`SampleCall`/`hasFormatValue`; the `Number=A/R/G` value-item layer; the `Null` datatype;
`representationProfile`. W3 confirmed all of these reach an actual converted graph.

**GFVO** — `File` exists and its comment covers "GFF3, GTF, GVF or VCF" contents, so F1 is
explicit. `Genotype`, `Sample` and `GameticPhase` exist, so genotype and phasing are
representable, but nothing indexes alleles or binds a value to a sample column, so F4–F7 need
conventions the ontology does not supply. GFVO instead models *particular field meanings* as
first-class concepts — `AlleleCount`, `AlleleFrequency`, `TotalNumberOfAlleles`, `SampleCount`,
`MappingQuality`, `BaseQuality`, `Coverage`, `ConditionalGenotypeQuality` — which is the
opposite design choice from declaring the mechanism: it is exactly why the curated set aligns
nine `vcfc:ReservedInfo_*`/`ReservedFormat_*` terms to GFVO concepts. No header-declaration,
version or missing-token class is defined, and the format-version question is outside a
multi-format feature ontology's stated purpose.

**HERO 1.0** — the only surveyed model besides VCF Core with first-class VCF file and record
terms: `VCFFile` (`filename`, `filepath`) and `VCFRecord` with `vcfChrom`, `vcfPos`, `vcfRef`,
`vcfAlt`, `vcfQual`, `vcfFilter`, `vcfInfo`. The decisive detail is `vcfInfo`: the curated set
records it as an **exactMatch to `vcfc:infoRaw`** — the whole INFO column as one literal. So
INFO survives, and every INFO-derived question (F7 especially) requires re-parsing that string.
`Genotype` and `Zygosity` exist; no phasing, no allele index, no FORMAT declarations, no header
lines, no version. The schema's own notes mention a MISSING value but define no class or
datatype for it, so F8 is a convention rather than a mechanism.

**GVO** — the paper is explicit about scope: 47 classes "corresponding to genomic variation
types", organised under `gvo:Variation`, collected from dbSNP, dbVar, gnomAD, SO, VariO and
HGVS. Its VCF contact surface is a small property set the curated alignments confirm —
`gvo:chrom`, `pos_vcf`, `ref_vcf`, `alt_vcf`, `qual`, `filter`, `info` — introduced because the
authors "plan to use GVO with the FALDO ontology to convert genomic variations distributed in
VCF format into RDF". Like HERO, `gvo:info` aligns to `vcfc:infoRaw`. File, header, sample and
version concepts are **outside its stated purpose**, not missing from it. F4, F7 and F8 are
marked not established because the ontology file could not be retrieved; the paper does not
settle them and the curated set only covers what the curator mapped.

**VCF2RDF** — an isomorphic map: the paper describes URIs "for all resources we found on the
VCF specification" organised into two classes, header and body, joined by line identifiers, and
its worked triple uses generic terms (`body`, `head`, `row_1000`). That design preserves the
file's content faithfully — which is why F1–F8 are *representable* — but it mints no domain
terms, so every feature is recovered by re-parsing the text the graph carries. F9 does not
arise: an isomorphic map has one representation by construction.

## W1.6 Two worked contrasts

**Allele-dependent values.** VCF 4.5 `##FORMAT=<ID=AD,Number=R,...>` means the AD list has one
element per allele, reference first. Answering "what is the read depth supporting ALT allele 2
in SAMPLE3?" requires three things at once: the declaration's `Number=R`, the allele's ordinal,
and the sample's cell. VCF Core carries all three (`fieldNumber`, `alleleIndex`, `SampleCall`).
HERO and GVO both retain INFO as one literal (`vcfInfo`/`gvo:info`, each aligned to
`vcfc:infoRaw`) and neither declares `Number`, so the consumer must re-parse the cell *and*
supply the cardinality rule from outside the graph. GFVO would answer it only for the fields it
happens to name as concepts. VCF2RDF preserves the characters and defers the whole question.

**Version-conditioned interpretation.** `CIPOS` is defined differently across VCF 4.1–4.5, and
the 4.5 local-allele families (`LA`, `LR`, `LG`) do not exist earlier. Reading such a field
correctly requires knowing the file's version. Only VCF Core attaches it (`fileFormat` plus the
`VCF4xFile` gates, which W3 saw the converter emit as `VCF45File`). In the other three the
version is either absent or, for VCF2RDF, present only as a header line to be re-read.

## W1.7 Bounded conclusion

The difference that substantiates the contribution is **not** breadth of variation modelling —
GVO's 47 variation classes and VRS's computable identity both exceed anything VCF Core attempts,
and the curated set aligns to them rather than competing. It is that VCF Core represents the
*interpretation context* a VCF file carries about itself: the declaration that gives a field its
cardinality and type, the version that selects which rule applies, the allele ordinal that makes
a genotype integer resolvable, and the sample column that scopes a value. In the inspected
artifacts, that context is either kept as text to re-parse (HERO, GVO, VCF2RDF) or replaced by
concepts for individual fields (GFVO).

Three limits on this conclusion. The comparison covers features VCF Core was built to serve, so
it is not a neutral ranking — a matrix chosen by GVO's authors would look different and they
would be right. Two of the four verdict columns rest on a paper plus curated terms rather than
an inspected artifact, and several `?` cells could resolve either way. And "requires additional
conventions" is a statement about what an inspected artifact establishes, never a claim that a
model's community could not represent something.
