"""D7-to-DAMA-persona projection through explicit activity-role occurrences."""
from collections import defaultdict,Counter
from pathlib import Path
from html import escape
import hashlib,json,re,textwrap
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PREFIX='dama-fairmm-tools-personas-sankey'
OUT=ROOT/'results/tools-personas';DOC=ROOT/'docs/tools-personas'

def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')

def main():
    corpus_path=ROOT/'artefacts/fairmm-crosswalk.json'
    d=json.loads(corpus_path.read_text(encoding='utf-8'))
    personas={p['name']:p for p in d['dama_personas']}
    names=sorted(personas,key=lambda x:(-len(x),x))
    # Protect comma-containing catalogue names before separating complete role
    # entries. Never match "Managers" inside an unknown longer role label.
    def parse_roles(raw):
        protected={}
        for name in names:
            if ',' not in name:continue
            token=f'__COMPOSITE_{len(protected)}__'
            if name in raw:raw=raw.replace(name,token);protected[token]=name
        tokens=[protected.get(t.strip(' .'),t.strip(' .')) for t in re.split(r'[,;]',raw) if t.strip(' .')]
        return sorted({t for t in tokens if t in personas}),[t for t in tokens if t not in personas]
    aligned=defaultdict(list)
    for a in d['alignments']:
        if a['dimension']=='D7' and a.get('activity_id'):aligned[a['activity_id']].append(a)
    grouped=defaultdict(list);unresolved=[]
    for a in d['activities']:
        if a['id'] not in aligned:continue
        for field,role in [('responsible_roles','Responsible'),('approving_roles','Approving'),('contributing_roles','Contributing')]:
            raw=a[field];matches,fragments=parse_roles(raw)
            if fragments:unresolved.append(dict(activity_id=a['id'],role=role,source_text=raw,unmatched_fragments=fragments))
            for name in matches:
                for kind in sorted({r['proposed_dimension_contribution_type'] for r in aligned[a['id']]}):
                    grouped[name,kind].append(dict(activity_id=a['id'],activity=a['activity'],area=a['area'],role=role,source_text=raw,source=a['source'],deliverable=a['deliverables'],alignment_ids=sorted(r['id'] for r in aligned[a['id']] if r['proposed_dimension_contribution_type']==kind)))
    links=[]
    for (name,kind),occurrences in sorted(grouped.items()):
        p=personas[name];records={r['id']:r for o in occurrences for r in aligned[o['activity_id']] if r['proposed_dimension_contribution_type']==kind}
        links.append(dict(id=p['id']+'-D7-'+kind,source='PERSONA-'+p['id'],target='D7',source_label=name,target_label='D7 · FAIR Tools and Infrastructures',kind=kind,value=1,underlying_record_count=len(records),activities=sorted({o['activity_id']+' · '+o['activity']+' · '+o['role'] for o in occurrences}),rationales=['The named DAMA persona occurs in an activity whose practice has proposed '+kind+' support for FAIRMM D7. This projection retains practice alignment type; it does not classify the individual persona as a Direct or Indirect contributor.'],deliverables=sorted({o['deliverable'] for o in occurrences}),conditions=sorted({r['condition'] for r in records.values()})+['Role occurrences are source responsibilities, not appointments or evidence that a person has implemented FAIR capability.'],principles=sorted({r['principle'] for r in records.values() if r.get('principle')}),original_fair_contribution_types=sorted({r['existing_contribution_type'] for r in records.values() if r.get('existing_contribution_type')}),descriptor_ids=sorted({x for r in records.values() for x in r['descriptor_candidates']}),sources=sorted({o['source'] for o in occurrences}),role_occurrences=occurrences,alignment_ids=sorted(records)))
    counts=Counter(l['kind'] for l in links)
    counts.setdefault('Direct',0);counts.setdefault('Indirect',0)
    person_names=sorted({name for name,kind in grouped})
    width=1800;height=max(1120,310+len(person_names)*52)
    top,bottom,left,right,bar=205,height-115,435,1265,16
    gap=28;unit=(bottom-top-gap*(len(person_names)-1))/len(links)
    degree=Counter()
    for l in links:degree[l['source']]+=1;degree[l['target']]+=1
    nodes=[];y=top
    for name in person_names:
        p=personas[name];key='PERSONA-'+p['id'];fragment=p['source'].split('#')[-1]
        nodes.append(dict(id=key,label=name,side='source',lines=textwrap.wrap(name,36),x=left,y=y,height=degree[key]*unit,documentation_url='../source-release.html#'+fragment));y+=degree[key]*unit+gap
    nodes.append(dict(id='D7',label='D7 · FAIR Tools and Infrastructures',side='target',lines=['D7 · FAIR Tools and','Infrastructures'],x=right,y=top+(bottom-top-len(links)*unit)/2,height=len(links)*unit,documentation_url='https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/'+d['sources']['fairmm_revision']+'/docs/fmm-d7.md'))
    ni={n['id']:n for n in nodes};offset=Counter()
    for l in links:
        src,dst=ni[l['source']],ni[l['target']]
        l['geometry']=dict(x0=left+bar,x1=right,y0=src['y']+offset[src['id']]*unit,y1=dst['y']+offset[dst['id']]*unit,thickness=unit)
        offset[src['id']]+=1;offset[dst['id']]+=1
    model=dict(title='DAMA personas and FAIRMM Tools and Infrastructure',width=width,height=height,nodes=nodes,links=links,counts=dict(counts),basis='D7 practice alignment joined to exact DAMA catalogue names in activity responsibility fields',unit='One equal-width ribbon per persona and practice alignment type; not a personal contribution assertion',source_sha256=hashlib.sha256(corpus_path.read_bytes()).hexdigest(),source_revisions=d['sources'],unresolved_role_fragments=unresolved,source_activity_count=len(aligned),source_alignment_count=sum(map(len,aligned.values())),conditional=True)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>DAMA personas linked to FAIRMM Tools and Infrastructure through activity roles</title><rect width="1800" height="{height}" fill="white"/><g font-family="Segoe UI,Arial,sans-serif" fill="#16283c">',f'<text x="48" y="57" font-size="31" font-weight="600">{escape(model["title"])}</text>',f'<text x="48" y="94" font-size="19">{len(person_names)} catalogue personas · {len(aligned)} D7-aligned activities · 17 November 2026</text>',f'<text x="48" y="136" font-size="18">Blue: {counts["Direct"]} persona–D7 links through Direct practice alignments; Indirect practice links: {counts["Indirect"]}</text>','<text x="48" y="173" font-size="17">DAMA personas (activity role occurrences)</text><text x="1299" y="173" font-size="17">FAIRMM dimension</text>']
    for l in links:
        g=l['geometry'];x0,x1,y0,y1,t=[g[k] for k in ['x0','x1','y0','y1','thickness']];c0=x0+(x1-x0)*.45;c1=x1-(x1-x0)*.45
        path=f'M{x0},{y0} C{c0},{y0} {c1},{y1} {x1},{y1} L{x1},{y1+t} C{c1},{y1+t} {c0},{y0+t} {x0},{y0+t} Z'
        svg.append(f'<path data-link="{escape(l["id"])}" d="{path}" fill="{"#2463a7" if l["kind"]=="Direct" else "#b75f08"}" fill-opacity=".35"><title>{escape(l["source_label"])}: {len(l["role_occurrences"])} activity-role occurrences</title></path>')
    for n in nodes:
        svg.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="16" height="{n["height"]}" fill="#405468"/>')
        for i,line in enumerate(n['lines']):
            x,anchor=(419,'end') if n['side']=='source' else (1299,'start');y=n['y']+n['height']/2+(i-(len(n['lines'])-1)/2)*23+6
            svg.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="18">{escape(line)}</text>')
    svg.extend([f'<text x="48" y="{height-65}" font-size="17">Ribbons retain practice alignment type. Responsible, Approving and Contributing roles are listed in the details.</text>',f'<text x="48" y="{height-35}" font-size="17">Persona participation does not establish personal accountability, FAIR implementation or maturity. Unmatched role labels are documented separately.</text></g></svg>'])
    svg='\n'.join(svg);ET.fromstring(svg)
    template=(ROOT/'scripts/templates/dimension_sankey.html').read_text(encoding='utf-8')
    template=template.replace('DAMA segments and FAIRMM dimensions',model['title']).replace('DAMA segments','DAMA personas').replace('FAIRMM dimensions','FAIRMM Tools and Infrastructure').replace('segment or dimension','persona or dimension').replace('Proposed Direct and Indirect dimension alignment','Activity-role projection of proposed D7 practice alignment').replace('Direct · 38',f'Direct practice links · {counts["Direct"]}').replace('Indirect · 7',f'Indirect practice links · {counts["Indirect"]}').replace('Each ribbon = one proposed relationship','Each ribbon = one persona–practice-type association').replace('dama-fairmm-dimensions-sankey',PREFIX).replace('const w=Math.max(300,Math.round(chart.clientWidth)),h=1020','const w=Math.max(300,Math.round(chart.clientWidth)),h=model.height-160').replace('shortNames[d.id]:d.label','(shortNames[d.id]||d.label):d.label')
    template=template.replace('Widths count distinct segment–dimension–type relationships, not strength, implementation or maturity. The aggregate overview and two extensions without a segment assignment are excluded. Segment 12 is a supporting discipline. Direct/Indirect dimension support is separate from source FAIR-principle classifications.','Widths count persona–practice-type associations. Alignment type belongs to the practice, not the person. Activity roles remain distinct from area-level supplier/participant/consumer occurrences; no responsibility is inferred from area membership.')
    template=template.replace('Ribbon width remains one relationship.','Ribbon width remains one relationship.').replace("text(detail,'h3','Rationale');", "text(detail,'h3','Source activity roles');list(detail,l.role_occurrences.map(o=>o.activity_id+' · '+o.activity+' · '+o.role+' · '+o.source_text));text(detail,'h3','Rationale');")
    template=template.replace("a.href=href;a.target", "a.href=href.startsWith('file:')?'../source-release.html#'+href.split('#').pop():href;a.target")
    dynamic=template.replace('__MODEL__',json.dumps(model,ensure_ascii=False).replace('</','<\\/'))
    offline=(ROOT/'scripts/templates/offline_dimension_sankey.html').read_text(encoding='utf-8').replace('__SVG__',svg).replace('__MODEL__',json.dumps(model,ensure_ascii=False).replace('</','<\\/'))
    version=hashlib.sha256(dynamic.encode()).hexdigest()[:12]
    loader=f'''<button id="load" type="button">Load interactive diagram</button><iframe id="frame" title="Tools and Infrastructure persona Sankey" width="100%" height="{height+400}" style="display:none;border:0"></iframe><script>document.getElementById('load').onclick=()=>{{let f=document.getElementById('frame');f.src='{PREFIX}.html?v={version}';f.style.display='block';document.getElementById('load').hidden=true}};window.addEventListener('message',e=>{{let f=document.getElementById('frame');if(e.source===f.contentWindow&&e.data?.type==='fairmm-sankey-height')f.height=String(e.data.height+20)}})</script>'''
    intro=f'{len(person_names)} DAMA catalogue personas connect through {len(aligned)} activities with {sum(map(len,aligned.values()))} proposed D7 alignment records. All current D7 practice alignments are Direct; none are Indirect. This is a projection through source activity roles, not a Direct classification of the personas themselves.'
    landing=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{model["title"]}</title><style>body{{font:16px/1.6 system-ui;max-width:1600px;margin:auto;padding:24px}}img{{width:100%}}button{{font:inherit;padding:10px}}</style><h1>{model["title"]}</h1><p>{intro}</p><img src="{PREFIX}.svg" alt="DAMA persona and FAIRMM D7 Sankey">{loader}<p><a href="{PREFIX}.html?v={version}">Open interactive diagram</a> · <a href="{PREFIX}-offline.html">Offline fallback</a> · <a href="{PREFIX}.json">Evidence data</a></p></html>'
    for folder in [OUT,DOC]:
        for ext,value in [('svg',svg),('html',dynamic),('-offline.html',offline),('json',json.dumps(model,ensure_ascii=False,indent=2)+'\n')]:write(folder/(PREFIX+('.'+ext if not ext.startswith('-') else ext)),value)
    write(OUT/'index.html',landing)
    md=f'# {model["title"]}\n\n{intro}\n\n![Tools and Infrastructure persona Sankey]({PREFIX}.svg)\n\n{loader}\n\n[Open interactive diagram]({PREFIX}.html?v={version}) · [Offline fallback]({PREFIX}-offline.html) · [Evidence JSON]({PREFIX}.json)\n\nThe diagram uses exact catalogue-name matches in Responsible, Approving and Contributing fields. Comma-containing catalogue names are matched before splitting labels. No acronym expansion, fuzzy equivalence, area-level responsibility inference or automatic supplier/consumer role conversion is applied. One equal-width ribbon groups each persona and D7 practice-alignment type; repeated FAIR IDs do not increase width. Select a ribbon for activities, original role text, deliverables, conditions and descriptor references.\n\n## Unmatched source role fragments\n\nThese remain unassigned rather than being silently merged into catalogue personas. The JSON retains the full source fields and coordinates.\n\n| Activity | Role | Unmatched text |\n|---|---|---|\n'+'\n'.join(f'| {x["activity_id"]} | {x["role"]} | {escape("; ".join(x["unmatched_fragments"]))} |' for x in unresolved)+'\n'
    write(DOC/'index.md',md)
    # Independent projection checks against the stored activity fields.
    acts={a['id']:a for a in d['activities']};fields={'Responsible':'responsible_roles','Approving':'approving_roles','Contributing':'contributing_roles'}
    for l in links:
        for o in l['role_occurrences']:
            assert o['source_text']==acts[o['activity_id']][fields[o['role']]]
            assert l['source_label'] in parse_roles(o['source_text'])[0]
            assert all(r in {a['id'] for a in aligned[o['activity_id']]} for r in o['alignment_ids'])
    assert len({(l['source'],l['target'],l['kind']) for l in links})==len(links)
    assert all(abs(offset[n['id']]*unit-n['height'])<1e-6 for n in nodes)
    assert '<select' not in dynamic
    report=dict(status='passed',personas=len(person_names),links=len(links),counts=dict(counts),aligned_activities=len(aligned),alignment_records=sum(map(len,aligned.values())),role_occurrences=sum(len(l['role_occurrences']) for l in links),unresolved_fields=len(unresolved),source_role_fidelity=True,unique_ribbons=True,ribbon_conservation=True,svg_valid=True,selector_free=True)
    write(OUT/'validation.json',json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
