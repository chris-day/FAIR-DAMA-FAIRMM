# FAIR DAMA FAIRMM documentary alignment

This independent project aligns DAMA practices and personas with FAIR Maturity Matrix v1.2.5. All outputs stay here; both sibling source repositories remain read-only.

The 16 November 2026 refresh uses the supplied DAMA ontology v1.1.0, DAMA Segments document v1.18.0 and V3 workbook. It contains 156 activity rows, 123 DAMA personas, 30 qualified FAIRMM persona comparisons and 472 proposed dimension assertions. The diagrams group these into 54 dimension relationships (45 Direct, 9 Indirect) and 127 cumulative level associations (62 Direct, 65 Indirect), derived from 26 onset judgements. Big Data & Data Science and Data Handling Ethics remain additional topics, separate from the 11 core areas. L0 is diagnostic only.

Read `docs/source-refresh.md` for the analysis, source reconciliation, changed relationships, onset reasoning and source attribution. The machine-readable report is `results/source-refresh-2026-11-16.json`.

## Diagrams

The five high-level connection views are in `results/high-level-connections/index.html`, with SPARQL embedded in the versioned high-level connections document. Run `.venv/Scripts/python.exe scripts/build_high_level_sankeys.py` and `pwsh -File scripts/render_high_level_sankeys.ps1` to regenerate them exclusively from the nine Turtle modules, then build the documentation. The enriched document is released as v1.1.0; the requested v1.0.0 path is retained as a compatibility copy and the original is preserved under `results/history/high-level-connections/`.

The focused Tools and Infrastructure/persona Sankey is in `results/tools-personas/index.html` and `docs/tools-personas/`. It projects D7 practice alignments through exact catalogue matches in activity responsibility fields; unmatched source role labels remain documented. Rebuild it with `.venv/Scripts/python.exe scripts/build_tools_persona_sankey.py` and `pwsh -File scripts/render_tools_persona_sankey.ps1`, then rebuild the documentation.

- `results/sankey/index.html`: dimensions, paired static and on-demand interactive diagram.
- `results/levels/index.html`: cumulative levels, paired static and on-demand interactive diagram.
- Prefixes remain `dama-fairmm-dimensions-sankey` and `dama-fairmm-levels-sankey`.

SVG, PNG, JSON, D3 interaction and offline fallbacks are provided. Hover/focus highlights connections; select a ribbon for rationale, deliverables, conditions and provenance. No selectors are required. The interactive version loads pinned D3 7.9.0 and d3-sankey 0.12.3 only on demand. Documentation labels open the bundled, line-addressable source view or pinned FAIRMM pages.

## Ontologies

The five canonical modules are in `artefacts/`: `fairmm-core.ttl`, `fairmm-v1.2.5.ttl`, `fairmm-personas.ttl`, `fairmm-dama-alignment.ttl`, `fairmm-dama-derived.ttl`. Project ontology release is 1.1.0; the FAIRMM framework edition stays 1.2.5. The namespace remains `urn:fair-dama-fairmm:alignment:`. No resources are represented as published in FAIR-DAMA.

For the combined graph, load the four source modules from `sources/2026-11-16/dama-ontologies-v1.1.0/` (FAIR vocabulary, DAMA vocabulary, mappings, personas), followed by the five modules above. Source TTL copies in `docs/ontology-data/dama-source-v1.1.0/` are byte-identical. RDF union loading is order-independent; this order follows conceptual dependencies. Documentation and SPARQL examples are in `docs/ontology.md` and `scripts/queries/`.

## Rebuild and validate

From this project directory, using the existing Python environment:

```powershell
pwsh -File scripts/refresh_source_release.ps1
```

This reads the three user-supplied files from the FAIR workspace, preserves their copies, validates the ZIP manifest, extracts XLSX using ZIP/XML, reconciles the documentary sources, records historical deltas and generates proposed release baselines. It then builds and validates all five modules, regenerates both diagrams from RDF, renders SVG/PNG and builds the local site with strict link checks. The current baseline filenames contain `approved` for loader compatibility; their metadata explicitly identifies them as proposed source-release updates.

To rebuild only the RDF, diagrams and site from the current crosswalk and release baselines:

```powershell
pwsh -File scripts/build_ontology_all.ps1
```

Use `.venv/Scripts/python.exe -m` commands when working directly. Dependencies are in `requirements.txt`; Graphviz supplies the ontology SVG and PowerShell/System.Drawing supplies the Sankey PNGs. The older Git-only extraction script is retained for historical work; it is not the entry point for this supplied release.

## Provenance

The supplied inputs, extracted package and workbook snapshot are under `sources/2026-11-16/`. Input SHA-256 hashes are recorded in the corpus and build manifest. Markdown and workbook statements, catalogue and section summaries, and ontology contributions and area assessments remain separate source layers. They are overlapping documentary assertions, not independent maturity evidence.

Original 45-dimension / 22-onset / 107-cumulative baselines and the previous corpus remain under `results/history/pre-2026-11-16-refresh/`. The historical corpus was pinned to FAIR-DAMA revision 438ad2d0c6be3c336254fe3ce6a5d93f111db8a0. The supplied release is not misattributed to the current source checkout. FAIRMM remains on FAIR-MM-V1.2.5, revision 8ff4676eb340b0da5034ffb3d0e901c594c3cfc4.

The original proposal is historical planning material; its proposed incorporation into FAIR-DAMA has not been executed. This project remains separate. No SHACL or operational pilot is included. Documentation deployment is configured in `.github/workflows/docs.yml`. Preserve component attribution and licensing notices, including DAMA International source-image copyright and the scoped FAIRMM notices.
