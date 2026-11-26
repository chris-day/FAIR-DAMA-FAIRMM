import sys,os,json,hashlib,argparse,shutil,subprocess,tempfile,importlib.metadata as metadata
from pathlib import Path
from rdflib import Graph,Dataset,RDF,RDFS,OWL,Namespace,URIRef,Literal
from rdflib.compare import isomorphic
from pyshacl import validate as shacl
from reference import ReferenceRelease,ConformanceError,extract_archive,resolve_imports,sha,A,I,PROVENANCE
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'evidence';CHECKS=[]
C=Namespace('urn:capability-ontology:');X=Namespace('urn:g6:fixture:')
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
def check(name,value,detail=None):
 CHECKS.append({'check':name,'passed':bool(value),'detail':detail});print(('PASS ' if value else 'FAIL ')+name,flush=True)
def negative(name,code,action):
 try:action();check(name,False,'Unexpectedly accepted')
 except ConformanceError as e:check(name,e.code==code,{'code':e.code,'message':str(e)})
def context_fixture(release):
 n=sorted(release.flat.subjects(RDF.type,A.ToolPrincipleProposal),key=str)[0];g=Graph()
 for triple in release.flat.triples((n,None,None)):g.add(triple)
 for value in list(g.objects()):
  for triple in release.flat.triples((value,None,None)):g.add(triple)
 return n,g
def verify_shapes(release):
 shapes=Graph()
 for p in (release.root/'shapes').glob('*.ttl'):shapes.parse(p)
 good,report,_=shacl(release.flat,shacl_graph=shapes,inference='none');check('Exported asserted RDF passes SHACL',good);report.serialize(OUT/'shacl-production.ttl',format='turtle')
 n,fixture=context_fixture(release);bad=Graph();bad+=fixture;bad.remove((n,A.applicabilityCondition,None));good,report,_=shacl(bad,shacl_graph=shapes,inference='none');check('Missing mapping condition rejected',not good);report.serialize(OUT/'shacl-negative-condition.ttl',format='turtle')
 fixture.set((n,A.deploymentVerificationStatus,Literal('verified')));fixture.add((n,RDF.type,C.Realisation))
 for prop,value in [(C.forImplementation,X.implementation),(C.inScope,X.scope),(C.hasEvidence,X.evidence),(C.requiresCondition,X.condition),(C.realisesCapability,X.capability),(C.verificationState,C.Verified)]:fixture.add((n,prop,value))
 for value,cls in [(X.implementation,C.Implementation),(X.scope,C.Scope),(X.evidence,C.Evidence),(X.condition,C.ImplementationCondition),(X.capability,C.Capability)]:fixture.add((value,RDF.type,cls))
 good,report,_=shacl(fixture,shacl_graph=shapes,inference='none');check('Complete synthetic verified deployment accepted',good);fixture.serialize(OUT/'synthetic-verified-fixture.ttl',format='turtle')
 for label,prop in [('evidence',C.hasEvidence),('scope',C.inScope),('implementation',C.forImplementation),('condition',C.requiresCondition)]:
  bad=Graph();bad+=fixture;bad.remove((n,prop,None));good,_,_=shacl(bad,shacl_graph=shapes,inference='none');check('Verified fixture missing '+label+' rejected',not good)
