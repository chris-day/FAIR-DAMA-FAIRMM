# Migration and compatibility notes

Candidate 1.0.0-rc.1 retains the G4-approved ontology content. The pipeline adds reproducible packaging and documentation; it does not add mapping claims or change source identities.

## Versions and identifiers

The integrated ontology remains 1.0.0, DAMA is 1.2.0, Capability is 1.0.0 and Shared Alignment is 1.0.0. The selected FAIR-MM release is 1.2.5. Its supplied source ontology headers still declare 1.1.0; they are preserved, not silently relabelled. The candidate suffix belongs to the distribution, not to source entity IRIs.

All 123 baseline DAMA persona IRIs remain queryable. Legacy persona and map namespaces are retained. Eleven core knowledge areas remain separate from the three additional topics. Supplier, participant and consumer involvement remains contextual. Exact tool spelling variants remain distinct; the 112 categories include documentary supporting artefacts as well as software categories.

## Loading and query scope

Use dist/integrated-ontology.ttl with the accompanying local catalogue and inputs for logical imports. Use dist/merged-asserted.ttl for a self-contained asserted graph. Use dist/merged.trig for source/provenance tracing. Keep the relative input directory structure: the catalogue and lock use local paths, and all original input bytes remain pinned.

The TriG default graph is empty. Construct the asserted query view only from the seven graph identifiers in the merge manifest. Do not automatically union archival, cumulative-derived, provenance or inference graphs. Original source graphs remain available for legacy inspection. A legacy import URI may resolve to a frozen source snapshot; it does not imply all historical files originally declared a complete import closure.

Nine owl:imports statements are omitted only from the flattened graph because their content is already included. Original ontology declarations and other annotations remain. Source headers and declaration-only resolver adaptations are documented separately. dist/materialised.ttl contains a separate classification delta; it is not operational evidence and must not be silently merged into asserted data.

The candidate archive canonicalises generated RDF. Its .ttl files use canonical N-Triples syntax, which is valid Turtle. Prefix layout and blank-node labels can differ from the development build; graph content remains equivalent. TriG blank nodes are canonically scoped per source graph. Never use a blank-node label as a durable identifier. Raw input files are excluded from textual/RDF normalization so their locked hashes continue to match.

## Inherited mapping exceptions

Nineteen DAMA tool labels still need identity review; seventeen FAIR-specific extensions have no approved catalogue entities. No tool–Capability or Capability–FAIR bridge is inferred from lexical similarity. Indicative ranges and P/E/M progression codes do not establish normative levels. New qualified support remains proposed and deployment-unverified.

All 18 competency queries execute, including expected empty production results. Unknown deployment evidence remains unknown; missing requires explicit scoped absence. Verified claims require implementation, scope, conditions and evidence. Full condition sets must agree for combined claims. Passing graph validation does not establish real-world FAIRness.

## Later rollout and rollback

G5 sign-off concerns this reproducible candidate and documentation. CI hosting, licence decisions and release review must be confirmed before public promotion. GraphDB staging belongs to G6: select the actual target/version/ruleset, back up data, implement the explicit graph policy, run the queries and rehearse rollback. No database was changed by this pipeline. Production deployment requires separate authorisation.
