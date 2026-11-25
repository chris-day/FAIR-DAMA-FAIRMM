"""Refresh documentary alignment from the three user-supplied November 2026 sources.

Read-only XLSX extraction uses the standard-library ZIP/XML APIs. Run with the
project Python interpreter; no workbook, source checkout or input is modified.
"""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import urlparse, unquote
from collections import Counter
import copy, hashlib, json, re, shutil, posixpath
import xml.etree.ElementTree as ET
from rdflib import Graph, RDF, RDFS
from rdflib.namespace import DCTERMS as DC
import build_fairmm_alignment as cross
import build_levels_sankey as lev

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[1]
RELEASE=ROOT/'sources/2026-11-16'
HISTORY=ROOT/'results/history/pre-2026-11-16-refresh'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):cross.save(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def workbook_rows(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(path) as z:
        strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for s in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
            target=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            target=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            records=[]
            for row in ET.fromstring(z.read(target)).findall('m:sheetData/m:row',ns):
                cells={}
                for cell in row:
                    v=cell.find('m:v',ns); inline=cell.find('m:is',ns)
                    value=(v.text or '') if v is not None else ''.join(inline.itertext()) if inline is not None else ''
                    if cell.get('t')=='s':value=strings[int(value)]
                    cells[re.sub(r'\d','',cell.get('r'))]=value
                records.append({'row':int(row.get('r')),'cells':cells})
            result[s.get('name')]=records
        return result

def main():
    RELEASE.mkdir(parents=True,exist_ok=True)
    for name in ['DAMA_Segments_High_Level_v1.18.0.md','DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx']:
        shutil.copyfile(WORK/name,RELEASE/name)
    shutil.copyfile(WORK/'outputs/DAMA_FAIR_Ontologies_v1.1.0.zip',RELEASE/'DAMA_FAIR_Ontologies_v1.1.0.zip')
    with ZipFile(RELEASE/'DAMA_FAIR_Ontologies_v1.1.0.zip') as z:
        for member in z.infolist():
            dest=(RELEASE/member.filename).resolve()
            if not dest.is_relative_to(RELEASE.resolve()):raise ValueError('Unsafe ZIP member')
            if not member.is_dir():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(member))
    package=RELEASE/'dama-ontologies-v1.1.0'
    manifest=json.loads((package/'manifest.json').read_text(encoding='utf-8-sig'))
    for name,sha in manifest['sha256'].items():assert digest(package/name)==sha,name
    doc=RELEASE/'DAMA_Segments_High_Level_v1.18.0.md'
    assert digest(doc)==manifest['sourceSha256'][doc.name]
    # Preserve the previous accepted documentary corpus and diagram baselines once.
    for rel in ['artefacts/fairmm-crosswalk.json','results/ontology/baselines/dimensions-approved.json','results/ontology/baselines/levels-approved.json']:
        dst=HISTORY/rel
        if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
    old=json.loads((HISTORY/'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    data=copy.deepcopy(old); text=cross.read(doc); lines=text.splitlines()
    sections=list(re.finditer(r'^## (\d+)\. (.+)$',text,re.M))
    summaries=[];activities=[];assertions=[];workbook=workbook_rows(RELEASE/'DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx')
    reconciled=[];differences=[]
    def norm(s):return re.sub(r'\s+',' ',s.replace('\\|','|')).strip()
    for i,m in enumerate(sections):
        number=int(m[1]);name=m[2];start=text[:m.start()].count('\n')
        body=text[m.start():sections[i+1].start() if i+1<len(sections) else text.index('\n## FAIR Alignment Gaps',m.start())]
        rs=list(cross.rows(body)); s=next(c for _,c in rs if len(c)==3 and c[0].startswith(str(number)+'. '))
        summary=dict(id=f'AREA-{number:02}',number=number,name=name,source=doc.as_uri()+f'#L{start+1}',source_layer='segment_summary',direct=cross.ids(s[1]),indirect=cross.ids(s[2]),aggregate=number==0,classification='core knowledge area' if 1<=number<=11 else 'aggregate overview' if number==0 else 'additional supporting topic')
        summaries.append(summary)
        for kind in ['direct','indirect']:
            for principle in summary[kind]:assertions.append(dict(id=f'S-{number:02}-{kind}-{principle}',area_id=summary['id'],source_layer='segment_summary',source=summary['source'],contribution_type=kind.title(),principle=principle,aggregate=number==0))
        header=None; n=0
        for ln,cells in rs:
            if len(cells)==12 and cells[0]=='Activities':header=cells;continue
            if header is None or len(cells)!=12:continue
            n+=1;aid=f'ACT-{number:02}-{n:03}';matches=[]
            for sheet,records in workbook.items():
                for record in records:
                    if norm(record['cells'].get('A',''))==norm(cells[0]):matches.append((sheet,record))
            # Use all twelve cells to disambiguate repeated labels across sheets.
            ranked=sorted(matches,key=lambda x:-sum(norm(x[1]['cells'].get(chr(65+j),''))==norm(cells[j]) for j in range(12)))
            if ranked:
                sheet,row=ranked[0];coord=f'{sheet}!A{row["row"]}:L{row["row"]}'
                diff=[{'column':chr(65+j),'markdown':cells[j],'workbook':row['cells'].get(chr(65+j),''),'comparison_class':'formatting' if re.sub(r'\W','',cells[j])==re.sub(r'\W','',row['cells'].get(chr(65+j),'')) else 'content'} for j in range(12) if norm(row['cells'].get(chr(65+j),''))!=norm(cells[j])]
                differences.extend(dict(activity_id=aid,coordinate=coord,**d) for d in diff)
                reconciled.append(dict(activity_id=aid,coordinate=coord,equal_columns=12-len(diff)))
            else:coord=None;differences.append(dict(activity_id=aid,issue='No exact activity-label match in workbook'))
            a=dict(id=aid,area_id=summary['id'],area=name,source=doc.as_uri()+f'#L{start+ln}',source_layer='activity_table',coordinate=coord,source_fields=dict(zip(header,cells)),activity=cells[0],deliverables=cells[1],responsible_roles=cells[2],approving_roles=cells[3],contributing_roles=cells[4],direct=cross.ids(cells[7]),indirect=cross.ids(cells[11]),rationale=cells[8],indirect_rationale=cells[9],source_evidence_test=cells[10],workbook_source=(RELEASE/'DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx').as_uri()+(f'#{coord}' if coord else ''))
            activities.append(a)
            if ranked:
                for kind,column in [('direct','H'),('indirect','L')]:
                    for principle in cross.ids(row['cells'].get(column,'')):
                        assertions.append(dict(id=f'WB-{aid}-{kind}-{principle}',activity_id=aid,area_id=a['area_id'],source_layer='workbook_activity_table',source=a['workbook_source'],coordinate=coord,contribution_type=kind.title(),principle=principle,rationale=row['cells'].get('I' if kind=='direct' else 'J',''),source_evidence_test=row['cells'].get('K',''),intermediate_practice=cross.VIA[principle] if kind=='indirect' else None))
            for kind in ['direct','indirect']:
                for principle in a[kind]:assertions.append(dict(id=f'{aid}-{kind}-{principle}',activity_id=aid,area_id=a['area_id'],source_layer='activity_table',source=a['source'],coordinate=coord,contribution_type=kind.title(),principle=principle,rationale=a['rationale'] if kind=='direct' else a['indirect_rationale'],source_evidence_test=a['source_evidence_test'],intermediate_practice=cross.VIA[principle] if kind=='indirect' else None))
    overview=[]
    overview_start=text.index('## DAMA Segments and FAIR Alignment')
    overview_text=text[overview_start:sections[0].start()]
    for ln,cells in cross.rows(overview_text):
        match=re.match(r'^(\d+)\. (.+)',cells[0])
        if len(cells)!=3 or not match:continue
        number=int(match[1]);source=doc.as_uri()+f'#L{text[:overview_start].count(chr(10))+ln}'
        row=dict(area_id=f'AREA-{number:02}',name=match[2],direct=cross.ids(cells[1]),indirect=cross.ids(cells[2]),source=source)
        overview.append(row)
        for kind in ['direct','indirect']:
            for principle in row[kind]:assertions.append(dict(id=f'OVERVIEW-{number:02}-{kind}-{principle}',area_id=row['area_id'],source_layer='catalogue_overview_summary',source=source,contribution_type=kind.title(),principle=principle))
    data['catalogue_overview']=overview
    pg=Graph().parse(package/'dama-persona-ontology.ttl',format='turtle');g=Graph().parse(package/'dama-fair-mapping.ttl',format='turtle')
    personas=[]
    for ln,c in cross.rows(text):
        if len(c)!=7 or c[0]=='Persona / source name':continue
        found=[p for p,label in pg.subject_objects(RDFS.label) if str(label)==c[0]]
        found=[p for p in found if (p,RDF.type,cross.PERSONA.Persona) in pg];assert len(found)==1,c[0]
        personas.append(dict(id=cross.slug(c[0]),name=c[0],description=c[1],supplier_in=[x.strip() for x in c[2].split(';') if x.strip()],participant_in=[x.strip() for x in c[3].split(';') if x.strip()],consumer_in=[x.strip() for x in c[4].split(';') if x.strip()],inherited_direct=cross.ids(c[5]),inherited_indirect=cross.ids(c[6]),source=doc.as_uri()+f'#L{ln}',source_iri=str(found[0])))
    duplicate_ids={key for key,count in Counter(p['id'] for p in personas).items() if count>1}
    for p in personas:
        if p['id'] in duplicate_ids:p['id']=p['source_iri'].rsplit('/',1)[-1]
    assert len({p['id'] for p in personas})==len(personas)
    names={p['name']:p for p in personas}
    corrs=copy.deepcopy(old['persona_correspondences'])
    for corr in corrs:
        for c in corr['candidates']:
            p=names[c['name']];c.update(dama_persona_id=p['id'],source=p['source'],source_iri=p['source_iri'],occurrence_categories={k:p[k] for k in ['supplier_in','participant_in','consumer_in']},inherited_direct=p['inherited_direct'],inherited_indirect=p['inherited_indirect'])
    # The new catalogue explicitly includes scientists, curators and platform roles.
    additions={'Data_Scientist':['Data Scientists'],'Curator':['Data Curators'],'Data_Engineer':['Ingestion Architects','Big Data Platform Architects'],'Data_Analyst':['Data Scientists'],'Data_Protection_Officer':['Data Governance Bodies'],'FAIR_Trainer':['Change Managers']}
    for corr in corrs:
        for name in additions.get(corr['fairmm_persona'],[]):
            p=names[name]
            if any(c['name']==name for c in corr['candidates']):continue
            corr['candidates'].append(dict(dama_persona_id=p['id'],name=name,source=p['source'],source_iri=p['source_iri'],occurrence_categories={k:p[k] for k in ['supplier_in','participant_in','consumer_in']},relationship='related counterpart; no equivalence asserted' if corr['confidence']=='Gap' else 'proposed functional correspondence; activity-specific scope required',inherited_direct=p['inherited_direct'],inherited_indirect=p['inherited_indirect']))
        if corr['fairmm_persona']=='Data_Scientist':corr.update(confidence='Close',qualification='Close; new source explicitly names Data Scientists; P C',rationale='Big Data & Data Science explicitly assigns hypotheses, analytical methods, exploration and communication to Data Scientists. FAIR-specific competence remains conditional.')
    for kind in ['Direct','Indirect']:
        for node in sorted(g.subjects(RDF.type,cross.MAP[kind+'Contribution']),key=str):
            p=g.value(node,cross.MAP.fromPractice)
            assertions.append(dict(id='ONT-'+str(node).split('#')[-1],source_layer='ontology_contribution',source=(package/'dama-fair-mapping.ttl').as_uri(),source_node=str(node),contribution_type=kind,principle=str(g.value(node,cross.MAP.targetsPrinciple)).split('/')[-1],practice=str(p),practice_label=str(g.value(p,RDFS.label)),intermediate_practice=str(g.value(node,cross.MAP.viaPractice)) if kind=='Indirect' else None,rationale=str(g.value(node,cross.MAP.rationale)),condition=str(g.value(node,cross.MAP.applicabilityCondition) or '')))
    for node in sorted(g.subjects(RDF.type,cross.MAP.AreaAlignmentAssessment),key=str):
        assertions.append(dict(id='ONT-AREA-'+str(node).split('#')[-1],source_layer='ontology_area_assessment',source=(package/'dama-fair-mapping.ttl').as_uri(),source_node=str(node),contribution_type=str(g.value(node,cross.MAP.alignmentType)),principle=str(g.value(node,cross.MAP.alignedPrinciple)).split('/')[-1],rationale=str(g.value(node,cross.MAP.rationale) or ''),condition='Area-level proposal retained separately from activity and summary classifications.'))
    area_topics={1:'DataGovernance',2:'DataArchitecture',3:'DataModelingAndDesign',4:'DataStorageAndOperations',5:'DataSecurity',6:'ReferenceAndMasterDataManagement',7:'DataWarehousingAndBusinessIntelligence',8:'DocumentsAndContentManagement',9:'MetadataManagement',10:'DataQualityManagement',11:'DataIntegrationAndInteroperability',12:'DataManagementMaturityAssessment',13:'BigDataAndDataScience',14:'DataHandlingEthics'}
    for a in assertions:
        if not a.get('source_node'):continue
        node=__import__('rdflib').URIRef(a['source_node'])
        topic=g.value(node,cross.MAP.fromTopic)
        if topic is None:
            practice=g.value(node,cross.MAP.fromPractice)
            if practice is not None:topic=g.value(practice,cross.MAP.inTopic) or g.value(practice,cross.MAP.inKnowledgeArea)
        if topic is not None:
            matches=[number for number,local in area_topics.items() if str(topic).endswith('#'+local)]
            if matches:a['area_id']=f'AREA-{matches[0]:02}'
        a['source_fields']={str(p):[str(o) for o in g.objects(node,p)] for p in sorted(set(g.predicates(node)),key=str)}
    data.update(schema_version='1.1.0',execution_date='2026-11-16',summaries=summaries,activities=activities,assertions=assertions,dama_personas=personas,persona_correspondences=corrs)
    # Source-specific organisational proposals do not manufacture FAIR principle IDs.
    cross.ORG_TARGETS.update({'ACT-13-001':['D3','D5'],'ACT-13-002':['D7'],'ACT-14-002':['D5'],'ACT-14-003':['D3','D5'],'ACT-14-004':['D6'],'ACT-14-005':['D6'],'ACT-14-006':['D5'],'ACT-14-007':['D5']})
    candidates=cross.align(activities,assertions,corrs,data['descriptors'])
    data['alignments']=[a for a in candidates if a['descriptor_support']]
    data['unresolved_descriptor_candidates']=[a for a in candidates if not a['descriptor_support']]
    from build_fairmm_ontology import git_revision
    inputs={p.as_uri():digest(p) for p in RELEASE.rglob('*') if p.is_file()}
    inputs.update({u:h for u,h in old['sources']['input_sha256'].items() if 'Pistoia-Alliance-Inc' in u})
    data['sources'].update(fair_dama_revision=git_revision(ROOT.parent/'FAIR-DAMA'),input_sha256=inputs,dama_source_release='DAMA ontologies v1.1.0 / document v1.18.0 / workbook V3 (2026-11-16)',ontology_directory=str(package.relative_to(ROOT)).replace('\\','/'),source_authority='User-supplied local release; FAIR-DAMA checkout revision is context only, not provenance for the supplied release.')
    data['reconciliation']={'policy':'Markdown source wording, workbook cells, ontology contributions and ontology area proposals retained separately; differences reported, not silently reconciled. Markdown activity rows drive proposed FAIRMM dimensions; workbook assertions are independently retained for comparison.','workbook_matched_activities':len(reconciled),'workbook_differences':differences,'historical_visualisation':'61 earlier v1.2.0 records retained in the historical corpus, superseded for this release by 74 explicitly separate ontology area assessments.'}
    write(ROOT/'artefacts/fairmm-crosswalk.json',data);write(ROOT/'docs/fairmm/data/crosswalk.json',data);write(ROOT/'results/executed/fairmm-crosswalk.json',data)
    write(RELEASE/'workbook-extract.json',workbook)
    report=dict(source_release=data['sources']['dama_source_release'],input_sha256=inputs,counts={k:len(data[k]) for k in ['summaries','activities','assertions','dama_personas','persona_correspondences','descriptors','alignments']},source_layers=dict(Counter(a['source_layer'] for a in assertions)),workbook_matches=reconciled,workbook_differences=differences,previous_counts={k:len(old[k]) for k in ['summaries','activities','assertions','dama_personas','alignments']})
    write(ROOT/'results/source-refresh-2026-11-16.json',report)
    from html import escape
    html=['<!doctype html><html lang="en"><meta charset="utf-8"><title>DAMA source release v1.18.0</title><style>body{font:16px/1.6 system-ui;max-width:1200px;margin:40px auto;padding:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{border-bottom:1px solid #aaa}</style><h1>DAMA source release v1.18.0</h1><p>Chris Day, 16 November 2026. DAMA source images copyright DAMA International. Source wording reproduced for this documentary crosswalk.</p>']
    html.append('<pre>')
    for n,line in enumerate(lines,1):
        heading=re.match(r'^## (\d+)\. ',line)
        if heading:html.append(f'<span id="section-{heading[1]}"></span>')
        html.append(f'<span id="L{n}">{escape(line)}</span>')
    html.append('</pre>')
    html.append('</html>')
    for p in [ROOT/'docs/source-release.html',ROOT/'results/source-release.html']:cross.save(p,'\n'.join(html))
    # Regenerate source-facing pages, then replace the old Git-only source claim.
    cross.pages(data,ROOT/'artefacts/FAIR_DAMA_FAIRMM_Proposed_Alignment_Plan.md',ROOT/'docs/fairmm')
    for p in (ROOT/'docs/fairmm').glob('*.md'):
        s=cross.read(p);s=s.replace(f'The baseline is FAIR–DAMA `{cross.DAMA_SHA[:12]}`', 'The DAMA source is the supplied ontology v1.1.0, document v1.18.0 and workbook V3 release (16 November 2026)')
        cross.save(p,s)
    print(json.dumps({k:v for k,v in report.items() if k in ['counts','source_layers','previous_counts']},indent=2))

if __name__=='__main__':main()
