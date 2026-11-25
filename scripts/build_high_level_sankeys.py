"""Five high-level connection Sankeys, extracted exclusively with SPARQL from RDF."""
from pathlib import Path
from collections import defaultdict,Counter
from html import escape
import hashlib,json,textwrap,re,shutil
import xml.etree.ElementTree as ET
from rdflib import Graph,RDF,RDFS,URIRef
from fairmm_rdf import ROOT,ART,MODULES,A,write

OUT=ROOT/'results/high-level-connections';DOC=ROOT/'docs/high-level-connections'
QUERIES=ROOT/'scripts/queries/high-level-connections'
PREFIX='''PREFIX align: <urn:fair-dama-fairmm:alignment:>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
'''
SPECS=[
 dict(key='dama-fair-principles',heading='DAMA → FAIR Principles',question='Which DAMA areas and topics have source activity assertions supporting each FAIR principle, and with which Direct/Indirect type?',basis='One equal-width ribbon per distinct area–principle–type. Activity assertion records remain available in ribbon details. Only the activity_table source layer is selected, avoiding duplicate counting across workbook, summary and ontology layers.',query=PREFIX+'''SELECT DISTINCT ?assertion ?area ?areaLabel ?practice ?practiceLabel ?principle ?kind ?source
WHERE {
  ?assertion a align:SourceAssertion ; align:sourceLayer "activity_table" ;
    align:inSourceTopic ?area ; align:hasPractice ?practice ;
    align:targetsPrinciple ?principle ; align:existingContributionType ?kind .
  ?area rdfs:label ?areaLabel . ?practice rdfs:label ?practiceLabel .
  OPTIONAL { ?assertion align:primarySource ?source }
}
ORDER BY ?area ?principle ?kind ?assertion
'''),
 dict(key='dama-fairmm-dimensions',heading='DAMA → FAIRMM Dimensions',question='Which DAMA areas and topics support each FAIRMM dimension through qualified Direct or Indirect assertions?',basis='One equal-width ribbon per distinct area–dimension–type, grouping qualified DimensionAlignment assertions. Two unassigned extension practices are excluded from this area-based view and reported separately. FAIRMM contribution type is not the original FAIR-principle classification.',query=PREFIX+'''SELECT DISTINCT ?assertion ?area ?areaLabel ?practice ?practiceLabel ?dimension ?dimensionLabel ?kind ?rationale ?condition
WHERE {
  ?assertion a align:DimensionAlignment ; align:sourceTopic ?area ;
    align:fromPractice ?practice ; align:targetsDimension ?dimension ;
    align:contributionType ?kind .
  ?area rdfs:label ?areaLabel . ?practice rdfs:label ?practiceLabel .
  ?dimension rdfs:label ?dimensionLabel .
  OPTIONAL { ?assertion align:rationale ?rationale }
  OPTIONAL { ?assertion align:applicabilityCondition ?condition }
}
ORDER BY ?area ?dimension ?kind ?assertion
'''),
 dict(key='dimensions-levels',heading='Dimensions × Levels',question='How do the seven dimensions and six ordered levels connect through the 42 contextual descriptors?',basis='Dimension → Descriptor → Level. Each descriptor contributes one unit on each adjacent leg: 42 descriptors, 84 graphical links. These are matrix membership relationships, not Direct/Indirect contributions or assessed maturity. Hover or focus a descriptor to read its explanatory RDF comment; select it for the summary and source.',query=PREFIX+'''SELECT DISTINCT ?dimension ?dimensionLabel ?descriptor ?descriptorID ?descriptorComment ?level ?levelLabel ?ordinal ?source
WHERE {
  ?descriptor a align:Descriptor ; align:inDimension ?dimension ;
    align:atLevel ?level ; dcterms:identifier ?descriptorID .
  ?dimension a align:Dimension ; rdfs:label ?dimensionLabel .
  ?level a align:MaturityLevel ; rdfs:label ?levelLabel ; align:levelOrdinal ?ordinal .
  OPTIONAL { ?descriptor rdfs:comment ?descriptorComment }
  OPTIONAL { ?descriptor align:primarySource ?source }
}
ORDER BY ?dimension ?ordinal
'''),
 dict(key='personas-activities-outcomes',heading='Personas → Activities → Outcomes',question='Which DAMA personas occur in recorded activity responsibilities, and which intended deliverables are connected to those practices?',basis='Persona → Activity → Intended deliverable. Persona-to-activity weight counts distinct RDF ActivityRoleOccurrence resources, retaining role categories in the details. An activity’s incoming count is allocated equally across its distinct deliverables to conserve flow. Width measures documentary role occurrences, not effort, accountability or verified outcomes. Only occurrences already materialised in the ontology are included; this is not a complete extraction of every workbook role. Area-level supplier/participant/consumer occurrences are not used.',query=PREFIX+'''SELECT DISTINCT ?occurrence ?persona ?personaLabel ?role ?practice ?practiceLabel ?deliverable ?deliverableLabel ?source
WHERE {
  ?occurrence a align:ActivityRoleOccurrence ; align:sourcePersona ?persona ;
    align:sourceRoleCategory ?role ; align:concernsPractice ?practice .
  ?persona rdfs:label ?personaLabel . ?practice rdfs:label ?practiceLabel ;
    align:hasDeliverable ?deliverable .
  ?deliverable rdfs:label ?deliverableLabel .
  OPTIONAL { ?occurrence dcterms:source ?source }
}
ORDER BY ?persona ?practice ?role ?deliverable ?occurrence
'''),
 dict(key='dama-levels',heading='DAMA → Levels',question='At which levels are DAMA area/type associations introduced or inherited, and which onset judgement and derivation rule explain them?',basis='One equal-width ribbon per cumulative area–level–type association. Each association retains its first-supported level, onset, introduced/inherited flag and derivation rule. L0 is visible but has no positive links. The 11 core areas and two additional topics are included; supporting Maturity Assessment has no positive onset in this view. Association does not establish attained maturity.',query=PREFIX+'''SELECT DISTINCT ?association ?area ?areaLabel ?level ?levelLabel ?ordinal ?kind ?onset ?firstLevel ?inherited ?rule
WHERE {
  ?association a align:CumulativeAssociation ; align:sourceTopic ?area ;
    align:targetsLevel ?level ; align:contributionType ?kind ;
    align:derivedFromOnset ?onset ; align:firstSupportedLevel ?firstLevel ;
    align:inherited ?inherited ; align:derivationRule ?rule .
  ?area rdfs:label ?areaLabel .
  ?level rdfs:label ?levelLabel ; align:levelOrdinal ?ordinal .
}
ORDER BY ?area ?ordinal ?kind
''')]

