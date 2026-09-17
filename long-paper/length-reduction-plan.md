# Reduction plan for the 12-page submission

The introduction table and its surrounding related-work prose have been shortened. Methods, results and discussion remain unchanged by this review. Locations below refer to the files as reviewed on 17 September 2026.

The table retains all 11 entries, citations, roles and substantive distinctions. Combining the Type and Purpose columns reduces the rendered table body from 537 to 334 PDF points, about 38%, using the existing font size. Together with shorter surrounding prose, this saves approximately 0.6 page of space. Main matter still reaches page 19; the remaining recommendations have not been applied or validated as a 12-page build.

## Recommended page budget

| Material | Target pages, including its figures and tables |
| --- | ---: |
| Title, abstract, introduction and related work | 2.75 |
| Methods | 3.25 |
| Results | 3.50 |
| Discussion | 1.50 |
| Conclusion, acknowledgments and AI declaration | 0.75 |
| Reserve for layout and float placement | 0.25 |
| **Total excluding references** | **12.00** |

Methods currently occupies approximately six pages, results approximately 5.6, and discussion approximately 2.8. These are spans between headings, rather than counts of exclusive pages. Meeting the budget requires substantial compression, especially in methods and results. The targets are editorial allocations, not measured savings from an implemented revision.

## First remove duplication

1. **Repeated inventory results:** in [results.tex:96](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:96), the passages at lines 97–99 and 101–105 repeat the 104/87 result, the enforcement breakdown and the evidence tiers. Retain one compact paragraph. Move the separate 17-fixture byte check to the companion report unless byte preservation remains a central claim.
2. **Repeated converter interpretation:** remove lines 146–151 in [results.tex:146](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:146). They repeat lines 135–140. State once that none of the observed divergences requires an additional vocabulary mechanism; retain the separate limitation that untested requirements cannot be assessed.
3. **Repeated model comparison:** remove the second explanation of HERO/GVO, GFVO and VCF2RDF at [results.tex:245](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:245). The same three findings already appear before Table 4. Keep the matrix and one concise explanation, plus the qualification that the comparison concerns documented support within the inspected artifacts.

These are low-risk deletions, but insufficient by themselves to recover seven pages.

## Methods: preserve the experimental design, relocate implementation detail

| Location | Recommended change | Essential content to retain |
| --- | --- | --- |
| [Research questions and representation, lines 7–27](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:7) | Compress the repeated motivation and contribution summary. Reduce the Explorer/tool description to a link. Keep the model figure, but shorten its caption to the profile difference and declaration links. | What the model represents; the two sample profiles; supported versions; distinction between representation and executed evidence. |
| [RQ1, lines 64–124](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:64) | Replace the five-item terminology list with a short paragraph defining a requirement, a case and its fixture/graph/query/expected-answer bundle. Combine the assessment rationale and graph-construction explanation. Move file paths, predicate inventories and detailed examples to the RQ1 documentation. | Specification-derived requirements versus curated inventory; answers authored before execution; preservation versus structure; both negative controls; unassessed requirements remain in the denominator. |
| [RQ2 replay, lines 126–151](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:126) | Explain the unchanged tests and different producer once. Move short commit IDs, digest strings, dynamic fixture discovery and witness-rebuild mechanics to the reproduction record. Describe the version-registry comparison beside RQ1, where its results are reported. | Python materializer versus RML/RMLStreamer implementation; both profiles; exact answer comparison; shared authorship; fragment-only IRI comparison limitation. |
| [Round-trip, lines 153–165](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:153) | Replace the two-script walkthrough and six individual mutations with approximately 100–130 words. Move script filenames and the emitted-term audit to companion material. | Fixed columns, genotypes, headers and field values reconstructed from structure; raw-source shortcuts forbidden; mutation checks; leading-phase normalization; expanded-profile-only scope. |
| [RQ3, lines 167–200](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:167) | Keep the short SPARQL listing: it makes the contribution concrete. Compress setup and acceptance criteria into two paragraphs, and shorten the listing caption. Move triple counts, input paths and per-projection comparison mechanics out. | Four synthetic sites, one sample, five invented annotations; four-literal join; common-assembly/as-written-allele assumptions; depth threshold chosen to distinguish interpretations; exact answers, exclusions and provenance checked. |
| [RQ4 and reproduction, lines 202–228](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/methods.tex:202) | Reduce RQ4 to one compact paragraph and reproduction to one availability paragraph. Move artifact filenames, download mechanics and log-directory contents to the repository. | Four inspected models, nine criteria, E/C/S definitions, reviewer/inspection limitations, why VRS is outside this comparison, released versions and a stable reproduction link. |

Aim to remove roughly 1,500–1,700 words from methods, chiefly procedural detail and repeated justification. Keep the controls and limitations even when moving the implementation details.

## Results: report each finding once

