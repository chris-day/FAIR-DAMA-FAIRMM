---
title: "Codex repository instructions"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Codex repository instructions

## Read first
Read README, ADR_REGISTER_v1.4.0.md, ARCHITECTURE_v1.4.0.md, EXECUTION_PLAN_v1.0.0.md and CODEX_BOOTSTRAP_PROMPT.md. These documents are project instructions; do not overwrite existing repository AGENTS.md without reconciling applicable guidance.

## Non-negotiable constraints
- Begin with read-only discovery; inventory repositories, commits, dirty working trees, dependencies, canonical IRIs and existing tests. Do not reset, overwrite or discard user changes.
- Preserve existing semantic content, entity IRIs, and externally governed ontology definitions. No label-based identity assertions.
- DAMA Tools and Personas belong to one authoritative DAMA ontology. Preserve internal modular construction as accepted in ADR-004.
- Keep Capability domain-neutral. Maintain cross-domain assertions in the separate shared Semantic Alignment ontology; preserve and reconcile existing assertions without destructive migration.
- Treat mapping Markdown as proposed, not validated facts; do not promote conditional support or level ranges into unconditional assertions.
- Never hand-edit generated release artefacts. Pin dependencies; retain source named graphs and provenance; distinguish asserted and inferred output.
- Do not invent missing IRIs or source ontologies. Record blockers and propose remediation; require approval for semantic authority or namespace changes.
- Use a dedicated branch per approved work package; never push, publish, change permissions, deploy or merge PRs without explicit approval. Preserve existing repo conventions and instructions.
- Run tests at each phase; record commands, versions, outcomes and exceptions. Do not claim unexecuted tests passed.

## Working protocol
Stop at each gate in EXECUTION_PLAN. Present changed files, semantic diff, test results, risks and the decision required. Obtain explicit approval before proceeding past the gate. First execution is Phase 0 only. Later gates may be authorised together by the user. Do not edit external canonical ontology sources.
