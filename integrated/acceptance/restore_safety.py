"""A failed restore must not replace the last accepted runtime Dataset."""
import json
from pathlib import Path
from rdflib import Dataset,URIRef,Literal,RDFS
from reference import ConformanceError,sha,blank_scopes,PROVENANCE,I
def exercise(release,snapshot,workspace,expected_results):
 snapshot=Path(snapshot);results=[]
 for fault in ['source-content','provenance']:
  destination=Path(workspace)/('invalid-'+fault+'-checkpoint');destination.mkdir(exist_ok=True);manifest=json.loads((snapshot/'snapshot.json').read_text(encoding='utf-8'));bad=Dataset();bad.parse(snapshot/'runtime.trig',format='trig')
  if fault=='source-content':
   gid=URIRef(release.lock['sources'][0]['graph']);graph=bad.graph(gid);target=sorted([(s,p,o) for s,p,o in graph.triples((None,RDFS.label,None)) if isinstance(s,URIRef) and isinstance(o,Literal)],key=lambda t:tuple(map(str,t)))[0];graph.remove(target);s,p,o=target;replacement=Literal(str(o)+' changed for fault test',lang=o.language) if o.language else Literal(str(o)+' changed for fault test',datatype=o.datatype);graph.add((s,p,replacement))
  else:bad.graph(PROVENANCE).add((URIRef('urn:g6:unexpected-metadata'),I.role,Literal('asserted')))
  assert blank_scopes(bad)==manifest['blank_node_scopes'];bad.serialize(destination/'runtime.trig',format='trig');manifest['dataset_sha256']=sha(destination/'runtime.trig');(destination/'snapshot.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');before=release.dataset;rejected=False;code=None
  try:release.restore(destination)
  except ConformanceError as error:code=error.code;rejected=code==fault
  untouched=release.dataset is before
  if untouched:release.verify_sources()
  results.extend([{'check':'Semantically corrupted '+fault+' checkpoint rejected despite valid byte checksum','passed':rejected,'detail':code},{'check':'Failed '+fault+' restore leaves last accepted runtime unchanged','passed':untouched,'detail':'Staged content and provenance validation precede runtime pointer replacement.'}])
 count=release.restore(snapshot);actual=release.queries();results.extend([{'check':'Valid checkpoint remains recoverable after rejected restores','passed':count==95008,'detail':'All content and provenance validated before accepting the retry.'},{'check':'Post-hardening recovery reproduces all 18 lexical and typed queries','passed':actual==expected_results,'detail':'Compared to the full accepted result goldens.'}]);return results
