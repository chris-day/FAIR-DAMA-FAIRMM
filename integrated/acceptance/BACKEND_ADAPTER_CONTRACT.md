# Future RDF store adapter acceptance

A store is compatible with this reference profile only after testing its actual version and configuration in an isolated acceptance dataset. Local RDFLib success is not vendor certification or production deployment acceptance.

| Operation | Required evidence |
|---|---|
| Import | Load the frozen flat/TriG/import closure without omitted source content or unresolved imports |
| Graph selection | Expose the same asserted view; exclude archival, derived and inferred graphs; preserve named provenance |
| Query | Run all 18 frozen queries; compare full bindings and duplicate/count semantics with the reference |
| RDF terms | Preserve URI/literal distinction, datatype, language and unbound values; normalize only RDF 1.1-equivalent string forms/language-tag case when translating to the reference record convention |
| Entailment | Keep the asserted view stable; disable or separately scope vendor inference unless that additional profile is accepted |
| Failed load | Reject missing/changed inputs, wrong identities and invalid graph configuration without accepting a partial dataset |
| Checkpoint | Export source, default and provenance contexts with release identity and integrity evidence |
| Recovery | Restore equivalent RDF and all query bindings; preserve blank-node relationships; reject damaged/wrong-release/semantically corrupt snapshots |
| Failed restore | Leave the last accepted dataset active; prove the backend's own transactional or staging/swap mechanism |

The current queries bind no blank nodes. If future queries introduce them, compare bindings under an appropriate blank-node bijection, not by serialized labels. Do not normalize away meaningful datatype or literal distinctions.

Run baseline acceptance before mixing application instance data into the dataset. New deployment evidence or private application graphs require their own explicit data/view profile; they must not silently change the frozen baseline's result goldens. Internal store/system graphs should not enter the release's declared graph scope.

Record backend edition/version, loader flags, default/union graph behaviour, SPARQL settings, inference configuration, failures and recovery commands. Target credentials, permissions, production backup and deployment authorisation remain separate. No particular RDF product is required by G6.
