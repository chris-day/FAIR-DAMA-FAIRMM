---
title: "Architectural Decision Register"
version: "1.4.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Architectural Decision Register

Status: approved working baseline; 11 accepted, 2 retained, none outstanding. Decisions reflect the conversation, not a Git commit.

| ADR | Decision | Status | Normative direction |
|---|---|---|---|
| ADR-001 | Single authoritative DAMA ontology | Accepted | One published ontology governs DAMA concepts; internal source partitions do not create independent authorities. |
| ADR-002 | Persona consolidation | Accepted | Incorporate Persona content into DAMA; preserve legacy entity IRIs, role context and existing references. |
| ADR-003 | Tool consolidation | Accepted | Represent DAMA tools inside DAMA, not as an independent domain ontology. |
| ADR-004 | Physical modularisation | Accepted | Option B: multiple internal source modules, one authoritative DAMA release. Latest explicit selection supersedes earlier Option A. |
| ADR-005 | Independent Capability ontology | Accepted | Domain-neutral functional abilities, requirements and realisations; no project-specific alignment assertions. |
| ADR-006 | Independent FAIR ontology | Retained | Reuse canonical FAIR principle entities and semantics without rewriting the external source. |
| ADR-007 | Independent FAIR-MM ontology | Retained | Retain authoritative maturity dimensions, levels and indicators; reconcile actual available ontology artefacts. |
| ADR-008 | Independent cross-domain alignment | Accepted | Option D with shared governance: separate independently versioned Semantic Alignment Ontology; authorised DAMA and FAIR maintainers may contribute and modify mappings under shared release governance. |
| ADR-009 | DAMA source consolidation | Accepted | Generate one consolidated DAMA ontology from internal source modules; validate and publish as one release. |
| ADR-010 | Inter-domain merge | Accepted | Integrate four domain ontologies and alignment ontology, preserving source semantics and provenance. |
| ADR-011 | Preserve existing entity IRIs | Accepted | Do not rename existing entities; future namespace migration requires separate approved ADR. |
| ADR-012 | Distribution formats | Accepted | Publish import-based ontology, flattened asserted Turtle and provenance-preserving TriG, plus dependency lock and provenance manifest. |
| ADR-013 | Automated governed releases | Accepted | Reproducible automated build, validation, regression testing and governed release approval. |

## ADR-008 governance details
Either authorised DAMA or FAIR maintainers may initiate and modify alignments. The alignment ontology has an independent identity, namespace and version. Source domain semantics remain owned by their authorities. Retain mapping provenance, rationale, conditions, evidence and status. Internal modules share one published release. Existing externally authoritative cross-domain assertions are preserved, not forcibly relocated. Generated integrated outputs are never edited by hand. Exact repository names, access grants and review thresholds are implementation decisions requiring approval. Recommended: cross-domain review for substantive changes; ordinary editorial changes need proportionate review. No access permissions are granted by this pack.

## Change control
Record proposed changes with rationale, alternatives, semantic impact, migration plan and tests. Do not silently reverse accepted ADRs. Architecture v1.4.0 supersedes v1.3.0 (ADR-008 resolved); v1.3.0 superseded the earlier atomic-source decision.
