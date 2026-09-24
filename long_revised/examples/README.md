# Listing and figure fixtures

Machine-readable counterparts of the fixtures printed in the manuscript. The
listings in the PDF align their columns for display; the files here are
tab-delimited, as VCF requires, and omit the step marks ①–③ that Listing 1 shares
with Figure 1. The fixtures are reductions of ones that live in
the experiment directories, kept here so the printed listings can be parsed and
re-run; they are not themselves experiment inputs. The queries are the full text
of what the manuscript prints or describes, and `rq3-local-allele-evidence.rq`
is the experiment input itself, copied byte for byte.

| File | Backs |
| --- | --- |
| `example.vcf` | Listing 1 and Figure 1, the RQ1 worked cases in `rq1.tex`, and RQ3's join table (Table 3). |
| `materialized/example-expanded.ttl` | The expanded-profile graph of `example.vcf`, as the pinned VCF Core v2.1.3 materializer produces it (611 triples): one resource per sample value, the resources Figure 1 draws in purple. |
| `materialized/example-condensed.ttl` | The condensed-profile graph of the same file (336 triples): no per-sample resources; each FORMAT field is one tab-separated vector per record, such as line 8's `LAD` vector `"20,30\t12,9"`, Figure 1's orange node. |
| `annotations.ttl` | The external snapshot `example.vcf` joins against for RQ3, reduced from `RQ3/inputs/annotations.ttl`. |
| `queries/r27-local-allele-map.rq` | Listing 2, in full. |
| `queries/r21-missingness.rq` | The R21 query that `rq1.tex` describes in prose, in full. |
| `queries/rq3-local-allele-evidence.rq` | Listing 3's source query, in full. Byte-identical to `RQ3/inputs/local-allele-evidence.rq`. |

## The worked cases

`example.vcf` carries three records and two sample columns. One allele runs
through the whole manuscript: `C` at `chr1:1`, where `S1`'s depth of 30 belongs
to `C` rather than to `A`. Figure 1 walks this record, R27 tests it, and RQ3
joins against it. The file exhibits both requirements discussed under RQ1:

- **R27** (local allele indices map to global record alleles) at `POS=1`. Both
  samples name one local allele, but different ones: `LAA=2` for `S1` and
  `LAA=1` for `S2`. Because `LAD` is declared `Number=LR`, the second value of
  each sample belongs to that sample's own local ALT allele — global allele 2
  (`C`) for `S1`, global allele 1 (`A`) for `S2`. The mapping is per sample, not
  per record.
- **R21** (explicit missingness versus an omitted field) at `POS=3`. `S1` writes
  `./.:.:.`, explicitly reporting a missing `LAD`; `S2` writes `0/0`, dropping
  the trailing `LAA` and `LAD` subfields altogether. The two must stay
  distinguishable.

## Verified answers

The two RQ1 queries run against the expanded-profile witness graph of
`example.vcf`.

`r27-local-allele-map.rq` returns eight rows over the two records that carry
allele depths; the four for `POS=1` are the ones quoted in `rq1.tex`:

```
?pos  ?sample  ?index  ?global  ?allele  ?depth
1     S1       0       0        G        20
1     S1       1       2        C        30
1     S2       0       0        G        12
1     S2       1       1        A        9
```

`r21-missingness.rq` returns exactly two rows, the second with `?raw` unbound:

```
?sample  ?raw
S1       "."
S2       (unbound)
```

`rq3-local-allele-evidence.rq` runs against `example.vcf` merged with
`annotations.ttl`. Listing 3 in the manuscript prints only its `WHERE` clause;
this is the whole query, including the `LAD >= 20` threshold and the provenance
fields the excerpt omits. It returns the two alterations quoted in `rq3.tex`:

```
?contig ?position ?ref ?alt ?depth ?sample ?fieldId ?number
chr1    1         G    C    30     S1      LAD      LR
chr1    2         A    T    25     S1      LAD      LR
```

The other two flagged alterations in `annotations.ttl`, `chr1:1 G>A` and
`chr1:2 A>C`, are excluded for two different reasons. No `LAD` value of `S1` is
linked to their alleles; `S2`'s values are, but at depths 9 and 7, below the
threshold. Resolve `Number=LR` positionally instead and `S1`'s depths of 30 and
25 go to exactly those alleles, above the threshold — that is the contrast
Table 3 tabulates.

## Reproducing

The queries run directly against `materialized/example-expanded.ttl`, which
needs only an RDF library; merge in `annotations.ttl` for the RQ3 query. They
return no rows on `materialized/example-condensed.ttl`, by design: they walk
per-sample resources that the condensed profile does not create, so those values
must first be decoded from the vectors. The decoding queries the assessment uses
for R21 and R27 are `r21-decode.rq` and `r27-decode.rq` in
`RQ1/methodology/queries/`; they target the registered fixtures rather than
`example.vcf`. Both files are the
materializer's output serialized as its own `--write` path does, so they are
byte-identical on regeneration and pass the same SHACL suite.

To regenerate them, or to materialize the fixture yourself:

The fixture materializes with the VCF Core vocabulary repository's
[`scripts/vcf_examples.py`](https://github.com/ecrum19/vcf-core-vocabulary/blob/main/scripts/vcf_examples.py),
the same materializer the assessments use. From a checkout of that repository at
tag `v2.1.3`, the version the manuscript cites:

```python
import sys; sys.path.insert(0, 'scripts')
from vcf_examples import materialize
for profile in ('expanded', 'condensed'):
    g = materialize('<path>/long_revised/examples/example.vcf', profile)
    open(f'<path>/long_revised/examples/materialized/example-{profile}.ttl', 'w').write(
        g.serialize(format='turtle').rstrip() + '\n')
```

The fixture materializes cleanly, and both graphs pass the repository's complete SHACL suite
(the shared profiles plus all five version overlays) and its decoded-value
checks, with no violations and no warnings.

One portability note on `rq3-local-allele-evidence.rq`: it casts with
`xsd:integer(?depth)` without declaring the `xsd:` prefix. Engines that pre-bind
`xsd:`, including the rdflib one used here, run it as written; a stricter engine
needs the prefix added. The file is kept byte-identical to the experiment input
rather than corrected here, so the two cannot drift apart.
