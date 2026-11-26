"""Generate semantic mapping documentation from the built RDF and actual test reports."""
import json,hashlib
from pathlib import Path
from collections import Counter
from rdflib import Graph,RDF,RDFS,OWL,Namespace,URIRef
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/generated'
A=Namespace('urn:fair-dama-fairmm:alignment:');C=Namespace('urn:capability-ontology:');D=Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-ontology.ttl#');P=Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl#');DC=Namespace('http://purl.org/dc/terms/')
def write(name,value):p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value.replace('\r\n','\n').encode('utf-8'))
def cell(v):return str(v).replace('|','\\|').replace('\n',' ')
def table(head,rows):return '| '+' | '.join(head)+' |\n|'+ '|'.join('---' for _ in head)+'|\n'+''.join('| '+' | '.join(cell(c) for c in row)+' |\n' for row in rows)
def compact(v):
 text=str(v)
 for prefix,ns in [('dama',D),('a',A),('cap',C),('persona',P),('fair',Namespace('https://w3id.org/fair/principles/terms/'))]:
  if text.startswith(str(ns)):return prefix+':'+text[len(str(ns)):]
 return text
def generate():
 OUT.mkdir(parents=True,exist_ok=True);g=Graph().parse(ROOT/'dist/merged-asserted.ttl');manifest=json.loads((ROOT/'dist/merge-manifest.jsonld').read_text(encoding='utf-8'));lock=json.loads((ROOT/'dist/ontology-lock.json').read_text());config=json.loads((ROOT/'release-config.json').read_text());cq=json.loads((ROOT/'validation/competency-results.json').read_text())
 def vals(s,p):return sorted(g.objects(s,p),key=str)
 def value(s,p):return '; '.join(map(str,vals(s,p)))
 def label(s):return value(s,RDFS.label) or compact(s)
 tools=sorted(set(g.subjects(RDF.type,D.ToolCategory)),key=lambda n:(label(n),str(n)));personas=set(g.subjects(RDF.type,P.Persona));proposals=sorted(set(g.subjects(RDF.type,A.ToolPrincipleProposal)),key=str);ranges=set(g.subjects(RDF.type,A.MaturityRangeProposal));hist=sorted(set(g.subjects(RDF.type,A.HistoricalRow)),key=lambda n:(int(next(g.objects(n,A.sourceLine))),str(n)));caps=sorted(set(g.subjects(RDF.type,A.CapabilityProposal)),key=lambda n:(label(n),str(n)))
 counts={'tools':len(tools),'personas':len(personas),'principle_proposals':len(proposals),'indicative_ranges':len(ranges),'historical_data_rows':len(hist),'capability_proposals':len(caps),'asserted_triples':len(g),'source_graphs':len(lock['sources'])}
 write('index.md',f'''# Generated semantic mapping documentation

Documentation {config['documentation_version']} | Ontology {config['ontology_release']} | Candidate {config['candidate_version']}

Generated from the asserted RDF, dependency lock and actual query reports. Do not edit these generated files by hand.

The model contains {len(tools)} exact catalogue tool categories, {len(personas)} preserved DAMA personas and {len(proposals)} qualified tool–principle proposals. All new proposals remain unverified. The {len(ranges)} D7 ranges and {len(caps)} capability interpretations are documentary proposals, not normative maturity requirements.

- [Tool catalogue](tools.md)
- [Qualified principle proposals](mapping-proposals.md)
- [Historical row dispositions](historical-dispositions.md)
- [Capability progression proposals](capability-proposals.md)
- [Query results](query-results.md)
- [Source and dependency inventory](sources.md)
- [Generated import diagram](architecture.mmd)

The 19 unresolved DAMA tool names and 17 FAIR-specific extensions remain inherited coverage exceptions. No unsupported tool–Capability or Capability–FAIR bridges were added. Zero query rows express documented graph coverage, not proof of impossibility. Source FAIR-MM ontology headers retain 1.1.0 while the selected framework release is 1.2.5.
''')
 rows=[]
 for tool in tools:
  occurrences=sorted(g.subjects(D.catalogueCategory,tool),key=str);sections=sorted({label(s) for occ in occurrences for s in g.objects(occ,D.inCatalogueSection)})
  rows.append([label(tool),compact(tool),len(occurrences),'; '.join(sections)])
 write('tools.md','# Tool catalogue\n\nExact labels are grouped only within the approved catalogue. Spelling variants remain distinct; no equivalence is asserted. Section references describe catalogue occurrence, not an activity-use or deployed-capability assertion.\n\n'+table(['Source label','Identifier','Occurrences','Source sections'],rows))
 conditions=sorted({str(v) for n in proposals for v in vals(n,A.applicabilityCondition)});cond_ids={v:'C'+str(i+1) for i,v in enumerate(conditions)};rows=[]
 for n in proposals:
  tool=next(g.objects(n,A.forTool));principle=next(g.objects(n,A.targetsPrinciple));rows.append([compact(n),label(tool),compact(principle),value(n,A.contributionType),value(n,A.normalizedMappingStatus),value(n,A.deploymentVerificationStatus),', '.join(cond_ids[str(v)] for v in vals(n,A.applicabilityCondition)),compact(next(g.objects(n,A.historicalRow)))])
 write('mapping-proposals.md','# Qualified tool principle proposals\n\nThese are historical proposed contributions. Direct and indirect support remain distinct. A category-level proposal is not evidence of implementation, resource FAIRness or organisational maturity. Each assertion carries its source row, scope, rationale and evidence requirement in RDF.\n\n'+table(['Assertion','Tool','Principle','Type','Review','Deployment','Conditions','Source row'],rows)+'\n## Implementation conditions\n\n'+ '\n\n'.join('**'+cond_ids[c]+'** '+c for c in conditions)+'\n')
 write('historical-dispositions.md','# Historical row dispositions\n\nThe RDF records all 131 historical data rows. Table headers remain in the original historical register, not as mapping assertions. Exact source text and line references remain pinned. Disposition does not imply substantive mapping approval.\n\n'+table(['Row','Source label','Section','Line','Disposition'],[[compact(n),value(n,A.sourceLabel),value(n,A.sourceSection),value(n,A.sourceLine),value(n,A.disposition)] for n in hist]))
 rows=[]
 for cap in caps:
  cells={value(n,A.levelLabel):value(n,A.progressionCode) for n in g.subjects(A.proposedCapability,cap) if (n,RDF.type,A.CapabilityProgressionProposal) in g};rows.append([label(cap),compact(cap)]+[cells.get('L'+str(i),'unknown') for i in range(6)])
 write('capability-proposals.md','# Capability progression proposals\n\nThese preserve the source P/E/M/absent progression codes as interpretations. They are not approved target profiles, intrinsic tool ratings or evidence that a deployment realises a capability. Existing interpretations are not equated with these proposal identifiers.\n\n'+table(['Label','Identifier','L0','L1','L2','L3','L4','L5'],rows))
 write('query-results.md','# Competency query results\n\nResults use only the explicit asserted union. Source and provenance graphs remain available by name. Expected synthetic fixtures are separate from actual production results. Zero rows preserve unknowns and inherited coverage exceptions. CQ10/CQ15 include lifecycle review targets; their counts are not counts of verified deployments.\n\n'+table(['Query','Production rows','Synthetic cases','Cases passed'],[[x['id'],x['production_rows'],len(x['cases']),sum(c['passed'] for c in x['cases'])] for x in cq])+'\nCQ02 preserves an unknown intermediate pathway when the historical source provides none. CQ18 requires matching implementation, scope, framework and complete condition sets with evidence; overlapping conditions alone are insufficient.\n')
 write('sources.md','# Pinned source inventory\n\nAll source documents are parsed separately. Archival, derived and inferred content is excluded from the default asserted view. The catalogue resolves imports locally; raw sources and declaration-only adapters retain distinct hashes.\n\n'+table(['Role','Local file','Triples','SHA-256'],[[r['role'],r['local_path'],r['triples'],r['sha256']] for r in manifest['source_graphs']]))
 sources=[r for r in lock['sources'] if r['role']=='asserted'];sources.sort(key=lambda r:r['ontology_IRIs'][0]);nodes={};labels={}
 for i,row in enumerate(sources):
  name='n'+str(i);labels[name]=Path(row['local_path']).name
  for iri in row['ontology_IRIs']+row['version_IRIs']:nodes[iri]=name
 edges=set()
 for row in sources:
  src=nodes[row['ontology_IRIs'][0]]
  for dep in row['dependencies']:
   if dep not in nodes:raise ValueError('Unresolved documented import '+dep)
   edges.add((src,nodes[dep]))
 entry=Graph().parse(ROOT/'dist/integrated-ontology.ttl')
 for dep in entry.objects(None,OWL.imports):edges.add(('integrated',nodes[str(dep)]))
 diagram='flowchart TD\n  integrated["Integrated ontology 1.0.0"]\n'+''.join(f'  {key}["{label}"]\n' for key,label in sorted(labels.items()))+''.join(f'  {src} -->|imports| {dest}\n' for src,dest in sorted(edges));write('architecture.mmd',diagram)
 summary={'counts':counts,'import_diagram_edges':len(edges),'input_graph':'dist/merged-asserted.ttl','documentation_version':config['documentation_version'],'files':sorted({p.name for p in OUT.iterdir() if p.is_file()}|{'generation-manifest.json'})}
 write('generation-manifest.json',json.dumps(summary,indent=2)+'\n');print(json.dumps(counts,indent=2))
if __name__=='__main__':generate()
