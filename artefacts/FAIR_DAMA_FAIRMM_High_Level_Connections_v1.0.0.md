---
title: "FAIR–DAMA–FAIRMM High-Level Connections"
version: "1.1.0"
created: "2026-11-19"
updated: "2026-11-19"
language: "en-GB"
status: "Proposed conceptual structure for elaboration"
scope: "Documentary alignment perspectives; no operational assessment or maturity attainment claims"
---

# FAIR–DAMA–FAIRMM High-Level Connections

This document proposes five connected views of FAIR delivery: FAIR Data Principles, Personas, FAIRMM Dimensions, FAIRMM Levels and DAMA Knowledge Areas. These are called **alignment perspectives** to distinguish them from the seven specific FAIRMM Dimensions.

Practices, activities, deliverables and supporting evidence form the connecting layer. They give each proposed relationship an explicit basis and preserve the distinction between a management capability, a person's participation and a demonstrated property of a data resource.

| Alignment perspective | What it describes | Principal connection |
|---|---|---|
| FAIR Data Principles | Properties required of data and metadata | DAMA practices contribute Directly or Indirectly to specific principles; those practices can also support FAIRMM capabilities. |
| Personas | People and roles involved in delivery | DAMA personas participate in activities; qualified proposed correspondences connect them to FAIRMM personas and contextual Producer, Consumer or Enabler roles. |
| FAIRMM Dimensions | Seven capability areas: FAIR Data, Leadership, Strategy, Personas, Processes, Knowledge, Tools and Infrastructure | DAMA practices support individual dimensions; each dimension has a contextual description at every maturity level. |
| FAIRMM Levels | Development of capability from L0 to L5 | Levels contextualise each dimension; proposed DAMA associations begin at an earliest supported level and carry forward. |
| DAMA Knowledge Areas | Management disciplines that organise delivery | Knowledge areas organise practices and activities, connecting deliverables, persona responsibilities and FAIR contributions. Additional topics remain separately classified. |

```mermaid
flowchart TB
    KA["DAMA Knowledge Areas<br/>+ separately classified additional topics"]
    P["Personas<br/>DAMA ↔ FAIRMM qualified correspondences"]
    A["Practices and activities"]
    O["Deliverables and supporting evidence"]
    F["FAIR Data Principles"]
    D["FAIRMM Dimensions"]
    L["FAIRMM Levels · L0–L5"]
    C["42 contextual descriptors<br/>7 dimensions × 6 levels"]

    KA -->|organise| A
    P -->|responsible, approving or contributing roles| A
    A -->|produce or maintain| O
    A -->|qualified Direct or Indirect contribution| F
    A -->|qualified Direct or Indirect alignment| D
    O -->|supports verification against| F
    O -->|supports interpretation against| C
    D -->|dimension context| C
    L -->|level context| C
    A -->|proposed earliest supported level| L
```

The diagram summarises relationship types. It does not imply that every practice connects to every perspective or that a proposed relationship establishes implementation.

### Ontology dataset and execution

The extraction dataset is a local RDF union of these nine Turtle modules:

- `artefacts/fairmm-core.ttl`, `fairmm-v1.2.5.ttl`, `fairmm-personas.ttl`, `fairmm-dama-alignment.ttl` and `fairmm-dama-derived.ttl`.
- `sources/2026-11-16/dama-ontologies-v1.1.0/fair-ontology.ttl`, `dama-ontology.ttl`, `dama-fair-mapping.ttl` and `dama-persona-ontology.ttl`.

Queries use the union as the default graph. Load the files explicitly; no remote `owl:imports`, inference, `SERVICE` calls or live assessment results are required. Direct/Indirect values belong to their declared assertion layer. Catalogue overview, activity and workbook assertions are not combined as independent evidence.

Reproduce all five views, PNGs, strict documentation build and independent checks from the independent project directory:

```powershell
pwsh -File scripts/build_high_level_all.ps1
```

Query files are also available under `scripts/queries/high-level-connections/`. The original ontologies are read-only inputs. The [diagram collection](../results/high-level-connections/index.html) links to all five static and on-demand interactive views, including offline interaction without D3 downloads. A ribbon's records show the exact SPARQL bindings used to construct it. In the personas view, intended deliverables are not verified outcomes; no observed evidence is fabricated.

## DAMA → FAIR Principles

This connection explains how management practices support resource-level FAIR requirements. Knowledge-area membership supplies the management context; the activity, its deliverable and its applicability conditions supply the basis for a qualified contribution assertion.

