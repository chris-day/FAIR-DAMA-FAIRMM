"""Deterministic review archive with canonical generated RDF and byte-pinned inputs."""
import json,hashlib,zipfile,sys,zlib
from pathlib import Path
from rdflib import Graph,Dataset,BNode,URIRef
from rdflib.compare import to_canonical_graph
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def nt(graph):return ''.join(sorted(to_canonical_graph(graph).serialize(format='nt').splitlines(keepends=True))).encode('utf-8')
def canonical_trig(path):
 data=Dataset();data.parse(path,format='trig');parts=[];seen=set()
 for graph in sorted(data.contexts(),key=lambda g:str(g.identifier)):
  if not len(graph):continue
  local={term for triple in graph for term in triple if isinstance(term,BNode)}
  if seen&local:raise ValueError('Cross-graph blank-node identity requires dataset canonicalisation; no silent rescoping allowed')
  seen|=local;canon=Graph();prefix='g'+sha(str(graph.identifier).encode())[:20]
  for triple in to_canonical_graph(graph):canon.add(tuple(BNode(prefix+str(t)) if isinstance(t,BNode) else t for t in triple))
  lines=sorted(canon.serialize(format='nt').splitlines());parts.append(str(graph.identifier).join(['<','> {\n'])+''.join('  '+line+'\n' for line in lines)+'}\n')
 return '\n'.join(parts).encode('utf-8')
def revision(root):
 git=next((parent/'.git' for parent in [root,*root.parents] if (parent/'.git').is_dir()),root/'.git')
 if git.is_dir():
  head=(git/'HEAD').read_text().strip()
  if not head.startswith('ref: '):return head
  ref=head[5:];p=git/ref
  if p.exists():return p.read_text().strip()
  if (git/'packed-refs').exists():
   for line in (git/'packed-refs').read_text().splitlines():
    if line.endswith(' '+ref):return line.split()[0]
 return 'unversioned-export'
def build(root=ROOT,source_revision=None,destination=None):
 root=Path(root);config=json.loads((root/'release-config.json').read_text());payload={};kinds={}
 include=['inputs','baseline','dist','queries','fixtures','shapes','scripts','docs','LICENSES','.github','specification']
 for folder in include:
  for path in sorted((root/folder).rglob('*')):
   if not path.is_file() or '__pycache__' in path.parts:continue
   rel=path.relative_to(root).as_posix()
   if folder=='dist' and path.name not in ['integrated-ontology.ttl','merged-asserted.ttl','merged.trig','ontology-lock.json','ontology-catalog.xml','merge-manifest.jsonld','materialised.ttl']:continue
   data=path.read_bytes();kind='authored-text-lf'
   if folder in ['inputs','baseline','specification']:kind='pinned-source-bytes'
   elif folder=='dist' and path.suffix=='.ttl':data=nt(Graph().parse(path));kind='canonical-rdf-as-valid-turtle'
   elif folder=='dist' and path.suffix=='.trig':data=canonical_trig(path);kind='canonical-source-scoped-trig'
   else:
    try:data=data.decode('utf-8').replace('\r\n','\n').encode('utf-8')
    except UnicodeDecodeError:kind='binary-bytes'
   payload[rel]=data;kinds[rel]=kind
 for name in ['README.md','build.py','validate.py','query_specs.py','requirements-validation.txt','source-pins.json','toolchain-lock.json','ci-actions-lock.json','release-config.json','integration-provenance.json','approvals.json','.gitattributes','.gitignore']:
  payload[name]=(root/name).read_bytes().decode('utf-8').replace('\r\n','\n').encode('utf-8');kinds[name]='authored-text-lf'
 payload['candidate-validation.json']=(root/'validation/candidate-validation.json').read_bytes().decode('utf-8').replace('\r\n','\n').encode('utf-8');kinds['candidate-validation.json']='stable-validation-summary'
 manifest={'candidate_version':config['candidate_version'],'ontology_release':config['ontology_release'],'documentation_version':config['documentation_version'],'selected_FAIRMM_release':config['selected_FAIRMM_release'],'date':config['release_date'],'source_revision':source_revision or revision(root),'integration_provenance':json.loads((root/'integration-provenance.json').read_text()),'channel':config['channel'],'owner_release_signoff':config['owner_release_signoff'],'licence_clearance':config['licence_clearance'],'public_distribution_authorised':False,'deployment_authorised':False,'packaging_policy':'Generated RDF canonicalised; source bytes untouched; owned text LF; sorted ZIP entries and fixed timestamp. Byte reproducibility assumes the recorded Python/zlib toolchain.','zlib_version':zlib.ZLIB_VERSION,'files':[{'path':name,'bytes':len(data),'sha256':sha(data),'transformation':kinds[name]} for name,data in sorted(payload.items())]}
 payload['release-manifest.json']=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
 out=Path(destination) if destination else root/'release'/('FAIR-DAMA-Integrated-'+config['candidate_version']+'.zip');out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  for name,data in sorted(payload.items()):
   info=zipfile.ZipInfo(name,tuple(config['archive_timestamp']));info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16;archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 digest=sha(out.read_bytes());out.with_suffix(out.suffix+'.sha256').write_bytes((digest+'  '+out.name+'\n').encode());return {'path':str(out),'sha256':digest,'files':len(payload),'bytes':out.stat().st_size,'manifest':manifest}
if __name__=='__main__':
 result=build();print(json.dumps({k:v for k,v in result.items() if k!='manifest'},indent=2))
