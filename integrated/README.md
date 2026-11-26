# FAIR-DAMA-Integrated component

This component maintains the accepted 1.0.0 ontology in the FAIR-DAMA-FAIRMM repository. The immutable accepted distribution is 1.0.0-rc.1; the host adaptation is 1.0.0-rc.1-repository.1. Gate acceptance records are in ../records/integrated/ and integration-provenance.json records upstream and host revisions.

Install requirements-validation.txt in a separate Python 3.11.9 environment. Run `python scripts/pipeline.py --robot-jar /path/to/robot-1.9.11.jar --java /path/to/java`. The host wrapper ../scripts/build_integrated.ps1 also runs optional G6 acceptance against the newly built candidate and synchronises site assets. See ../docs/integrated/operations.md.

The pipeline removes only this component's generated dist/, validation/, release/ and docs/generated/ directories, then rebuilds, validates and creates a reproducible review archive. Pinned source inputs and the host's documentary artefacts are never overwritten by it. Host source drift fails before candidate creation.

Generated validation reports and runtime checkpoints remain ignored; preserve them in the local review handover. The original accepted archive and separate approvals are retained by the host. No nested Git history, virtual environment, publication or deployment is included. Existing licence notices remain in docs/THIRD_PARTY_NOTICES.md and LICENSES/.
