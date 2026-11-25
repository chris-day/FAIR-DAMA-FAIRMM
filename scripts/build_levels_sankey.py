"""Curated level-onset analysis with explicit cumulative closure; no maturity scoring."""
from collections import Counter
from html import escape
import hashlib
import json
from pathlib import Path
import re
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT, DOC = ROOT / 'results/levels', ROOT / 'docs/levels'
PREFIX = 'dama-fairmm-levels-sankey'
LEVELS = ['Life is unFAIR', 'Started the FAIR journey', 'Getting FAIR', 'Pretty FAIR', 'Really FAIR', 'FAIRest of them all']

# Every first-level judgement is authored against a specific descriptor clause
# and source practice, rather than inferred from a generic keyword score.
# Tuple: descriptor, exact phrase, source activity numbers, rationale, via practice.
RULES = {
1: dict(
 direct=('D3-L1','A vision and plan for FAIR data begins to emerge',[2,6,16],'A FAIR-specific strategy, policy and communication programme directly deliver the embryonic vision and guidelines described at L1.',None),
 indirect=('D5-L1','guidelines for creating FAIR data',[6,8],'Governance policy and sponsorship enable implementation; they do not publish FAIR resources themselves.','Commission and implement identifier-aware metadata publication'),
 progression=[('D3-L2','vision, strategy and plan has approval'),('D2-L3','budgets include a component for FAIR implementation'),('D3-L4','integration of FAIR metrics into the data governance process'),('D3-L5','Metrics and methodologies to measure these outcomes')]),
2: dict(
 direct=('D4-L1','design architectures',[4,8],'FAIRMM explicitly describes emerging architects and process flows at L1. FAIR-specific architecture designs directly support that planning capability; implemented shared models are a later step.',None),
 indirect=('D7-L1','At least one policy on unique resource locators',[7],'Namespace and architecture requirements enable persistent identification but are not evidence that identifiers are globally unique or persistent.','Implement and operate the identifier requirements in an identifier service'),
 progression=[('D1-L2','conformed to a local model'),('D7-L3','enterprise-wide data model'),('D1-L4','cross-domain data or industry model'),('D1-L5','knowledge language or ontology')]),
3: dict(
 direct=('D7-L1','Excel templates',[5,6],'FAIRMM includes pragmatic creation and curation tools at L1. Data design and information-product work can directly provide FAIR-aware capture forms and schemas when actually used for those purposes.',None),
 indirect=('D5-L1','guidelines for creating FAIR data',[9,10],'Modelling standards and design review enable teams to implement FAIR-aware capture and access; design approval alone does not establish resource FAIRness.','Build and validate metadata-aware data capture and access services'),
 progression=[('D1-L2','conformed to a local model'),('D7-L3','data is made FAIR from the onset'),('D1-L4','Data starts to be "generated" FAIR'),('D1-L5','new data generated is "FAIR by design"')]),
4: dict(
 direct=('D7-L2','Initial infrastructure and tooling are in place for the first working POCs',[1,13],'The earliest specific operational-delivery match is L2, where working POC infrastructure is in place. L1 infrastructure inventories and plans are retained as enabling support, not operational delivery.',None),
 indirect=('D7-L1','Initial plans for tooling and infrastructure for POCs start to take shape',[10,12],'Technology requirements and evaluation support the initial FAIR tooling plan before operational infrastructure is established.','Install and support the metadata and identifier infrastructure for the POC'),
 progression=[('D7-L2','Initial infrastructure and tooling are in place for the first working POCs'),('D7-L3','Established processes for producing and managing FAIR data'),('D7-L4','periodically evaluates historical and current solutions'),('D5-L5','planned processes to maintain FAIR implementation standards and tools')]),
5: dict(
 direct=('D1-L1','governance for accessibility',[2,3],'FAIR-specific access policies directly support the accessibility governance explicitly present at L1. This is a policy capability, not a claim that the protocol has been tested.',None),
 indirect=('D1-L1','governance for accessibility',[1,4],'Security requirements and control specifications enable implementation of permitted access in retrieval services.','Configure and operate authentication and authorization in the retrieval service'),
 progression=[('D1-L2','Controls on access at the system level'),('D1-L3','controls in place on Access at the data level'),('D7-L4','Defined Interaction mechanisms with FAIR data have been consistently implemented'),('D7-L5','Authentication and Authorization Infrastructure')]),
6: dict(
 direct=('D7-L1','Master Data Management (MDM) system',[4,7],'FAIRMM explicitly starts MDM systems and controlled vocabularies at L1. Implemented, FAIR-specific reference/master solutions can directly support that early capability without implying enterprise coverage.',None),
 indirect=('D5-L1','what constitutes reference data',[1,2],'Defining reference-data requirements and contributors enables implementation and curation of the authoritative data.','Implement governed reference/master resources and their metadata'),
 progression=[('D7-L2','Tools to work with controlled vocabularies'),('D1-L3','Data embeds local master and reference data'),('D1-L4','Data embeds Enterprise master and reference data'),('D5-L5','planned processes to maintain FAIR implementation standards and tools')]),
7: dict(
 direct=('D1-L3',"analytics-ready 'data-marts'",[3,4],'L3 explicitly introduces analytics-ready data marts. L1/L2 data-lake cataloguing does not by itself establish a warehouse or BI capability, so the direct onset is conservatively placed at L3.',None),
 indirect=('D1-L1','Some data is cataloged and hosted in a data lake',[1,2],'BI requirements and architecture planning can inform which data should be catalogued for future analysis. This is enabling support; a data lake is not equated to a warehouse.','Catalogue and document identified data required by the analytical use case'),
 progression=[('D1-L2','is cataloged'),('D1-L3',"analytics-ready 'data-marts'"),('D1-L4','Cross-domain Analytics is enabled'),('D7-L5','Data Exploration')]),
8: dict(
 direct=('D7-L1','content management systems',[2,7],'Centralized content systems and descriptive indexing are explicit L1 tooling examples. Their configured metadata facilities can directly support this early capability.',None),
 indirect=('D5-L1','content management',[1,4],'Records strategy and retention arrangements enable maintained metadata publication; retention alone does not establish FAIR A2.','Publish and maintain indexed content metadata with independent retention arrangements'),
 progression=[('D7-L2','assigning PIDs to key documents'),('D7-L3','Metadata preservation policy'),('D7-L4','Registry of FAIRification Tools'),('D7-L5','FAIR Metadata Publication')]),
9: dict(
 direct=('D1-L1','emerging awareness and application of metadata',[5,7],'Capturing descriptions and managing searchable metadata directly support the catalogue and metadata capability already emerging at L1.',None),
 indirect=('D5-L1','metadata centralization',[1,3],'Metadata requirements and standards enable consistent resource descriptions; an agreed profile alone is not a published metadata record.','Capture, publish and validate metadata conforming to the agreed profile'),
 progression=[('D5-L2','licenses, refresh cycles, lineage'),('D7-L3','metadata collection templates'),('D1-L4','Enterprise-level Metadata standards are applied'),('D5-L5','Mechanisms exist to sustain metadata across organizations')]),
10: dict(
 direct=('D5-L1','data discovery, profiling, and optimization',[3,10],'Profiling and curation are explicitly present at L1. Quality assessment can directly deliver that capability when applied to the FAIR use case, even though the source principle mappings remain indirect.',None),
 indirect=('D4-L1','curator',[2,6],'Quality requirements and tests enable curators to improve descriptive completeness, consistency and accuracy. Generic business-data quality is insufficient.','Curate and validate the actual discovery and reuse descriptions'),
 progression=[('D5-L2','Regular retrospectives on pilot projects'),('D5-L3','evaluating and implementing FAIR standards'),('D6-L4','validating instance metadata against annotation requirements and data shapes'),('D7-L5','FAIR Data Validation')]),
11: dict(
 direct=('D5-L1','strategic integration approach',[1,2],'The L1 process descriptor explicitly includes targeted strategic integration initiatives. Integration planning and discovery directly support that early process capability; cross-organisation interoperability is not claimed.',None),
 indirect=('D7-L1','Initial plans for tooling and infrastructure',[6,8],'Architecture and mappings enable implemented exchange and publication services. Data movement or canonical messages alone do not establish FAIR interoperability.','Develop and validate standardized data exchange and publication services'),
 progression=[('D5-L2','integrated proof-of-concept projects'),('D1-L3','integrated, processed and audited'),('D3-L4','federated domain-specific FAIR data'),('D5-L5','seamless FAIR data exchange among entities')]),
}