Direct contributions produce or verify evidence relevant to a particular principle. Indirect contributions identify an intermediate practice through which that evidence would be produced or verified. Source classifications from summaries, activity tables, ontology examples and area-level proposals remain distinct.

Further elaboration will describe the practice-to-principle pathways, required deliverables, intermediate practices, evidence requirements and source-layer differences.




<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** Which DAMA areas and topics have source activity assertions supporting each FAIR principle, and with which Direct/Indirect type?

**Interpretation and counting basis:** One equal-width ribbon per distinct area–principle–type. Activity assertion records remain available in ribbon details. Only the activity_table source layer is selected, avoiding duplicate counting across workbook, summary and ontology layers.

```sparql
PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?assertion ?area ?areaLabel ?practice ?practiceLabel ?principle ?kind ?source
WHERE {
  ?assertion a align:SourceAssertion ; align:sourceLayer "activity_table" ;
    align:inSourceTopic ?area ; align:hasPractice ?practice ;
    align:targetsPrinciple ?principle ; align:existingContributionType ?kind .
  ?area rdfs:label ?areaLabel . ?practice rdfs:label ?practiceLabel .
  OPTIONAL { ?assertion align:primarySource ?source }
}
ORDER BY ?area ?principle ?kind ?assertion
```

**Extraction result:** 173 distinct query rows; 27 nodes; 64 graphical links. Link types: Indirect 31, Direct 33.