def ident(uri):return uri.rsplit(':',1)[-1] if uri.startswith(str(A)) else uri.rsplit('/',1)[-1].split('#')[-1]
def colour(kind):return {'Direct':'#2463a7','Indirect':'#b75f08','Descriptor':'#7752a0','Deliverable':'#607080','Responsible':'#258373','Approving':'#9a7031','Contributing':'#647cb3'}.get(kind,'#258373')

def make_model(spec,rows,g):
    nodes={};groups=defaultdict(list)
    def node(uri,label,column):
        nodes[uri]=dict(id=uri,label=label,column=column,side='source' if column==0 else 'target',comment=str(g.value(URIRef(uri),RDFS.comment) or ''),documentation_url=str(g.value(URIRef(uri),A.primarySource) or g.value(URIRef(uri),URIRef('http://purl.org/dc/terms/source')) or ''))
        return uri
    key=spec['key']
    if key in ['dama-fair-principles','dama-fairmm-dimensions','dama-levels']:
        target,lab={'dama-fair-principles':('principle',None),'dama-fairmm-dimensions':('dimension','dimensionLabel'),'dama-levels':('level','levelLabel')}[key]
        for r in rows:
            s=node(r['area'],r['areaLabel'],0);t=node(r[target],r[lab] if lab else ident(r[target]),1)
            groups[s,t,r['kind']].append(r)
        if key=='dama-levels':node(str(A.L0),str(g.value(A.L0,RDFS.label)),1)
    elif key=='dimensions-levels':
        for r in rows:
            s=node(r['dimension'],r['dimensionLabel'],0);m=node(r['descriptor'],r['descriptorID'],1);t=node(r['level'],r['levelLabel'],2)
            groups[s,m,'Descriptor'].append(r);groups[m,t,'Descriptor'].append(r)
    else:
        for r in rows:
            s=node(r['persona'],r['personaLabel'],0);m=node(r['practice'],r['practiceLabel'],1);t=node(r['deliverable'],r['deliverableLabel'],2)
            role=ident(r['role']).replace('_roles','').title()
            groups[s,m,role].append(r);groups[m,t,'Deliverable'].append(r)
    links=[]
    for (source,target,kind),records in sorted(groups.items()):
        weight=1
        if key=='personas-activities-outcomes':
            if kind=='Deliverable':
                incoming={r['occurrence'] for r in rows if r['practice']==source}
                outcomes={r['deliverable'] for r in rows if r['practice']==source}
                weight=len(incoming)/len(outcomes)
            else:weight=len({r['occurrence'] for r in records})
        links.append(dict(id='edge-'+hashlib.sha256((source+target+kind).encode()).hexdigest()[:16],source=source,target=target,source_label=nodes[source]['label'],target_label=nodes[target]['label'],kind=kind,value=weight,record_count=len(records),records=records))
    columns=max(n['column'] for n in nodes.values())+1
    column_counts=Counter(n['column'] for n in nodes.values())
    height=max(1120,max(column_counts.values())*88+370)
    width=2400 if columns==3 else 1800
    top,bottom=220,height-150;gap=64;incoming=Counter();outgoing=Counter()
    for l in links:outgoing[l['source']]+=l['value'];incoming[l['target']]+=l['value']
    degree={k:max(incoming[k],outgoing[k]) for k in nodes}
    available=[(bottom-top-gap*(column_counts[c]-1))/sum(degree[k] for k,n in nodes.items() if n['column']==c) for c in column_counts]
    unit=min(available)
    xs=[435,1265] if columns==2 else [435,1120,1900]
    for c in range(columns):
        members=sorted((n for n in nodes.values() if n['column']==c),key=lambda n:n['id'])
        total=sum(degree[n['id']]*unit for n in members)+gap*(len(members)-1);y=top+(bottom-top-total)/2
        for n in members:
            label=n['label'];short=label if len(label)<=82 else label[:79]+'…'
            n.update(x=xs[c],y=y,height=max(6,degree[n['id']]*unit),lines=textwrap.wrap(short,34)[:3]);y+=degree[n['id']]*unit+gap
    so=Counter();to=Counter()
    for l in links:
        s,t=nodes[l['source']],nodes[l['target']]
        l['geometry']=dict(x0=s['x']+16,x1=t['x'],y0=s['y']+so[s['id']]*unit,y1=t['y']+to[t['id']]*unit,thickness=l['value']*unit)
        so[s['id']]+=l['value'];to[t['id']]+=l['value']
    for n in nodes.values():
        if 0<n['column']<columns-1:assert abs(incoming[n['id']]-outgoing[n['id']])<1e-8,n['id']
    return dict(title=spec['heading'],key=key,question=spec['question'],basis=spec['basis'],width=width,height=height,nodes=list(nodes.values()),links=links,columns=columns,counts=dict(Counter(l['kind'] for l in links)),query_rows=len(rows),input='SPARQL over nine local Turtle modules; no crosswalk or diagram JSON inputs')