# Additional topics retain their source classification; they are not new core
# DMBOK2 knowledge areas. L1 planning/process support is separate from delivery
# of analytics-ready data (L3) or achievement of a complete maturity level.
RULES[13] = dict(
 direct=('D3-L1','A vision and plan for FAIR data begins to emerge',[1],
         'Big Data Strategy & Standards directly supports an emerging FAIR vision and plan only when FAIR objectives and acceptance criteria are explicitly commissioned. This is strategic onset, not deployed analytical capability.',None),
 indirect=('D1-L1','emerging awareness and application of metadata',[3,4],
           'Sourcing and ingestion enable early resource descriptions and provenance when capture is made explicit.',
           'Capture, publish and validate resource-linked sourcing and ingestion metadata'),
 progression=[('D1-L2','conformed to a local model'),('D1-L3',"analytics-ready 'data-marts'"),('D1-L4','Cross-domain Analytics is enabled'),('D7-L5','Data Exploration')])
RULES[14] = dict(
 direct=('D5-L1','guidelines for creating FAIR data',[3,4],
         'An ethical data-handling strategy and communications plan can directly deliver early FAIR-specific process guidelines when they explicitly cover authorization and permitted reuse. Generic ethics policy alone is insufficient.',None),
 indirect=('D1-L1','governance for accessibility',[1,2,6,7],
           'Ethical risk assessment and monitoring can commission controlled access and licensing; the policies do not establish the implemented resource properties.',
           'Implement and test resource-specific authorization and accessible usage licensing'),
 progression=[('D5-L2','licenses, refresh cycles, lineage'),('D5-L3','evaluating and implementing FAIR standards'),('D3-L4','integration of FAIR metrics into the data governance process'),('D5-L5','planned processes to maintain FAIR implementation standards and tools')])


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')


