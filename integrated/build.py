"""Pinned, offline ontology closure and three equivalent integration distributions."""
import json,hashlib
from pathlib import Path
from xml.etree.ElementTree import parse,Element,SubElement,tostring
from rdflib import Graph,Dataset,URIRef,Namespace,Literal,RDF,OWL
ROOT=Path(__file__).resolve().parent
I=Namespace('urn:fair-dama-fairmm:integrated:');A=Namespace('urn:fair-dama-fairmm:alignment:');C=Namespace('urn:capability-ontology:');D=Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-ontology.ttl#');F=Namespace('https://w3id.org/fair/principles/terms/');DC=Namespace('http://purl.org/dc/terms/');PROV=Namespace('http://www.w3.org/ns/prov#')
ONTO=I.ontology;PROVENANCE=URIRef('urn:fair-dama-fairmm:graph:provenance:1.0.0')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_pins(root=ROOT):
 for entry in json.loads((root/'source-pins.json').read_text(encoding='utf-8')):
  p=root/Path(entry['path'].replace('\\','/'))
  if not p.exists() or digest(p)!=entry['sha256']:raise ValueError('Missing or changed pinned input: '+entry['path'])
def resolver(root=ROOT):
 catalog=root/'inputs/alignment/ontology-catalog.xml';result={e.attrib['name']:(catalog.parent/e.attrib['uri']).resolve() for e in parse(catalog).getroot()}
 # Canonical domain inputs already pass their own profiles. Keep Capability domain-neutral.
 for name in ['capability-1.0.0.ttl','dama-1.2.0.ttl']:
  p=root/'inputs/domains'/name;g=Graph().parse(p)
  for s in g.subjects(RDF.type,OWL.Ontology):
   for iri in [s]+list(g.objects(s,OWL.versionIRI)):result[str(iri)]=p
 fair=next((root/'inputs/originals').rglob('fair-ontology.ttl'));result[str(F['FAIR-Vocabulary'])]=fair
 return result
def resolve_closure(imports,lookup):
 graphs={};edges=[];active=[];complete=set()
 def visit(iri):
  if iri in active:raise ValueError('Import cycle: '+' -> '.join(active+[iri]))
  if iri in complete:return
  if iri not in lookup:raise ValueError('Unresolved import: '+iri)
  p=lookup[iri];g=graphs.get(p)
  if g is None:g=Graph().parse(p,format='turtle');graphs[p]=g
  ids=set(map(str,g.subjects(RDF.type,OWL.Ontology)))|set(map(str,g.objects(None,OWL.versionIRI)))
  if iri not in ids:raise ValueError('Wrong ontology identity: '+iri)
  active.append(iri)
  for dependency in sorted(map(str,g.objects(None,OWL.imports))):edges.append([iri,dependency]);visit(dependency)
  active.pop();complete.add(iri)
 for iri in imports:visit(iri)
 return graphs,sorted(edges)