def static_svg(model):
    w,h=model['width'],model['height']
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(model["title"])}</title><rect width="{w}" height="{h}" fill="white"/><g font-family="Segoe UI,Arial,sans-serif" fill="#16283c">',f'<text x="48" y="57" font-size="32" font-weight="600">{escape(model["title"])}</text>',f'<text x="48" y="98" font-size="19">Ontology-derived documentary connections · 19 November 2026 · {len(model["links"])} graphical links</text>']
    x=48
    for kind,count in model['counts'].items():
        legend='42 descriptors · 84 links' if model['key']=='dimensions-levels' and kind=='Descriptor' else f'{kind} · {count}'
        out.append(f'<rect x="{x}" y="128" width="28" height="12" fill="{colour(kind)}"/><text x="{x+40}" y="141" font-size="18">{escape(legend)}</text>');x+=300
    for l in model['links']:
        p=l['geometry'];x0,x1,y0,y1,t=[p[k] for k in ['x0','x1','y0','y1','thickness']];c0=x0+(x1-x0)*.45;c1=x1-(x1-x0)*.45
        path=f'M{x0},{y0} C{c0},{y0} {c1},{y1} {x1},{y1} L{x1},{y1+t} C{c1},{y1+t} {c0},{y0+t} {x0},{y0+t} Z'
        dash=' stroke="#783b00" stroke-dasharray="6 4" stroke-width="1"' if l['kind']=='Indirect' else ''
        out.append(f'<path data-link="{l["id"]}" d="{path}" fill="{colour(l["kind"])}" fill-opacity=".35"{dash} tabindex="0" role="button"><title>{escape(l["source_label"]+" → "+l["target_label"]+" · "+l["kind"])}</title></path>')
    for n in model['nodes']:
        tooltip=n['label']+(' — '+n['comment'] if n.get('comment') else '')
        out.append(f'<rect data-node="{escape(n["id"])}" x="{n["x"]}" y="{n["y"]}" width="16" height="{n["height"]}" fill="#405468"><title>{escape(tooltip)}</title></rect>')
        for i,line in enumerate(n['lines']):
            x,anchor=(n['x']-16,'end') if n['column']==0 else (n['x']+28,'start');y=n['y']+n['height']/2+(i-(len(n['lines'])-1)/2)*22+6
            out.append(f'<text data-node="{escape(n["id"])}" x="{x}" y="{y}" text-anchor="{anchor}" font-size="18" stroke="white" stroke-width="5" paint-order="stroke">{escape(line)}<title>{escape(tooltip)}</title></text>')
    for i,line in enumerate(textwrap.wrap(model['basis'],width=180 if w==1800 else 240)):
        out.append(f'<text x="48" y="{h-100+i*22}" font-size="16">{escape(line)}</text>')
    out.append('</g></svg>');svg='\n'.join(out);ET.fromstring(svg);return svg

