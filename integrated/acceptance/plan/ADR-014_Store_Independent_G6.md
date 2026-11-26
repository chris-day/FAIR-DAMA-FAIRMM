# ADR 014 Store independent operational acceptance

Status: accepted for implementation by the user's instruction on 26 November 2026 to update G6 and execute it.

The ontology architecture 1.4.0 and ADR-001 through ADR-013 remain unchanged. This decision revises the operational execution gate and requirement R17, rather than redefining domain semantics or source authority. The original supplied pack remains immutable; revised planning files live here.

G6 uses RDFLib as the local reference engine, pySHACL for constraints and ROBOT/HermiT for OWL validation. It accepts the frozen G5 candidate through flat Turtle, named-graph TriG and catalogue-resolved imports. Queries use only the declared asserted view, with source/provenance graphs separately available for tracing. Archive, derived and inferred content must not leak into that view.

The gate requires equivalent RDF and all 18 query results, negative operational cases, an integrity-checked runtime snapshot, recovery of source/default graphs and full query results, and handover instructions. Recovery tests occur only in the local test workspace. Publication, hosted CI execution, repository provisioning and production deployment are not authorised.

A later RDF-store adapter must prove the same loading, graph policy, result-term semantics, entailment separation and recovery behaviour on its actual target. Backend transaction, concurrency, security and performance behaviour is outside this local Memory-store acceptance. GraphDB is an optional future target, not a mandatory dependency.

G5 technical approval is recorded separately from the frozen archive's historical pending-review fields. No unspecified licence grant or public promotion authority is inferred from the user's gate approval.