[Static and on-demand interactive Sankey](../results/high-level-connections/dama-fair-principles/index.html) · [Static SVG](../results/high-level-connections/dama-fair-principles/high-level-dama-fair-principles-sankey.svg) · [Static PNG](../results/high-level-connections/dama-fair-principles/high-level-dama-fair-principles-sankey.png) · [Standalone query](../results/high-level-connections/dama-fair-principles/query.rq) · [Extracted evidence rows](../results/high-level-connections/dama-fair-principles/extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->

## DAMA → FAIRMM Dimensions

This connection explains which organisational capabilities DAMA practices support. The seven FAIRMM Dimensions provide complementary capability perspectives rather than subdivisions of the FAIR Data Principles.

Each proposed alignment retains its originating practice and knowledge-area or additional-topic context, one dimension target, a Direct or Indirect contribution type, rationale, conditions and supporting descriptor references. The FAIRMM contribution type remains separate from the source FAIR-principle classification.

Further elaboration will examine each dimension, its supporting DAMA practices and deliverables, conditional support, uncovered capabilities and relevant personas. The focused Tools and Infrastructure/persona Sankey provides an initial example of this traversal.




<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** Which DAMA areas and topics support each FAIRMM dimension through qualified Direct or Indirect assertions?

**Interpretation and counting basis:** One equal-width ribbon per distinct area–dimension–type, grouping qualified DimensionAlignment assertions. Two unassigned extension practices are excluded from this area-based view and reported separately. FAIRMM contribution type is not the original FAIR-principle classification.

```sparql
PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?assertion ?area ?areaLabel ?practice ?practiceLabel ?dimension ?dimensionLabel ?kind ?rationale ?condition
WHERE {
  ?assertion a align:DimensionAlignment ; align:sourceTopic ?area ;
    align:fromPractice ?practice ; align:targetsDimension ?dimension ;
    align:contributionType ?kind .
  ?area rdfs:label ?areaLabel . ?practice rdfs:label ?practiceLabel .
  ?dimension rdfs:label ?dimensionLabel .
  OPTIONAL { ?assertion align:rationale ?rationale }
  OPTIONAL { ?assertion align:applicabilityCondition ?condition }
}
ORDER BY ?area ?dimension ?kind ?assertion
```

**Extraction result:** 470 distinct query rows; 21 nodes; 54 graphical links. Link types: Direct 45, Indirect 9.

[Static and on-demand interactive Sankey](../results/high-level-connections/dama-fairmm-dimensions/index.html) · [Static SVG](../results/high-level-connections/dama-fairmm-dimensions/high-level-dama-fairmm-dimensions-sankey.svg) · [Static PNG](../results/high-level-connections/dama-fairmm-dimensions/high-level-dama-fairmm-dimensions-sankey.png) · [Standalone query](../results/high-level-connections/dama-fairmm-dimensions/query.rq) · [Extracted evidence rows](../results/high-level-connections/dama-fairmm-dimensions/extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->

## Dimensions × Levels

This connection supplies the 42 contextual descriptions against which proposed capability alignments are interpreted: seven dimensions across six maturity levels.

Dimensions and levels are flat vocabularies of named individuals. Their contextual Descriptor individuals each reference exactly one dimension and one level. Descriptors are contextual descriptions, not subprinciples. Level ordering is explicit; neither dimensions nor levels are subclasses of one another.

Further elaboration will preserve exact descriptor wording separately from interpreted capabilities and examine how scope, integration, governance and operational expectations develop across L0–L5.




<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** How do the seven dimensions and six ordered levels connect through the 42 contextual descriptors?

**Interpretation and counting basis:** Dimension → Descriptor → Level. Each descriptor contributes one unit on each adjacent leg: 42 descriptors, 84 graphical links. These are matrix membership relationships, not Direct/Indirect contributions or assessed maturity. Hover or focus a descriptor to read its explanatory RDF comment; select it for the summary and source.

```sparql
PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?dimension ?dimensionLabel ?descriptor ?descriptorID ?descriptorComment ?level ?levelLabel ?ordinal ?source
WHERE {
  ?descriptor a align:Descriptor ; align:inDimension ?dimension ;
    align:atLevel ?level ; dcterms:identifier ?descriptorID .
  ?dimension a align:Dimension ; rdfs:label ?dimensionLabel .
  ?level a align:MaturityLevel ; rdfs:label ?levelLabel ; align:levelOrdinal ?ordinal .
  OPTIONAL { ?descriptor rdfs:comment ?descriptorComment }
  OPTIONAL { ?descriptor align:primarySource ?source }
}
ORDER BY ?dimension ?ordinal
```

**Extraction result:** 42 distinct query rows; 55 nodes; 84 graphical links. Link types: Descriptor 84.

[Static and on-demand interactive Sankey](../results/high-level-connections/dimensions-levels/index.html) · [Static SVG](../results/high-level-connections/dimensions-levels/high-level-dimensions-levels-sankey.svg) · [Static PNG](../results/high-level-connections/dimensions-levels/high-level-dimensions-levels-sankey.png) · [Standalone query](../results/high-level-connections/dimensions-levels/query.rq) · [Extracted evidence rows](../results/high-level-connections/dimensions-levels/extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->

## Personas → Activities → Outcomes

This connection explains who participates, through which source responsibilities, and with which intended outputs. Responsible, Approving and Contributing activity-role occurrences remain separate from area-level Supplier, Participant and Consumer occurrences.

Qualified Close, Partial or Gap correspondences connect DAMA and FAIRMM persona catalogues. A Gap identifies a missing or insufficient correspondence; it does not assert equivalence. Producer, Consumer and Enabler assignments remain contextual to an activity or practice. FAIRMM Personas is both a capability dimension and a separate catalogue of actor archetypes; these resources have different meanings.

Persona participation does not automatically inherit a practice's Direct or Indirect classification, appoint an individual or establish personal accountability. Deliverables are intended outputs; demonstrated FAIR outcomes require supporting evidence.

Further elaboration will describe role occurrences, persona correspondences, activity handoffs, decision rights, deliverables, evidence and unresolved source labels. The existing persona Sankey traces participation through activities rather than inferring responsibility from area membership.




<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** Which DAMA personas occur in recorded activity responsibilities, and which intended deliverables are connected to those practices?

**Interpretation and counting basis:** Persona → Activity → Intended deliverable. Persona-to-activity weight counts distinct RDF ActivityRoleOccurrence resources, retaining role categories in the details. An activity’s incoming count is allocated equally across its distinct deliverables to conserve flow. Width measures documentary role occurrences, not effort, accountability or verified outcomes. Only occurrences already materialised in the ontology are included; this is not a complete extraction of every workbook role. Area-level supplier/participant/consumer occurrences are not used.

```sparql
PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?occurrence ?persona ?personaLabel ?role ?practice ?practiceLabel ?deliverable ?deliverableLabel ?source
WHERE {
  ?occurrence a align:ActivityRoleOccurrence ; align:sourcePersona ?persona ;
    align:sourceRoleCategory ?role ; align:concernsPractice ?practice .
  ?persona rdfs:label ?personaLabel . ?practice rdfs:label ?practiceLabel ;
    align:hasDeliverable ?deliverable .
  ?deliverable rdfs:label ?deliverableLabel .
  OPTIONAL { ?occurrence dcterms:source ?source }
}
ORDER BY ?persona ?practice ?role ?deliverable ?occurrence
```

**Extraction result:** 356 distinct query rows; 237 nodes; 465 graphical links. Link types: Responsible 116, Approving 80, Contributing 160, Deliverable 109.

[Static and on-demand interactive Sankey](../results/high-level-connections/personas-activities-outcomes/index.html) · [Static SVG](../results/high-level-connections/personas-activities-outcomes/high-level-personas-activities-outcomes-sankey.svg) · [Static PNG](../results/high-level-connections/personas-activities-outcomes/high-level-personas-activities-outcomes-sankey.png) · [Standalone query](../results/high-level-connections/personas-activities-outcomes/query.rq) · [Extracted evidence rows](../results/high-level-connections/personas-activities-outcomes/extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->

## DAMA → Levels

This connection provides the cumulative association view. An earliest-supported-level judgement identifies the first level at which a particular practice contribution is supported by a descriptor and the documentary source.

For an onset at level k, associations carry forward through L5 while retaining the originating area or topic, practice, first-supported level and contribution type. Introduced and inherited associations remain distinguishable, with explicit onset and derivation references. Indirect support is never promoted to Direct through inheritance.

L0 remains diagnostic, without positive alignment assertions. Cumulative area association does not establish that an organisation has attained a maturity level or require every earlier process to remain unchanged. The 11 core knowledge areas remain distinct from additional supporting topics, and inclusion in a diagram does not change that classification.

Further elaboration will examine onset rationales, progression context, cumulative derivation rules, scope exceptions and the evidence that would be needed for a separate maturity assessment.




<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** At which levels are DAMA area/type associations introduced or inherited, and which onset judgement and derivation rule explain them?

**Interpretation and counting basis:** One equal-width ribbon per cumulative area–level–type association. Each association retains its first-supported level, onset, introduced/inherited flag and derivation rule. L0 is visible but has no positive links. The 11 core areas and two additional topics are included; supporting Maturity Assessment has no positive onset in this view. Association does not establish attained maturity.

```sparql
PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?association ?area ?areaLabel ?level ?levelLabel ?ordinal ?kind ?onset ?firstLevel ?inherited ?rule
WHERE {
  ?association a align:CumulativeAssociation ; align:sourceTopic ?area ;
    align:targetsLevel ?level ; align:contributionType ?kind ;
    align:derivedFromOnset ?onset ; align:firstSupportedLevel ?firstLevel ;
    align:inherited ?inherited ; align:derivationRule ?rule .
  ?area rdfs:label ?areaLabel .
  ?level rdfs:label ?levelLabel ; align:levelOrdinal ?ordinal .
}
ORDER BY ?area ?ordinal ?kind
```

**Extraction result:** 127 distinct query rows; 19 nodes; 127 graphical links. Link types: Direct 62, Indirect 65.

[Static and on-demand interactive Sankey](../results/high-level-connections/dama-levels/index.html) · [Static SVG](../results/high-level-connections/dama-levels/high-level-dama-levels-sankey.svg) · [Static PNG](../results/high-level-connections/dama-levels/high-level-dama-levels-sankey.png) · [Standalone query](../results/high-level-connections/dama-levels/query.rq) · [Extracted evidence rows](../results/high-level-connections/dama-levels/extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->

---

**Proposed presentation:** arrange the five alignment perspectives around a central **Practices and Evidence** hub. Selectable relationships could open the relevant detailed Sankeys and qualified ontology assertions. This is a conceptual presentation proposal, not an implemented interface.

**Local documentary basis:** the supplied DAMA ontology v1.1.0, DAMA Segments document v1.18.0 and V3 workbook release of 16 November 2026; FAIRMM branch `FAIR-MM-V1.2.5`, revision `8ff4676eb340b0da5034ffb3d0e901c594c3cfc4`. See the [source refresh](../docs/source-refresh.md), [ontology documentation](../docs/ontology.md) and [Tools and Infrastructure persona analysis](../docs/tools-personas/index.md). Existing component attribution and licensing notices remain applicable.

**Versioning:** use semantic versions. Major versions change the conceptual structure or relationship meanings; minor versions add substantive elaboration or new connections; patch versions correct wording, references or presentation without changing meaning. Preserve this initial version as the starting point for subsequent elaboration.

**Change history:** v1.0.0 — 19 November 2026: initial five-perspective structure, connection diagram and five connection sections captured from the agreed discussion for further elaboration.

**v1.1.0 — 19 November 2026:** added executable SPARQL and five RDF-derived static/interactive Sankey views. The original v1.0.0 content is preserved under `results/history/high-level-connections/`. The requested v1.0.0 filename remains an enriched compatibility copy; the semantic release filename is v1.1.0.
