# W1 — Comparison with existing models

Completed 2026-09-12; W1.4 finished 2026-09-13, when the two artifacts that had resisted
retrieval were obtained and inspected. Every verdict below names the artifact it rests on.

## W1.1 Comparison set

Four models, all already discussed in the manuscript, chosen because each states a *different*
purpose for the same subject matter — which is what makes the contrast informative.

| Model | Pinned artifact inspected | Evidence quality |
| --- | --- | --- |
| **GFVO** | `gfvo.xml`, BioInterchange/Ontologies `master`, retrieved 2026-09-12 | ontology inspected |
| **HERO-Genomics** | `hero_genomics.ttl` v1.0, `hereditary.dei.unipd.it`, retrieved 2026-09-12 | ontology inspected |
| **GVO** | `http://genome-variation.org/resource/gvo`, `owl:versionInfo` **2021-11-18**, retrieved 2026-09-13 (content-negotiated Turtle; the host serves **plain HTTP only**, which is why an earlier HTTPS attempt failed) | ontology inspected |
| **VCF2RDF** | `diegopenhanut/vcf-resources` @ `gh-pages` (pushed 2018-09-17), the published term set behind Penha et al., *Bioinformatics* 33(4):547–548, 2017; live at `diegopenhanut.github.io/vcf-resources/v4_2/` | published term set inspected; converter behaviour still from the paper |

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
| F2 header declarations | **E** | **S** | **S** | **S** | **E** |
| F3 version | **E** | **S** | **S** | **S** | **C** |
| F4 ordered alleles | **E** | **C** | **C** | **S** | **C** |
| F5 genotype structure | **E** | **C** | **C** | **S** | **C** |
| F6 per-sample FORMAT | **E** | **C** | **C** | **S** | **C** |
| F7 allele-dependent values | **E** | **C** | **C** | **S** | **C** |
| F8 missingness | **E** | **S** | **C** | **C** | **C** |
| F9 profile choice | **E** | **S** | **S** | **S** | **S** |

No cell is now `?`: both remaining artifacts were retrieved and inspected on 2026-09-13.

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

**GVO** — the retrieved ontology (279 triples) is exactly what the paper describes, and its
shape settles every cell. It declares **48 classes and 12 datatype properties, and zero object
properties**. Forty-seven of the classes are variation types under a bare `gvo:Variation` root
(`SNV`, `MNV`, `Indel`, `Inv`, `Dup`, `Bnd`, the `DelME`/`InsME` mobile-element families, …),
each with a `skos:definition` and `rdfs:seeAlso` links to SO and VariO. The 12 properties are
`chrom`, `pos`, `ref`, `alt`, `lft`, `rgt` — GVO's own normalised coordinates — alongside
`pos_vcf`, `ref_vcf`, `alt_vcf`, `qual`, `filter`, `info`, kept for VCF as written. Like HERO,
`gvo:info` aligns to `vcfc:infoRaw`.

Two inspected facts decide F4, F7 and F8, which were previously `?`. First, **every property is
an `owl:DatatypeProperty`**: with no object property in the ontology, nothing can be attached to
an allele, a sample or a declaration as a resource, so allele indexing and per-allele value
binding are not merely unconventionalised but unexpressible in GVO's own terms — and since its
stated purpose is typing variation, that is **outside scope** (F4, F7), not a defect. Second,
the 12 properties carry **an `rdfs:label` and nothing else** — no `rdfs:domain`, `rdfs:range`,
`skos:definition` or comment (`gvo:info` is labelled just "Info"; `gvo:qual`, "Qual"). The
VCF-facing surface is therefore declared but not axiomatised, which is consistent with the
authors' stated plan to pair GVO with FALDO rather than to model the file. F8 is **C**: a
literal-valued property can carry `"."`, but distinguishing it from an absent triple is a
convention the ontology does not supply. File, header, sample, version and profile concepts are
absent, as the paper's scope implies.

