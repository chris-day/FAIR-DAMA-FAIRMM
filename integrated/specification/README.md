---
title: "DAMA–FAIR Codex Implementation Pack"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# DAMA–FAIR Codex Implementation Pack

Pack version 1.0.0 | Approved architecture 1.4.0 | Implementation not started.

## Start here
1. Extract the ZIP into a separate planning folder in the existing multi-repository Codex workspace (do not overwrite repository files).
2. Open Codex with access to the existing DAMA and FAIR-MM working trees and relevant FAIR sources. If absent, locate them in Phase 0; do not create substitute ontologies.
3. Supply CODEX_BOOTSTRAP_PROMPT.md and point Codex to this pack. Reconcile AGENTS.md with existing repository guidance.
4. Execute Phase 0 only; review the reconciliation report at G0 before authorising implementation.

## Document precedence
ADR register and architecture are the approved design baseline. Requirements and merge specification operationalise them; execution plan governs gates. Mapping v1.1.0 is an unchanged historical input, not an authority for ontology architecture: its suggestion of a standalone DAMA Tool Ontology is superseded by ADR-003. Its illustrative namespaces, level ranges and proposed mappings require validation. Existing source artefacts are authoritative for their actual domain semantics. Any conflict is reported, not silently resolved.

## Pack contents
See manifest.json for file hashes. This pack contains specifications and handoff instructions, not implemented ontologies or executed validation results. No GitHub repositories have been modified. Source inventory is provisional until Codex inspects the current workspace.
