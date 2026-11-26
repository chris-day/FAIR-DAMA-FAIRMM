"""One fail-closed local/CI entrypoint. Assemble review artefacts; never publish or deploy."""
import sys,os,json,hashlib,shutil,subprocess,urllib.request,importlib.metadata as metadata,tempfile,zipfile,argparse
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rdflib import Graph,Dataset,RDF,OWL,RDFS,XSD,URIRef
from rdflib.compare import isomorphic
import yaml
from package_candidate import build as package,revision
from build import verify_pins
CONFIG=json.loads((ROOT/'release-config.json').read_text());OUT=ROOT/'validation';COMMANDS=[]
def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def clean(path):
 path=path.resolve();assert path.is_relative_to(ROOT) and path!=ROOT
 if path.exists():shutil.rmtree(path)
def run(name,args,cwd=ROOT,expect_inconsistent=False):
 env=os.environ.copy();env.update({'PYTHONHASHSEED':'0','PYTHONUTF8':'1'});p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace');(OUT/(name+'.log')).write_bytes((p.stdout+p.stderr).encode('utf-8'));ok=p.returncode==0 if not expect_inconsistent else p.returncode!=0 and 'inconsistent' in (p.stdout+p.stderr).lower();COMMANDS.append({'stage':name,'command':list(map(str,args)),'exit_code':p.returncode,'passed':ok});write(OUT/'pipeline-commands.json',COMMANDS);print(name+': '+('passed' if ok else 'FAILED'),flush=True)
 if not ok:
  print(p.stdout+p.stderr,flush=True)
  raise RuntimeError(name+' failed; see validation/'+name+'.log')
def runtime(java):
 if sys.version.split()[0]!=CONFIG['python_version']:raise RuntimeError('Expected Python '+CONFIG['python_version'])
 deps={}
 for line in (ROOT/'requirements-validation.txt').read_text().splitlines():
  if not line.strip() or line.startswith('#'):continue
  name,wanted=line.split('==');actual=metadata.version(name)
  if actual!=wanted:raise RuntimeError('Locked dependency mismatch '+name+': '+actual+' != '+wanted)
  deps[name]=actual
 result=subprocess.run([java,'-version'],capture_output=True,text=True);version=result.stdout+result.stderr
 if result.returncode or '"'+CONFIG['java_version']+'"' not in version:raise RuntimeError('Java runtime does not match configured '+CONFIG['java_version'])
 write(OUT/'runtime.json',{'python':sys.version,'dependencies':deps,'java':version,'platform':sys.platform,'hosted_CI_executed':bool(os.environ.get('GITHUB_ACTIONS'))})
def robot_jar(provided):
 lock=json.loads((ROOT/'toolchain-lock.json').read_text());wanted=lock['robot']['sha256'];path=Path(provided).resolve() if provided else ROOT/'.tools/robot-1.9.11.jar'
 if not path.exists():
  if provided:raise FileNotFoundError(path)
  path.parent.mkdir(exist_ok=True);urllib.request.urlretrieve(lock['robot']['download'],path)
 if digest(path)!=wanted:raise RuntimeError('ROBOT checksum mismatch')
 return path
def workflow_checks():
 host=ROOT.parent/'.github/workflows/integrated.yml'
 if host.exists():assert host.read_bytes()==(ROOT/'.github/workflows/candidate.yml').read_bytes(),'Host/component workflow drift'
 flow=yaml.load((ROOT/'.github/workflows/candidate.yml').read_text(),Loader=yaml.BaseLoader);assert flow['permissions']=={'contents':'read'};assert set(flow['on'])=={'pull_request','workflow_dispatch'}
 locks=json.loads((ROOT/'ci-actions-lock.json').read_text())['actions'];used=[]
 for step in flow['jobs']['candidate']['steps']:
  if 'uses' in step:
   name,sha=step['uses'].split('@');assert len(sha)==40 and sha==locks[name]['sha'];used.append(name)
 assert set(used)==set(locks);write(OUT/'workflow-validation.json',{'passed':True,'pinned_actions':len(used),'repository_permissions':'read-only','hosted_run':'Not performed by local validation'})