**VCF2RDF** — the published term set corrects the reading taken from the paper alone. It is not
term-free: `v4_2/` publishes **59 dereferenceable resources**, each an HTML page carrying the
term's gloss from the VCF 4.2 specification. They include the header-declaration components
`INFO_ID`, `FORMAT_ID`, `FILTER_ID`, `ALT_ID`, **`Number`** ("How many values a propertie can
have"), **`Type`** ("Can be integer, Float, Flag (boolean), Character, String") and
`Description`; the file-level `reference`, `contig`, `contig_URL`, `assembly`, `SAMPLE` and
`PEDIGREE`; and one resource per reserved key of that version (`INFO_ID_AF`, `INFO_ID_DP`,
`FORMAT_ID_GT`, `FORMAT_ID_PL`, …), each reproducing the specification's own prose.

So **F2 is E, not C** — the earlier verdict was wrong, and it was wrong because it rested on the
paper rather than the artifact. A declaration's ID, Number, Type and Description each have a
published predicate; nothing needs re-parsing to reach them. The rest of the row stands. There
is no allele-index term (`ALT` is one resource, "Alternative alelle"), no genotype decomposition
(`FORMAT_ID_GT` carries the specification's paragraph about `/` and `|` as *prose*, not as
structure), no missing-value term, and `SAMPLE` is the `##SAMPLE` header line — "Define sample to
genome mappings" — not a genotype column, so F6 still needs a convention. F3 stays C: the version
lives in the IRI path segment `v4_2`, a namespace convention rather than a declared property, and
only that one version was ever published. F9 does not arise.

Two limits on this column. The pages carry glosses, not RDF axioms — no `rdf:type`, domain or
range is asserted for any term — so what is inspected is a published, dereferenceable
*vocabulary*, not an ontology. And whether the converter populates these predicates from a real
file is still established only by the paper's design description; no output was inspected.

## W1.6 Two worked contrasts

**Allele-dependent values.** VCF 4.5 `##FORMAT=<ID=AD,Number=R,...>` means the AD list has one
element per allele, reference first. Answering "what is the read depth supporting ALT allele 2
in SAMPLE3?" requires three things at once: the declaration's `Number=R`, the allele's ordinal,
and the sample's cell. VCF Core carries all three (`fieldNumber`, `alleleIndex`, `SampleCall`).
HERO and GVO both retain INFO as one literal (`vcfInfo`/`gvo:info`, each aligned to
`vcfc:infoRaw`) and neither declares `Number`, so the consumer must re-parse the cell *and*
supply the cardinality rule from outside the graph. GFVO would answer it only for the fields it
happens to name as concepts. VCF2RDF is the interesting case: it **does** publish `Number`, so
the cardinality rule is in the graph — but with no allele-index term, the consumer still has to
split the list itself and count ALT alleles by re-reading the ALT literal. Having the declaration
is necessary and, on its own, not sufficient; the binding to an allele is the part that has to be
represented rather than inferred.

**Version-conditioned interpretation.** `CIPOS` is defined differently across VCF 4.1–4.5, and
the 4.5 local-allele families (`LA`, `LR`, `LG`) do not exist earlier. Reading such a field
correctly requires knowing the file's version. Only VCF Core attaches it (`fileFormat` plus the
`VCF4xFile` gates, which W3 saw the converter emit as `VCF45File`). In the other three the
version is either absent or, for VCF2RDF, carried by the term namespace itself — its resources
live under `/v4_2/`, so a graph is implicitly 4.2 and only 4.2 was ever published. That is a
workable convention for one version and no answer at all to a 4.1–4.5 corpus.

## W1.7 Bounded conclusion

The difference that substantiates the contribution is **not** breadth of variation modelling —
GVO's 47 variation classes and VRS's computable identity both exceed anything VCF Core attempts,
and the curated set aligns to them rather than competing. It is that VCF Core represents the
*interpretation context* a VCF file carries about itself: the declaration that gives a field its
cardinality and type, the version that selects which rule applies, the allele ordinal that makes
a genotype integer resolvable, and the sample column that scopes a value. In the inspected
artifacts, that context is either kept as text to re-parse (HERO, GVO), replaced by concepts for
individual fields (GFVO), or — VCF2RDF — declared for the header and left unbound for the data.

The completed inspection sharpened the claim in one place and weakened it in another. GVO's
verdicts moved from `?` to **outside scope**, which is the fairer reading: an ontology of 48
variation classes and no object properties is not failing at file modelling, it is doing
something else. VCF2RDF's F2 moved the other way, from *convention* to **explicit** — it
publishes `Number`, `Type` and `Description` as terms, which is more than the paper's
"isomorphic map" framing suggested, and the earlier verdict was an error of reading a paper
instead of an artifact.

Three limits on this conclusion. The comparison covers features VCF Core was built to serve, so
it is not a neutral ranking — a matrix chosen by GVO's authors would look different and they
would be right. All four columns now rest on inspected artifacts, but for VCF2RDF that artifact
is a published term set, not converter output, so what its graphs actually contain is still
taken from the paper. And "requires additional conventions" is a statement about what an
inspected artifact establishes, never a claim that a model's community could not represent
something.
