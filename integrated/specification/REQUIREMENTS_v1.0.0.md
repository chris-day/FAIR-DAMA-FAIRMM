---
title: "Semantic and Technical Requirements"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Semantic and Technical Requirements

| ID | Requirement | Verification |
|---|---|---|
| R01 | Four independent domain ontologies and one independent shared alignment ontology | Source inventory and dependency graph |
| R02 | One published DAMA ontology includes tools and personas | Coverage and legacy entity tests |
| R03 | Internal DAMA and alignment modules consolidate deterministically | Build tests |
| R04 | Preserve existing entity IRIs and semantic content | Baseline graph diff and approved exceptions |
| R05 | Capability vocabulary remains domain-neutral | Dependency and predicate review |
| R06 | Alignments retain conditions, rationale, provenance, status and evidence requirements | SHACL and review |
| R07 | Direct and indirect support remain distinct; no automatic verified FAIRness | Negative competency tests |
| R08 | D7 contribution is contextual; maturity is organisational, not intrinsic to a tool | Context and negative tests |
| R09 | Authorised DAMA and FAIR maintainers can contribute alignment changes under governed release | Review governance and approved permissions |
| R10 | Canonical FAIR and FAIR-MM semantics are not silently changed | Source checksums and comparison |
| R11 | Pin complete import closure and retain source graph provenance | Lock and manifest tests |
| R12 | Publish logical import entrypoint, flat asserted Turtle and TriG | Parse and graph comparison |
| R13 | Keep inference separate; specify reasoning profile | Reasoner report and output checks |
| R14 | Validate using SHACL and competency queries; retain positive and negative fixtures | CI reports |
| R15 | Generate mapping tables and context diagrams from RDF | Reproducibility and coverage tests |
| R16 | Preserve historical mapping baseline and track every row disposition | Mapping reconciliation register |
| R17 | GraphDB deployment has explicit dataset policy, test queries and rollback | Staging evidence |
| R18 | Release is independently versioned, approved and reproducible | Release manifest and approval record |

Use normative language for project requirements only; do not imply ISO or FAIR-MM conformance certification. All mappings are proposed until reviewed. Include explicit unknown/not applicable states; absence of an assertion is not proof of absence.
