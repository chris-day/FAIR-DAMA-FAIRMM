import sys,json,hashlib,subprocess,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
from rdflib import Graph,Dataset,RDF,RDFS,OWL,URIRef,Literal,Namespace
from rdflib.compare import isomorphic
from pyshacl import validate as shacl
from build import I,A,C,D,F,DC,PROV,PROVENANCE,ONTO,verify_pins,resolver,resolve_closure
OUT=ROOT/'validation';OUT.mkdir(exist_ok=True);checks=[]
def check(label,value,detail=None):checks.append({'check':label,'passed':bool(value),'detail':detail});print(('PASS ' if value else 'FAIL ')+label,flush=True)
def rejected(label,fn):
 try:fn();check(label,False,'Unexpectedly accepted')
 except ValueError as error:check(label,True,str(error))
def rows(result):return sorted([[str(v) if v is not None else None for v in row] for row in result],key=lambda row:json.dumps(row))
def query_view(dataset,manifest):
 view=Dataset()
 for gid in manifest['asserted_graphs']:
  for triple in dataset.graph(URIRef(gid)):view.default_context.add(triple)
 for row in manifest['source_graphs']:
  for triple in dataset.graph(URIRef(row['graph'])):view.graph(URIRef(row['graph'])).add(triple)
 for triple in dataset.graph(PROVENANCE):view.graph(PROVENANCE).add(triple)
 return view
verify_pins();check('All pinned inputs match',True)
manifest=json.loads((ROOT/'dist/merge-manifest.jsonld').read_text());lock=json.loads((ROOT/'dist/ontology-lock.json').read_text());dataset=Dataset();dataset.parse(ROOT/'dist/merged.trig',format='trig');flat=Graph().parse(ROOT/'dist/merged-asserted.ttl');entry=Graph().parse(ROOT/'dist/integrated-ontology.ttl')
check('TriG default graph empty',len(dataset.default_context)==0)
expected=Graph()
for gid in manifest['asserted_graphs']:
 for triple in dataset.graph(URIRef(gid)):
  if triple[1]!=OWL.imports:expected.add(triple)
for triple in entry:
 if triple[1]!=OWL.imports:expected.add(triple)
check('Flat equals asserted source union after declared import removal',isomorphic(flat,expected))
check('No remaining imports in self-contained flat graph',not list(flat.triples((None,OWL.imports,None))))
check('All source ontology declarations preserved',set(expected.subjects(RDF.type,OWL.Ontology))==set(flat.subjects(RDF.type,OWL.Ontology)))
check('No cumulative associations in asserted output',not list(flat.subjects(RDF.type,A.CumulativeAssociation)))
check('No fixture identifiers in asserted output',not any(str(term).startswith('urn:g4-fixture:') for triple in flat for term in triple))
check('No verified deployment claims in production',not list(flat.subjects(A.deploymentVerificationStatus,Literal('verified'))) and not list(flat.subjects(C.verificationState,C.Verified)))
for source in lock['sources']:
 p=ROOT/source['local_path'];g=Graph().parse(p);stored=dataset.graph(URIRef(source['graph']));check('Source round-trip '+source['local_path'],isomorphic(g,stored));check('Locked source hash '+source['local_path'],hashlib.sha256(p.read_bytes()).hexdigest()==source['SHA-256'])
 meta=dataset.graph(PROVENANCE);gid=URIRef(source['graph']);check('Explicit provenance '+source['local_path'],(gid,I.sha256,Literal(source['SHA-256'])) in meta and (gid,PROV.wasDerivedFrom,URIRef(source['source_uri'])) in meta and (gid,I.lockPath,Literal(source['local_path'])) in meta)
