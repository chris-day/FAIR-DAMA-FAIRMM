---
title: "Competency Questions"
version: "1.0.0"
architecture_baseline: "1.4.0"
date: 2026-11-25
language: en-GB
---

# Competency Questions

Implement executable SPARQL queries and expected result fixtures after canonical IRIs are reconciled. Use explicit named graph or union policy. Test positive and negative cases, including empty results.

| ID | Question | Acceptance |
|---|---|---|
| CQ01 | Which tools directly support F4? | Only qualified direct mappings; include status and conditions |
| CQ02 | Which tools indirectly support R1.2? | Do not conflate direct and indirect |
| CQ03 | Which tools contribute to D7 L3? | Explicit dimension-level association, not inferred from generic range |
| CQ04 | Which capabilities contribute to D7 L4? | Return implementation context |
| CQ05 | What additional capabilities are needed for L4 from L3? | Compare approved profiles against evidenced realisations; unknown remains unknown |
| CQ06 | Which activities use tools supporting I1? | Join through actual activity-tool associations |
| CQ07 | Which principles lack documented direct tool mappings? | Report graph coverage, not proof of impossibility |
| CQ08 | Which tools contribute across multiple dimensions? | Return distinct dimension identities |
| CQ09 | What evidence and source support a mapping? | Trace provenance and rationale |
| CQ10 | Which mappings are conditional or unverified? | Include proposed and unknown status |
| CQ11 | Which deployments realise capabilities? | Separate category potential from deployment evidence |
| CQ12 | What gaps exist against a target maturity profile? | Return missing and unknown separately |
| CQ13 | Which knowledge areas have documented contributions? | Counts by distinct assertion; avoid maturity ranking |
| CQ14 | Which tools could be repurposed? | Potential capability only; no verified claim |
| CQ15 | Which mappings are approved, proposed or deprecated? | Preserve lifecycle state |
| CQ16 | Can every baseline persona IRI still be queried? | All preserved or approved exception |
| CQ17 | Can source graphs be traced to pinned dependencies? | Every source graph has provenance |
| CQ18 | Do incompatible contexts prevent combined principle/level claims? | Negative fixture yields no combined verified assertion |

Queries must be reviewed for join fan-out, duplicates, language labels, open-world semantics and deployment graph configuration. Store expected fixtures and actual test reports in repository.
