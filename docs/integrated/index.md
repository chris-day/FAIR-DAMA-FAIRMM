# Integrated ontology

FAIR-DAMA-Integrated provides a validated, source-pinned ontology distribution alongside this repository's documentary crosswalk. The integrated ontology version is 1.0.0; the selected FAIR-MM framework edition is 1.2.5. Existing source ontology headers retain project release 1.1.0. These identify different versioned components.

The accepted baseline is distribution 1.0.0-rc.1. The repository adaptation is 1.0.0-rc.1-repository.1; its packaging and host revision differ while the asserted graph remains the accepted 95,008-triple graph. G1–G6 acceptance records are retained separately from this adaptation's review status.

## Choose a graph

| View | Scope | Use |
| --- | --- | --- |
| Documentary | Existing nine-module union, including cumulative derived associations | Existing historical diagrams and crosswalk queries |
| Integrated asserted | Seven asserted sources and the integrated header; no cumulative-derived union or inference | Accepted competency queries and asserted validation |
| Source/provenance dataset | Sixteen named source graphs plus provenance; empty default graph | Source auditing and explicit named-graph queries |

The 127 cumulative associations remain documentary derivations, and proposed mappings remain unverified. No maturity assessment or verified deployment is inferred.

## Downloads

- [Standalone asserted Turtle](downloads/merged-asserted.ttl)
- [Source-separated TriG](downloads/merged.trig)
- [Repository adaptation archive](downloads/FAIR-DAMA-Integrated-1.0.0-rc.1-repository.1.zip), including the modular entry point, catalogue and locked inputs
- [Download checksums](downloads/manifest.json)
- [Generated semantic reference](reference/index.md)
- [Local build and recovery](operations.md)
- [Licences and attribution](licences.md)

Load the standalone asserted Turtle directly. For modular loading, extract the whole archive and use its offline catalogue; the entry point alone does not contain the import closure. For TriG, select the intended named graphs explicitly. Do not enable an automatic union of every graph.
