# VCF Core: Long-Paper Evidence and Revision Checklist

**Purpose:** Strengthen the long VCF Core paper for SWAT4HCLS 2027 by connecting its central contribution to clear, reproducible evidence.

**Basis:** The author's selected takeaways from the manuscript review. This is an implementation plan, not a new assessment of the repositories or a statement of conference requirements. All boxes begin unchecked; mark existing work complete when its evidence has been located and reviewed.

## 1. Guiding claim and boundaries

The central claim is that **VCF interpretation context can be preserved across versions and representation profiles**, not merely that genomic data can be exposed as RDF.

Organize the work around three questions:

- **RQ1:** Does VCF Core preserve the intended meaning of the VCF constructs it claims to support?
- **RQ2:** Do the version-specific artifacts and alternative profiles behave as documented?
- **RQ3:** Does the resulting representation enable a useful, reproducible integration task while retaining source context?

### Scope limits

Reuse existing fixtures, tests, assessment inventories, mappings, and documentation before adding anything. Approximately **8-12 comparison features** and **8-12 competency questions** are planning guides, not quotas; fewer are acceptable when they cover the important decisions without duplication.

This plan does **not** require an exhaustive survey of genomic ontologies, complete VCF conformance, universal byte-for-byte reconstruction, a production clinical workflow, a new benchmark framework, or a large performance study. Address gaps that affect the central claims; document and bound the rest.

The author-supplied implementation target is **VCF-RDFizer v2.x using VCF Core Vocabulary (vcfcv) v2.1.0**. Record the exact tested converter release rather than treating `v2.*.*` as an executable version or evidence for every v2 release.

## 2. Workflow and execution order

| Workstream | Suggested owner | Dependency | Main output |
|---|---|---|---|
| W0. Establish the evidence baseline | Coordinating agent | None | Pinned inputs and existing-artifact map |
| W1. Compare relevant representations | Comparison agent | W0 | Feature comparison with source evidence |
| W2. Clarify and strengthen assessment | Assessment/test agent | W0; coordinate execution with W3 | Evidence map, competency checks, grounded coverage summary |
| W3. Establish implementation evidence | Converter agent | W0 | Exact-release compatibility record and smoke test |
| W4. Execute one integration example | Integration agent | W2 fixture/expected-answer agreement and W3 executable path | Reproducible example with checked answers |
| W5. Revise and verify the manuscript | Coordinating/editor agent | W1-W4 results | Claim-linked evaluation and revised discussion |

**Parallel work:** W1, W2, and W3 can begin after W0. W4 can prepare its question and annotation inputs in parallel, but should finalize its results only after the vocabulary release and conversion path are established.

**Shared-edit rule:** Assign one owner to shared fixtures, expected answers, and manuscript integration. Subagents should propose changes to those artifacts rather than overwrite each other's work. Use existing project conventions; the deliverables below are logical outputs, not a requirement to create a new directory or file for each item.

### Lightweight agent handoff

Each workstream returns: completed task IDs; changed artifact paths; input versions; commands/checks run and their outcomes; supported claims; and remaining blockers. Report `not run`, `blocked`, and `failed` distinctly. Do not mark a task complete because its code or prose has merely been drafted.

A reusable delegation instruction is:

> Complete workstream [ID] against the pinned inputs in W0. Reuse existing artifacts, stay within the workstream's scope, and coordinate shared-file changes. Return the deliverables, reproducible commands and results, supported claims, and unresolved limitations. Separate observed results from proposed work; do not invent outcomes or broaden the paper's claims.

## W0. Establish the evidence baseline

**Goal:** Identify what already exists and agree on the exact artifacts being assessed.

- [ ] **W0.1 - Pin the inputs.** Record the long manuscript, VCF Core 2.1.0 tag/commit, exact VCF-RDFizer v2 release/commit, and specification sources used by the existing assessments. Record any working-tree changes separately.
- [ ] **W0.2 - Locate reusable evidence.** Identify current coverage inventories, versioned registries, validation profiles, fixtures, regression tests, conversion examples, query tests, and assessment scripts. Briefly note what each establishes; do not duplicate their contents.
- [ ] **W0.3 - Assign owners and select priorities.** Assign W1-W4 and agree which difficult modeling decisions need the strongest evidence. Select provisional comparison features and competency questions together where they overlap.
- [ ] **W0.4 - Separate baseline from changes.** Preserve the initial assessment results. Record which fixes or additions are made during this work so final counts are not mixed with older results.