lookup=resolver();rejected('Unresolved import rejected',lambda:resolve_closure(['urn:g4:missing'],lookup));rejected('Wrong identity rejected',lambda:resolve_closure(['urn:g4:wrong'],{'urn:g4:wrong':ROOT/'inputs/domains/capability-1.0.0.ttl'}))
with tempfile.TemporaryDirectory(dir=OUT) as tmp:
 t=Path(tmp);p=t/'p.ttl';p.write_text('tampered');(t/'source-pins.json').write_text(json.dumps([{'path':'p.ttl','sha256':'0'*64}]))
 rejected('Wrong checksum rejected',lambda:verify_pins(t));p.unlink();rejected('Missing pinned file rejected',lambda:verify_pins(t))
 for n,other in [('a','b'),('b','a')]:
  (t/(n+'.ttl')).write_text('<urn:g4:'+n+'> a <http://www.w3.org/2002/07/owl#Ontology>; <http://www.w3.org/2002/07/owl#imports> <urn:g4:'+other+'> .')
 rejected('Import cycle rejected',lambda:resolve_closure(['urn:g4:a'],{'urn:g4:a':t/'a.ttl','urn:g4:b':t/'b.ttl'}))
# A deterministic rebuild must preserve both distributions and the metadata manifest.
before=(ROOT/'dist/merge-manifest.jsonld').read_bytes();before_dataset=dataset
subprocess.run([sys.executable,str(ROOT/'build.py')],check=True,capture_output=True)
again=Dataset();again.parse(ROOT/'dist/merged.trig',format='trig');check('Repeated asserted build equivalent',isomorphic(flat,Graph().parse(ROOT/'dist/merged-asserted.ttl')));check('Manifest reproducible',before==(ROOT/'dist/merge-manifest.jsonld').read_bytes())
check('Dataset graph identities reproducible',{str(g.identifier) for g in dataset.contexts()}=={str(g.identifier) for g in again.contexts()})
for gid in [r['graph'] for r in manifest['source_graphs']]+[str(PROVENANCE)]:check('Dataset graph content reproducible '+gid,isomorphic(dataset.graph(URIRef(gid)),again.graph(URIRef(gid))))
# Run all queries against a deliberately selected asserted-default view.
view=query_view(dataset,manifest);fixture_spec=json.loads((ROOT/'fixtures/expected-results.json').read_text());cq=[]
for name,spec in fixture_spec.items():
 query=(ROOT/'queries'/(name+'.rq')).read_text(encoding='utf-8');production=rows(view.query(query));(OUT/(name+'-production.json')).write_text(json.dumps(production,indent=2),encoding='utf-8');cases=[]
 for case,s in spec['cases'].items():
  test=Dataset();facts=Graph().parse(ROOT/'fixtures'/s['file'])
  for triple in facts:test.default_context.add(triple)
  positive=case=='positive'
  if spec.get('fixture_named_source') and case!='empty':
   gid=URIRef('urn:g4-fixture:source-graph')
   for triple in facts:test.graph(gid).add(triple)
   if positive:test.graph(PROVENANCE).add((gid,I.sha256,Literal('fixture-hash')));test.graph(PROVENANCE).add((gid,I.role,Literal('asserted')))
  if spec.get('fixture_provenance') and case!='empty':
   gid=URIRef('urn:g4-fixture:source-graph');pg=test.graph(PROVENANCE);pg.add((gid,PROV.wasDerivedFrom,URIRef('urn:g4-fixture:source')));pg.add((gid,I.lockPath,Literal('fixture.ttl')));pg.add((gid,I.role,Literal('asserted')))
   if positive:pg.add((gid,I.sha256,Literal('fixture-hash')))
  actual=rows(test.query(query));wanted=sorted(s['expected'],key=lambda row:json.dumps(row));ok=actual==wanted;check(name+' fixture '+case,ok,{'actual':actual,'expected':wanted} if not ok else None);cases.append({'case':case,'passed':ok,'expected':wanted,'actual':actual})
 if spec.get('baseline_identity_check'):check('CQ16 deletion detected against baseline fixture',spec['cases']['positive']['expected']!=spec['cases']['negative']['expected'])
 cq.append({'id':name,'production_rows':len(production),'cases':cases,'empty_result_interpretation':'No source-qualified relationship is recorded; absence is not proof of impossibility.' if not production else None})