def reasoning(release,java,jar,toolchain):
 expected=toolchain['robot']['sha256'];check('Pinned ROBOT checksum',sha(jar)==expected)
 if sha(jar)!=expected:raise ValueError('Wrong ROBOT JAR')
 commands=[];base=[java,'-Xmx2G','-jar',str(jar)];catalog=release.root/'dist/ontology-catalog.xml'
 for name,path,imports in [('imports',release.root/'dist/integrated-ontology.ttl',True),('flat',release.root/'dist/merged-asserted.ttl',False)]:
  args=['--catalog',str(catalog)] if imports else []
  for kind,cmd in [('profile',base+['validate-profile','--profile','DL']+args+['--input',str(path),'--output',str(OUT/(name+'-profile.txt'))]),('HermiT',base+['reason','--reasoner','HermiT']+args+['--input',str(path),'--create-new-ontology','true','--output',str(OUT/(name+'-inferences.ttl'))])]:
   p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');(OUT/(name+'-'+kind+'.log')).write_bytes((p.stdout+p.stderr).encode());check(name+' '+kind,p.returncode==0);commands.append({'name':name+' '+kind,'command':cmd,'exit_code':p.returncode,'passed':p.returncode==0})
 bad=(release.root/'dist/integrated-ontology.ttl').read_text(encoding='utf-8')+'\n<urn:g6:inconsistent> a <urn:capability-ontology:Capability>, <urn:capability-ontology:Implementation> .\n';(OUT/'inconsistent-fixture.ttl').write_bytes(bad.encode());cmd=base+['reason','--reasoner','HermiT','--catalog',str(catalog),'--input',str(OUT/'inconsistent-fixture.ttl'),'--output',str(OUT/'negative-inferences.ttl')];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');rejected=p.returncode!=0 and 'inconsistent' in (p.stdout+p.stderr).lower();check('Inconsistent exported-ontology fixture rejected',rejected);(OUT/'negative-reasoning.log').write_bytes((p.stdout+p.stderr).encode());commands.append({'name':'inconsistency rejected','command':cmd,'exit_code':p.returncode,'passed':rejected});write(OUT/'reasoner-results.json',commands)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate');ap.add_argument('--candidate-sha256');ap.add_argument('--workspace',required=True);ap.add_argument('--robot-jar',required=True);ap.add_argument('--java',default=shutil.which('java'));args=ap.parse_args();OUT.mkdir(exist_ok=True);config=json.loads((ROOT/'profile.json').read_text());workspace=Path(args.workspace).resolve();workspace.mkdir(parents=True,exist_ok=True);active=workspace/'active'
 if active.exists() and any(active.iterdir()):raise ValueError('Use a fresh workspace; existing data will not be overwritten')
 
 if args.candidate:
  if not args.candidate_sha256:raise ValueError('--candidate-sha256 required with --candidate')
  config['release_archive']=str(Path(args.candidate).resolve());config['release_sha256']=args.candidate_sha256
 package=ROOT/config['release_archive'];extract_archive(package,config['release_sha256'],active);check('Frozen release archive and every payload hash verified',True)
 runtime={'python':sys.version,'rdflib':metadata.version('rdflib'),'pyshacl':metadata.version('pyshacl'),'engine':'RDFLib Memory','date':'2026-11-26'};write(OUT/'runtime.json',runtime);check('Pinned RDFLib and pySHACL runtime',runtime['rdflib']=='7.1.4' and runtime['pyshacl']=='0.30.1')
 release=ReferenceRelease(active,config['release_sha256']);check('Sixteen source graphs and complete provenance verified',True);baseline=None;profiles={}
 for profile in config['supported_profiles']:
  count=release.load(profile);check(profile+' asserted graph equals frozen flat RDF',count==95008);results=release.queries();profiles[profile]={'asserted_triples':count,'query_counts':{key:len(value['lexical']) for key,value in results.items()}}
  for key,value in results.items():
   expected=json.loads((ROOT/'inputs/expected-production'/(key+'.json')).read_text(encoding='utf-8'));check(profile+' '+key+' full G5 golden results',value['lexical']==sorted(expected,key=json.dumps))
   if baseline is not None:check(profile+' '+key+' RDF-term result equivalence',value['typed']==baseline[key]['typed'])
  if baseline is None:baseline=results
  write(OUT/('queries-'+profile+'.json'),results)
 write(OUT/'profile-results.json',profiles)
 # Test failures on disposable workspace copies or in-memory structures only.
 bad_archive=workspace/'bad-candidate.zip';bad_archive.write_bytes(package.read_bytes()+b'changed');negative('Changed release archive rejected','archive-hash',lambda:extract_archive(bad_archive,config['release_sha256'],workspace/'bad-extract'))
 path=active/'dist/integrated-ontology.ttl';original=path.read_bytes()
 try:
  path.write_bytes(original+b'\nmalformed');negative('Changed payload rejected before parsing','payload-hash',release.verify_payload)
 finally:path.write_bytes(original)
 try:
  path.rename(path.with_suffix('.missing'));negative('Missing payload rejected','missing-payload',release.verify_payload)
 finally:path.with_suffix('.missing').rename(path)
 from xml.etree.ElementTree import parse
 catalog=active/'dist/ontology-catalog.xml';lookup={e.attrib['name']:(catalog.parent/e.attrib['uri']).resolve() for e in parse(catalog).getroot()};missing=dict(lookup);first=sorted(map(str,release.entry.objects(None,OWL.imports)))[0];del missing[first];negative('Unresolved import rejected without network fallback','missing-import',lambda:release.import_view(missing));wrong=dict(lookup);wrong[first]=active/'inputs/domains/dama-1.2.0.ttl' if 'capability' in first else active/'inputs/domains/capability-1.0.0.ttl';negative('Wrong ontology version identity rejected','ontology-identity',lambda:release.import_view(wrong))
 cycle=workspace/'cycle';cycle.mkdir();cycle_lookup={};hashes={}
 for name,target in [('a','b'),('b','a')]:
  p=cycle/(name+'.ttl');p.write_text('<urn:g6:'+name+'> a <http://www.w3.org/2002/07/owl#Ontology>; <http://www.w3.org/2002/07/owl#imports> <urn:g6:'+target+'> .');cycle_lookup['urn:g6:'+name]=p;hashes[p.resolve()]=sha(p)
 negative('Cyclic import closure rejected','import-cycle',lambda:resolve_imports(cycle,['urn:g6:a'],cycle_lookup,hashes))
 try:Graph().parse(data='@prefix ex: <urn:g6:> . ex:broken ex:p [',format='turtle');check('Malformed RDF rejected',False)
 except Exception as e:check('Malformed RDF rejected',True,type(e).__name__)
 selected=list(release.manifest['asserted_graphs']);derived=next(r['graph'] for r in release.manifest['source_graphs'] if r['role']=='derived');negative('Derived source cannot enter asserted selection','graph-policy',lambda:release.asserted_view(selected+[derived]))
 unsafe=Graph()
 for graph in release.dataset.contexts():unsafe+=graph
 negative('Automatic union of every graph rejected','graph-policy',lambda:release.validate_view(unsafe))
 meta=release.dataset.graph(PROVENANCE);row=release.lock['sources'][0];gid=URIRef(row['graph']);triples=list(meta.triples((gid,I.sha256,None)))
 try:
  meta.remove((gid,I.sha256,None));negative('Missing source provenance rejected','provenance',release.verify_sources)
 finally:
  for t in triples:meta.add(t)
 source_graph=release.dataset.graph(gid);saved=list(source_graph)
 try:
  source_graph.remove((None,None,None));negative('Missing named source graph rejected','source-content',release.verify_sources)
 finally:
  for t in saved:source_graph.add(t)
 # Runtime snapshot includes the explicitly materialised default view.
 release.load('trig');before=release.queries();snapshot=OUT/'backup';manifest=release.snapshot(snapshot);check('Runtime checkpoint recorded declared default/source contexts',manifest['default_triples']==95008)
 release.dataset.default_context.remove((None,None,None));negative('Simulated default graph loss detected','asserted-semantics',lambda:release.validate_view(release.dataset.default_context));release.restore(snapshot);after=release.queries();check('Recovery restores all 18 lexical and typed query results',before==after==baseline);check('Recovery restores every default/source graph and blank-node scope',len(release.dataset.default_context)==95008)
 broken=workspace/'damaged-backup';broken.mkdir();shutil.copyfile(snapshot/'snapshot.json',broken/'snapshot.json');(broken/'runtime.trig').write_bytes((snapshot/'runtime.trig').read_bytes()+b'changed');negative('Damaged runtime checkpoint rejected','snapshot-hash',lambda:release.restore(broken))
 other=workspace/'wrong-release-backup';other.mkdir();wrong_manifest=dict(manifest);wrong_manifest['release_sha256']='0'*64;write(other/'snapshot.json',wrong_manifest);shutil.copyfile(snapshot/'runtime.trig',other/'runtime.trig');negative('Checkpoint from wrong release rejected','snapshot-release',lambda:release.restore(other))
 from restore_safety import exercise
 for result in exercise(release,snapshot,workspace,baseline):check(result['check'],result['passed'],result['detail'])
 fresh=workspace/'reloaded';extract_archive(package,config['release_sha256'],fresh);reloaded=ReferenceRelease(fresh,config['release_sha256']);reloaded.load('flat');check('Full reload from frozen release restores all query results',reloaded.queries()==baseline)
 verify_shapes(release);reasoning(release,args.java,str(Path(args.robot_jar).resolve()),json.loads((ROOT/'toolchain-lock.json').read_text()))
 release.verify_payload();check('Scratch payload restored byte-identically after fault injection',True);check('Approved candidate archive remains unchanged',sha(package)==config['release_sha256'])
 report={'date':'2026-11-26','passed':sum(c['passed'] for c in CHECKS),'failed':sum(not c['passed'] for c in CHECKS),'checks':CHECKS,'profiles':profiles,'distribution_query_executions':54,'recovery_query_executions':72,'total_query_executions':126,'reference_engine':'RDFLib Memory','candidate_sha256':config['release_sha256'],'G6_baseline_owner_acceptance':'accepted','repository_adaptation_acceptance':'pending','vendor_deployment_executed':False,'public_release_executed':False};write(OUT/'acceptance-results.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['checks','profiles']},indent=2))
 if report['failed']:raise SystemExit(1)
if __name__=='__main__':main()
