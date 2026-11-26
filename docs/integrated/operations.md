# Build, validate and recover

Keep the existing documentary environment unchanged. Create a separate Python 3.11.9 environment for integrated/requirements-validation.txt. Use the checksum-pinned ROBOT 1.9.11 JAR and Java 17.0.21.1 recorded in integrated/toolchain-lock.json and release-config.json.

From the repository root:

```powershell
pwsh -File scripts/build_integrated.ps1 -Python /absolute/path/to/python.exe -RobotJar /absolute/path/to/robot-1.9.11.jar -Java /absolute/path/to/java.exe -Acceptance -Workspace /absolute/path/to/fresh-scratch -SyncSite
```

This verifies host source pins, builds, runs queries and SHACL/OWL validation, creates a reproducible review candidate, rehearses G6 loading and recovery against that new candidate, and synchronises local documentation downloads. It does not build or deploy the site. Build the site separately using the existing documentary environment with `python -m zensical build --clean --strict`.

The host workflow is .github/workflows/integrated.yml; its component-local copy is verified byte-for-byte and included in the packaged source. It has read-only permissions, PR/manual triggers and no deployment step. Hosted results are available only after an actual hosted run.

## Explicit query views

```sh
python integrated/scripts/graph_views.py --view integrated-asserted --query integrated/queries/CQ01.rq
python integrated/scripts/graph_views.py --view documentary
python integrated/scripts/graph_views.py --view source-provenance
```

Existing documentary commands and diagram defaults continue to use their historical graph scope. Source refreshes that change pinned ontology files require an explicit integrated baseline review before the integrated build can pass again.

## Recovery

The acceptance runner accepts `--candidate` with `--candidate-sha256` to test the repository adaptation. Its default profile tests the unchanged accepted archive under releases/integrated/1.0.0-rc.1/. Use a fresh scratch workspace for every run.

Runtime checkpoints comprise runtime.trig and snapshot.json. Restore checks byte hashes, release identity, asserted/source graphs, provenance and blank-node sharing before replacing the current dataset. Failed restores leave the last accepted runtime active. Full re-extraction of the immutable candidate is the fallback. See integrated/acceptance/HANDOVER.md and BACKEND_ADAPTER_CONTRACT.md for the reference API and future backend acceptance requirements.

RDFLib Memory recovery does not establish vendor transactions, concurrency, authentication, performance or cluster failover.
