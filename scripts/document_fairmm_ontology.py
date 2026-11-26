"""Generate module documentation and the execution report from validation results."""
import json
from pathlib import Path
from fairmm_rdf import ROOT,OUT,ART,MODULES,write


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in row)+' |' for row in rows])


def main():
    validation=json.loads((OUT/'validation.json').read_text())
    regression=json.loads((OUT/'rdf-sankey-regression.json').read_text())
    manifest=json.loads((OUT/'build-manifest.json').read_text())
    descriptions={
      'fairmm-core.ttl':'OWL/RDFS classes, typed properties, cardinality restrictions and contribution semantics.',
      'fairmm-v1.2.5.ttl':'Framework version, seven dimensions, six ordered levels and 42 source descriptors.',
      'fairmm-personas.ttl':'Thirty FAIRMM personas, three data roles and qualified counterpart comparisons.',
      'fairmm-dama-alignment.ttl':'Source practices, source-layer assertions, dimension alignments, level onsets and contextual role candidates.',
      'fairmm-dama-derived.ttl':'Cumulative level associations derived from RDF onset assertions and level ordinals.',
    }
    rows=[(f'[{name}](ontology-data/{name})',manifest['modules'][name],descriptions[name]) for name in MODULES]
    counts=validation['counts']
    onsets=counts['OnsetAlignment']; cumulative=counts['CumulativeAssociation']; dimensions=regression['dimensions']['actual']
    def current(text):
        return text.replace('22 onset judgements',f'{onsets} onset judgements').replace('107 projections',f'{cumulative} projections').replace('22 introduced',f'{onsets} introduced').replace('85 inherited',f'{cumulative-onsets} inherited').replace('107 independent',f'{cumulative} independent').replace('45 dimension relationships',f'{dimensions} dimension relationships').replace('107 level relationships',f'{cumulative} level relationships').replace('107 cumulative level relationships',f'{cumulative} cumulative level relationships').replace('22 onsets',f'{onsets} onsets').replace('approved baselines','source-release regression baselines').replace('approved JSON','source-release JSON').replace('Frozen approved JSON baselines remain preserved for provenance.','Previous 45-dimension / 22-onset / 107-cumulative baselines remain in results/history/pre-2026-11-16-refresh; current projections are proposed, not user-approved judgements.')
    doc='''# FAIRMM ontology

The FAIRMM ontology follows the existing FAIR–DAMA patterns: named individuals in flat vocabularies, explicit framework membership and qualified contribution assertions. Dimension and maturity-level vocabularies have no subprinciples. Levels are ordered individuals, not subclasses of each other.

![FAIRMM ontology structure](assets/images/fairmm-ontology.svg)

For the accepted integrated asserted distribution and source/provenance dataset, see [Integrated ontology](integrated/index.md). The module tables and existing diagrams below describe the documentary model.

## Download the modules

'''+table(['Module','Triples','Contents'],rows)+'''

Load all five files together. Module imports use local URN identifiers and are resolved by the supplied loader; it never fetches remote imports.

## Vocabulary structure

`Dimension` and `MaturityLevel` are classes. Their seven and six named individuals belong to `FAIRMM-v1.2.5` through `dcterms:hasPart`. Version-specific enumeration classes and `owl:AllDifferent` follow the existing FAIR/DAMA vocabulary pattern. The 42 descriptors are separate individuals, each with one `inDimension` and one `atLevel` relation. Framework membership does not make descriptors subdivisions or subprinciples.

Each vocabulary member has an identifier, label, definition, version context and pinned source. Levels have ordinal values 0–5, five immediate `nextLevel` links and the explicit `precedes` ordering. Ordering alone does not imply capability inheritance or organisational maturity.

The term namespace remains `urn:fair-dama-fairmm:alignment:`. Existing D1–D7 and descriptor identifiers are reused. New classes, levels and supporting resources stay in that independent namespace; no new resource is represented as published in FAIR–DAMA.

## Qualified alignments and pattern reuse

`DimensionAlignment` targets exactly one dimension. `OnsetAlignment` targets exactly one first-supported level. Each assertion retains its practice, source knowledge-area/topic context, contribution type, rationale, applicability condition, evidence requirement and review status. The two extensions without an assigned source area remain explicitly unassigned; no area is invented.

Direct support produces or verifies evidence addressing the target capability. Indirect support names an intermediate practice using `viaPractice`. A separate `sourceIntermediatePractice` relation preserves enabling paths attached to original FAIR-principle assertions. Source FAIR classification is not substituted for dimension or level contribution type.

The original FAIR-targeted properties are not repurposed: their domains and ranges would otherwise classify FAIRMM alignments as FAIR contribution assertions. The new properties reuse the pattern without changing upstream meanings.

Source summary, activity-table, ontology-example and visualisation assertions remain distinct named resources. Enabling labels from the Sankey remain recorded alongside their normalized Indirect classification. Original source fields are linked resources, with headings, positions and exact text. Descriptor support, role occurrences, deliverables and counterpart candidates are also linked resources, not JSON blobs in RDF literals.

Exact descriptor text is stored in `fullSourceBlock`. Source-cited clauses use `DescriptorEvidence`. Proposed interpretations are separate `CapabilityInterpretation` resources; they are not treated as new authoritative FAIRMM wording.

## Personas and role context

Thirty FAIRMM persona individuals and Producer, Consumer and Enabler data roles are represented. Persona correspondences retain Close, Partial or Gap status. Gap counterpart records are explicitly related counterparts, without equivalence or identity assertions.

Area-level Supplier/Participant/Consumer occurrences remain distinct from Responsible/Approving/Contributing activity-role occurrences. Data-role assignment candidates identify a persona, a specific practice, a role and their source occurrence. They are proposals, not appointments or declarations of legal authority. General role suggestions remain attached to correspondence records with an explicit requirement for activity context.

The source knowledge-area labels retain their original edition context. Existing recorded correspondences to the canonical DAMA vocabulary are preserved, but differing labels are not merged with `owl:sameAs` or an equivalent-class assertion.

## Cumulative association

The 22 onset judgements are original proposed alignments. The separate derived module contains 107 projections: 22 introduced associations at their onset levels and 85 inherited associations at higher levels. These projections are not 107 independent capability judgements and must not be added to the onset count as independent evidence.

Every derived association names its onset, derivation rule, first supported level, target level and introduced/inherited status. The practice, area and Direct/Indirect type are retained. The rule is implemented both as an RDF-driven materializer and as an independently checked [SPARQL CONSTRUCT](ontology-data/queries/cumulative-construct.rq).

L0 descriptors and diagnostic reviews are retained, but no positive L0 alignment is asserted. Cumulative area association does not require every early process to remain unchanged. No organisation is declared to have attained any maturity level.

## Validation and regression

'''+f"The current build passes **{validation['check_count']} ontology checks**, including negative cases for duplicate descriptor levels, missing Indirect pathways, changed inherited type and positive L0 claims. Validation uses RDFLib, ordinary scripts and SPARQL. No SHACL files or dependencies are used.\n\n"+table(['Resource','Count'],[(k,v) for k,v in counts.items()])+'''

Both Sankeys are regenerated from RDF-extracted records using the existing renderers. Their static/on-demand D3 presentation and selector-free interaction are preserved. Approved JSON is used only for regression comparison. The 45 dimension relationships and 107 level relationships match exactly; intermediate activity record counts and first-level/inherited flags also agree.

Validation checks exact descriptor source blocks, persona definitions, all original activity-table fields, source-layer classification, target types, required fields, cumulative closure and unchanged source checkouts. OWL axioms document the model; the scripts provide the closed checks that OWL's open-world semantics do not perform by themselves. This is structural and documentary validation, not an operational pilot or full formal OWL consistency proof.

## Query examples

Run a query from the project root:

```powershell
.venv/Scripts/python.exe scripts/query_fairmm_ontology.py scripts/queries/earliest-levels.rq
.venv/Scripts/python.exe scripts/query_fairmm_ontology.py scripts/queries/indirect-pathways.rq
.venv/Scripts/python.exe scripts/query_fairmm_ontology.py scripts/queries/contextual-roles.rq
```

Available downloads: [dimension links](ontology-data/queries/dimension-links.rq), [level links](ontology-data/queries/level-links.rq), [earliest levels](ontology-data/queries/earliest-levels.rq), [Indirect pathways](ontology-data/queries/indirect-pathways.rq), [persona comparisons](ontology-data/queries/persona-correspondences.rq), [contextual roles](ontology-data/queries/contextual-roles.rq), and [source layers](ontology-data/queries/source-layers.rq).

## Reproduce the build

```powershell
pwsh -File scripts/build_ontology_all.ps1
```

The pipeline creates the modules, validates them, extracts RDF diagram inputs, regenerates the SVG/HTML/PNG outputs, renders this ontology diagram and builds the documentation. The sibling FAIR–DAMA and FAIR-Maturity-Matrix repositories remain read-only. Nothing is pushed or deployed.

## Sources and attribution

FAIRMM source material is attributed to the Pistoia Alliance FAIR Maturity Matrix contributors, branch `FAIR-MM-V1.2.5`, revision `'''+manifest['source_revisions']['fairmm_revision']+'''`. The repository carries GPL-3.0; the persona overview separately states CC BY 4.0. The [upstream repository licence](ontology-data/FAIRMM-LICENSE.txt) is retained. These notices are not replaced by a blanket licence for all components.

FAIR–DAMA mappings and definitions are attributed to Chris Day, revision `'''+manifest['source_revisions']['fair_dama_revision']+'''`, under the source repository's CC0 licence. The original FAIR vocabulary retains its own identifiers, authorship and CC BY 4.0 notice. Pinned references and source digests are recorded in the build manifest.
'''
    doc=current(doc).replace('Source summary, activity-table, ontology-example and visualisation assertions remain distinct named resources. Enabling labels from the Sankey remain recorded alongside their normalized Indirect classification.','Catalogue overview, detailed section summary, Markdown activity, workbook activity, ontology contribution and ontology area-assessment assertions remain distinct named resources. Historical visualisation assertions remain in the archived corpus.').replace('Approved JSON','Source-release proposed JSON')
    doc=doc.replace('Exact descriptor text is stored in `fullSourceBlock`.', 'All 42 descriptors have an English `rdfs:comment` explaining the corresponding FAIRMM dimension–level cell in plain language. These comments are project-authored paraphrases, not verbatim upstream definitions, additional assessment requirements or maturity results. Their source context is the descriptor’s pinned `primarySource`; the exact original wording remains in `fullSourceBlock`. The [descriptor comments query](ontology-data/queries/descriptor-comments.rq) retrieves both separately. The high-level interactive and offline Sankeys show the comment on descriptor hover, keyboard focus and selection. Exact descriptor text is stored in `fullSourceBlock`.')
    if manifest['source_revisions'].get('dama_source_release'):
        doc=doc.replace('FAIR–DAMA mappings and definitions are attributed to Chris Day, revision `'+manifest['source_revisions']['fair_dama_revision']+'`, under the source repository\'s CC0 licence.','DAMA mappings and definitions are attributed to Chris Day, supplied ontology v1.1.0 / document v1.18.0 / workbook V3 release, 16 November 2026. The checkout revision is context only. Preserve source-component notices and DAMA International source-image copyright. See the [source refresh](source-refresh.md) for provenance and combined load order.')
        doc+='\n\n## Source ontology dependencies\n\nUse the supplied v1.1.0 source modules for this release: [FAIR](ontology-data/dama-source-v1.1.0/fair-ontology.ttl), [DAMA](ontology-data/dama-source-v1.1.0/dama-ontology.ttl), [FAIR mappings](ontology-data/dama-source-v1.1.0/dama-fair-mapping.ttl), [DAMA personas](ontology-data/dama-source-v1.1.0/dama-persona-ontology.ttl). These are byte-identical copies from the supplied package; the sibling repository is unchanged.\n'
    write(ROOT/'docs/ontology.md',doc)
    for path in (ROOT/'scripts/queries').glob('*.rq'):write(ROOT/'docs/ontology-data/queries'/path.name,path.read_text())
    write(ROOT/'docs/ontology-data/FAIRMM-LICENSE.txt',(ROOT/'docs/fairmm/data/FAIRMM-LICENSE.txt').read_text())
    for name in ['validation.json','rdf-sankey-regression.json']:
        write(ROOT/'docs/ontology-data'/name,(OUT/name).read_text())
    report='''# FAIRMM ontology execution report

Five modular OWL/RDFS Turtle files have been built in the independent FAIR-DAMA-FAIRMM project. Both source repositories remain unchanged. No SHACL, operational pilot, push or deployment is included.

'''+table(['Module','Triples'],manifest['modules'].items())+'\n\n'+table(['Resource','Count'],counts.items())+f'''

## Validation results

All {validation['check_count']} ontology checks passed. The four malformed cases were rejected. An independent SPARQL CONSTRUCT agrees with the RDF-driven cumulative materializer. Source definitions, activity fields, original classifications and component provenance were checked.

RDF-regenerated Sankeys match the approved baselines: **45 dimension relationships** and **107 cumulative level relationships**, retaining **22 onsets**. The derived projection includes 22 introduced and 85 inherited associations. RDF extract files and the comparison report are in this folder.

## Reusable resources

- [Ontology documentation](../../docs/ontology.md)
- [Ontology SVG](fairmm-ontology.svg)
- [Validation details](validation.json)
- [Sankey regression](rdf-sankey-regression.json)
- [Build manifest](build-manifest.json)

The module files are in `../../artefacts/`, the query examples in `../../scripts/queries/`, and the one-command build is `../../scripts/build_ontology_all.ps1`. Frozen approved JSON baselines remain preserved for provenance.

Validation is structural and documentary. It does not constitute an operational assessment or a full formal OWL consistency proof.
'''
    write(OUT/'Execution_Report.md',current(report))
    print('Generated ontology documentation, query downloads and execution report')


if __name__=='__main__':main()