def table(headers, rows):
    def cell(value):
        return str(value).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(c) for c in row)+' |' for row in rows])


def build():
    corpus = json.loads((ROOT/'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    descriptors = {d['id']:d for d in corpus['descriptors']}
    areas = {s['number']:s for s in corpus['summaries'] if s['number'] in RULES}
    activities = {a['id']:a for a in corpus['activities']}
    checks=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    def evidence(did, phrase):
        d=descriptors[did]
        matches=[p.strip() for p in re.split(r'\n\s*\n',d['source_markdown']) if phrase.lower() in p.lower()]
        check('Exact descriptor clause '+did+' / '+phrase,bool(matches))
        return dict(descriptor_id=did,phrase=phrase,clause=matches[0],source=d['source'])
    origins=[]
    reviews=[]
    baselines=[]
    for number,rule in RULES.items():
        area=areas[number]
        base_dim='D3' if number==1 else 'D7' if number in [4,8] else 'D4' if number==5 else 'D1'
        baselines.append(dict(area_id=area['id'],level=0,classification='diagnostic only',source=descriptors[base_dim+'-L0']['source'],descriptor=base_dim+'-L0',rationale='L0 describes missing or fragmented FAIR capabilities; it does not establish positive alignment.'))
        for kind in ['direct','indirect']:
            did,phrase,nums,rationale,via=rule[kind]
            onset=int(did[-1])
            source_activities=[activities[f'ACT-{number:02}-{n:03}'] for n in nums]
            origin=dict(id=f'ONSET-{number:02}-{kind}',area_id=area['id'],area_name=area['name'],kind=kind.title(),first_supported_level=onset,rationale=rationale,intermediate_practice=via,earliest_level_evidence=evidence(did,phrase),activity_ids=[a['id'] for a in source_activities],activities=[a['activity'] for a in source_activities],deliverables=[a['deliverables'] for a in source_activities],source_references=sorted({a['source'] for a in source_activities}),source_fair_direct=sorted({p for a in source_activities for p in a['direct']}),source_fair_indirect=sorted({p for a in source_activities for p in a['indirect']}),status='proposed documentary judgement; not an assessed maturity level')
            check(origin['id']+' indirect pathway',kind!='indirect' or bool(via))
            origins.append(origin)
        for level in range(1,6):
            if level==1:
                supporting=[o['earliest_level_evidence'] for o in origins if o['area_id']==area['id'] and o['first_supported_level']==1]
            else:
                supporting=[evidence(*rule['progression'][level-2])]
            reviews.append(dict(area_id=area['id'],level=level,descriptor_evidence=supporting,direct_active=level>=int(rule['direct'][0][-1]),indirect_active=level>=int(rule['indirect'][0][-1]),interpretation='Progression clauses describe increasingly demanding scope and practices. Carried association does not establish implementation of the full descriptor.'))
    links=[]
    for origin in origins:
        first=origin['first_supported_level']
        for level in range(first,6):
            progress=next(r for r in reviews if r['area_id']==origin['area_id'] and r['level']==level)
            ev=[origin['earliest_level_evidence']]+progress['descriptor_evidence']
            ev=list({e['descriptor_id']+' '+e['phrase']:e for e in ev}.values())
            carried=level>first
            rationale=[origin['rationale'],f'First supported at L{first}; '+(f'carried forward to L{level} under the requested cumulative association.' if carried else 'introduced at this level.')]
            if origin['intermediate_practice']:rationale.append('Indirect pathway via: '+origin['intermediate_practice'])
            rationale += [e['descriptor_id']+': '+e['clause'] for e in progress['descriptor_evidence']]
            links.append(dict(id=f'{origin["area_id"]}-L{level}-{origin["kind"]}',source=origin['area_id'],target=f'L{level}',kind=origin['kind'],value=1,source_label=origin['area_name'],target_label=f'L{level} · {LEVELS[level]}',onset_id=origin['id'],first_supported_level=first,inherited=carried,inheritance_path=list(range(first,level+1)),intermediate_practice=origin['intermediate_practice'],rationales=rationale,deliverables=origin['deliverables'],activities=origin['activities'],underlying_record_count=1,principles=sorted(set(origin['source_fair_direct']+origin['source_fair_indirect'])),original_fair_contribution_types=[k for k,key in [('Direct','source_fair_direct'),('Indirect','source_fair_indirect')] if origin[key]],conditions=['The named practice must explicitly support the cited FAIRMM capability at the stated scope.','Cumulative association retains the area and contribution type; it is not a claim that a complete higher maturity level is achieved.','Higher-level implementation, resources and competence remain to be established.'],descriptor_ids=sorted({e['descriptor_id'] for e in ev}),sources=sorted(set(origin['source_references']+[e['source'] for e in ev])),evidence=ev))
    counts=Counter(l['kind'] for l in links)
    check('All selected core areas and additional topics',set(areas)==set(RULES) and {l['source'] for l in links}=={s['id'] for s in areas.values()})
    check('No positive L0 relationships',not any(l['target']=='L0' for l in links))
    check('Unique segment/level/type tuples',len({(l['source'],l['target'],l['kind']) for l in links})==len(links))
    for origin in origins:
        actual={int(l['target'][1:]) for l in links if l['onset_id']==origin['id']}
        check('Cumulative closure '+origin['id'],actual==set(range(origin['first_supported_level'],6)))
        check('No classification upgrade '+origin['id'],all(l['kind']==origin['kind'] for l in links if l['onset_id']==origin['id']))
    level_counts={f'L{i}':dict(Counter(l['kind'] for l in links if l['target']==f'L{i}')) for i in range(6)}
    for level in range(1,5):
        earlier={(l['source'],l['kind']) for l in links if l['target']==f'L{level}'}
        later={(l['source'],l['kind']) for l in links if l['target']==f'L{level+1}'}
        check(f'L{level} associations retained at L{level+1}',earlier<=later)
    W,H,left,right,bar,top,bottom=1800,1120,435,1265,16,205,1005
    degree=Counter()
    for link in links:degree[link['source']]+=1;degree[link['target']]+=1
    unit=(bottom-top-(len(areas)-1)*24)/len(links)
    nodes=[]
    for side,items,gap in [('source',[(a['id'],str(i)+'. '+a['name']) for i,a in areas.items()],24),('target',[(f'L{i}',f'L{i} · {n}'+(' (baseline)' if i==0 else '')) for i,n in enumerate(LEVELS)],28)]:
        total=sum(degree[k]*unit for k,_ in items)+gap*(len(items)-1)
        y=top+(bottom-top-total)/2
        for key,label in items:
            href=('../source-release.html#section-'+str(int(key[-2:])) if areas[int(key[-2:])]['source'].startswith('file:') else 'https://fair-dama.perdl.com/dama/segments/'+areas[int(key[-2:])]['source'].split('/')[-1].split('.md')[0]+'/') if side=='source' else ('https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/'+corpus['sources']['fairmm_revision']+'/docs/level'+key[1:]+'.md')
            nodes.append(dict(id=key,side=side,label=label,lines=textwrap.wrap(label,36 if side=='source' else 34),x=left if side=='source' else right,y=y,height=degree[key]*unit,degree=degree[key],documentation_url=href))
            y+=degree[key]*unit+gap
    ni={n['id']:n for n in nodes};so=Counter();to=Counter()
    links.sort(key=lambda l:(l['source'],l['target'],l['kind']))
    for l in links:
        l['geometry']=dict(x0=left+bar,x1=right,y0=ni[l['source']]['y']+so[l['source']]*unit,y1=ni[l['target']]['y']+to[l['target']]*unit,thickness=unit)
        so[l['source']]+=1;to[l['target']]+=1
    for n in nodes:check('Ribbon conservation '+n['id'],abs(n['height']-degree[n['id']]*unit)<1e-7)
    model=dict(title='DAMA knowledge areas and FAIRMM maturity levels',width=W,height=H,nodes=nodes,links=links,counts=dict(counts),onsets=origins,level_review=reviews,diagnostic_baseline=baselines,reviewed_descriptor_ids=sorted(descriptors),level_counts=level_counts,source_revisions=corpus['sources'],unit='One equal-width ribbon per knowledge area, level and contribution type',method='Curated descriptor-to-practice onset judgements, followed by monotone cumulative closure; no maturity scores',excluded=['Aggregate Data Management overview','Supporting Maturity Assessment discipline'],conditional=True)
    check('All 42 descriptors retained as review references',len(model['reviewed_descriptor_ids'])==42)
    return render_model(model,areas,corpus,checks)


def render_model(model,areas,corpus,checks=None):
    """Render an already-built model, including one extracted from the RDF modules."""
    if checks is None:checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    origins=model['onsets'];level_counts=model['level_counts'];links=model['links'];counts=model['counts']
    svg=static_svg(model)
    ET.fromstring(svg);check('SVG parses',True)
    # Reuse the established D3 interaction without adding selectors.
    template=(ROOT/'scripts/templates/dimension_sankey.html').read_text(encoding='utf-8')
    template=template.replace('DAMA segments and FAIRMM dimensions','DAMA knowledge areas and FAIRMM maturity levels').replace('DAMA segments','DAMA knowledge areas').replace('FAIRMM dimensions','FAIRMM maturity levels').replace('Proposed Direct and Indirect dimension alignment','Proposed cumulative level alignment').replace('Direct · 38',f'Direct · {counts["Direct"]}').replace('Indirect · 7',f'Indirect · {counts["Indirect"]}').replace('Each ribbon = one proposed relationship','One ribbon = one area–level–type association').replace('segment or dimension','area or level').replace('The aggregate overview and two extensions without a segment assignment are excluded. Segment 12 is a supporting discipline. Direct/Indirect dimension support is separate from source FAIR-principle classifications.','L0 is diagnostic only. The aggregate overview and Maturity Assessment are excluded. Direct/Indirect level support is separate from source FAIR-principle classifications; inherited associations do not establish higher-level implementation.').replace('underlying documentary records','onset basis').replace('Candidate descriptor references','Descriptor references (onset and progression)').replace('dama-fairmm-dimensions-sankey',PREFIX)
    template=template.replace("const nodes=model.nodes.filter(n=>active.has(n.id)).map",'const nodes=model.nodes.map').replace('.nodeWidth(12).nodePadding',".nodeAlign(d=>d.side==='source'?0:1).nodeWidth(12).nodePadding").replace(".attr('height',d=>d.y1-d.y0)",".attr('height',d=>Math.max(6,d.y1-d.y0))")
    template=template.replace('Proposed Direct and Indirect DAMA segment to FAIRMM dimension alignment','Cumulative DAMA knowledge area to FAIRMM level alignment').replace('Widths count distinct segment–dimension–type relationships','Widths count cumulative area–level–type associations').replace('a area or level','an area or level')
    dynamic=template.replace('__MODEL__',json.dumps(model,ensure_ascii=False).replace('</','<\\/'))
    offline=(ROOT/'scripts/templates/offline_dimension_sankey.html').read_text(encoding='utf-8').replace('DAMA and FAIRMM offline Sankey','DAMA and FAIRMM levels offline Sankey').replace('__SVG__',svg).replace('__MODEL__',json.dumps(model,ensure_ascii=False).replace('</','<\\/'))
    for folder in [OUT,DOC]:
        write(folder/(PREFIX+'.svg'),svg);write(folder/(PREFIX+'.html'),dynamic);write(folder/(PREFIX+'-offline.html'),offline);write(folder/(PREFIX+'.json'),json.dumps(model,ensure_ascii=False,indent=2)+'\n')
    analysis=analysis_page(areas,origins,level_counts,corpus)
    analysis=analysis.replace('The 11 numbered core areas','The 11 core areas and the two additional topics (Big Data & Data Science and Data Handling Ethics)').replace('22 onset judgements, 55 area-and-level progression reviews, 11 L0 diagnostic reviews',f'{len(origins)} onset judgements, {len(model["level_review"])} area-and-level progression reviews, {len(model["diagnostic_baseline"])} L0 diagnostic reviews').replace('existing dimension diagrams are preserved','both dimension and level diagrams are regenerated').replace('FAIR–DAMA source: Chris Day, revision','DAMA source: Chris Day, supplied v1.1.0 ontology / v1.18.0 document / V3 workbook release, 16 November 2026. Checkout context only: revision').replace('`, CC0. Upstream notices','`. Preserve source-component notices and DAMA International image copyright. Upstream notices')
    write(OUT/'dama-fairmm-levels-analysis.md',analysis);write(DOC/'analysis.md',analysis)
    version=hashlib.sha256(dynamic.encode()).hexdigest()[:12]
    url=PREFIX+'.html?v='+version
    loader='''<button id="load-levels" type="button">Load interactive diagram</button>
<iframe id="levels-frame" title="Interactive cumulative FAIRMM level alignment" width="100%" height="1350" loading="lazy" style="border:0;display:none;"></iframe>
<script>(()=>{const button=document.getElementById('load-levels'),frame=document.getElementById('levels-frame');button.addEventListener('click',()=>{frame.src='__URL__';frame.style.display='block';button.hidden=true});window.addEventListener('message',e=>{if(e.source===frame.contentWindow&&e.data?.type==='fairmm-sankey-height'&&Number.isFinite(e.data.height))frame.height=String(Math.max(600,Math.min(9000,e.data.height+20)))})})();</script>'''.replace('__URL__',url)
    md=f'''# DAMA knowledge areas and FAIRMM maturity levels

![Cumulative Direct and Indirect knowledge-area alignment]({PREFIX}.svg)

The earliest supported level is proposed from the full L0–L5 descriptors. Every association is carried forward through L5, preserving its Direct or Indirect type. L0 is a diagnostic baseline with no positive ribbons. There are {len(links)} cumulative ribbons derived from {len(origins)} onset judgements, not {len(links)} independent capabilities.

{loader}

[Open interactive diagram]({url}) · [Offline fallback]({PREFIX}-offline.html) · [SVG]({PREFIX}.svg) · [Data]({PREFIX}.json)

[Read the onset analysis and source evidence](analysis.md). Hover nodes, select ribbons for rationale and deliverables, and select labels to open documentation. No dropdown selectors are required.

The 11 core areas retain the source terminology, including Data Development and Data Operations. Big Data & Data Science and Data Handling Ethics are included as additional topics. The aggregate overview and supporting Maturity Assessment discipline are excluded. Higher levels increase scope and capability requirements; the diagram does not assign organisational maturity or require every early process to remain unchanged.
'''
    write(DOC/'index.md',md)
    landing=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DAMA and FAIRMM levels Sankey</title><style>body{{font:16px/1.6 system-ui,sans-serif;color:#16283c;background:#fff;max-width:1600px;margin:auto;padding:24px}}img{{width:100%;height:auto}}button{{font:inherit;padding:10px 16px}}a{{color:#2463a7}}</style></head><body><h1>DAMA knowledge areas and FAIRMM maturity levels</h1><p>{len(origins)} proposed onset judgements expand to {len(links)} cumulative associations. All associations persist to higher levels; L0 remains diagnostic only.</p><img src="{PREFIX}.svg" alt="Static cumulative DAMA knowledge area and FAIRMM level alignment"><p>Hover nodes to highlight connections, select ribbons for the first supported level and carried-forward evidence, or select labels for documentation.</p>{loader}<p><a href="{url}">Open interactive diagram separately</a> · <a href="{PREFIX}-offline.html">Offline version</a> · <a href="dama-fairmm-levels-analysis.md">Analysis</a> · <a href="{PREFIX}.json">Source data</a></p><p>Equal width counts area–level–type associations, not strength or maturity. Current-level descriptor clauses are additional context; inherited association does not prove their implementation.</p></body></html>'''
    write(OUT/'index.html',landing)
    write(OUT/'dama-fairmm-levels-validation.json',json.dumps(dict(status='passed',checks=checks,counts=dict(counts),cumulative_links=len(links),onset_judgements=len(origins),level_counts=level_counts),indent=2)+'\n')
    print(json.dumps(dict(onsets=len(origins),cumulative_links=len(links),counts=dict(counts),level_counts=level_counts,checks=len(checks))))


def static_svg(model):
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 1120" role="img" aria-labelledby="title desc"><title id="title">Cumulative DAMA knowledge area and FAIRMM level alignment</title><desc id="desc">L1 associations persist through L5. L0 has no positive alignment. Direct and Indirect are separate contribution types.</desc><rect width="1800" height="1120" fill="white"/><g font-family="Segoe UI,Arial,sans-serif" fill="#16283c">','<text x="48" y="57" font-size="31" font-weight="600">DAMA knowledge areas and FAIRMM maturity levels</text>','<text x="48" y="94" font-size="19">Proposed cumulative association · FAIRMM v1.2.5 · 15 November 2026</text>',f'<rect x="48" y="122" width="38" height="15" fill="#2463a7"/><text x="98" y="136" font-size="18">Direct · {model["counts"]["Direct"]}</text>',f'<rect x="260" y="122" width="38" height="15" fill="#b75f08"/><text x="310" y="136" font-size="18">Indirect · {model["counts"]["Indirect"]}</text>','<text x="480" y="136" font-size="18">One ribbon per area–level–type; inherited links retain their type</text>','<text x="48" y="183" font-size="17">DAMA knowledge areas</text><text x="1298" y="183" font-size="17">FAIRMM maturity levels</text></g>']
    parts.append('<g class="ribbons">')
    for l in model['links']:
        g=l['geometry'];x0,x1,y0,y1,t=[g[k] for k in ['x0','x1','y0','y1','thickness']];c0=x0+(x1-x0)*.45;c1=x1-(x1-x0)*.45
        path=f'M{x0},{y0} C{c0},{y0} {c1},{y1} {x1},{y1} L{x1},{y1+t} C{c1},{y1+t} {c0},{y0+t} {x0},{y0+t} Z'
        extra=' stroke="#783b00" stroke-width="0.8" stroke-dasharray="6 4"' if l['kind']=='Indirect' else ''
        color='#2463a7' if l['kind']=='Direct' else '#b75f08'
        label=f'{l["source_label"]} → {l["target_label"]} · {l["kind"]}; first L{l["first_supported_level"]}'+('; carried forward' if l['inherited'] else '; introduced here')
        parts.append(f'<path d="{path}" fill="{color}" fill-opacity="0.30"{extra} data-link="{l["id"]}" tabindex="0" role="button" aria-label="{escape(label)}"><title>{escape(label)}</title></path>')
    parts.append('</g><g font-family="Segoe UI,Arial,sans-serif" fill="#16283c" font-size="18">')
    for n in model['nodes']:
        parts.append(f'<rect data-node="{n["id"]}" x="{n["x"]}" y="{n["y"]}" width="16" height="{max(6,n["height"])}" fill="#405468"/>')
        for i,line in enumerate(n['lines']):
            y=n['y']+n['height']/2+(i-(len(n['lines'])-1)/2)*23+6
            x,anchor=(419,'end') if n['side']=='source' else (1299,'start')
            parts.append(f'<text data-node="{n["id"]}" x="{x}" y="{y}" text-anchor="{anchor}">{escape(line)}</text>')
    parts+=['<text x="48" y="1055" font-size="17">22 onset judgements → 107 cumulative associations. L0 is diagnostic, not positive alignment.</text>','<text x="48" y="1085" font-size="17">Area presence compounds; scope, implementation and maturity must still be established independently.</text></g></svg>']
    return '\n'.join(parts).replace('22 onset judgements → 107 cumulative associations',f'{len(model["onsets"])} onset judgements → {len(model["links"])} cumulative associations').replace('15 November 2026','16 November 2026')


def analysis_page(areas,origins,counts,corpus):
    rows=[]
    for i,a in areas.items():
        direct=next(o for o in origins if o['area_id']==a['id'] and o['kind']=='Direct')
        indirect=next(o for o in origins if o['area_id']==a['id'] and o['kind']=='Indirect')
        rows.append((a['name'],'L'+str(direct['first_supported_level']),'L'+str(indirect['first_supported_level']),direct['rationale']))
    result='''# FAIRMM level alignment analysis

The full seven-dimension descriptions at L0–L5 are the evidence baseline. The earliest supported association is a proposed documentary judgement about a specific DAMA practice and FAIRMM clause, not a claim that the whole knowledge area or an organisation attains that level. Direct support produces or verifies a named level capability; Indirect support enables an intermediate practice that does so. Existing FAIR-principle classifications remain separate and unchanged.

## Earliest supported association

'''+table(['DAMA knowledge area','Direct onset','Indirect onset','Direct onset rationale'],rows)+'''

Most knowledge areas can contribute at L1 because FAIRMM includes strategy, roles, profiling, governance and initial tools at that level. Higher levels predominantly change deployment scope, operational integration and interoperability rather than introducing entirely new DAMA disciplines. Operational delivery is placed at L2 when working POC infrastructure is explicit; warehouse/BI delivery is placed at L3 when analytics-ready data marts are explicit. Earlier requirements work remains Indirect. These conservative distinctions can be revised if more specific source evidence is agreed.

## Cumulative association

An area–type association introduced at level k appears at every level k through L5. Each carried relationship references its onset judgement and identifies the inheritance path. Indirect never becomes Direct just because the level increases. Both types may coexist because different source practices contribute differently.

L0 is reviewed as a diagnostic baseline: deficits such as absent FAIR strategy or fragmented tools are not positive contributions. The L0 node has no incoming ribbons. FAIRMM describes levels as generally cumulative and notes exceptions for specific processes; the requested compounding rule is applied to knowledge-area association, not to the unchanged retention of every early process. L5 remains aspirational.

'''+table(['Level','Direct associations','Indirect associations','Total'],[(key,value.get('Direct',0),value.get('Indirect',0),sum(value.values())) for key,value in counts.items()])+'''

## Scope and provenance

The 11 numbered core areas retain the FAIR–DAMA segment terminology. Data Development corresponds to the modelling/design-oriented source section and Data Operations to storage/operations; no ontology identity or framework-edition equivalence is asserted. The overview and supporting Maturity Assessment discipline are excluded. The two source checkouts are read only; existing dimension diagrams are preserved. No operational pilot is performed.

The JSON includes 22 onset judgements, 55 area-and-level progression reviews, 11 L0 diagnostic reviews, source activity IDs, original principle lists, exact descriptor clauses, and cumulative paths. Current-level clauses provide progression context, not proof of implementation. All 42 upstream descriptor references remain listed for review.

FAIRMM source: Pistoia Alliance FAIR Maturity Matrix contributors, branch FAIR-MM-V1.2.5, revision `'''+corpus['sources']['fairmm_revision']+'''`. The repository licence is GPL-3.0; its persona overview separately states CC BY 4.0. FAIR–DAMA source: Chris Day, revision `'''+corpus['sources']['fair_dama_revision']+'''`, CC0. Upstream notices are retained in the sibling source checkout and the existing crosswalk documentation.

## Onset evidence and indirect pathways

'''
    for o in origins:
        e=o['earliest_level_evidence']
        result+=f'### {o["area_name"]} {o["kind"]}\n\nFirst supported: **L{o["first_supported_level"]}**, carried through L5. {o["rationale"]}\n\n'
        if o['intermediate_practice']:result+='Intermediate practice: '+o['intermediate_practice']+'.\n\n'
        result+=f'FAIRMM evidence: [{e["descriptor_id"]}]({e["source"]}); exact matching phrase: “{e["phrase"]}”.\n\n'
        result+='DAMA activities: '+', '.join(o['activity_ids'])+'. Deliverables: '+'; '.join(o['deliverables'])+'.\n\n'
    return result


if __name__=='__main__':
    build()