def render(spec,model):
    key=spec['key'];prefix='high-level-'+key+'-sankey'
    svg=static_svg(model)
    template=(ROOT/'scripts/templates/high_level_sankey.html').read_text(encoding='utf-8')
    data=json.dumps(model,ensure_ascii=False).replace('</','<\\/')
    dynamic=template.replace('__MODEL__',data).replace('__STATIC__',svg).replace('__TITLE__',escape(spec['heading'])).replace('__MODE__','dynamic')
    offline=template.replace('__MODEL__',data).replace('__STATIC__',svg).replace('__TITLE__',escape(spec['heading'])).replace('__MODE__','offline')
    for folder in [OUT/key,DOC/key]:
        write(folder/(prefix+'.svg'),svg);write(folder/(prefix+'.html'),dynamic);write(folder/(prefix+'-offline.html'),offline)
        write(folder/(prefix+'.json'),json.dumps(model,ensure_ascii=False,indent=2)+'\n')
        write(folder/'extracted-rows.json',json.dumps(model['extracted_rows'],ensure_ascii=False,indent=2)+'\n')
        write(folder/'query.rq',spec['query'])
    hashed=hashlib.sha256(dynamic.encode()).hexdigest()[:12]
    loader=f'''<button id="load" type="button">Load interactive diagram</button><iframe id="frame" title="{escape(spec['heading'])} Sankey" width="100%" height="1200" style="display:none;border:0"></iframe><script>document.getElementById('load').onclick=()=>{{const f=document.getElementById('frame');f.src='{prefix}.html?v={hashed}';f.style.display='block';document.getElementById('load').hidden=true}};window.addEventListener('message',e=>{{const f=document.getElementById('frame');if(e.source===f.contentWindow&&e.data?.type==='high-level-height'&&Number.isFinite(e.data.height))f.height=String(Math.min(30000,e.data.height+20))}})</script>'''
    links=f'[Interactive diagram]({prefix}.html?v={hashed}) · [Offline interaction]({prefix}-offline.html) · [SVG]({prefix}.svg) · [PNG]({prefix}.png) · [Query](query.rq) · [Extracted rows](extracted-rows.json) · [Graph data]({prefix}.json)'
    md=f'# {spec["heading"]}\n\n**Question:** {spec["question"]}\n\n{spec["basis"]}\n\n![Ontology-derived Sankey]({prefix}.svg)\n\n{loader}\n\n{links}\n\n## SPARQL\n\n```sparql\n{spec["query"]}```\n\nThe query is executed against the nine-module local RDF union. No automatic OWL imports or inference are used. All source triples remain unchanged.\n'
    write(DOC/key/'index.md',md)
    landing=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{escape(spec["heading"])}</title><style>body{{font:16px/1.6 system-ui;max-width:1800px;margin:auto;padding:24px}}img{{width:100%}}button{{font:inherit;padding:10px}}</style><h1>{escape(spec["heading"])}</h1><p>{escape(spec["question"])}</p><p>{escape(spec["basis"])}</p><img src="{prefix}.svg" alt="Ontology-derived Sankey">{loader}<p><a href="{prefix}.html?v={hashed}">Interactive diagram</a> · <a href="{prefix}-offline.html">Offline interaction</a> · <a href="{prefix}.png">PNG</a> · <a href="query.rq">SPARQL</a> · <a href="extracted-rows.json">Extracted rows</a></p></html>'
    write(OUT/key/'index.html',landing)
    return dict(key=key,query_rows=model['query_rows'],nodes=len(model['nodes']),links=len(model['links']),counts=model['counts'],flow_conserved=True)

