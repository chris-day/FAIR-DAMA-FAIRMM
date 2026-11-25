# Proposed alignment of FAIR DAMA with FAIR Maturity Matrix

Draft for review · 14 November 2026 · FAIRMM branch FAIR-MM-V1.2.5

Use FAIR principles as the bridge between DAMA practices and FAIRMM, and use persona equivalences to identify who could deliver, enable or use the resulting evidence. Preserve the existing Direct and Indirect classifications. Add a separate relationship to the seven FAIRMM dimensions, because organisational leadership and strategy can directly support a maturity dimension while contributing indirectly to resource FAIRness.

The proposal below covers the existing knowledge-area mappings, all 30 FAIRMM personas, evidence priorities and a staged implementation plan. It proposes alignment; it does not assign an organisation a maturity level.

## Sources and scope

Both repositories were cloned into `research-repos` in the FAIR workspace. Source snapshots are:

| Source | Revision | Main evidence |
| --- | --- | --- |
| FAIR–DAMA | `438ad2d0c6be3c336254fe3ce6a5d93f111db8a0` | Segment summaries and activity tables, persona catalogue, contribution ontology |
| FAIR Maturity Matrix | `8ff4676eb340b0da5034ffb3d0e901c594c3cfc4` on `FAIR-MM-V1.2.5` | Seven dimensions, six levels, persona descriptions and Producer/Consumer/Enabler definitions |

