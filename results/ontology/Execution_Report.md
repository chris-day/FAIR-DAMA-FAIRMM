# FAIRMM ontology execution report

Five modular OWL/RDFS Turtle files have been built in the independent FAIR-DAMA-FAIRMM project. Both source repositories remain unchanged. No SHACL, operational pilot, push or deployment is included.

| Module | Triples |
| --- | --- |
| fairmm-core.ttl | 339 |
| fairmm-v1.2.5.ttl | 1080 |
| fairmm-personas.ttl | 4510 |
| fairmm-dama-alignment.ttl | 68525 |
| fairmm-dama-derived.ttl | 4128 |

| Resource | Count |
| --- | --- |
| Dimension | 7 |
| MaturityLevel | 6 |
| Descriptor | 42 |
| Persona | 30 |
| DataRole | 3 |
| DimensionAlignment | 472 |
| OnsetAlignment | 26 |
| CumulativeAssociation | 127 |
| RoleAssignmentCandidate | 1445 |
| AreaRoleOccurrence | 278 |
| ActivityRoleOccurrence | 356 |
| SourceAssertion | 606 |

## Validation results

All 970 ontology checks passed. The four malformed cases were rejected. An independent SPARQL CONSTRUCT agrees with the RDF-driven cumulative materializer. Source definitions, activity fields, original classifications and component provenance were checked.

RDF-regenerated Sankeys match the source-release regression baselines: **54 dimension relationships** and **127 cumulative level relationships**, retaining **26 onsets**. The derived projection includes 26 introduced and 101 inherited associations. RDF extract files and the comparison report are in this folder.

## Reusable resources

- [Ontology documentation](../../docs/ontology.md)
- [Ontology SVG](fairmm-ontology.svg)
- [Validation details](validation.json)
- [Sankey regression](rdf-sankey-regression.json)
- [Build manifest](build-manifest.json)

The module files are in `../../artefacts/`, the query examples in `../../scripts/queries/`, and the one-command build is `../../scripts/build_ontology_all.ps1`. Frozen source-release JSON baselines remain preserved for provenance.

Validation is structural and documentary. It does not constitute an operational assessment or a full formal OWL consistency proof.
