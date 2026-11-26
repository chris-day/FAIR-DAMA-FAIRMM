"""Read-only release loading and explicit operational Dataset views; no RDF-store vendor API."""
import json,hashlib,zipfile,ntpath
from pathlib import Path,PurePosixPath
from collections import Counter,defaultdict
from xml.etree.ElementTree import parse
from rdflib import Graph,Dataset,URIRef,Literal,BNode,RDF,OWL,Namespace
from rdflib.compare import isomorphic
I=Namespace('urn:fair-dama-fairmm:integrated:');A=Namespace('urn:fair-dama-fairmm:alignment:');PROV=Namespace('http://www.w3.org/ns/prov#')
PROVENANCE=URIRef('urn:fair-dama-fairmm:graph:provenance:1.0.0')
class ConformanceError(ValueError):
 def __init__(self,code,message):self.code=code;super().__init__(code+': '+message)
def require(test,code,message):
 if not test:raise ConformanceError(code,message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def inside(root,relative):
 root=Path(root).resolve();name=str(relative).replace('\\','/');p=PurePosixPath(name)
 require(not p.is_absolute() and not ntpath.splitdrive(name)[0] and '..' not in p.parts,'path','Unsafe relative path')
 result=(root/name).resolve();require(result.is_relative_to(root),'path','Path leaves release root');return result
def extract_archive(archive,expected_sha,destination):
 require(Path(archive).exists(),'archive-missing','No candidate archive');require(sha(archive)==expected_sha,'archive-hash','Candidate checksum differs');root=Path(destination).resolve();root.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():inside(root,name)
  require(z.testzip() is None,'archive','ZIP CRC failure');manifest=json.loads(z.read('release-manifest.json'))
  for row in manifest['files']:require(hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'],'payload-hash','Archived payload '+row['path'])
  z.extractall(root)
 return root
def resolve_imports(root,imports,lookup,hashes):
 root=Path(root).resolve();graphs={};active=[];done=set()
 def visit(iri):
  require(iri not in active,'import-cycle',' -> '.join(active+[iri]));
  if iri in done:return
  require(iri in lookup,'missing-import',iri);p=Path(lookup[iri]).resolve();require(p.is_relative_to(root),'path','Import escapes release root');require(p in hashes,'unlocked-import',str(p));require(p.exists(),'missing-input',str(p));require(sha(p)==hashes[p],'input-hash',str(p))
  if p not in graphs:graphs[p]=Graph().parse(p,format='turtle')
  g=graphs[p];identities=set(map(str,g.subjects(RDF.type,OWL.Ontology)))|set(map(str,g.objects(None,OWL.versionIRI)));require(iri in identities,'ontology-identity',iri);active.append(iri)
  for target in sorted(map(str,g.objects(None,OWL.imports))):visit(target)
  active.pop();done.add(iri)
 for iri in imports:visit(iri)
 return graphs
def lexical_rows(result):return sorted([[str(v) if v is not None else None for v in row] for row in result],key=json.dumps)
def term(value):
 if value is None:return None
 if isinstance(value,URIRef):return {'kind':'iri','value':str(value)}
 if isinstance(value,Literal):return {'kind':'literal','value':str(value),'datatype':str(value.datatype) if value.datatype else None,'language':value.language}
 return {'kind':'blank-node','value':str(value)}
def typed_rows(result):return sorted([[term(v) for v in row] for row in result],key=lambda r:json.dumps(r,sort_keys=True))
def blank_scopes(dataset):
 scopes=defaultdict(set)
 for graph in dataset.contexts():
  for triple in graph:
   for node in triple:
    if isinstance(node,BNode):scopes[node].add(str(graph.identifier))
 return dict(Counter('|'.join(sorted(ids)) for ids in scopes.values()))
class ReferenceRelease:
 def __init__(self,root,archive_sha):
  self.root=Path(root).resolve();self.archive_sha=archive_sha;self.verify_payload();self.manifest=json.loads((self.root/'dist/merge-manifest.jsonld').read_text(encoding='utf-8'));self.lock=json.loads((self.root/'dist/ontology-lock.json').read_text(encoding='utf-8'));self.entry=Graph().parse(self.root/'dist/integrated-ontology.ttl');self.flat=Graph().parse(self.root/'dist/merged-asserted.ttl');self.dataset=Dataset();self.dataset.parse(self.root/'dist/merged.trig',format='trig');self.dataset.default_union=False;self._provenance=Graph()
  for triple in self.dataset.graph(PROVENANCE):self._provenance.add(triple)
  require(len(self.dataset.default_context)==0,'default-policy','Released TriG default graph must be empty');self.verify_sources();self.active_profile=None
 def verify_payload(self):
  manifest=json.loads((self.root/'release-manifest.json').read_text(encoding='utf-8'))
  for row in manifest['files']:
   p=inside(self.root,row['path']);require(p.exists(),'missing-payload',row['path']);require(sha(p)==row['sha256'],'payload-hash',row['path'])
  for row in json.loads((self.root/'source-pins.json').read_text(encoding='utf-8')):
   p=inside(self.root,row['path']);require(p.exists(),'missing-input',row['path']);require(sha(p)==row['sha256'],'input-hash',row['path'])
 def verify_sources(self,dataset=None):
  current=self.dataset if dataset is None else dataset
  registry=self.manifest['source_graphs'];active=set(self.manifest['asserted_graphs']);declared={r['graph'] for r in registry if r['role']=='asserted'};require(active==declared and len(active)==7,'graph-policy','Asserted graph selection differs from registry');require(len(registry)==len({r['graph'] for r in registry})==16,'source-registry','Expected sixteen distinct source graphs')
  meta=current.graph(PROVENANCE)
  require(isomorphic(meta,self._provenance),'provenance','Provenance graph differs from frozen release')
  for row in self.lock['sources']:
   p=inside(self.root,row['local_path']);require(p.exists(),'missing-input',row['local_path']);require(sha(p)==row['SHA-256'],'input-hash',row['local_path']);gid=URIRef(row['graph']);g=current.graph(gid)
   require(len(g)>0,'source-content','Missing source graph '+str(gid))
   require(isomorphic(Graph().parse(p,format='turtle'),g),'source-content','Source graph differs '+str(gid))
   required=[(gid,I.sha256,Literal(row['SHA-256'])),(gid,PROV.wasDerivedFrom,URIRef(row['source_uri'])),(gid,I.lockPath,Literal(row['local_path'])),(gid,I.role,Literal(row['role']))]
   require(all(t in meta for t in required),'provenance','Incomplete provenance '+str(gid))
 def asserted_view(self,selection=None):
  expected=set(self.manifest['asserted_graphs']);chosen=expected if selection is None else set(selection);require(chosen==expected,'graph-policy','Only the registered asserted graphs may populate the default view');g=Graph()
  for gid in sorted(chosen):
   for t in self.dataset.graph(URIRef(gid)):
    if t[1]!=OWL.imports:g.add(t)
  for t in self.entry:
   if t[1]!=OWL.imports:g.add(t)
  return g
 def import_view(self,lookup_override=None):
  catalog=self.root/'dist/ontology-catalog.xml';lookup={e.attrib['name']:(catalog.parent/e.attrib['uri']).resolve() for e in parse(catalog).getroot()}
  if lookup_override is not None:lookup=lookup_override
  pins={inside(self.root,r['path']):r['sha256'] for r in json.loads((self.root/'source-pins.json').read_text(encoding='utf-8'))};graphs=resolve_imports(self.root,sorted(map(str,self.entry.objects(None,OWL.imports))),lookup,pins);g=Graph()
  for source in list(graphs.values())+[self.entry]:
   for t in source:
    if t[1]!=OWL.imports:g.add(t)
  return g
 def validate_view(self,g):
  require(not list(g.subjects(RDF.type,A.CumulativeAssociation)),'graph-policy','Cumulative associations entered asserted view');require(len(g)==len(self.flat),'asserted-semantics','Asserted triple count differs');require(isomorphic(g,self.flat),'asserted-semantics','Asserted RDF differs from frozen flat graph')
 def load(self,profile):
  require(profile in ['flat','trig','imports'],'profile','Unsupported profile')
  graph=self.flat if profile=='flat' else self.asserted_view() if profile=='trig' else self.import_view();self.validate_view(graph);self.dataset.default_context.remove((None,None,None))
  for triple in graph:self.dataset.default_context.add(triple)
  self.active_profile=profile;return len(graph)
 def queries(self):
  require(self.active_profile is not None,'profile','Load a reference profile first');results={}
  for n in range(1,19):
   key=f'CQ{n:02}';query=(self.root/'queries'/(key+'.rq')).read_text(encoding='utf-8');value=list(self.dataset.query(query));results[key]={'lexical':lexical_rows(value),'typed':typed_rows(value)}
  return results
 def snapshot(self,destination):
  require(self.active_profile is not None,'profile','No active view');destination=Path(destination);destination.mkdir(parents=True,exist_ok=True);data=destination/'runtime.trig';self.dataset.serialize(data,format='trig');manifest={'release_sha256':self.archive_sha,'dataset_sha256':sha(data),'active_profile':self.active_profile,'default_graph_policy':'Explicit materialized asserted view; source distribution default remains empty','default_triples':len(self.dataset.default_context),'contexts':sorted(str(g.identifier) for g in self.dataset.contexts()),'blank_node_scopes':blank_scopes(self.dataset)};(destination/'snapshot.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');return manifest
 def restore(self,destination):
  destination=Path(destination);manifest=json.loads((destination/'snapshot.json').read_text(encoding='utf-8'));require(manifest['release_sha256']==self.archive_sha,'snapshot-release','Snapshot belongs to another release');require(sha(destination/'runtime.trig')==manifest['dataset_sha256'],'snapshot-hash','Snapshot bytes changed');restored=Dataset();restored.parse(destination/'runtime.trig',format='trig');restored.default_union=False
  require(sorted(str(g.identifier) for g in restored.contexts())==manifest['contexts'],'snapshot-contexts','Snapshot context set differs');require(blank_scopes(restored)==manifest['blank_node_scopes'],'snapshot-blank-scopes','Blank-node scope relationships differ');self.validate_view(restored.default_context);self.verify_sources(dataset=restored);self.dataset=restored;self.active_profile=manifest['active_profile'];return len(restored.default_context)