**Done when:** An incoming agent can locate the exact inputs, relevant existing evidence, and its assigned edit scope without guessing.

## W1. Compare relevant ontologies and vocabularies

**Guiding question:** Which important representation problem can VCF Core demonstrably handle that an existing model cannot handle without substantial additional conventions?

### Tasks

- [ ] **W1.1 - Select a small comparison set.** Choose the most relevant predecessors already discussed in the manuscript, normally around three or four. Candidates include GFVO, VCF2RDF, HERO-Genomics, and GVO; justify the selection instead of treating this as a mandatory list. Use other models only where their stated purpose makes comparison informative.
- [ ] **W1.2 - Select approximately 8-12 features.** Prioritize file-scoped declarations; ordered alleles and genotype indices; allele-dependent values; sample-specific FORMAT values; missingness; version distinctions; source provenance; and representation-profile choices. Merge overlapping features and omit features peripheral to the actual contribution.
- [ ] **W1.3 - Define what counts as support.** For each feature, write a short operational criterion and, where useful, point to a representative fixture or competency question. Avoid vague criteria such as "supports VCF" or "has provenance."
- [ ] **W1.4 - Inspect pinned primary artifacts.** Record the model version or commit and the exact documentation, term, axiom, mapping, or example supporting each assessment. Distinguish what a publication describes from what a released artifact demonstrates.
- [ ] **W1.5 - Populate the comparison.** Assess VCF Core under the same criteria as the other models. Use the four statuses below, with a brief explanation and evidence location for each substantive judgment.
- [ ] **W1.6 - Demonstrate the important differences.** Select one or two difficult examples showing the extra convention, extension, or interpretation needed in another representation. Reuse W2 fixtures where possible. No full converter implementation for each competing model is required.
- [ ] **W1.7 - Draft a bounded conclusion.** Explain which differences substantiate VCF Core's contribution and which reflect different intended scopes. Avoid an overall winner, a class/property-count ranking, or a blanket claim that another model cannot represent something.

### Required comparison statuses

| Status | Intended meaning |
|---|---|
| **Explicitly represented** | The inspected artifacts provide a documented representation meeting the stated criterion. |
| **Representable with additional conventions or extensions** | Representation is possible, but requires a specified addition or convention not established by the inspected model itself. |
| **Outside the stated scope** | The feature is not part of the model's documented purpose; this is not automatically a defect. |
| **Not established from the available artifacts** | Evidence is insufficient to decide; absence of located evidence is not proof of impossibility. |

**Deliverable:** One concise comparison matrix, evidence pointers, and one or two worked contrasts. Reuse existing related-work documentation when suitable.

**Done when:** The novelty argument rests on inspectable representation differences, including fair treatment of uncertainty and scope.

## W2. Clarify and strengthen assessment evidence

**Goal:** Make it easy to see what exists, what is instantiated, what is independently checked, and what remains uncertain.

### A. Map existing evidence before adding tests

- [ ] **W2.1 - Inventory current test capabilities.** Map existing fixtures and tests to RQ1-RQ3 and the chosen features. Identify duplicate checks and important gaps. Do not use test counts alone as a measure of coverage.
- [ ] **W2.2 - Distinguish evidence strength.** Record the three levels below separately. An item can have evidence at more than one level. Also record whether executable checks have actually been run on the pinned artifacts and with what result.

| Evidence level | What it establishes | What it does not establish by itself |
|---|---|---|
| **Representational mechanism exists** | A term, relation, encoding, rule, or documented pattern is available. | Correct instantiation, complete validation, or correct query behavior. |
| **Example instantiates the mechanism** | A concrete fixture demonstrates how the mechanism is used. | General correctness or an independently verified interpretation. |
| **Behavior is independently checked** | An executed check agrees with a separately established expected interpretation or answer. | Correctness outside the tested scope. |

- [ ] **W2.3 - Build a compact evidence map.** For each selected capability, link the specification requirement and applicable version(s), vocabulary mechanism, fixture, expected interpretation, executable check, observed result, and limitation. Extend an existing inventory rather than building a parallel tracking system.

