---
title: "Provisional Ontology Source Inventory"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Provisional Ontology Source Inventory

## Known source references from prior inspection (not freshly verified)
| Source | Location | Previously observed |
|---|---|---|
| DAMA | https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-ontology.ttl | Version 1.1.0; tool entities not observed |
| Persona | https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl | Existing module, version 1.1.0 previously reported |
| DAMA–FAIR mapping | https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-fair-mapping.ttl | Existing mappings; preserve all assertions and history |
| DAMA catalogue | https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/DAMA_Segments_High_Level_v1.18.0.md | Source tool and context catalogue |
| FAIR principles | https://peta-pico.github.io/FAIR-nanopubs/principles/ontology.ttl | Canonical principle vocabulary; verify source authority and revision |
| FAIR-MM | https://github.com/chris-day/FAIR-Maturity-Matrix | D7 docs/fmm-d7.md and level0.md–level5.md; RDF ontology location not established |
| Capability | To discover or create after G1 | Proposed independent ontology |
| Semantic Alignment | To discover or create after G1 | Proposed separate shared ontology |

Historical inspection referenced DAMA repository commit b172944e41d5d27be93f72317e78c32c6787d6cb. Verify access and actual revision; do not use it as an approved lock automatically. Mapping baseline is bundled unchanged. No fresh repository inspection was performed when assembling this pack.

## Phase 0 required inventory fields
Repository, branch, commit, clean/dirty state, path, retrieval URI, ontology IRI, version IRI, declared version, format, namespace, SHA-256, licence, imports and resolved closure, counts of triples/classes/properties/individuals, graph identifiers, existing mappings and statuses, consumers, tests, owner, migration risk. Capture source file and line or RDF subject reference for findings. Inspect existing FAIR-MM RDF before proposing a new vocabulary. Record missing sources as blockers, not empty graphs.
