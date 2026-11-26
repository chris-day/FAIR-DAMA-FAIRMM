# FAIR-DAMA-Integrated repository integration proposal

26 November 2026 | Proposed; implementation awaits user approval

## Recommendation

Integrate the accepted FAIR-DAMA-Integrated implementation as a maintained component within FAIR-DAMA-FAIRMM. Keep the existing documentary alignment and diagram generation operational, with explicit graph views. Preserve the accepted release archive and its evidence as the immutable baseline. Do not replace the existing five FAIR-MM files with a merged graph.

## Findings from the local checkout

- Target: D:/Work-Documents/13_Research/2026_Research/FAIR/research-repos/FAIR-DAMA-FAIRMM; branch main, HEAD 6c0d0fce21dcbe8ba851a9481707aea5f54c2ec6. This is a local inspection; remote freshness has not been checked.
- There are 31 tracked unstaged files and no staged or untracked files in the inspected status. These include README, scripts, documentary source files and generated diagrams. Preserve all pre-existing changes and distinguish them from integration edits.
- All five artefacts/fairmm-*.ttl files match the integrated release's pinned originals byte-for-byte.
- The existing README describes a documentary nine-module union, including cumulative derived relationships. That is a legitimate historical view but differs from the accepted asserted view, which excludes archival/derived sources.
- Existing requirements pin RDFLib 7.5.0 and Zensical 0.1.1. The accepted validation stack pins RDFLib 7.1.4 and pySHACL 0.30.1. Separate environments avoid an unreviewed dependency migration.
- Existing generators overwrite artefacts and documentation. The imported pipeline also cleans its own dist, validation, release and docs/generated directories. Component-local roots must be retained and checked.
- The accepted pipeline expects its workflow at a component-relative .github path and packages repository revision metadata. Hosting inside a larger repository requires explicit workflow validation and component/upstream revision handling.
- Existing README statements that SHACL and integration are absent need scoped updates. Historical reports remain historical.

## Proposed layout

```text
FAIR-DAMA-FAIRMM/
  artefacts/                         existing canonical documentary modules
  sources/                          existing documentary source snapshots
  integrated/
    build.py, validate.py, query_specs.py
    scripts/, inputs/, baseline/, queries/, fixtures/, shapes/
    specification/, LICENSES/, docs/
    source-pins.json, toolchain-lock.json, release-config.json
    requirements-validation.txt, ci-actions-lock.json
    acceptance/                     portable G6 reference code, plan and goldens
    dist/                           generated integrated RDF and metadata
    validation/, release/            generated evidence and new candidate packages
  releases/integrated/1.0.0-rc.1/     immutable accepted candidate and SHA-256
  records/integrated/                gate approvals, acceptance and provenance
  docs/integrated/                   site overview, downloads and graph policies
  scripts/build_integrated.ps1       component orchestration
  .github/workflows/integrated.yml   optional triggered validation, no publication
```

Import source contents without nested .git directories or old virtual environments. Preserve upstream G5/G6 commit IDs as metadata; new commits belong to the host repository. Keep the existing accepted ZIP byte-identical. Initial component input copies remain hash-pinned; verify their equality to canonical repository sources rather than silently changing paths or deduplicating them during import. Regeneration of those sources must fail the drift check until an explicit baseline update is reviewed.

## Implementation stages

1. **Protect and capture the starting state.** Record HEAD, status, file hashes and a recoverable snapshot of all existing local modifications. Create a local integration branch in the current checkout, without stashing, resetting or committing unrelated edits. If the checkout has changed since this proposal, reconcile the new state before editing overlapping files.
2. **Import the accepted component.** Copy the maintained G5 build sources and portable G6 acceptance implementation into the proposed paths. Retain the original archive, locks, licences, approvals and revision records. Keep large runtime checkpoints and historical execution logs in the handover archive rather than duplicating them in normal Git history. Record a component inventory and provenance manifest.
3. **Connect builds and graph views.** Add an explicit integrated build command with a separate environment. Preserve existing build commands and default diagram behaviour. Expose clearly named documentary, integrated-asserted and source/provenance dataset views; include the archival cumulative view only by explicit selection. Scope clean operations to generated component paths. Adapt packaging and workflow validation to the host repository, recording both host and upstream revisions.
4. **Integrate documentation and downloads.** Update README, ontology documentation and Zensical navigation. Explain version identities: FAIR-MM framework 1.2.5, preserved project ontology headers 1.1.0, integrated ontology 1.0.0 and accepted distribution 1.0.0-rc.1. Provide source-module and integrated downloads, licences, graph scope, validation evidence and recovery instructions. Copy site downloads through a manifest-controlled step and verify their checksums. Existing diagrams retain their documentary labels; any new asserted-only diagram is a separate view.
5. **Add repository validation.** Add a read-only, manually triggered/PR workflow for the integrated component, with pinned actions and isolated dependencies. Update the pipeline's workflow checks for the new location. Local execution remains the acceptance authority for this task; hosted execution is reported only if actually run. An unrelated existing site deployment workflow, if present later, must not be triggered as part of this change.
6. **Validate and present the integration.** Run existing ontology, source-union, diagram and site regressions, then the integrated build/query/SHACL/OWL suite and G6 loading/recovery suite. Test from a relocated clean copy, inspect the resulting diff and deliver a change inventory, commands, results and rollback instructions. Prepare local commits containing only integration changes; preserve pre-existing edits outside those commits.

## Acceptance criteria

- The five existing canonical FAIR-MM files and accepted candidate archive are byte-identical to the approved baseline.
- All pre-existing local modifications are preserved and independently recoverable.
- Integrated asserted graph remains isomorphic to the accepted 95,008-triple graph; all 18 complete query results match the accepted goldens on flat, TriG and offline import profiles.
- Sixteen source graphs, full provenance and derived/asserted separation remain valid. No inference or blanket union is enabled implicitly.
- Integrated SHACL/OWL and G6 restore/reload checks pass. Failed restores leave the active dataset unchanged.
- Existing diagram semantics and regression baselines remain intact. Any pre-existing regression failure is documented separately and resolved or explicitly reported before claiming acceptance.
- Documentation builds with strict checks; new download links and checksum manifests agree.
- The old accepted ZIP retains its exact checksum. A newly built host-repository candidate may have a different archive checksum because revision metadata and layout changed; its provenance and semantic equivalence are verified. No claim of old/new archive byte identity is made.
- A repeat build of the new candidate is deterministic under the pinned toolchain.

## Approval scope and boundaries

Approval authorises the local integration, documentation changes, validation and preparation of reviewable local commits described above. It does not authorise pushing, merging, publishing a GitHub Release, deploying the site, changing licence grants, upgrading validation dependencies or resolving mapping gaps through new assertions. Store integration remains optional follow-on work. Access to write the D: repository may require a separate filesystem permission grant from the desktop sandbox; plan approval and filesystem access are distinct.

Rollback restores integration-touched files from the captured starting snapshot and removes only newly introduced integration paths after review. Do not use a repository-wide reset or destructive clean against a checkout containing existing work.