### B. Establish a compact competency-question suite

- [ ] **W2.4 - Choose approximately 8-12 competency questions.** Reuse questions implicit in existing tests. Cover the difficult interpretation decisions, including at least one meaningful version transition and expanded/condensed equivalence where those capabilities are claimed. Each question should have an observable, bounded answer.
- [ ] **W2.5 - Establish expected answers independently.** For small fixtures, use manually derived and reviewed expected logical values or answer tables. For larger examples, an independent extraction path may help within its supported scope. Do not generate both the observed and expected answers with the same conversion logic.
- [ ] **W2.6 - Execute and report the checks.** Record expected versus observed answers, versions/profiles tested, and mismatches. Fix claim-critical defects or narrow the claim. Keep useful negative regression checks; do not expand into exhaustive invalid-input testing.
- [ ] **W2.7 - Add a semantic round-trip check.** Recover selected logical VCF content from the structured RDF representation and compare it with the expected content. Exercise difficult features and both sample profiles where supported, documenting condensed decoding. An untouched raw VCF string must not serve as the recovery shortcut.

**Round-trip boundary:** Ignore only differences irrelevant to the stated logical comparison, such as RDF triple order or generated resource names. Preserve interpretation-relevant distinctions such as allele/sample order, missing versus actual values, field definitions, and version context. State exactly which content is recovered; do not imply whole-file reconstruction from a partial check.

### C. Ground coverage numbers and limitations

- [ ] **W2.8 - Explain each denominator.** For every retained coverage number, state what is counted, the inclusion rule, applicable version(s), evidence threshold, and supported claim. Keep logical constructs, specification requirements, registry entries, and executed tests distinct. Recompute results from the pinned artifacts rather than copying manuscript totals.
- [ ] **W2.9 - Classify consequential gaps.** Distinguish representation gaps, additional validation gaps, and source-byte requirements. Separately indicate missing implementation, missing evidence, or unresolved interpretation. Identify which gaps threaten the central claim; do not require manual reclassification of every inventory entry when existing metadata already supports the summary.
- [ ] **W2.10 - Produce a readable results summary.** Show representative successes, important failures/unknowns, and their consequences. Keep the detailed evidence map in companion artifacts. Explain overlapping categories rather than combining unlike denominators into a single percentage.

**Deliverable:** Updated evidence map, a compact executed competency suite and semantic round-trip check, and one grounded coverage/limitations table.

**Done when:** A reviewer can trace the principal claims to independently checked behavior and understand why remaining gaps do or do not undermine those claims.

## W3. Establish exact-release implementation evidence

**Goal:** Document the author's stated VCF-RDFizer v2 / vcfcv 2.1.0 relationship with a reproducible implementation record.

- [ ] **W3.1 - Record the exact converter release.** Identify the tested v2 release/tag and commit, the vocabulary release, and the implementation evidence for their relationship. Replace wildcard version references in reproducibility instructions.
- [ ] **W3.2 - Check the emitted representation.** Inspect output namespaces, relevant terms, profile structures, and validation setup against VCF Core 2.1.0. Check the selected behaviors, not just a dependency declaration or package version.
- [ ] **W3.3 - Run a small reproducible conversion.** Prefer the fixture selected with W2/W4. Record the command, relevant environment/dependency versions, emitted graph, validation results, and smoke-query outcome. Exercise both profiles when used to support the paper's claims.
- [ ] **W3.4 - Document the precise support boundary.** State that the tested VCF-RDFizer release uses vcfcv 2.1.0, with its supporting artifact and tested capabilities. Do not turn this into a claim that every vocabulary term, constraint, or historical VCF version is implemented unless separately evidenced. Resolve any mismatch explicitly rather than silently substituting hand-authored RDF for converter output.

**Deliverable:** A short compatibility/reproduction record and manuscript-ready implementation statement naming exact versions.

**Done when:** A reader can reproduce output using the submitted vocabulary release and distinguish vocabulary adoption from complete feature support.

## W4. Execute one convincing integration example

**Goal:** Replace one prospective discussion scenario with a small, verified demonstration that exercises a distinctive modeling choice.

**Target flow:**

`VCF input -> VCF Core 2.1.0 graph -> explicit biomedical links -> SPARQL query -> checked answers with source provenance`