def update_document(reports):
    path=ART/'FAIR_DAMA_FAIRMM_High_Level_Connections_v1.0.0.md'
    history=ROOT/'results/history/high-level-connections/FAIR_DAMA_FAIRMM_High_Level_Connections_v1.0.0.md'
    if not history.exists():write(history,path.read_text(encoding='utf-8'))
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'\n<!-- SPARQL-SANKEY-START -->.*?<!-- SPARQL-SANKEY-END -->\n','\n',text,flags=re.S)
    if '### Ontology dataset and execution' not in text:
        at=text.index('## DAMA → FAIR Principles')
        dataset='''### Ontology dataset and execution

The extraction dataset is a local RDF union of these nine Turtle modules:

- `artefacts/fairmm-core.ttl`, `fairmm-v1.2.5.ttl`, `fairmm-personas.ttl`, `fairmm-dama-alignment.ttl` and `fairmm-dama-derived.ttl`.
- `sources/2026-11-16/dama-ontologies-v1.1.0/fair-ontology.ttl`, `dama-ontology.ttl`, `dama-fair-mapping.ttl` and `dama-persona-ontology.ttl`.

Queries use the union as the default graph. Load the files explicitly; no remote `owl:imports`, inference, `SERVICE` calls or live assessment results are required. Direct/Indirect values belong to their declared assertion layer. Catalogue overview, activity and workbook assertions are not combined as independent evidence.

Reproduce all five views, PNGs, strict documentation build and independent checks from the independent project directory:

```powershell
pwsh -File scripts/build_high_level_all.ps1
```

Query files are also available under `scripts/queries/high-level-connections/`. The original ontologies are read-only inputs. The [diagram collection](../results/high-level-connections/index.html) links to all five static and on-demand interactive views, including offline interaction without D3 downloads. A ribbon's records show the exact SPARQL bindings used to construct it. In the personas view, intended deliverables are not verified outcomes; no observed evidence is fabricated.

'''
        text=text[:at]+dataset+text[at:]
    for spec,report in zip(SPECS,reports):
        marker='## '+spec['heading'];start=text.index(marker);end=text.find('\n## ',start+len(marker))
        if end<0:end=text.find('\n---\n',start)
        prefix='high-level-'+spec['key']+'-sankey';base='../results/high-level-connections/'+spec['key']+'/'
        block=f'''\n<!-- SPARQL-SANKEY-START -->
### SPARQL — Sankey extraction

**Sankey question:** {spec['question']}

**Interpretation and counting basis:** {spec['basis']}

```sparql
{spec['query']}```

**Extraction result:** {report['query_rows']} distinct query rows; {report['nodes']} nodes; {report['links']} graphical links. Link types: {', '.join(k+' '+str(v) for k,v in report['counts'].items())}.

[Static and on-demand interactive Sankey]({base}index.html) · [Static SVG]({base}{prefix}.svg) · [Static PNG]({base}{prefix}.png) · [Standalone query]({base}query.rq) · [Extracted evidence rows]({base}extracted-rows.json).

The generator executes this exact query against the local nine-module RDF union and retains the result rows with the diagram. Labels and relationship records come from RDF. Diagram JSON and the historical crosswalk are not extraction inputs. The input module hashes and per-view counts are recorded in the [build manifest](../results/high-level-connections/build-manifest.json).
<!-- SPARQL-SANKEY-END -->
'''
        text=text[:end]+block+text[end:]
    text=text.replace('version: "1.0.0"','version: "1.1.0"')
    text+='\n**v1.1.0 — 19 November 2026:** added executable SPARQL and five RDF-derived static/interactive Sankey views. The original v1.0.0 content is preserved under `results/history/high-level-connections/`. The requested v1.0.0 filename remains an enriched compatibility copy; the semantic release filename is v1.1.0.\n' if '**v1.1.0 —' not in text else ''
    write(path,text);write(ART/'FAIR_DAMA_FAIRMM_High_Level_Connections_v1.1.0.md',text)