def main():
 verify_pins();out=ROOT/'dist';out.mkdir(exist_ok=True);lookup=resolver()
 origins={item['path'].replace('\\','/'):item['source_uri'] for item in json.loads((ROOT/'source-pins.json').read_text(encoding='utf-8'))}
 imports=[str(D['ontology-version-1.2.0']),str(C['ontology:version:1.0.0']),str(F['FAIR-Vocabulary']),str(A['ontology:version:1.1.0']),str(A['ontology:alignment:version:1.0.0'])]
 entry=Graph();entry.add((ONTO,RDF.type,OWL.Ontology));entry.add((ONTO,OWL.versionIRI,I['ontology:version:1.0.0']));entry.add((ONTO,OWL.versionInfo,Literal('1.0.0')));entry.add((ONTO,DC.title,Literal('FAIR DAMA integrated ontology',lang='en')));entry.add((DC.title,RDF.type,OWL.AnnotationProperty))
 for iri in imports:entry.add((ONTO,OWL.imports,URIRef(iri)))
 entry.serialize(out/'integrated-ontology.ttl',format='turtle')
 graphs,edges=resolve_closure(imports,lookup);dataset=Dataset();provenance=dataset.graph(PROVENANCE);registry=[];lock=[];flattened=Graph();removed=[]
 def source(p,g,role):
  sha=digest(p);gid=URIRef('urn:fair-dama-fairmm:graph:'+role+':sha256:'+sha);target=dataset.graph(gid)
  for t in g:target.add(t)
  rel=p.relative_to(ROOT).as_posix();identities=sorted(map(str,g.subjects(RDF.type,OWL.Ontology)));versions=sorted(map(str,g.objects(None,OWL.versionIRI)))
  row={'graph':str(gid),'role':role,'local_path':rel,'sha256':sha,'triples':len(g),'ontology_IRIs':identities,'version_IRIs':versions}
  origin=origins[rel]
  registry.append(row);provenance.add((gid,RDF.type,PROV.Entity));provenance.add((gid,PROV.wasDerivedFrom,URIRef(origin)));provenance.add((gid,I.sha256,Literal(sha)));provenance.add((gid,I.role,Literal(role)));provenance.add((gid,I.lockPath,Literal(rel)))
  for identity in identities:provenance.add((gid,I.ontologyIRI,URIRef(identity)))
  lock.append({'source_uri':origin,'immutable_revision':'sha256:'+sha,'SHA-256':sha,'local_path':rel,'ontology_IRIs':identities,'version_IRIs':versions,'dependencies':sorted(map(str,g.objects(None,OWL.imports))),'role':role,'graph':str(gid),'licence_policy':'Preserve component notices; see input rights statements and README; no new licence grant.'})
 for p,g in sorted(graphs.items(),key=lambda pair:str(pair[0])):
  source(p,g,'asserted')
  for t in g:
   if t[1]==OWL.imports:removed.append([v.n3() for v in t])
   else:flattened.add(t)
 for p in sorted((ROOT/'inputs/originals').rglob('*.ttl')):source(p,Graph().parse(p),'derived' if p.name=='fairmm-dama-derived.ttl' else 'archival')
 for t in entry:
  if t[1]!=OWL.imports:flattened.add(t)
 flattened.serialize(out/'merged-asserted.ttl',format='turtle');dataset.serialize(out/'merged.trig',format='trig')
 lookup[str(ONTO)]=out/'integrated-ontology.ttl';lookup[str(I['ontology:version:1.0.0'])]=out/'integrated-ontology.ttl'
 cat=Element('catalog',{'xmlns':'urn:oasis:names:tc:entity:xmlns:xml:catalog','prefer':'public'})
 import os
 for iri,p in sorted(lookup.items()):SubElement(cat,'uri',{'name':iri,'uri':os.path.relpath(p,out).replace('\\','/')})
 (out/'ontology-catalog.xml').write_bytes(tostring(cat,encoding='utf-8',xml_declaration=True))
 (out/'ontology-lock.json').write_text(json.dumps({'release':'1.0.0','selected_FAIRMM_release':'1.2.5','sources':lock,'import_edges':edges},indent=2),encoding='utf-8')
 manifest={'@context':{'prov':'http://www.w3.org/ns/prov#'},'@id':str(I['build:1.0.0']),'@type':'prov:Activity','release':'1.0.0','selected_FAIRMM_release':'1.2.5','source_declared_FAIRMM_ontology_version':'1.1.0','asserted_graphs':[r['graph'] for r in registry if r['role']=='asserted'],'source_graphs':registry,'provenance_graph':str(PROVENANCE),'flattening_transformations':{'removed_import_statements':sorted(removed),'preserved':'All other source triples, including ontology declarations and annotations; blank nodes scoped per parsed document.','added':'Integrated entrypoint header without imports.'},'query_policy':'Explicit union of asserted_graphs only; TriG default graph empty. CQ17 uses the provenance graph. Archival, derived and inference graphs excluded from default asserted view.','asserted_triples':len(flattened),'provenance_triples':len(provenance),'reasoning':'Separate outputs, never inserted into merged-asserted.ttl','commands':['python build.py','python validate.py'],'validation_references':['../validation/distribution-tests.json','../validation/competency-results.json','../validation/reasoner-results.json'],'toolchain_reference':'../toolchain-lock.json'}
 manifest['@context']={'prov':str(PROV),'@vocab':str(I)+'manifest:', 'asserted_graphs':{'@id':str(I)+'manifest:assertedGraph','@type':'@id'},'provenance_graph':{'@id':str(I)+'manifest:provenanceGraph','@type':'@id'},'graph':{'@id':str(I)+'manifest:graph','@type':'@id'}}
 (out/'merge-manifest.jsonld').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps({'closure_sources':len(graphs),'source_graphs':len(registry),'import_edges':len(edges),'asserted_triples':len(flattened)},indent=2))
if __name__=='__main__':main()