The [FAIR–DAMA site](https://fair-dama.perdl.com/) provides the publication context. Its live endpoint was unavailable during this review; the cloned documentation is the evidence baseline. The newer local workbook dated 30 October was not substituted for the repository baseline.

Key source links, pinned to the reviewed revisions:

- [DAMA segment summaries and activity tables](https://github.com/chris-day/FAIR-DAMA/tree/438ad2d0c6be3c336254fe3ce6a5d93f111db8a0/docs/dama/segments)
- [DAMA persona catalogue and inference rules](https://github.com/chris-day/FAIR-DAMA/blob/438ad2d0c6be3c336254fe3ce6a5d93f111db8a0/docs/dama/personas.md)
- [DAMA contribution ontology](https://github.com/chris-day/FAIR-DAMA/blob/438ad2d0c6be3c336254fe3ce6a5d93f111db8a0/artefacts/dama-fair-mapping.ttl)
- [FAIRMM dimensions](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4/docs/FMMdimensions.md), [levels](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4/docs/FMMlevels.md) and [Level 3 descriptors](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4/docs/level3.md)
- [FAIRMM persona catalogue](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/tree/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4/docs/FAIR_personas) and [data roles](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/8ff4676eb340b0da5034ffb3d0e901c594c3cfc4/docs/FAIR_roles/FAIRMM_roles.md)

## Relationship rules

Keep four independent fields for each alignment:

| Relationship | Meaning | Decision rule |
| --- | --- | --- |
| Existing FAIR contribution | Direct or Indirect relationship already recorded in FAIR–DAMA | Preserve source, granularity and applicability conditions |
| Proposed FAIRMM dimension support | Direct or Indirect support for a named dimension descriptor | Direct when a deliverable addresses that descriptor; Indirect when it enables another practice that does |
| Persona equivalence | Close functional match, partial match, or gap | Compare responsibilities and tasks; retain the original names and many-to-many matches |
| Data role | Producer, Consumer, Enabler, or a combination | Assign for the actual dataset and activity, rather than from a job title or DAMA supplier/participant/consumer label alone |

In the contribution ontology, Direct means a practice produces or verifies evidence addressing a FAIR subprinciple. Indirect means it enables an intermediate practice that produces or verifies that evidence. An Enabler can therefore contribute directly: a metadata specialist who publishes and tests a catalogue entry can directly support F4. Conversely, a Producer who merely supplies data need not directly establish any FAIR requirement.

The DAMA persona table derives principle lists by taking the union across every area in which the persona is a supplier, participant or consumer. Those inherited lists are discovery aids. A persona equivalence does not transfer the entire list into an activity assignment, establish accountability, or demonstrate implementation.

Use this trace for each proposed record:

`DAMA activity and deliverable → existing FAIR contribution → FAIR principle → relevant FAIRMM dimension and level descriptor`

Attach the DAMA persona occurrence, proposed FAIRMM persona, data role, evidence test and any intermediate practice to that record. A shared principle generates a candidate relationship; the descriptor and evidence decide whether it is useful.

## Existing principle mappings and proposed dimension alignments

The Direct and Indirect columns below reproduce the numbered segment summaries. D1–D7 abbreviate FAIRMM dimensions: Data, Leadership, Strategy, Personas, Processes, Knowledge, and Tools and infrastructures. The final column is a new proposal.

| DAMA area | Existing Direct FAIR IDs | Existing Indirect FAIR IDs | Proposed primary FAIRMM alignment |
| --- | --- | --- | --- |
| Data Governance | None identified | None identified | Direct D2/D3/D4 through FAIR-specific authority, strategy and appointments; indirect D1 through implementation teams |
| Data Architecture Management | I1, I2, I3, R1.2, R1.3 | F1 | Direct D7 and D5 through implemented representations and architectural controls; D1 through resource tests |
| Data Development | A1, I1, I3, R1.2 | None identified | Direct D5/D7 through development workflows, services and provenance capture; D1 through outputs |
| Data Operations Management | None identified | A2, R1.1, R1.2 | Direct D5/D7 through FAIR-specific retention and service operations; indirect D1 through surviving metadata, applicable licences and provenance |
| Data Security Management | A1.2 | A1.2 | Direct D5/D7 through retrieval controls; direct or indirect D1 according to configuration versus policy |
| Reference & Master Data Management | I3, R1.2 | None identified | Direct D5/D7 through governed resource links and lineage; D1 through linked records |
| Data Warehousing & Business Intelligence | F4, A1 | None identified | Direct D1/D7 through searchable, retrievable data products; D5 through repeatable publication |
| Document & Content Management | F2, F4, A1, A1.2, I2 | A2 | Direct D1/D5/D7 through descriptions, search, access and vocabulary use; metadata survival remains an indirect principle mapping |
| Meta-data Management | F2, F4, A1, I1, I3, R1, R1.2, R1.3 | F3, A2 | Direct D1/D5/D7 through metadata, catalogues, lineage and validation; indirect F3/A2 retained |
| Data Quality Management | None identified | F2, R1 | Direct D5 through quality controls explicitly applied to FAIR descriptions; indirect D1 through improved metadata |
| Data Integration & Interoperability | F2, F4, A1.2, R1, R1.2 | A1, A1.1, A1.2, A2, I1, I3, R1, R1.2, R1.3 | Direct D5/D7 through integration procedures and services; D1 relationships preserve each activity's classification |
| Data Management Maturity Assessment | No specific IDs | No specific IDs | Direct support for assessment and improvement across D1–D7 when the instrument uses FAIRMM descriptors; indirect support for subsequent FAIR improvements |

The Data Management overview is an aggregate of the original ten segments. Exclude it from mapping counts to avoid duplication. Maturity Assessment is a supporting discipline, not an additional core knowledge area.

D6 requires an explicit addition: role-specific FAIR learning objectives, practical exercises and demonstrated competence. General documentation or a named SME is insufficient. D4 likewise needs agreed responsibilities, interactions and capacity, beyond a catalogue of role names.

### Reconcile the source layers

The segment baseline has ten principles with potential direct support and five with indirect support only: F1, F3, A1.1, A2 and R1.1. The ontology separately proposes specific direct practices for F3 and R1.1, and an I1 integration practice that is more specific than the integration summary. It also contains governance examples for indirect R1.1/R1.2 even though the governance segment has no principle IDs.

Record these as distinct assertions with distinct sources. Do not overwrite the summaries or count ontology examples as additional observed implementation. The site Sankey's 51 direct and 10 enabling mappings are another presentation scope; do not use those totals as a denominator for activity, persona or maturity coverage.

## Proposed persona equivalences

All rows below are proposed functional correspondences, based on the two catalogues. “Close” still requires confirmation of local responsibilities. “Partial” requires a scope or competence check. “Gap” means the DAMA catalogue lacks an explicit equivalent. The source catalogue contains 30 FAIRMM personas, excluding its overview, file list and template.

P = Producer, C = Consumer, E = Enabler. Roles shown are starting hypotheses for the stated activity. Principle examples refer to the existing area mappings unless marked as a proposed extension.

| FAIRMM persona | DAMA persona candidates | Equivalence and likely data roles | Proposed relationship and condition |
| --- | --- | --- | --- |
| Business_Analyst | Business and Data Analysts; BI Analysts | Partial; C/E | Direct D5 requirements and acceptance criteria; indirect F2/R1 via metadata requirements and delivery teams |
| Business_Leader | Business Executives; Executives; Senior management | Close; E/C | Direct D2 sponsorship and funding; indirect FAIR outcomes through commissioned practices |
| Business_Owner | Business Executives and Managers; Managers and Executives | Partial; E/C | Direct D3 business outcomes; indirect FAIR outcomes. Confirm authority for a defined business asset |
| Citizen_Data_Scientist | Business Users; BI and Reporting Users | Partial; C/P | D4/D6 capability extension; consumption validates usability, but generic analytics does not establish FAIR |
| Clinical_Data_Manager | Data Stewards; Data Quality Analysts | Gap in clinical remit; E/P/C | Add clinical lifecycle and regulatory competence; indirect F2/R1 until specific metadata practices are assigned |
| Curator | Meta-data Specialist; Records Management Staff; Data Stewards | Partial; E/P | Direct F2/F4/R1 through curated records and searchable publication; indirect A2 through preservation practices |
| Data_Analyst | BI Analysts; Data Analysts; BI Specialists | Partial because FAIRMM emphasises dashboards and recurring reports; C/P | Direct F4/A1 only when the work implements or tests the relevant BI discovery/access service |
| Data_Engineer | Software Developers; Database Administrators; ETL, Service, Interface Developers | Partial; E/P | Direct A1/I1/R1.2 via development practices; indirect A2 via operations; test implemented outputs |
| Data_Integration_Specialist | Data Integration (ETL) Specialists; ETL, Service, Interface Developers | Close; E/P | Direct F2/F4/A1.2/R1/R1.2 where the integration activity supports them; indirect I1/I3 through its intermediate practices |
| Data_Owner | Executive Data Stewards; Business Data Stewards; Data Governance Council | Partial; E/C | Direct D4 only with documented decision rights; indirect A1.2/R1.1 through access and publication teams. Stewardship does not imply legal rights |
| Data_Protection_Officer | Data Security Administrators; Audit / Compliance | Partial; E | Direct A1.2 for retrieval-control implementation/testing; indirect for policy. Confirm privacy remit independently |
| Data_Quality_Manager | Data Quality Analysts; Data Stewardship Council | Partial; E/C | Direct D5 metadata-quality controls; indirect F2/R1. Generic business-data quality is insufficient |
| Data_Scientist | Data Analysts; Knowledge Workers | Gap in explicit scientific/statistical remit; C/P | Add experiment/model responsibilities; published analytical outputs need their own FAIR tests |
| Data_Standards_and_Governance_Expert | Business Data Stewards; Coordinating Data Stewards; Data Governance Office; Standards Organizations | Partial; E | Direct D3/D5 policy and standards work; indirect resource outcomes. A standards body is a collective counterpart, not an individual appointment |
| Data_Steward | Data Stewards; Business Data Stewards; Data Stewards and SMEs | Close; E/P/C | Direct F2/R1.2 for metadata/provenance publication; indirect for coordination. Select the activity rather than inheriting all area IDs |
| Data_Strategy_Owner | DM Executive; Data Management Executive; CDO/CIO | Close function, confirm mandate; E/C | Direct D3 strategy and roadmap; indirect resource outcomes through funded implementation |
| FAIR_Community_Manager | Coordinating Data Stewards; Organizational Effectiveness Group | Partial; E | Direct D6 community learning and D4 collaboration when facilitation is explicit; indirect uptake of FAIR practices |
| FAIR_Data_Architect | Data Architects; Data Architects and Modelers; Other Enterprise Architects | Close function plus FAIR competence; E/P | Direct I1/I2/I3/R1.2/R1.3 in architecture; indirect F1 via identifier implementation |
| FAIR_Trainer | Subject Matter Experts; Organizational Effectiveness Group | Gap in explicit training role; E | Add D6 curriculum, delivery and competence assessment; indirect FAIR outcomes via trained practitioners |
| Knowledge-Enabled_Citizen | Knowledge Workers; Business Users | Partial; C | Validate D1/D6 benefits from interoperable data products; do not infer the high maturity described in FAIRMM from the DAMA title |
| Lab_Manager | Managers; Data Producers | Gap in laboratory remit; E/P/C | Add laboratory workflows and record controls; candidate D5 alignment after scope confirmation |
| Legal_Data_Expert | Audit / Compliance; Government and Industry Regulators | Gap in internal legal advisory remit; E | Indirect R1.1 via licence advice and publication. Regulator is a stakeholder counterpart, not an internal legal expert |
| Master_Data_Manager | Business Data Stewards; Data Providers; Data Stewards in Reference & Master Data | Partial; E/P | Direct I3/R1.2 through qualified master-data relationships and lineage; semantic artefacts need additional checks |
| Ontologist | Data Modelers; Meta-data Specialist; Data Architects | Partial; E/P | Direct I1/I2 through formal shared models and FAIR vocabularies only where those practices are implemented |
| Project_Manager | Project Managers; Project and Program Managers | Close; E/C | Direct D3/D5 delivery plans and acceptance gates; indirect FAIR outcomes through technical and curation teams |
| Reference_Data_Manager | Data Stewards; Data Providers in Reference & Master Data | Partial; E/P | Direct I3/R1.2 through linked reference resources and provenance; I2 is an extension requiring vocabulary FAIRness evidence |
| Researcher | Data Creators; Data Producers; Knowledge Workers | Gap in explicit research remit; P/C | Define research generation and reuse tasks; validate their outputs independently |
| Subject_Matter_Expert | Subject Matter Experts; Subject Matter Experts (SMEs); Business Subject Matter Experts | Close; C/E | Indirect F2/R1 via concept elicitation and descriptive-quality review; a direct test contribution requires an explicit assignment |
| Technology_Leader | CIO; Chief Information Officer; CIO/CTO; CDO/CIO | Close; E/C | Direct D2/D3/D7 technology direction and resourcing; indirect FAIR evidence through delivery teams |
| Autonomous_AI_Agent | No explicit equivalent; Internal Customers and Systems is only a broad system category | Gap; C/P/E by workflow | Add a non-human actor with human oversight; test discovery, access, semantic handling and recorded provenance. Never equate a generic system with an autonomous agent |

The strongest initial matches are Data Steward, Technology Leader, Business Leader, Project Manager and Data Integration Specialist. FAIR Data Architect and Data Strategy Owner are strong functional candidates whose FAIR competence or decision mandate needs confirmation. Data Owner, DPO and Legal Data Expert need particular care because titles alone do not establish rights or specialist authority.

## Priority alignments and evidence

Start with one bounded data product and its metadata, identifier, access service and lifecycle. The following seven cases exercise both Direct and Indirect relationships without changing the baseline classifications.

| Priority | Proposed chain | Evidence and maturity relevance |
| --- | --- | --- |
| 1 | Meta-data Management → Curator/Data Steward → F2/F4/R1 → D1/D5/D7 | Inspect representative descriptions and search results; record descriptive completeness, accuracy and successful discovery |
| 2 | Data Security policy → Data Owner/DPO → access-service team → A1.2 | Preserve policy as Indirect and tested protocol configuration as Direct; test allowed and denied requests with appropriate identities |
| 3 | Architecture requirements → FAIR Data Architect → identifier-service implementation → F1 | Preserve existing Indirect F1; propose a new Direct practice only after tests of global uniqueness, persistence arrangements and identifier resolution |
| 4 | Metadata requirements → Curator/Data Engineer → explicit data identifier in metadata → F3 | Keep summary Indirect and ontology Direct assertion separate; inspect identifiers in actual records and confirm the described resource |
| 5 | Integration architecture → Integration Specialist/Data Engineer → retrieval protocol → A1/A1.1 | Existing integration support is Indirect; test identifier-based retrieval for A1 and separately examine openness, cost and implementability for A1.1 |
| 6 | Operations retention → Records Management/Curator → preserved metadata service → A2 | Test metadata retrieval after the underlying data has been withdrawn; retained data or backups alone do not satisfy A2 |
| 7 | Governance/legal advice → Data Owner/Legal Data Expert → publisher attaches applicable licence → R1.1 | Existing operations support remains Indirect; ontology supplies a proposed Direct publishing practice. Inspect licence applicability, clarity and accessibility |

Also test R1.2 with associated sources, agents, transformations, versions and dates; I1 with independently parseable shared representations; I2 with evidence that the vocabulary itself follows FAIR principles; I3 with explicit qualified relations; and R1.3 against the relevant community standards. These tests prevent generic lineage, modelling or reference-data claims from being treated as full FAIR evidence.

### Worked record

For `MetadataManagement!A10:F10`, the activity “Query, Report and Analyse Metadata” names Data Lineage among its deliverables. The existing activity table proposes Direct R1.2 with conditions. The area catalogue includes Data Stewards, but that does not establish who performs this particular activity.

Propose Data_Steward or Curator as an Enabler/Producer, confirm the operational assignment, and link the record to D1 provenance, D5 repeatable capture and D7 lineage infrastructure. Inspect linked provenance records for selected data and metadata. Separately record any governance assignment of provenance responsibility as Indirect, via the publication practice. Neither a role appointment nor one lineage sample establishes a FAIRMM level.

## Applying the maturity levels

FAIRMM has seven complementary dimensions and six levels, L0–L5. Dimensions can mature at different rates and scope matters. Use the exact dimension text on each level page as the assessment criterion; the table below is a proposed sequence for collecting evidence, not a replacement scoring rubric.

| Stage | Alignment work | Evidence to seek |
| --- | --- | --- |
| L0 baseline | Identify absent, implicit or inconsistent FAIR practices | Scoped inventory and evidence gaps; missing evidence remains unknown until assessed |
| L1 awareness | Identify sponsors, candidate personas and initial FAIR use cases | Awareness activities, pilot proposals and initial responsibilities |
| L2 pilots | Implement the priority chains for a small data-product sample | Working pilot records, identifiers, access tests and designated roles |
| L3 repeatable departmental practice | Embed validated activities, roles and training in workflows | Departmental production use, formal procedures, capacity and locally demonstrated machine interpretation |
| L4 enterprise practice | Extend common standards, governance and monitoring across departments | Repeatable enterprise coverage, operational measures and cross-domain use |
| L5 ecosystem practice | Demonstrate cross-organisation interoperability and automated reuse | Shared standards and observed partner/agent workflows; FAIRMM describes this level as aspirational |

For each dimension, report current evidence, unmet descriptor elements and a target level. Do not derive levels from the number of mappings or personas, average seven dimensions into an unsupported overall score, or assume a pilot establishes enterprise coverage. Where a descriptor has several requirements, partial evidence should be recorded as partial support.

## Implementation plan

| Phase | Proposed work and outputs | Suggested review roles | Completion condition |
| --- | --- | --- | --- |
| 1 Source reconciliation | Extract each area/activity mapping with source coordinates; separate summaries, ontology examples and visualisation records | Metadata specialist and maturity assessor | Every existing assertion has a source, granularity and original Direct/Indirect label; differing assertions remain distinguishable |
| 2 Persona validation | Review the 30 correspondences; retain all DAMA names and variants; select activity-specific assignments and data roles | Data strategy owner, stewards and function leads | Each accepted match has responsibilities, scope, confidence and a named local reviewer; gaps have proposed additions |
| 3 FAIRMM descriptor mapping | Create records for relevant dimensions and exact L0–L5 descriptors; include FAIR-specific D2/D3/D4/D6 evidence | Maturity assessor with leadership and training representatives | Every proposed dimension relationship names a descriptor, deliverable and evidence test; Indirect records name an intermediate practice |
| 4 Pilot assessment | Run the seven priority cases and the remaining principle tests on one data product | Curator, architect, integration specialist and access-service team | An evidence pack distinguishes proposal, observed evidence, partial support, failure and unknown; no automatic maturity score |
| 5 Extend and publish | Review findings, reconcile accepted additions and prepare website tables and ontology changes | Repository maintainers and persona representatives | Reviewed crosswalk is ready for publication with provenance and versioning; publication is a separate implementation step |

Use a register with: alignment ID; repository/revision; source path and row/heading; DAMA area/activity/deliverable; original FAIR ID and contribution type; source-layer type; proposed intermediate practice; DAMA persona and occurrence category; FAIRMM persona and equivalence confidence; data roles; dimension and exact level descriptor; proposed dimension contribution type; applicability condition; evidence test; observation/result; scope/date; reviewer; and review status.

Retain distinct “proposed”, “reviewed” and “observed” statuses. Review checks should reject a Direct relationship supported only by a title or policy, an Indirect relationship with no intermediate practice, an equivalence that silently assigns legal rights, or a maturity claim based only on coverage counts.

The initial deliverable should be a reviewed crosswalk and pilot evidence pack. Once those are stable, extend FAIR–DAMA with a FAIRMM alignment page, persona correspondence table and separate dimension/descriptor relationships in the ontology. Keep persona equivalence weaker than identity: do not use `owl:sameAs` for these functional matches.
