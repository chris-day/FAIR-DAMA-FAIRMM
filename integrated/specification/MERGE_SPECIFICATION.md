---
title: "Ontology Merge Specification"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Ontology Merge Specification

## Inputs and outputs
Inputs: pinned DAMA modules, pinned alignment modules, FAIR, FAIR-MM and Capability authoritative releases and full imports. Build DAMA and Alignment separately; then integrate. No byte concatenation of Turtle. Parse sources independently, preserve blank node scoping and base IRI resolution; use RDF graph union with reviewed header handling. Keep original source graphs in TriG. Preserve all axioms and annotations except explicitly reviewed metadata transformations. Do not silently drop imports or source ontology declarations; define a flattened output header policy and document how self-contained closure avoids network dependence. Import-based entrypoint references pinned ontology versions via a catalogue. Validate that intended asserted content matches the union under RDF graph isomorphism after declared transformations.

## Pipeline
1. Resolve lock entries, check hashes, licences, identity and cycles; fail closed on unresolved imports.
2. Parse, inventory, compare baseline and detect incompatible definitions, not merely repeated declarations.
3. Consolidate internal source modules; establish one published ontology header per authoritative release; record legacy header migration.
4. Integrate asserted graphs. Keep source named graphs and explicit PROV-O derivation metadata; never infer provenance from graph names alone.
5. Run selected OWL reasoner and SHACL using documented entailment and dataset settings; report profile limitations. Materialised inference, if generated, is a separate graph/output.
6. Generate outputs, validate parseability, compare graph content, produce lock and manifest. Test reproducibility by rebuilding from identical inputs; compare canonical graph/dataset digests or isomorphism, not arbitrary serializer ordering.

| Output | Requirement |
|---|---|
| integrated-ontology.ttl | Import entrypoint |
| merged-asserted.ttl | Self-contained asserted graph |
| merged.trig | Source-separated dataset with provenance |
| ontology-lock.json | Immutable dependencies and hashes |
| ontology-catalog.xml | Local resolution where needed |
| merge-manifest.jsonld | Source versions, transformations, build tooling, validation references |
| materialised.ttl | Optional separate inference graph |
| RDF/XML and JSON-LD | Optional compatibility exports |

Exact filenames and versioning conventions follow verified repo practice. Lock schema requires source URI, immutable revision or version IRI, SHA-256, local path, ontology IRI and dependency list. Build records must include tool versions and commands. Define GraphDB default/union graph policy explicitly; do not assume named graphs are automatically reasoned over. Preserve licence notices.