def main():
    files=[ART/name for name in MODULES]+[ROOT/'sources/2026-11-16/dama-ontologies-v1.1.0'/name for name in ['fair-ontology.ttl','dama-ontology.ttl','dama-fair-mapping.ttl','dama-persona-ontology.ttl']]
    digests={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    g=Graph()
    for p in files:g.parse(p,format='turtle')
    reports=[]
    for spec in SPECS:
        write(QUERIES/(spec['key']+'.rq'),spec['query'])
        rows=[{str(k):str(v) for k,v in row.asdict().items()} for row in g.query(spec['query'])]
        assert rows,spec['key']
        model=make_model(spec,rows,g);model['extracted_rows']=rows
        model['input_module_sha256']=digests;model['query_sha256']=hashlib.sha256(spec['query'].encode()).hexdigest()
        reports.append(render(spec,model))
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digests[str(p.relative_to(ROOT))] for p in files)
    unassigned=sum(1 for n in g.subjects(RDF.type,A.DimensionAlignment) if g.value(n,A.sourceTopic) is None)
    manifest=dict(status='passed',input_modules=digests,union_triples=len(g),source_modules_unchanged=True,unassigned_dimension_extensions_excluded=unassigned,views=reports,extraction='RDFLib SPARQL SELECT DISTINCT; no JSON source inputs; no OWL inference')
    write(OUT/'build-manifest.json',json.dumps(manifest,indent=2)+'\n');update_document(reports)
    index='# High-level ontology connections\n\nFive documentary views extracted with SPARQL from the supplied DAMA source ontologies and the five FAIRMM modules. Source definitions, proposed capability support, role participation and maturity association retain their distinct meanings.\n\n'
    landing='<!doctype html><html lang="en"><meta charset="utf-8"><title>High-level ontology connections</title><h1>High-level ontology connections</h1><ul>'
    for spec in SPECS:index+=f'- [{spec["heading"]}]({spec["key"]}/index.md)\n';landing+=f'<li><a href="{spec["key"]}/index.html">{escape(spec["heading"])}</a></li>'
    write(DOC/'index.md',index);write(OUT/'index.html',landing+'</ul></html>')
    print(json.dumps(manifest['views'],indent=2))

if __name__=='__main__':main()
