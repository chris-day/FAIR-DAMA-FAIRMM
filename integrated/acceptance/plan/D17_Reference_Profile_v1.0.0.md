# D17 store independent reference validation profile

Version 1.0.0 | 26 November 2026 | G6 execution profile

1. Verify the frozen candidate archive, every manifest payload hash, input pin and ontology/version identity.
2. Load the canonical flat graph, named-graph TriG and full catalogue-resolved import closure locally.
3. Construct the explicit asserted view: union the seven asserted source graphs, remove only the documented imports and add the integrated header without imports. Retain the empty distribution default graph until the runtime view is deliberately materialised. Reject archival/derived graph selection.
4. Execute all 18 queries on all three views. Compare complete result rows against G5 goldens and compare RDF-term kinds/datatypes/languages across views, ignoring row order.
5. Run integrated SHACL, complete synthetic verified-context fixtures and negative mutations. Run profile/consistency checks on the actual exported import and flat distributions with the pinned OWL tools.
6. Reject changed/missing payloads or dependencies, wrong ontology identities, cycles, malformed RDF, invalid graph selection, incomplete provenance and damaged snapshots.
7. Snapshot the runtime Dataset with an explicit manifest, checksum, release identity and blank-node scope invariants. Simulate local data loss; restore and verify every graph and all 18 query results. Reject semantically altered checkpoints even if their byte checksum is updated, and retain the prior accepted runtime on failure. Also rehearse complete reload from the frozen release.
8. Deliver commands, evidence, source revisions, limits and a future adapter contract. G6 owner acceptance follows review.

The reference store is RDFLib Memory. A runtime checkpoint may contain its deliberately materialised asserted default graph; that differs from the released TriG's intentionally empty default graph and is declared in the checkpoint manifest. Native TriG preserves cross-graph blank-node sharing in that runtime snapshot. Snapshot data is not a replacement public release.
