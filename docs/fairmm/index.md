# FAIRMM alignment

The documentary crosswalk connects DAMA activities and their existing Direct and Indirect FAIR relationships to the seven FAIR Maturity Matrix dimensions. It preserves the source classifications and adds conditional dimension relationships and persona correspondences.

The DAMA source is the supplied ontology v1.1.0, document v1.18.0 and workbook V3 release (16 November 2026) and FAIRMM branch **FAIR-MM-V1.2.5**, revision `8ff4676eb340`. The crosswalk contains **156 activity rows**, **30 FAIRMM persona comparisons**, **42 dimension and level references**, and **472 proposed dimension relationships**. Counts describe documentary records, not maturity or implementation.

## Explore the alignment

- [Knowledge areas and source reconciliation](areas.md)
- [Persona correspondences](personas.md)
- [Persona links to Direct and Indirect FAIR contributions](persona-relationships.md)
- [Dimensions and maturity references](dimensions.md)
- [Documentary review and remaining decisions](review.md)
- [Download the complete crosswalk](data/crosswalk.json)
- [Modular FAIRMM ontologies](../ontology.md)

## Interpreting relationships

**Direct FAIR contribution** retains the source assertion that a practice can produce or verify relevant resource evidence. **Indirect FAIR contribution** retains enabling support and names a proposed intermediate practice. Both remain conditional on implementation.

**Dimension support** is a separate proposal. Governance can directly address Leadership or Strategy while having no specific principle ID in the source summary. A tool list alone cannot establish Tools and infrastructures, and a policy alone cannot establish resource FAIRness.

Persona correspondences are functional candidates. Close, Partial and Gap express the result of comparing the documentary roles; they do not appoint people or confer decision rights. Producer, Consumer and Enabler depend on the actual activity. An Enabler may contribute directly to FAIR evidence.

The operational pilot was excluded at the user's request. No operational test results or maturity levels are assigned. All descriptor links are candidate support requiring the full descriptor to be assessed in context.

## Source layers

| Layer | Principle assertion records | Interpretation |
| --- | --- | --- |
| segment_summary | 82 | Separate source scope; do not sum as maturity coverage |
| workbook_activity_table | 173 | Separate source scope; do not sum as maturity coverage |
| activity_table | 173 | Separate source scope; do not sum as maturity coverage |
| catalogue_overview_summary | 64 | Separate source scope; do not sum as maturity coverage |
| ontology_contribution | 40 | Separate source scope; do not sum as maturity coverage |
| ontology_area_assessment | 74 | Separate source scope; do not sum as maturity coverage |

The segment summaries, Markdown activity tables, workbook activity tables, ontology contributions and ontology area assessments have different scopes. The Data Management overview is an aggregate and is excluded from primary coverage totals. The inherited persona principle lists remain separate from activity responsibilities.

## Sources and attribution

FAIRMM source material is attributed to the **Pistoia Alliance FAIR Maturity Matrix contributors**, [FAIR-MM-V1.2.5 source](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/tree/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4). Its repository carries [GPL-3.0](data/FAIRMM-LICENSE.txt); the persona overview separately states [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These source notices are preserved rather than applying one licence to every component. The crosswalk adds proposed correspondences and conditional dimension relationships; the extracted source blocks retain their upstream notices. DAMA source classifications are attributed to Chris Day, supplied ontology v1.1.0 / document v1.18.0 / workbook V3 release. Preserve the component notices and DAMA International source-image copyright; see the [source refresh](../source-refresh.md). The JSON manifest records SHA-256 digests of the source inputs.
