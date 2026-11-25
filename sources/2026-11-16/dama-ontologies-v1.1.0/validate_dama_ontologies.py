"""Offline RDF, SPARQL and source-fidelity validation; no imports are fetched.

This is a structural/documentary validator, not a complete OWL reasoner or an
operational FAIR assessment. Exits nonzero on any failed invariant.
"""
from pathlib import Path
import argparse,hashlib,json,re,unicodedata,zipfile,xml.etree.ElementTree as E
from collections import Counter
from rdflib import Graph,Namespace,URIRef,Literal,RDF,RDFS,OWL,XSD
from rdflib.collection import Collection
from rdflib.compare import isomorphic

ROOT=Path(__file__).resolve().parents[1]
BASE='https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/'
D=Namespace(BASE+'dama-ontology.ttl#');M=Namespace(BASE+'dama-fair-mapping.ttl#');P=Namespace(BASE+'dama-persona-ontology.ttl#')
F=Namespace('https://w3id.org/fair/principles/terms/');DC=Namespace('http://purl.org/dc/terms/');SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
FILES=['dama-ontology.ttl','dama-fair-mapping.ttl','dama-persona-ontology.ttl','fair-ontology.ttl']

def validate(directory,check_mirrors=False):
 directory=Path(directory);checks=[]
 def check(label,condition):
  checks.append({'check':label,'passed':bool(condition)})
  if not condition:raise AssertionError(label)
 graphs={name:Graph().parse(directory/name,format='turtle') for name in FILES}
 check('All four Turtle modules parse',len(graphs)==4)
 union=Graph()
 for graph in graphs.values():union+=graph
 area=graphs[FILES[0]];mapping=graphs[FILES[1]];persona=graphs[FILES[2]];fair=graphs[FILES[3]]
 before=ROOT/'outputs/ontology-update-20261116/before'
 old={name:Graph().parse(before/name,format='turtle') for name in FILES}
 check('External FAIR vocabulary bytes unchanged',hashlib.sha256((directory/FILES[3]).read_bytes()).hexdigest()==hashlib.sha256((before/FILES[3]).read_bytes()).hexdigest())
 core=set(area.subjects(RDF.type,D['DMBOK2-2017-KnowledgeArea']))
 check('Exactly 11 original core knowledge areas',len(core)==11 and core==set(old[FILES[0]].subjects(RDF.type,D['DMBOK2-2017-KnowledgeArea'])))
 definition=area.value(D['DMBOK2-2017-KnowledgeArea'],OWL.equivalentClass)
 check('Closed core enumeration remains exactly the original 11',set(Collection(area,area.value(definition,OWL.oneOf)))==core)
 check('Framework hasPart core list unchanged',set(area.objects(D['DMBOK2-2017'],DC.hasPart))==core)
 extra={D.BigDataAndDataScience,D.DataHandlingEthics,D.DataManagementMaturityAssessment}
 check('Additional topics have distinct, explicit classification',set(area.subjects(RDF.type,D.AdditionalTopic))==extra and not extra.intersection(core))
 check('Framework links all three additional topics separately',set(area.objects(D['DMBOK2-2017'],D.hasAdditionalTopic))==extra)
 check('Core and additional-topic classes are explicitly disjoint',(D.AdditionalTopic,OWL.disjointWith,D.KnowledgeArea) in area)
 check('The three supporting topics are explicitly distinct individuals',any(set(Collection(area,members))==extra for node in area.subjects(RDF.type,OWL.AllDifferent) for members in area.objects(node,OWL.distinctMembers)))
 check('Original DAMA individuals retain their identities',all((n,RDF.type,D['DMBOK2-2017-KnowledgeArea']) in area for n in core))
 valid_topics=core|extra
 for property_ in [M.inKnowledgeArea,M.inTopic,M.fromTopic]:
  check('Valid DAMA targets for '+str(property_).split('#')[-1],all(o in valid_topics for o in mapping.objects(None,property_)))
 check('No additional topic is used as an inKnowledgeArea target',not set(mapping.objects(None,M.inKnowledgeArea)).intersection(extra))
 check('inKnowledgeArea specializes the broader inTopic property',(M.inKnowledgeArea,RDFS.subPropertyOf,M.inTopic) in mapping)
 fair_ids={F[x] for x in ['F1','F2','F3','F4','A1','A1.1','A1.2','A2','I1','I2','I3','R1','R1.1','R1.2','R1.3']}
 check('FAIR vocabulary contains all 15 numbered IDs',set(fair.subjects(RDF.type,F['FAIR-SubPrinciple']))==fair_ids)
 for property_ in [M.targetsPrinciple,M.alignedPrinciple,M.evidenceForPrinciple,P.reportedDirectFAIRPrinciple,P.reportedIndirectFAIRPrinciple]:
  check('Valid FAIR targets for '+str(property_).split('#')[-1],set(union.objects(None,property_))<=fair_ids)
 old_mapping=old[FILES[1]]
 examples=set(old_mapping.subjects(RDF.type,M.DirectContribution))|set(old_mapping.subjects(RDF.type,M.IndirectContribution))
 check('All nine original practice examples retained',len(examples)==9 and all(set(old_mapping.triples((n,None,None)))<=set(mapping.triples((n,None,None))) for n in examples))
 direct=set(mapping.subjects(RDF.type,M.DirectContribution));indirect=set(mapping.subjects(RDF.type,M.IndirectContribution))
 check('Contribution counts: 7 direct, 33 indirect',len(direct)==7 and len(indirect)==33)
 check('No assertion is both direct and indirect',not direct.intersection(indirect))
 for node in direct|indirect:
  check('One source and FAIR target: '+str(node).split('#')[-1],len(set(mapping.objects(node,M.fromPractice)))==1 and len(set(mapping.objects(node,M.targetsPrinciple)))==1)
  source=mapping.value(node,M.fromPractice);pid=mapping.value(node,M.targetsPrinciple)
  check('Typed source practice: '+str(node).split('#')[-1],(source,RDF.type,M.Practice) in mapping or (source,RDF.type,M.SourceActivity) in mapping)
  check('Rationale and provenance: '+str(node).split('#')[-1],bool(mapping.value(node,M.rationale)) and bool(mapping.value(node,DC.source)))
  if node in indirect:
   via=set(mapping.objects(node,M.viaPractice))
   check('Indirect pathway and matching evidence practice: '+str(node).split('#')[-1],bool(via) and all((v,RDF.type,M.Practice) in mapping and (v,M.evidenceForPrinciple,pid) in mapping for v in via))
  else:check('Direct assertion has no indirect pathway: '+str(node).split('#')[-1],not list(mapping.objects(node,M.viaPractice)))
 doc=(ROOT/'DAMA_Segments_High_Level_v1.18.0.md').read_text(encoding='utf-8')
 records=[]
 for line in doc.split('## Persona\n',1)[1].split('## Appendix\n',1)[0].splitlines():
  if not line.startswith('| ') or line.startswith('| Persona / source name |'):continue
  cells=[re.sub(r'\\([\\*_`\[\]|])',r'\1',x.strip()) for x in re.split(r'(?<!\\)\|',line)[1:-1]]
  if all(re.fullmatch(r':?-+:?',cell) for cell in cells):continue
  records.append(cells)
 profiles=set(persona.subjects(RDF.type,P.Persona));by_label={str(persona.value(p,RDFS.label)):p for p in profiles}
 topics=set(persona.subjects(RDF.type,P.SourceTopic))
 check('123 persona names match the document without collisions',len(profiles)==123 and set(by_label)=={r[0] for r in records})
 check('All 108 original persona IRIs preserved',set(old[FILES[2]].subjects(RDF.type,P.Persona))<=profiles)
 check('All 15 numbered source topics represented',len(topics)==15)
 for row in records:
  node=by_label[row[0]]
  check('Persona description: '+row[0],str(persona.value(node,SKOS.definition))==row[1])
  for col,property_ in [(2,P.supplierIn),(3,P.participantIn),(4,P.consumerIn)]:
   expected={v.strip() for v in row[col].split(';') if v.strip()}
   actual={str(persona.value(t,RDFS.label)) for t in persona.objects(node,property_)}
   check('Persona '+str(property_).split('#')[-1]+': '+row[0],actual==expected)
  for col,property_ in [(5,P.reportedDirectFAIRPrinciple),(6,P.reportedIndirectFAIRPrinciple)]:
   expected={F[v.strip()] for v in row[col].split(',') if v.strip()}
   check('Persona '+str(property_).split('#')[-1]+': '+row[0],set(persona.objects(node,property_))==expected)
 check('Spelling variants retain distinct identities',by_label['CDO/CIO']!=by_label['CDO / CIO'])
 for prop in [P.correspondsToKnowledgeArea,P.partiallyCorrespondsToKnowledgeArea]:check('Core-only correspondence range '+str(prop).split('#')[-1],set(persona.objects(None,prop))<=core)
 check('Additional topics correspond through the topic property',all(list(persona.subjects(P.correspondsToTopic,n)) for n in extra))

 # Workbook -> JSON -> RDF fidelity: read only, no Excel calculation involved.
 newareas=json.loads((ROOT/'outputs/dama-20261116/new-areas.json').read_text(encoding='utf-8'))['areas']
 N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(ROOT/'outputs/dama-20261116/DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx') as z:
  rels={n.attrib['Id']:n.attrib['Target'] for n in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
  sheets={sh.attrib['name']:rels[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']] for sh in E.fromstring(z.read('xl/workbook.xml')).find('s:sheets',N)}
  expected_assertions=set();expected_role_links=set()
  for item in newareas:
   target=sheets[item['sheet']];target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
   tree=E.fromstring(z.read(target));cells={c.attrib['r']:(''.join(t.text or '' for t in c.findall('.//s:t',N)) if c.attrib.get('t')=='inlineStr' else c.findtext('s:v',default='',namespaces=N)) for c in tree.findall('.//s:c',N)}
   for r,row in enumerate(item['rows'],2):
    check(f'Exact workbook row {item["sheet"]}!{r}',[cells.get(chr(65+c)+str(r),'') for c in range(12)]==row)
    node=URIRef(str(M)+f'activity/{item["sheet"]}/row-{r}')
    check('Activity label and row provenance '+item['sheet']+str(r),str(mapping.value(node,RDFS.label))==row[0] and int(mapping.value(node,M.sourceRow))==r)
    for c,prop in [(2,M.proposedResponsiblePersona),(3,M.proposedApprovingPersona),(4,M.proposedContributingPersona)]:
     expected={by_label[v.strip()] for v in row[c].split(';') if v.strip()}
     check('Proposed activity roles '+item['sheet']+str(r)+'/'+str(c),set(mapping.objects(node,prop))==expected)
    for c,typ in [(7,M.DirectContribution),(11,M.IndirectContribution)]:
     for pid in [v.strip() for v in row[c].split(';') if v.strip()]:expected_assertions.add((node,F[pid],typ))
    check('Activity evidence requirement '+item['sheet']+str(r),str(mapping.value(node,M.evidenceRequirement))==row[10])
    check('No inferred implementation claim '+item['sheet']+str(r),'Proposed' in str(mapping.value(node,M.assessmentStatus)))
 actual_assertions={(mapping.value(a,M.fromPractice),mapping.value(a,M.targetsPrinciple),typ) for typ in [M.DirectContribution,M.IndirectContribution] for a in mapping.subjects(RDF.type,typ) if a not in examples}
 check('All 31 new activity contributions match the source cells exactly',len(expected_assertions)==31 and actual_assertions==expected_assertions)
 source_activities=set(mapping.subjects(RDF.type,M.SourceActivity))
 check('All 16 source activities retained, including unmapped training',len(source_activities)==16)
 check('No direct Ethics mapping invented',not any('DataHandlingEthics' in str(n) for n,p,t in actual_assertions if t==M.DirectContribution))
 check('Only the documented conditional R1 direct Big Data mapping',[(str(n).split('#')[-1],str(p).split('/')[-1]) for n,p,t in actual_assertions if t==M.DirectContribution]==[('activity/BigDataDataScience/row-6','R1')])
 for prop in [M.proposedResponsiblePersona,M.proposedApprovingPersona,M.proposedContributingPersona]:check('No dangling persona references '+str(prop).split('#')[-1],set(mapping.objects(None,prop))<=profiles)

 visual=json.loads((ROOT/'outputs/dama-fair-sankey-v1.3.0/data.json').read_text(encoding='utf-8'))
 assessments=set(mapping.subjects(RDF.type,M.AreaAlignmentAssessment))
 check('Exactly 74 area-level assessments',len(assessments)==74)
 expected={(l['source'],l['target'],l['kind'],l['basis'],l['description']) for l in visual['links']}
 actual={(str(area.value(mapping.value(n,M.fromTopic),RDFS.label)),str(mapping.value(n,M.alignedPrinciple)).split('/')[-1],str(mapping.value(n,M.alignmentType)),str(mapping.value(n,M.alignmentBasis)),str(mapping.value(n,M.rationale))) for n in assessments}
 check('Every Sankey record agrees exactly with the area assessment layer',actual==expected)
 check('Area assessments are not practice contributions',not assessments.intersection(direct|indirect))
 check('Area and practice assessment classes are explicitly disjoint',(M.AreaAlignmentAssessment,OWL.disjointWith,M.FAIRContribution) in mapping)
 check('All 13 additional-topic Sankey links reference source activities',sum(bool(list(mapping.objects(n,M.derivedFromActivity))) for n in assessments)==13)
 check('Area mapping counts: 52 Direct / 10 Enabling / 12 Indirect',Counter(str(mapping.value(n,M.alignmentType)) for n in assessments)=={'Direct':52,'Enabling':10,'Indirect':12})
 # Confirm expected doc heading fragments for the DAMA source declarations.
 headings=set()
 for heading in re.findall(r'(?m)^#{1,4} (.+)$',doc):headings.add(''.join(c for c in heading.lower() if c in '-_ ' or unicodedata.category(c)[0] in ('L','N','M')).replace(' ','-'))
 sources=list(union.objects(None,DC.source))
 check('Document source anchors resolve',all(str(s).split('#',1)[1] in headings for s in sources if 'DAMA_Segments_High_Level_v1.18.0.md#' in str(s)))
 check('Ontology revision metadata is consistent',all(str(graphs[name].value(URIRef(BASE+name),OWL.versionInfo))=='1.1.0' for name in FILES[:3]))
 # Execute independent cross-module joins rather than merely parsing the TTL.
 bindings={'dama':D,'map':M,'persona':P,'rdf':RDF,'rdfs':RDFS}
 query='''SELECT DISTINCT ?persona ?topic ?area WHERE {
 ?persona persona:participantIn ?topic .
 ?topic persona:correspondsToTopic ?area .
 ?area a dama:AdditionalTopic . }'''
 rows=list(union.query(query,initNs=bindings))
 check('SPARQL cross-module persona/additional-topic query returns all new topic groups',{r[2] for r in rows}==extra)
 query='''SELECT ?assertion ?intermediate ?principle WHERE {
 ?assertion a map:IndirectContribution ; map:targetsPrinciple ?principle ; map:viaPractice ?intermediate .
 ?intermediate map:evidenceForPrinciple ?principle . }'''
 check('SPARQL resolves every indirect evidence pathway',len(list(union.query(query,initNs=bindings)))==33)
 if check_mirrors:
  for name in FILES:check('Repository mirror equivalent: '+name,isomorphic(graphs[name],Graph().parse(ROOT/'research-repos/FAIR-DAMA/artefacts'/name,format='turtle')))
 report={'version':'1.1.0','status':'passed','method':'RDFLib Turtle parsing, explicit RDF/OWL structural invariants, source fidelity and offline SPARQL joins. No remote imports or complete OWL reasoning.','checksPassed':len(checks),'checks':checks,'triples':{name:len(g) for name,g in graphs.items()},'counts':{'coreAreas':11,'additionalTopics':3,'personas':123,'sourceActivities':16,'originalExampleContributions':9,'newActivityContributions':31,'directContributions':7,'indirectContributions':33,'areaAlignments':74}}
 (directory/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 (directory/'VALIDATION.md').write_text('# DAMA–FAIR ontology validation\n\nVersion: 1.1.0\n\n**Passed '+str(len(checks))+' checks.**\n\n'+report['method']+'\n\n| Check group | Result |\n|---|---|\n| Core area identity and closed enumeration | 11 original areas retained |\n| Additional topics | Big Data & Data Science, Data Handling Ethics, Maturity Assessment kept separate |\n| Persona fidelity | 123 source entries, all role categories and reported FAIR links matched |\n| Source activities | All 16 rows, roles and evidence matched to the workbook |\n| Practice contributions | Nine original examples plus 31 source-derived assertions |\n| Indirect pathways | All 33 assertions have typed evidence-producing intermediate practices |\n| Area-level proposals | All 74 Sankey records retained separately |\n| Source provenance | Document anchors and worksheet rows checked |\n| FAIR vocabulary | All 15 IDs present; original vocabulary bytes unchanged |\n\nThe remaining five indirect-only principles in the activity-based analysis remain F1, F3, A1.1, A2 and R1.1. The broader implementation proposal must not be substituted for that analysis. This validation does not demonstrate that any dataset or metadata service is FAIR.\n',encoding='utf-8')
 print(f'PASS: {len(checks)} checks; '+', '.join(f'{name}: {len(g)} triples' for name,g in graphs.items()))
 return report

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--ontology-dir',type=Path);parser.add_argument('--source-root',type=Path,default=ROOT);parser.add_argument('--check-mirrors',action='store_true');args=parser.parse_args()
 ROOT=args.source_root.resolve()
 validate(args.ontology_dir or ROOT/'outputs/dama-ontologies-v1.1.0',args.check_mirrors)
