# Local operations handover

## Frozen baseline

Use the archive at ../../releases/integrated/1.0.0-rc.1/FAIR-DAMA-Integrated-1.0.0-rc.1.zip, as resolved from this acceptance directory by profile.json. Its expected SHA-256 is in profile.json. It is the G5-approved technical candidate; its historical internal review fields remain unchanged. Later gate approvals are recorded alongside it. Nothing here grants a new licence or public publication authority.

## Repeat acceptance

Install ../requirements-validation.txt in an isolated environment, obtain the checksum-pinned ROBOT JAR and use a fresh disposable workspace:

```sh
python run_acceptance.py --workspace ./scratch/g6-new --robot-jar /path/to/robot-1.9.11.jar --java /path/to/java
```

The runner refuses to overwrite an existing active release. It verifies the archive and extracted files before parsing. It checks flat, TriG and catalogue-resolved import profiles against complete G5 result goldens. Typed results distinguish IRIs, literals, datatypes, language and unbound values. Row order is ignored.

## Load and query directly

```python
from pathlib import Path
from reference import extract_archive, ReferenceRelease
import json

profile = json.loads(Path("profile.json").read_text())
root = extract_archive(profile["release_archive"], profile["release_sha256"], "./scratch/manual/active")
release = ReferenceRelease(root, profile["release_sha256"])
release.load("trig")  # alternatively: flat or imports
results = release.queries()
```

The default graph is deliberately materialised from the seven asserted sources, with only the documented import removal and integrated-header addition. Source/provenance named graphs remain available. Archival, cumulative-derived and inferred graphs are excluded. No network import fallback is available.

## Checkpoint and restore

```python
release.snapshot("./scratch/manual/checkpoint")
release.restore("./scratch/manual/checkpoint")
```

A checkpoint is runtime.trig plus snapshot.json. The manifest records the release identity, data checksum, active profile, default graph policy, contexts and blank-node scope relationships. Keep the files together and retain the immutable release archive independently. Do not confuse a runtime checkpoint's materialised default graph with the distribution's empty default graph.

Restore validates bytes, release identity, default RDF, every source graph and the complete provenance graph before replacing the accepted Dataset. A failed restore leaves the prior runtime active. Evidence includes damaged-byte, wrong-release and semantically altered-but-checksummed checkpoints. Full reload from the immutable release is the fallback recovery path.

## Fault response

For a checksum, identity, graph-policy or provenance error, stop using that candidate load. Do not weaken the lock, add network fallbacks or automatically union every named graph. Re-extract the approved archive into a fresh workspace, validate it, then restore a matching verified checkpoint or reload the frozen release. Preserve the failed-workspace logs for diagnosis; never apply fault tests to live user data.

## Boundaries

This is an RDFLib Memory reference, with filesystem checkpoints. It does not validate vendor transactions, concurrent writers, service authentication, latency, cluster failover or a particular backend's inference rules. Those require the adapter acceptance in BACKEND_ADAPTER_CONTRACT.md. The current model still contains the approved mapping gaps and no verified production deployments.

For the rebuilt repository adaptation, pass --candidate /absolute/path/to/archive.zip and --candidate-sha256 SHA256. The baseline G6 acceptance is retained separately; passing this runner does not automatically approve repository adaptation changes.