**Suggested question:**

> Which sample observations correspond to alterations with a selected biomedical annotation, and which source files, declarations, and sample-level evidence support those observations?

### Tasks

- [ ] **W4.1 - Bound the example.** Choose one primary difficulty, or two closely related ones: allele-dependent values, missingness, version interpretation, or source-specific provenance. Make the expected query result depend on handling that difficulty correctly. Reuse W2 fixtures and the W3 conversion path where possible.
- [ ] **W4.2 - Document the inputs.** Record VCF version, sample/record counts, relevant features, and data provenance. Use a small public subset or clearly labeled synthetic fixture. Pin a small external annotation/concept snapshot; a live federated endpoint is not required.
- [ ] **W4.3 - Make the integration links explicit.** Record the mapping rule and any assumptions about identifiers, reference compatibility, alteration identity, and sample identity. Use documented mappings or transparently curated links. Clearly label synthetic assertions and unresolved mappings; do not invent biological findings or conflate a sample column with a patient.
- [ ] **W4.4 - Implement the query.** Return enough information to inspect the annotation link and trace each observation back to its file, record, sample, and relevant declaration/value. Use existing external vocabulary terms where suitable; identify any application-specific predicates.
- [ ] **W4.5 - Check expected and observed answers.** Establish expected rows separately from the query implementation, including a meaningful excluded or missing case. Compare identities, values, and provenance, not just result counts. Explain any intentionally omitted observations.
- [ ] **W4.6 - Package reproduction and limitations.** Provide inputs or retrieval instructions, conversion/mapping/query commands, expected answers, observed results, and concise limitations. State whether the example demonstrates representation, mapping, and answer correctness; do not imply clinical validity or broad performance results.

**Deliverable:** One runnable example plus a compact manuscript description covering inputs, mappings, query, expected/observed answers, recovered provenance, and limitations.

**Done when:** The example runs against the pinned release, produces the checked answers, and visibly benefits from retaining the interpretation context at the center of the paper.

## W5. Integrate evidence into the long paper

**Goal:** Present an established, bounded contribution with clearly identified ongoing work.

- [ ] **W5.1 - Align claims and results.** Organize the evaluation around RQ1-RQ3. Link each principal claim to a comparison, executed check, or integration result. Mark proposal-only capabilities as future work.
- [ ] **W5.2 - Update related work.** Integrate W1's main contrasts and a compact feature table. Preserve complementary framing and distinguish additional conventions from proven absence of support.
- [ ] **W5.3 - Rewrite the assessment explanation.** Use W2's evidence levels, denominator definitions, and limitation categories. Explain the significance of results rather than leading with overlapping counts.
- [ ] **W5.4 - Update implementation and discussion.** Name the exact VCF-RDFizer/vcfcv versions from W3. Replace or shorten one prospective scenario using W4's executed example. Reduce term-by-term description and repeated future applications to create space.
- [ ] **W5.5 - Bound ongoing work.** Identify remaining validation, interpretation, mapping, and reuse work without implying that the completed evidence is only hypothetical. Avoid broad "full semantic coverage" or complete-conformance wording unless the revised evidence supports it.
- [ ] **W5.6 - Perform final consistency checks.** Re-run the agreed checks after final edits; reconcile versions, namespaces, counts, figures/tables, claims, and artifact links. Compile the manuscript in the selected submission template and inspect pagination and readability without shrinking the format to compensate for excess detail.

**Deliverable:** Revised long-paper source and a brief change/evidence summary. Do not introduce a second full report unless the author requests one.

## Final completion gate

- [ ] The comparison answers the novelty question using sourced, feature-level evidence.
- [ ] Mechanism availability, example instantiation, and independently checked behavior are distinguishable.
- [ ] Important version/profile claims have executed checks, and all retained coverage numbers have understandable denominators.
- [ ] The exact tested converter release produces the vocabulary representation described in the paper.
- [ ] One integration example has checked answers and recoverable source provenance.
- [ ] Remaining limitations are explicit; no central conclusion depends solely on unexecuted future work.

**Stopping rule:** Stop adding experiments when these gates are met and the central claims are supported at their stated scope. Track worthwhile extensions as follow-up work rather than enlarging this submission indefinitely.