original_personas=next((ROOT/'inputs/originals').rglob('dama-persona-ontology.ttl'));pg=Graph().parse(original_personas);P=Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl#');baseline=set(map(str,pg.subjects(RDF.type,P.Persona)));actual={row[0] for row in json.loads((OUT/'CQ16-production.json').read_text())};check('CQ16 all 123 baseline persona IRIs retained',baseline==actual and len(actual)==123)
check('CQ17 every source graph has complete provenance',len(json.loads((OUT/'CQ17-production.json').read_text()))==len(lock['sources'])==16)
check('CQ01 production direct F4 baseline is five',next(r for r in cq if r['id']=='CQ01')['production_rows']==5)
check('CQ18 no source verified combination',next(r for r in cq if r['id']=='CQ18')['production_rows']==0)
(OUT/'competency-results.json').write_text(json.dumps(cq,indent=2),encoding='utf-8')
# Integrated constraints, with fixtures outside production outputs.
shapes=Graph()
for p in (ROOT/'shapes').glob('*.ttl'):shapes.parse(p)
ok,report,_=shacl(flat,shacl_graph=shapes,inference='none');check('Integrated asserted SHACL positive',ok);report.serialize(OUT/'integrated-shacl.ttl',format='turtle')
n=next(flat.subjects(RDF.type,A.ToolPrincipleProposal));small=Graph()
for triple in flat.triples((n,None,None)):small.add(triple)
for value in list(small.objects()):
 for triple in flat.triples((value,None,None)):small.add(triple)
small.remove((n,A.applicabilityCondition,None));ok,report,_=shacl(small,shacl_graph=shapes,inference='none');check('Integrated missing condition rejected',not ok);report.serialize(OUT/'negative-condition-shacl.ttl',format='turtle')
verified=Graph();verified+=small
for triple in flat.triples((n,A.applicabilityCondition,None)):verified.add(triple)
X=Namespace('urn:g4-fixture:');verified.set((n,A.deploymentVerificationStatus,Literal('verified')));verified.add((n,RDF.type,C.Realisation))
for prop,value in [(C.forImplementation,X.implementation),(C.inScope,X.scope),(C.hasEvidence,X.evidence),(C.requiresCondition,X.condition),(C.realisesCapability,X.capability),(C.verificationState,C.Verified)]:verified.add((n,prop,value))
for value,cls in [(X.implementation,C.Implementation),(X.scope,C.Scope),(X.evidence,C.Evidence),(X.condition,C.ImplementationCondition),(X.capability,C.Capability)]:verified.add((value,RDF.type,cls))
ok,report,_=shacl(verified,shacl_graph=shapes,inference='none');check('Synthetic verified deployment with full evidence/context accepted',ok);verified.serialize(OUT/'synthetic-verified-fixture.ttl',format='turtle')
for label,prop in [('actual evidence',C.hasEvidence),('implementation context',C.forImplementation),('implementation condition',C.requiresCondition)]:
 invalid=Graph();invalid+=verified;invalid.remove((n,prop,None));ok,_,_=shacl(invalid,shacl_graph=shapes,inference='none');check('Synthetic verified fixture missing '+label+' rejected',not ok)
record={'passed':sum(r['passed'] for r in checks),'failed':sum(not r['passed'] for r in checks),'checks':checks,'asserted_triples':len(flat),'source_graphs':len(lock['sources']),'CQs':len(cq),'dataset_policy':'Explicit asserted union, never automatic union of archival/derived/provenance graphs.'}
(OUT/'distribution-tests.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in record.items() if k!='checks'},indent=2))
if record['failed']:raise SystemExit(1)
if __name__=='__main__':pass
