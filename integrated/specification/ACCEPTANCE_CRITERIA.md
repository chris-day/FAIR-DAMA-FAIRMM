---
title: "Release Acceptance Criteria"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Release Acceptance Criteria

| Gate | Exit criteria |
|---|---|
| G0 | Complete source inventory, canonical identifiers, baseline counts and imports, existing tests and consumers, risks and unknowns; no source modifications |
| G1 | Confirmed modelling patterns and namespaces, migration plan, governance and repository boundaries, reasoner and deployment profile, test design approved |
| G2 | Consolidated DAMA contains tools/personas with legacy identity and content preserved; Capability independently reusable; validation and baseline comparisons pass |
| G3 | Independent shared alignment ontology, every historical mapping row disposition recorded, existing mappings reconciled, qualified assertions reviewed; no verified claims without evidence |
| G4 | Complete pinned closure, consistent integrated model, SHACL positive/negative fixtures and competency queries pass, asserted/inferred separation and distribution equivalence tested |
| G5 | Reproducible CI release candidate with lock, manifest, version decisions, generated documentation, licence and migration notes, signed-off review |
| G6 | Staged GraphDB import, dataset policy and query checks, rollback and operational handover; production deployment separately authorised |

Every gate must include evidence links or local paths, exact commit and commands, status per criterion, unresolved exceptions and explicit owner approval. No invented test results. Acceptance of this pack is not acceptance of the implementation.