def reason(java,jar):
 base=[java,'-Xmx2G','-jar',str(jar)];catalog=ROOT/'dist/ontology-catalog.xml'
 for name,path,with_catalog in [('import',ROOT/'dist/integrated-ontology.ttl',True),('flat',ROOT/'dist/merged-asserted.ttl',False)]:
  args=['--catalog',str(catalog)] if with_catalog else []
  run(name+'-profile',base+['validate-profile','--profile','DL']+args+['--input',str(path),'--output',str(OUT/(name+'-profile.txt'))])
  run(name+'-HermiT',base+['reason','--reasoner','HermiT']+args+['--input',str(path),'--create-new-ontology','true','--output',str(OUT/(name+'-inferences-raw.ttl'))])
 bad=(ROOT/'dist/integrated-ontology.ttl').read_text(encoding='utf-8')+'\n<urn:g5:negative> a <urn:capability-ontology:Capability>, <urn:capability-ontology:Implementation> .\n';(OUT/'inconsistent.ttl').write_bytes(bad.encode())
 run('inconsistency-rejected',base+['reason','--reasoner','HermiT','--catalog',str(catalog),'--input',str(OUT/'inconsistent.ttl'),'--output',str(OUT/'negative-inferences.ttl')],expect_inconsistent=True)
 a=Graph().parse(OUT/'import-inferences-raw.ttl');b=Graph().parse(OUT/'flat-inferences-raw.ttl');asserted=Graph().parse(ROOT/'dist/merged-asserted.ttl');builtin=(XSD.date,RDF.type,RDFS.Datatype)
 for graph in [a,b]:
  for h in set(graph.subjects(RDF.type,OWL.Ontology)):graph.remove((h,None,None))
 extra=(set(a)-set(b))|(set(b)-set(a));assert all(t in asserted or t==builtin for t in extra)
 for graph in [a,b]:
  for triple in list(graph):
   if triple in asserted or triple==builtin:graph.remove(triple)
 assert isomorphic(a,b);a.serialize(ROOT/'dist/materialised.ttl',format='turtle');write(OUT/'inference-equivalence.json',{'passed':True,'inferred_delta_triples':len(a),'normalisation':'Ontology headers, already asserted statements and redundant built-in xsd:date declaration only.'})
def quality():
 current=Graph().parse(ROOT/'dist/merged-asserted.ttl');approved=Graph().parse(ROOT/'baseline/g4-approved-asserted.ttl');assert isomorphic(current,approved)
 with tempfile.TemporaryDirectory(dir=OUT) as directory:
  t=Path(directory);(t/'nested').mkdir();p=t/'nested/pinned.txt';p.write_bytes(b'fixture');write(t/'source-pins.json',[{'path':'nested\\pinned.txt','sha256':digest(p)}]);verify_pins(t)
 manifest=Graph().parse(ROOT/'dist/merge-manifest.jsonld',format='json-ld');assert len(manifest)>0
 write(OUT/'release-quality.json',{'passed':True,'G4_approved_graph_preserved':True,'Windows_style_pin_paths_portable':True,'JSONLD_manifest_RDF_triples':len(manifest)})
def candidate_summary():
 validation=json.loads((OUT/'distribution-tests.json').read_text());cq=json.loads((OUT/'competency-results.json').read_text());docs=json.loads((ROOT/'docs/generated/generation-manifest.json').read_text());infer=json.loads((OUT/'inference-equivalence.json').read_text());assert validation['failed']==0 and len(cq)==18 and all(c['passed'] for q in cq for c in q['cases'])
 assert docs['counts']=={'tools':112,'personas':123,'principle_proposals':189,'indicative_ranges':42,'historical_data_rows':131,'capability_proposals':15,'asserted_triples':95008,'source_graphs':16}
 summary={'candidate_version':CONFIG['candidate_version'],'integration_checks':validation['passed'],'CQs':len(cq),'synthetic_cases':sum(len(q['cases']) for q in cq),'production_query_rows':{q['id']:q['production_rows'] for q in cq},'reasoning_outcomes':5,'inference_delta_triples':infer['inferred_delta_triples'],'documentation_counts':docs['counts'],'G4_graph_preserved':True,'mapping_status':'proposed and deployment-unverified; inherited exceptions retained','owner_release_signoff':'pending','hosted_CI_run_claimed':False}
 write(OUT/'candidate-validation.json',summary);return summary
