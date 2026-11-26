# Local integration rollback

Before reverting, preserve any work created after this integration. The pre-integration tracked-file snapshot and starting-state.json are in the local Repository-Integration review output folder linked by the final report. Verify the recorded snapshot checksum before using it.

Revert only integration changes. For files with pre-existing work (especially README.md and docs/index.md), restore their captured pre-integration working bytes rather than resetting to Git HEAD. Newly introduced integration paths can be removed after checking they contain no later work. The original main branch remains at the recorded starting revision; no push or merge was performed. Avoid repository-wide reset/clean commands.