- **Source audit: the largest single prose cut.** Condense [lines 17–47](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:17) to a short corpus summary: 94 requirements, 38 fixtures, 210 cases and 79 queries, with source traceability. Move the 344 intervals, 1,134 assertions, 149/154/831 classifications, three worked audit examples, repeated-statement counts and individual issue links to the companion report. Retain that example availability influenced selection, that some interpretation statements remain generic, and that unresolved interpretation contributes to the unassessed set. Do not attribute all missing coverage to specification defects.
- **Coverage table: shorten its explanation.** In [lines 61–94](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:61), remove the arithmetic example and repeated instructions for reading the denominator. Define N, ND and U once. The three identical demonstrated columns can be combined under an explicit heading such as “Preservation, both profiles / expanded structure”; retain condensed structure separately and explain the equality in the caption. Alternatively, keep all columns and shorten only the caption.
- **Registry and inventory results:** keep 333 explicit declarations matched, 104 represented constructs and 87 with enforcement evidence. Move the per-version registry-count lists, evidence-tier breakdown and category-level enforcement fractions to the companion tables. Preserve the qualification that 333 counts explicit comparable declarations and 104 is a curated inventory, not 104 executed retrieval tests.
- **Converter findings:** keep the 693/102/45 outcome split and the four divergence categories. Shorten Table 3 to category, count and one example; remove the surrounding repeated explanation. Preserve the corrected local-allele error and the remaining empty-LAA problem. Remove the release-note list of repaired accessors and aliases.
- **Round-trip and profiles:** reduce [lines 154–170](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:154) to two compact paragraphs retaining the recovery totals, the empty-versus-absent exception and the fact that profile disagreements concern sample-level access. Move the reconstructed cell string and individual emitted triples to the detailed report.
- **Remove the “VCF Core version-level checks” paragraph** at [line 173](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/results.tex:173). Its small-example triple counts, vocabulary-term counts and ancillary regression totals add denominators without answering another central question; the experiment record can retain them.
- **RQ3:** keep the correct and incorrectly associated alterations, their depths, and the equal-row-count contrast. Shorten the individual exclusion explanations and the repeated statements of what this demonstrates. Preserve a brief synthetic-example limitation.
- **RQ4:** keep Table 4 and one paragraph explaining the three representation patterns. Remove the account of the authors' earlier VCF2RDF verdict and most of the GVO class/property inventory. Retain the distinction between “outside scope” and “needs additional conventions,” and the inspection-only limitation. Discuss complementarity in the discussion once.

Aim to remove roughly 1,400–1,600 words from results, with further space saved by shorter captions. Preserve the coverage and comparison tables because they make the claims inspectable.

## Discussion: retain the requested six-topic flow

Target about 800–900 words across the same six subsections, compared with roughly 1,670 currently counted by TeXcount. The discussion should interpret the results instead of presenting them a second time.

| Topic | Target words | What to keep and what to cut |
| --- | ---: | --- |
| Coverage basis and findings | 120–140 | Keep demonstrated coverage versus representational capability and the practical profile distinction. Refer to Table 2 instead of repeating 104, 87, 53/94 and 51/91 in full. |
| Closing the gaps | 120–140 | Keep priorities for structural variation, allele-dependent cases and specification clarification. Remove the R45/R67/R68 inventory and repeated 37-of-40 breakdown. |
| Converter assessment | 120–140 | Keep reusable expected-answer tests as a development instrument. Refer back to the local-allele defect; remove the repeated outcome totals, divergence taxonomy and round-trip totals. |
| Why the integration example matters | 160–180 | Protect this topic: why local alleles were chosen, why plausible rows and provenance can still be wrong, and why explicit links make interpretation reusable. Give the synthetic scope and join assumptions in one sentence. |
| Position among existing models | 120–140 | Keep source observations versus variation/clinical descriptions, and one concrete complementarity example. Refer to Table 4 for the model-specific findings. |
| Future work and independent review | 120–140 | Keep independent replication, real datasets and mappings, and profile/performance evaluation, including the SciSPARQL direction if desired. Compress the three clinical scenarios to a short clause. |

The scope qualifications should survive this compression: shared authorship, untested requirements, synthetic integration data, expanded-only round-tripping and inspection-based comparison. They need not be explained repeatedly in methods, results, discussion and conclusion.

## Two additional cuts to make the budget achievable

- **Introduction results preview:** replace [intro_rw.tex:102–106](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/intro_rw.tex:102) with one or two sentences. The four research questions immediately above should remain; their full answers already appear in the abstract and results.
- **Conclusion:** reduce [main_long.tex:78–92](/Users/eliascrum/PhD_Things/SWAT4HCLS_2027/long-paper/main_long.tex:78) to approximately 100–130 words. Remove the repeated numerical results and detailed limitations list; keep the contribution, its demonstrated scope and the invitation to reuse and test it. Preserve acknowledgments and the AI disclosure.

Apply duplication cuts first, then move procedural/audit detail, then shorten discussion and captions. Recompile after each stage and use the `endofmain` marker to check the limit. Keep the template, margins and body font unchanged. The model diagram, concise integration query, coverage denominator, corrected allele-association example and fair comparison of model scope are the strongest material to protect.