def archive_validation(archive):
 with tempfile.TemporaryDirectory(dir=OUT,prefix='archive-check-') as directory:
  root=Path(directory)
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   for name in z.namelist():assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name.replace('\\','/')).parts
   manifest=json.loads(z.read('release-manifest.json'));assert all(hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'] for row in manifest['files']);z.extractall(root)
  verify_pins(root);a=Graph().parse(root/'dist/merged-asserted.ttl');b=Graph().parse(ROOT/'dist/merged-asserted.ttl');assert isomorphic(a,b)
  canonical=Dataset();canonical.parse(root/'dist/merged.trig',format='trig');original=Dataset();original.parse(ROOT/'dist/merged.trig',format='trig')
  for graph in original.contexts():assert isomorphic(graph,canonical.graph(graph.identifier))
 write(OUT/'archive-validation.json',{'passed':True,'payload_hashes_verified':len(manifest['files']),'pinned_inputs_survive_export':True,'canonical_Turtle_and_TriG_equivalent':True})
def clean_reproduce(first,source_revision):
 with tempfile.TemporaryDirectory(dir=OUT,prefix='clean-release-') as directory:
  root=Path(directory)
  for name in ['inputs','baseline','queries','fixtures','shapes','scripts','docs','LICENSES','.github','specification']:
   if (ROOT/name).exists():shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for p in ROOT.iterdir():
   if p.is_file():shutil.copyfile(p,root/p.name)
  (root/'validation').mkdir();shutil.copyfile(OUT/'competency-results.json',root/'validation/competency-results.json');shutil.copyfile(OUT/'candidate-validation.json',root/'validation/candidate-validation.json')
  run('clean-rebuild',[sys.executable,str(root/'build.py')],cwd=root)
  shutil.copyfile(ROOT/'dist/materialised.ttl',root/'dist/materialised.ttl')
  run('clean-documentation',[sys.executable,str(root/'scripts/generate_docs.py')],cwd=root)
  assert isomorphic(Graph().parse(ROOT/'dist/merged-asserted.ttl'),Graph().parse(root/'dist/merged-asserted.ttl'))
  second=package(root,source_revision=source_revision,destination=root/'candidate.zip');assert first['sha256']==second['sha256'],'Candidate archive not reproducible'
 write(OUT/'candidate-reproducibility.json',{'passed':True,'method':'Clean relocated build, fresh RDF-derived documentation and independent canonical packaging; reuse only validated evidence and equivalent inference delta.','sha256':first['sha256'],'archive_bytes':first['bytes'],'byte_identical':True})
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--robot-jar');ap.add_argument('--java');args=ap.parse_args()
 for name in ['dist','validation','release','docs/generated']:clean(ROOT/name)
 OUT.mkdir();java=args.java
 if not java:java=str(Path(os.environ['JAVA_HOME'])/'bin/java') if os.environ.get('JAVA_HOME') else shutil.which('java')
 if not java:raise RuntimeError('Java required')
 runtime(java);workflow_checks();jar=robot_jar(args.robot_jar)
 run('host-source-pins',[sys.executable,str(ROOT/'scripts/verify_host_sources.py')]);run('query-contracts',[sys.executable,str(ROOT/'query_specs.py')]);run('build',[sys.executable,str(ROOT/'build.py')]);run('integration-validation',[sys.executable,str(ROOT/'validate.py')]);reason(java,jar);quality();run('documentation',[sys.executable,str(ROOT/'scripts/generate_docs.py')]);summary=candidate_summary();source_revision=revision(ROOT);first=package(ROOT,source_revision=source_revision);archive_validation(first['path']);clean_reproduce(first,source_revision)
 evidence=ROOT/'release/evidence';shutil.copytree(OUT,evidence,ignore=shutil.ignore_patterns('archive-check-*','clean-release-*'))
 write(ROOT/'release/acceptance-summary.json',{**summary,'candidate_sha256':first['sha256'],'candidate_bytes':first['bytes'],'reproducibility':'passed','hosted_CI_executed':bool(os.environ.get('GITHUB_ACTIONS')),'source_revision':source_revision});print(json.dumps({'candidate':first['path'],'sha256':first['sha256'],'checks':summary['integration_checks'],'hosted_CI_executed':bool(os.environ.get('GITHUB_ACTIONS'))},indent=2))
if __name__=='__main__':main()
