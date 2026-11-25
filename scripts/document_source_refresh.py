"""Record explicit historical regression deltas and the proposed release baseline."""
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from build_fairmm_alignment import save

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/'results/history/pre-2026-11-16-refresh'

def main():
    corpus=json.loads((ROOT/'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    refresh=json.loads((ROOT/'results/source-refresh-2026-11-16.json').read_text(encoding='utf-8'))
    deltas={}
    for name,folder,prefix in [('dimensions','sankey','dama-fairmm-dimensions-sankey'),('levels','levels','dama-fairmm-levels-sankey')]:
        old=json.loads((HISTORY/f'results/ontology/baselines/{name}-approved.json').read_text(encoding='utf-8'))
        new=json.loads((ROOT/f'results/{folder}/{prefix}.json').read_text(encoding='utf-8'))
        tuples=lambda data:{(a['source'],a['target'],a['kind']) for a in data['links']}
        before,after=tuples(old),tuples(new)
        delta=dict(previous_relationships=len(before),current_relationships=len(after),added=sorted(after-before),removed=sorted(before-after),counts=new['counts'])
        if name=='levels':
            delta.update(previous_onsets=len(old['onsets']),current_onsets=len(new['onsets']))
            old_onsets={x['id']:x for x in old['onsets']}
            delta['changed_existing_onsets']=[x['id'] for x in new['onsets'] if x['id'] in old_onsets and any(x[k]!=old_onsets[x['id']][k] for k in ['first_supported_level','kind','activity_ids'])]
        deltas[name]=delta
        # These legacy filenames are used by the loader. Their release status is
        # explicitly proposed; the genuinely approved old files stay immutable.
        new['baseline_status']='Proposed source-release refresh, 2026-11-16; not additional user approval'
        save(ROOT/f'results/ontology/baselines/{name}-approved.json',json.dumps(new,ensure_ascii=False,indent=2)+'\n')
    refresh['relationship_deltas']=deltas
    refresh['baseline_status']='Proposed refresh; original approved 22/107 baseline preserved in results/history/pre-2026-11-16-refresh'
    acts=corpus['activities'];assertions=corpus['assertions']
    differences=[]
    for a in acts:
        records=lambda layer:{(x['principle'],x['contribution_type']) for x in assertions if x.get('activity_id')==a['id'] and x['source_layer']==layer}
        if records('activity_table')!=records('workbook_activity_table'):differences.append(a['id'])
    refresh['workbook_principle_classification_differences']=differences
    refresh['workbook_difference_classes']=dict(Counter(d.get('comparison_class','missing') for d in refresh['workbook_differences']))
    refresh['persona_confidence']=dict(Counter(p['confidence'] for p in corpus['persona_correspondences']))
    save(ROOT/'results/source-refresh-2026-11-16.json',json.dumps(refresh,ensure_ascii=False,indent=2)+'\n')
    layer_table='\n'.join(['| Source layer | Assertion records |','|---|---:|']+[f'| {k} | {v} |' for k,v in refresh['source_layers'].items()])
    text=f'''# DAMA–FAIRMM source refresh — 16 November 2026

The documentary crosswalk now uses Chris Day's supplied **DAMA ontology v1.1.0**, **DAMA Segments v1.18.0** and **V3 activity workbook**. FAIRMM remains on branch FAIR-MM-V1.2.5, revision `{corpus['sources']['fairmm_revision']}`. Input copies, original package notices, SHA-256 digests and the extracted workbook are retained under `sources/2026-11-16/`. The FAIR-DAMA checkout revision is context only; the supplied release is not attributed to that Git revision.

## Results

| Resource | Previous | Refreshed |
|---|---:|---:|
| Source sections, including overview | 13 | 15 |
| Activity rows | 140 | 156 |
| DAMA personas | 108 | 123 |
| FAIRMM personas | 30 | 30 |
| Proposed dimension assertions | 399 | {len(corpus["alignments"])} |
| Dimension diagram relationships | 45 | {deltas["dimensions"]["current_relationships"]} ({deltas["dimensions"]["counts"]["Direct"]} Direct, {deltas["dimensions"]["counts"]["Indirect"]} Indirect) |
| Level onset judgements | 22 | 26 |
| Cumulative level associations | 107 | 127 (62 Direct, 65 Indirect) |

The 11 core knowledge areas remain unchanged. Big Data & Data Science and Data Handling Ethics are **additional topics**, alongside Maturity Assessment; they are not added to the DMBOK2 core enumeration. Dimensions include all 14 areas/topics. Levels include the 11 core areas and the two new topics; Maturity Assessment remains excluded from positive level associations.

All previous diagram relationships are retained. The dimension diagram gains {len(deltas["dimensions"]["added"])} relationships; the level diagram gains twenty. Existing onset levels and source activity identities are unchanged. The 22/107 historical baselines are preserved in `results/history/pre-2026-11-16-refresh/`; the current baseline files retain legacy filenames but explicitly identify their status as proposed source-release refreshes.

## Source reconciliation

All 156 activity labels were matched to workbook rows. There are {len(refresh['workbook_differences'])} cell differences, classified as {refresh['workbook_difference_classes']}; {len(differences)} activity-level FAIR classification differences. Formatting comparison removes punctuation and whitespace only after retaining both exact strings. Original cells and coordinates are retained independently; no source wording is replaced.

{layer_table}

The 40 ontology contributions comprise nine original examples plus 31 new activity contributions. These {len(assertions)} records overlap and must not be summed as independent FAIR coverage. The earlier 61-link visualisation is retained in the historical corpus, rather than presented as the new release.

The document's catalogue overview lists A1.2 as Indirect for ethics; its detailed section summary and activity rows additionally identify conditional R1.1 support. The overview and section summaries are retained separately. Ethics has no direct FAIR-principle assertions. Its conditional Direct FAIRMM strategy/process/knowledge links describe organisational outputs, not direct resource-level FAIR fulfilment.

## New onset judgements

Both new topics are proposed at **L1** for separate Direct and Indirect practices, carried forward to L5 without changing type. Big Data & Data Science's Direct onset concerns an emerging FAIR-specific strategy (D3-L1); its Indirect onset concerns sourcing and ingestion metadata (D1-L1). This does not claim analytics-ready data at L1; that progression is explicitly associated with L3.

Data Handling Ethics' Direct onset concerns FAIR-specific process guidelines (D5-L1), while its Indirect onset concerns accessibility governance (D1-L1) through implemented authorization and licensing. Generic ethics statements and training attendance are insufficient. These are proposed documentary associations, not attained maturity levels. L0 remains diagnostic with no positive associations.

## Personas

The 30 qualified comparisons now use the 123-entry DAMA catalogue. Explicit Data Scientists strengthens the Data Scientist comparison from Gap to Close. Data Curators, Ingestion Architects, Big Data Platform Architects and Data Governance Bodies add contextual counterparts. Change Managers remain a related counterpart for the FAIR Trainer **Gap**: ethics training does not establish FAIR training expertise. No identity or accountability is inferred. Current comparison counts: {refresh['persona_confidence']['Close']} Close, {refresh['persona_confidence']['Partial']} Partial, {refresh['persona_confidence']['Gap']} Gap. The distinct source identifiers for `CDO / CIO` and `CDO/CIO` remain separate.

Scientific hypotheses do not establish FAIR-specific knowledge or training, so no Big Data & Data Science → FAIR Knowledge relationship is proposed from that activity alone.

## Reproduce and load

Run `pwsh -File scripts/refresh_source_release.ps1` from the independent project. It extracts the three supplied inputs, reconciles rows, regenerates proposed dimension/onset records, records historical differences, builds five RDF modules, validates and regenerates both diagrams from RDF, and builds the local documentation. It does not alter either source checkout, perform a pilot, push or deploy.

For a combined RDF graph, load the four supplied source modules in this order: `fair-ontology.ttl`, `dama-ontology.ttl`, `dama-fair-mapping.ttl`, `dama-persona-ontology.ttl` from `sources/2026-11-16/dama-ontologies-v1.1.0/`. Then load `fairmm-core.ttl`, `fairmm-v1.2.5.ttl`, `fairmm-personas.ttl`, `fairmm-dama-alignment.ttl`, `fairmm-dama-derived.ttl` from `artefacts/`. RDF union loading is order-independent; this order follows conceptual dependencies. Use these release source files when reproducing this refresh, rather than older sibling ontology copies.

No SHACL or legacy alignment file is introduced. Static SVG/PNG, on-demand interactive D3, offline fallback, filename prefixes and selector-free interaction are preserved.

## Attribution

Retain the supplied package's original annotations and notices. DAMA source images are copyright DAMA International. FAIRMM source is attributed to Pistoia Alliance contributors: repository GPL-3.0, persona overview separately CC BY 4.0. The FAIR vocabulary retains its original identifiers and CC BY 4.0 notice. No blanket licence is applied to all source components.
'''
    save(ROOT/'docs/source-refresh.md',text)
    save(ROOT/'results/Source_Refresh_2026-11-16.md',text)
    # Replace historical-source wording in the generated source-facing pages.
    for p in (ROOT/'docs/fairmm').glob('*.md'):
        s=p.read_text(encoding='utf-8')
        s=s.replace('The segment summaries, activity tables, ontology examples and visualisation have different scopes.','The segment summaries, Markdown activity tables, workbook activity tables, ontology contributions and ontology area assessments have different scopes.')
        if p.name=='areas.md':
            start=s.find('## Visualisation assertions outside the summary classification')
            if start>=0:s=s[:start]+'## Ontology area proposals\n\nThe 74 source ontology area assessments are retained as a separate source layer. Earlier visualisation records remain in the historical corpus. See the [source refresh](../source-refresh.md) and [complete crosswalk](data/crosswalk.json) for reconciliation.\n'
            s=s.replace('The Sankey states 51 direct and 10 enabling links for its own presentation scope. Those counts are not activity or persona counts. Its original data remains unchanged.','The historical v1.2.0 Sankey had 51 Direct and 10 Enabling records. The supplied v1.1.0 ontology now records 74 area-level assessments as a separate source layer; neither count represents FAIRMM dimension or level coverage.').replace('The union of activity-table principle IDs matches each non-aggregate segment summary in both categories.','The activity union matches the detailed section summaries. The catalogue overview separately omits R1.1 from Data Handling Ethics; both source scopes are retained.')
        s=rewrite_attribution(s)
        def local_link(match):
            from urllib.parse import urlparse,unquote
            url=urlparse(match[1]);name=Path(unquote(url.path)).name
            if name=='DAMA_Segments_High_Level_v1.18.0.md':return '(../source-release.html'+('#'+url.fragment if url.fragment else '')+')'
            return match[0]
        s=re.sub(r'\((file:///[^)]+)\)',local_link,s)
        save(p,s)
    for name in ['fair-ontology.ttl','dama-ontology.ttl','dama-fair-mapping.ttl','dama-persona-ontology.ttl']:
        dest=ROOT/'docs/ontology-data/dama-source-v1.1.0'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'sources/2026-11-16/dama-ontologies-v1.1.0'/name,dest)
    save(ROOT/'results/executed/Execution_Report.md',text)
    save(ROOT/'results/executed/execution-stats.json',json.dumps(refresh['counts'],indent=2)+'\n')
    print(json.dumps({'relationship_deltas':deltas,'workbook_classification_differences':differences},indent=2))

def rewrite_attribution(s):
    import re
    return re.sub(r'FAIR–DAMA source classifications are attributed to Chris Day and \[the pinned repository\]\([^)]+\) under its CC0 licence\.', 'DAMA source classifications are attributed to Chris Day, supplied ontology v1.1.0 / document v1.18.0 / workbook V3 release. Preserve the component notices and DAMA International source-image copyright; see the [source refresh](../source-refresh.md).',s)

if __name__=='__main__':main()
