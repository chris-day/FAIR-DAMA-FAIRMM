---
title: "Validation and Regression Strategy"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Validation and Regression Strategy

| Suite | Positive and negative cases |
|---|---|
| Syntax | Parse each source and distribution; reject malformed RDF |
| Dependency | Complete import closure; reject wrong hash, missing import, unintended version |
| Identity | All legacy entity IRIs retained; reject silent renames |
| Semantic content | Compare baseline graph and migration graph, reconcile removed or changed statements explicitly |
| OWL | Consistency and unsatisfiable named classes; document chosen reasoner/profile; fail on unapproved inconsistency |
| SHACL | Required class membership, principle and dimension-level references, contribution type, status, rationale, provenance, capability, conditional evidence |
| Conditional support | Missing implementation condition or verification evidence must not produce verified conformance |
| Maturity | Tool category must not imply organisation level; incompatible contexts do not join |
| SPARQL | CQ01–CQ18 with expected results, negative fixtures and named graph configurations |
| Distribution | Asserted flat graph vs source union after documented header transformations; round-trip parsing |
| Reproducibility | Two clean builds from pinned inputs; compare semantic digests, lock and manifest |
| Documentation | Table row disposition reconciled to original mapping; diagrams generated from RDF |
| Deployment | Staging query and inference checks, backup and rollback rehearsal |

Candidate tooling: RDFLib, Jena RIOT, ROBOT, suitable OWL reasoner, pySHACL and GitHub Actions. Select after G0/G1, pin versions, record commands and limitations. SHACL validates graph constraints, not actual FAIRness. Require verified deployment evidence only where verified status is asserted; proposed mappings can remain conditional. Keep test fixtures outside production graphs. CI failure blocks release; no silent test skips. Record approved waivers with scope, rationale, owner and expiry.
