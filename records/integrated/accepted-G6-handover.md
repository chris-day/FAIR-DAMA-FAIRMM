# DAMA / FAIR implementation pack — final handover

Accepted and closed on 26 November 2026. The owner approved G1–G5 and accepted the revised G6 with “G6 accepted”. G6 uses local RDFLib, pySHACL and HermiT validation. Original source files and the original implementation pack remain unchanged.

The accepted technical baseline is FAIR-DAMA-Integrated 1.0.0-rc.1, using FAIR-MM release 1.2.5. Acceptance does not rename or republish the frozen candidate. Preserved source headers retain their documented historical version discrepancy.

- Frozen candidate: Reference-Acceptance/inputs/FAIR-DAMA-Integrated-1.0.0-rc.1.zip
- Candidate SHA-256: c193f63f21823324f77b5c5ccb8a68246f9250d2f33f3752e4c5c3cee0e52e4c
- G5 source revision: 7e3b862c958e8e4c313d611769724772b600bf84
- G6 implementation revision: a826eda507fa4856f686f4d389fbdabd502b0ee3
- G6 acceptance record revision: 5fb8d6bae7fa886e50b5b9dd11cb23d75cfcf1ba

Validation passed 135 checks: 129 in the main run and six targeted restore follow-up checks, with zero failures. All 126 query executions passed across flat, TriG, offline import closure and recovery scenarios. The asserted view contains 95,008 triples; the runtime retains 16 source graphs and full provenance. Recovery rejects corrupted content before replacing the active dataset.

The acceptance report explains execution scope and limitations. Reference-Acceptance/HANDOVER.md contains rerun, load, query and recovery instructions. Reference-Acceptance/evidence contains the detailed results and checkpoint. Reference-Acceptance/plan contains the revised plan, acceptance criteria and ADR-014. BACKEND_ADAPTER_CONTRACT.md defines future store-specific conformance work.

The technical implementation pack is complete. Vendor deployment, hosted CI and public publication were not performed. New-content licence selection remains outstanding before public promotion; existing notices and previously documented mapping gaps remain. A backend integration or public-release preparation can be commissioned separately.
