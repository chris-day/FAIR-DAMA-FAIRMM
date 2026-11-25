"""Independent RDF/query round-trip, projection and delivery checks for five views."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,struct,subprocess,tempfile
import xml.etree.ElementTree as ET
from rdflib import Graph,RDF
from fairmm_rdf import ROOT,A,write

OUT=ROOT/'results/high-level-connections'
def main():
    manifest=json.loads((OUT/'build-manifest.json').read_text(encoding='utf-8'))
    graph=Graph();checks=[]
    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    for rel,sha in manifest['input_modules'].items():
        path=ROOT/rel;check('Unchanged ontology '+rel,hashlib.sha256(path.read_bytes()).hexdigest()==sha);graph.parse(path,format='turtle')
    document=(ROOT/'artefacts/FAIR_DAMA_FAIRMM_High_Level_Connections_v1.0.0.md').read_text(encoding='utf-8')
    check('Exactly five SPARQL subsections',document.count('### SPARQL — Sankey extraction')==5)
    check('Versioned release is identical',(ROOT/'artefacts/FAIR_DAMA_FAIRMM_High_Level_Connections_v1.1.0.md').read_text(encoding='utf-8')==document)
    sizes={}
    for view in manifest['views']:
        key=view['key'];folder=OUT/key;prefix='high-level-'+key+'-sankey'
        data=json.loads((folder/(prefix+'.json')).read_text(encoding='utf-8'))
        query=(folder/'query.rq').read_text(encoding='utf-8')
        check('Exact query embedded '+key,query in document)
        actual=[{str(k):str(v) for k,v in r.asdict().items()} for r in graph.query(query)]
        check('SPARQL result fidelity '+key,actual==data['extracted_rows']==json.loads((folder/'extracted-rows.json').read_text(encoding='utf-8')))
        check('Query digest '+key,hashlib.sha256(query.encode()).hexdigest()==data['query_sha256'])
        check('Source resource nodes exist '+key,all((__import__('rdflib').URIRef(n['id']),None,None) in graph for n in data['nodes']))
        ni={n['id']:n for n in data['nodes']};incoming=Counter();outgoing=Counter()
        for link in data['links']:
            check('Positive forward edge '+key+' '+link['id'],link['value']>0 and ni[link['source']]['column']<ni[link['target']]['column'])
            check('Exact evidence rows on edge '+key+' '+link['id'],all(r in actual for r in link['records']))
            incoming[link['target']]+=link['value'];outgoing[link['source']]+=link['value']
        check('Intermediate flow conserved '+key,all(abs(incoming[n['id']]-outgoing[n['id']])<1e-8 for n in data['nodes'] if 0<n['column']<data['columns']-1))
        check('Unique graph links '+key,len({(l['source'],l['target'],l['kind']) for l in data['links']})==len(data['links']))
        xml=ET.parse(folder/(prefix+'.svg'))
        check('One SVG path per graph edge '+key,len(xml.findall('.//{http://www.w3.org/2000/svg}path[@data-link]'))==len(data['links']))
        check('PNG dimensions '+key,struct.unpack('>II',(folder/(prefix+'.png')).read_bytes()[16:24])==(data['width'],data['height']))
        for file in folder.iterdir():
            if file.suffix in ['.svg','.png','.html','.json','.rq'] and file.name!='index.html':
                check('Identical documentation copy '+key+'/'+file.name,file.read_bytes()==(ROOT/'docs/high-level-connections'/key/file.name).read_bytes())
        html=(folder/(prefix+'.html')).read_text(encoding='utf-8')
        check('Selector-free '+key,'<select' not in html)
        landing=(folder/'index.html').read_text(encoding='utf-8')
        check('On-demand iframe '+key,'Load interactive diagram' in landing and not re.search(r'<iframe[^>]*\bsrc=',landing))
        scripts=re.findall(r'<script>(.*?)</script>',html,re.S)
        with tempfile.TemporaryDirectory(prefix='fairmm-js-') as tmp:
            for i,script in enumerate(scripts):
                p=Path(tmp)/f'view-{i}.js';p.write_text(script,encoding='utf-8')
                result=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
                check('JavaScript syntax '+key+' '+str(i),result.returncode==0)
        sizes[key]=dict(nodes=len(data['nodes']),links=len(data['links']),rows=len(actual))
        if key=='dama-fair-principles':check('Principle view retains only activity source layer',all((__import__('rdflib').URIRef(r['assertion']),A.sourceLayer,__import__('rdflib').Literal('activity_table')) in graph for r in actual))
        if key=='dama-fairmm-dimensions':check('All assigned dimension assertions represented',{r['assertion'] for r in actual}=={str(n) for n in graph.subjects(RDF.type,A.DimensionAlignment) if graph.value(n,A.sourceTopic) is not None})
        if key=='dimensions-levels':
            from rdflib import RDFS,URIRef
            check('All descriptor summaries extracted in SPARQL',all(r.get('descriptorComment')==str(graph.value(URIRef(r['descriptor']),RDFS.comment)) and r.get('descriptorComment') for r in actual))
            check('Node summaries equal ontology comments',all(n['comment']==str(graph.value(URIRef(n['id']),RDFS.comment)) for n in data['nodes'] if (URIRef(n['id']),RDF.type,A.Descriptor) in graph))
            check('Hover and focus handlers wired',all(token in html for token in ['showNode(d.id,e)','showNode(n.dataset.node,e)',"tooltip.setAttribute('role','tooltip')"]))
            check('Persistent selection shows comment',"if(n.comment){add('p',n.comment)" in html)
            check('All 42 descriptors represented',{r['descriptor'] for r in actual}=={str(n) for n in graph.subjects(RDF.type,A.Descriptor)} and len(actual)==42)
            check('Matrix has two legs per descriptor',len(data['links'])==2*len(actual))
        if key=='personas-activities-outcomes':
            occurrences={r['occurrence'] for r in actual}
            check('Role occurrences covered exactly',occurrences=={str(n) for n in graph.subjects(RDF.type,A.ActivityRoleOccurrence)})
            check('Role-occurrence input flow matches RDF',sum(l['value'] for l in data['links'] if ni[l['source']]['column']==0)==len(occurrences))
        if key=='dama-levels':
            check('No positive L0 alignment',not any(l['target']==str(A.L0) for l in data['links']))
            check('All cumulative associations retained',{r['association'] for r in actual}=={str(n) for n in graph.subjects(RDF.type,A.CumulativeAssociation)})
            check('Origin type preserved',all(str(graph.value(__import__('rdflib').URIRef(r['onset']),A.contributionType))==r['kind'] for r in actual))
    check('Built site includes all five views',all((ROOT/'site/high-level-connections'/v['key']/'index.html').exists() for v in manifest['views']))
    report=dict(status='passed',check_count=len(checks),checks=checks,views=sizes,browser_preview='Local file URL preview rejected by browser policy; no browser runtime interaction is claimed. JavaScript syntax, embedded offline controls, RDF round-trips, images and strict site build checked.')
    write(OUT/'validation.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','check_count','views']},indent=2))

if __name__=='__main__':main()
