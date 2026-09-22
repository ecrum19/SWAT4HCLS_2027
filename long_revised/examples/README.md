# Listing and figure fixtures

Machine-readable counterparts of the fixtures printed in the manuscript. The
listings in the PDF align their columns for display; the files here are
tab-delimited, as VCF requires. The fixtures are reductions of ones that live in
the experiment directories, kept here so the printed listings can be parsed and
re-run; they are not themselves experiment inputs. The queries are the full text
of what the manuscript prints or describes, and `rq3-local-allele-evidence.rq`
is the experiment input itself, copied byte for byte.

| File | Backs |
| --- | --- |
| `example.vcf` | Listing 1 and Figure 1, and the RQ1 worked cases in `rq1.tex`. |
| `representation.vcf` | RQ3's join table (Table 4), reduced from `RQ3/`'s local-allele fixture. |
| `annotations.ttl` | The external snapshot `representation.vcf` joins against, reduced from `RQ3/inputs/annotations.ttl`. |
| `queries/r27-local-allele-map.rq` | Listing 2, in full. |
| `queries/r21-missingness.rq` | The R21 query that `rq1.tex` describes in prose, in full. |
| `queries/rq3-local-allele-evidence.rq` | Listing 3's source query, in full. Byte-identical to `RQ3/inputs/local-allele-evidence.rq`. |

## The worked cases

`example.vcf` carries four records and two sample columns, and exhibits both
requirements discussed under RQ1:

- **R27** (local allele indices map to global record alleles) at `POS=2`. Both
  samples name one local allele, but different ones: `LAA=2` for `S1` and
  `LAA=1` for `S2`. Because `LAD` is declared `Number=LR`, the second value of
  each sample belongs to that sample's own local ALT allele — global allele 2
  (`C`) for `S1`, global allele 1 (`A`) for `S2`. The mapping is per sample, not
  per record.
- **R21** (explicit missingness versus an omitted field) at `POS=4`. `S1` writes
  `./.:.:.`, explicitly reporting a missing `LAD`; `S2` writes `0/0`, dropping
  the trailing `LAA` and `LAD` subfields altogether. The two must stay
  distinguishable.

## Verified answers

The two RQ1 queries run against the expanded-profile witness graph of
`example.vcf`.

`r27-local-allele-map.rq` returns twelve rows over the three records that carry
allele depths; the four for `POS=2` are the ones quoted in `rq1.tex`:

```
?pos  ?sample  ?index  ?global  ?allele  ?depth
2     S1       0       0        G        20
2     S1       1       2        C        30
2     S2       0       0        G        12
2     S2       1       1        A        9
```

`r21-missingness.rq` returns exactly two rows, the second with `?raw` unbound:

```
?sample  ?raw
S1       "."
S2       (unbound)
```

`rq3-local-allele-evidence.rq` runs against `representation.vcf` merged with
`annotations.ttl`. Listing 3 in the manuscript prints only its `WHERE` clause;
this is the whole query, including the `LAD >= 20` threshold and the provenance
fields the excerpt omits. It returns the two alterations quoted in `rq3.tex`:

```
?contig ?position ?ref ?alt ?depth ?sample ?fieldId ?number
chr1    1         G    C    30     sample  LAD      LR
chr1    2         A    T    25     sample  LAD      LR
```

The other two flagged alterations in `annotations.ttl` are excluded because no
`LAD` item points at their allele. Resolve `Number=LR` positionally instead and
both gain a depth above the threshold — that is the contrast Table 4 tabulates.

## Reproducing

Both fixtures materialize with the VCF Core vocabulary repository's
[`scripts/vcf_examples.py`](https://github.com/ecrum19/vcf-core-vocabulary/blob/main/scripts/vcf_examples.py),
the same materializer the assessments use. From a checkout of that repository:

```python
import sys; sys.path.insert(0, 'scripts')
from vcf_examples import materialize
g = materialize('<path>/long_revised/examples/example.vcf', 'expanded')
print(len(list(g.query(open('<path>/examples/queries/r21-missingness.rq').read()))))
```

Both fixtures materialize cleanly and pass the repository's complete SHACL suite
(the shared profiles plus all five version overlays) and its decoded-value
checks, with no violations and no warnings.

One portability note on `rq3-local-allele-evidence.rq`: it casts with
`xsd:integer(?depth)` without declaring the `xsd:` prefix. Engines that pre-bind
`xsd:`, including the rdflib one used here, run it as written; a stricter engine
needs the prefix added. The file is kept byte-identical to the experiment input
rather than corrected here, so the two cannot drift apart.
