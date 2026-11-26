---
title: "Codex Bootstrap Prompt"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Codex Bootstrap Prompt

Use this as the first instruction in the existing Codex workspace:

> Read the DAMA_FAIR_Codex_Implementation_Pack_v1.0.0 in full, starting with README.md and AGENTS.md. Architecture v1.4.0 and ADR-001 through ADR-013 are the approved working design. All ADRs are resolved. ADR-004 uses internal DAMA source modules; ADR-008 requires an independent shared Semantic Alignment Ontology maintainable by authorised DAMA or FAIR maintainers. Do not reinterpret these decisions. Execute Phase 0 only, in read-only discovery mode. Inspect the actual repositories and existing AGENTS.md instructions, working trees, ontology identities, entity IRIs, imports, versions, tests, mappings, source material and deployment configuration. Reconcile the historical inventory and mapping baseline with current source. Identify missing authoritative FAIR-MM artefacts, collisions, migration risks and existing consumers. Produce an Ontology_Source_Reconciliation_Report_v1.0.0.md and proposed G1 implementation design, including source evidence, dependency inventory, semantic impact, risks, acceptance criteria and exact work-package sequence. Do not modify ontologies, overwrite repository files, create repositories, change permissions, push, merge, publish or deploy. Report any inaccessible dependencies honestly. Stop at G0 and request approval before implementation.

After G0 approval, follow EXECUTION_PLAN and gate protocol. Work on approved branches and retain prior semantic content. Never treat illustrative IRIs as canonical. Do not use the historical mapping's standalone tool ontology recommendation: ADR-003 supersedes it.
