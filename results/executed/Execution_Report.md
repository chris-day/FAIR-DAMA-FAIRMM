# DAMA–FAIRMM source refresh — 16 November 2026

The documentary crosswalk now uses Chris Day's supplied **DAMA ontology v1.1.0**, **DAMA Segments v1.18.0** and **V3 activity workbook**. FAIRMM remains on branch FAIR-MM-V1.2.5, revision `8ff4676eb340b0da5034ffb3d0e901c594c3cfc4`. Input copies, original package notices, SHA-256 digests and the extracted workbook are retained under `sources/2026-11-16/`. The FAIR-DAMA checkout revision is context only; the supplied release is not attributed to that Git revision.

## Results

| Resource | Previous | Refreshed |
|---|---:|---:|
| Source sections, including overview | 13 | 15 |
| Activity rows | 140 | 156 |
| DAMA personas | 108 | 123 |
| FAIRMM personas | 30 | 30 |
| Proposed dimension assertions | 399 | 472 |
| Dimension diagram relationships | 45 | 54 (45 Direct, 9 Indirect) |
| Level onset judgements | 22 | 26 |
| Cumulative level associations | 107 | 127 (62 Direct, 65 Indirect) |

The 11 core knowledge areas remain unchanged. Big Data & Data Science and Data Handling Ethics are **additional topics**, alongside Maturity Assessment; they are not added to the DMBOK2 core enumeration. Dimensions include all 14 areas/topics. Levels include the 11 core areas and the two new topics; Maturity Assessment remains excluded from positive level associations.

All previous diagram relationships are retained. The dimension diagram gains 9 relationships; the level diagram gains twenty. Existing onset levels and source activity identities are unchanged. The 22/107 historical baselines are preserved in `results/history/pre-2026-11-16-refresh/`; the current baseline files retain legacy filenames but explicitly identify their status as proposed source-release refreshes.

## Source reconciliation

All 156 activity labels were matched to workbook rows. There are 192 cell differences, classified as {'formatting': 192}; 0 activity-level FAIR classification differences. Formatting comparison removes punctuation and whitespace only after retaining both exact strings. Original cells and coordinates are retained independently; no source wording is replaced.

| Source layer | Assertion records |
|---|---:|
| segment_summary | 82 |
| workbook_activity_table | 173 |
| activity_table | 173 |
| catalogue_overview_summary | 64 |
| ontology_contribution | 40 |
| ontology_area_assessment | 74 |

The 40 ontology contributions comprise nine original examples plus 31 new activity contributions. These 606 records overlap and must not be summed as independent FAIR coverage. The earlier 61-link visualisation is retained in the historical corpus, rather than presented as the new release.

The document's catalogue overview lists A1.2 as Indirect for ethics; its detailed section summary and activity rows additionally identify conditional R1.1 support. The overview and section summaries are retained separately. Ethics has no direct FAIR-principle assertions. Its conditional Direct FAIRMM strategy/process/knowledge links describe organisational outputs, not direct resource-level FAIR fulfilment.

## New onset judgements

Both new topics are proposed at **L1** for separate Direct and Indirect practices, carried forward to L5 without changing type. Big Data & Data Science's Direct onset concerns an emerging FAIR-specific strategy (D3-L1); its Indirect onset concerns sourcing and ingestion metadata (D1-L1). This does not claim analytics-ready data at L1; that progression is explicitly associated with L3.

Data Handling Ethics' Direct onset concerns FAIR-specific process guidelines (D5-L1), while its Indirect onset concerns accessibility governance (D1-L1) through implemented authorization and licensing. Generic ethics statements and training attendance are insufficient. These are proposed documentary associations, not attained maturity levels. L0 remains diagnostic with no positive associations.

## Personas

The 30 qualified comparisons now use the 123-entry DAMA catalogue. Explicit Data Scientists strengthens the Data Scientist comparison from Gap to Close. Data Curators, Ingestion Architects, Big Data Platform Architects and Data Governance Bodies add contextual counterparts. Change Managers remain a related counterpart for the FAIR Trainer **Gap**: ethics training does not establish FAIR training expertise. No identity or accountability is inferred. Current comparison counts: 9 Close, 15 Partial, 6 Gap. The distinct source identifiers for `CDO / CIO` and `CDO/CIO` remain separate.

Scientific hypotheses do not establish FAIR-specific knowledge or training, so no Big Data & Data Science → FAIR Knowledge relationship is proposed from that activity alone.

## Reproduce and load

Run `pwsh -File scripts/refresh_source_release.ps1` from the independent project. It extracts the three supplied inputs, reconciles rows, regenerates proposed dimension/onset records, records historical differences, builds five RDF modules, validates and regenerates both diagrams from RDF, and builds the local documentation. It does not alter either source checkout, perform a pilot, push or deploy.

For a combined RDF graph, load the four supplied source modules in this order: `fair-ontology.ttl`, `dama-ontology.ttl`, `dama-fair-mapping.ttl`, `dama-persona-ontology.ttl` from `sources/2026-11-16/dama-ontologies-v1.1.0/`. Then load `fairmm-core.ttl`, `fairmm-v1.2.5.ttl`, `fairmm-personas.ttl`, `fairmm-dama-alignment.ttl`, `fairmm-dama-derived.ttl` from `artefacts/`. RDF union loading is order-independent; this order follows conceptual dependencies. Use these release source files when reproducing this refresh, rather than older sibling ontology copies.

No SHACL or legacy alignment file is introduced. Static SVG/PNG, on-demand interactive D3, offline fallback, filename prefixes and selector-free interaction are preserved.

## Attribution

Retain the supplied package's original annotations and notices. DAMA source images are copyright DAMA International. FAIRMM source is attributed to Pistoia Alliance contributors: repository GPL-3.0, persona overview separately CC BY 4.0. The FAIR vocabulary retains its original identifiers and CC BY 4.0 notice. No blanket licence is applied to all source components.
