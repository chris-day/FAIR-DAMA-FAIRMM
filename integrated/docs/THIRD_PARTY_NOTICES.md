# Component notices and licence review

This is an owner-review candidate. Source notices are preserved; this file makes no new licence grant or claim that mixed-source redistribution has been cleared.

| Component | Evidence retained | Recorded notice |
|---|---|---|
| DAMA repository sources | LICENSES/DAMA-repository-CC0-1.0.txt and pinned source attribution | Repository CC0 1.0; source creator/provenance retained |
| FAIR principle vocabulary | Original fair-ontology.ttl dcterms:license statement | CC BY 4.0 URI, http://creativecommons.org/licenses/by/4.0/; preserve attribution |
| FAIR-MM upstream documentation | LICENSES/FAIRMM-repository-GPL-3.0.txt and pinned source snapshots | Repository GPL v3 notice; component scope must be reviewed |
| FAIR-MM personas | Supplied RDF rights statement | Persona overview separately states CC BY 4.0; do not overwrite this with a blanket repository assumption |
| Local generated ontologies and shared alignment | Original supplied files and source rights/provenance text | Generated local artefact rights are not inferred solely from an upstream repository licence |
| New pipeline, Capability content and documentation | Authored source and commit history | Owner licence selection remains pending; no public grant invented |
| Validation tools | toolchain-lock.json and checksum-pinned retrieval | Tools are dependencies, not bundled binaries in the candidate |

The ROBOT JAR and Python/Java installations are not included. Their exact versions and retrieval/checksum information remain in the toolchain records. GitHub Actions are pinned to commits in ci-actions-lock.json. Inclusion in a reproducible build does not relicense any dependency.

G5 owner review must record the licence selected for new content, confirm component attribution and reuse treatment, and approve the release candidate. Public distribution remains unauthorised until that decision. The pipeline can assemble and validate an internal candidate while this review is pending; it cannot publish a public release or change repository permissions.
