"""Build the v1.1.0 ontology revision from the v1.18.0 document and v1.3.0 Sankey.

Stages changes before validation. Existing example contributions and identifiers
are retained; activity, area-proposal and persona evidence layers stay distinct.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,unicodedata
from rdflib import Graph,Namespace,URIRef,Literal,BNode,RDF,RDFS,OWL,XSD
from rdflib.collection import Collection

ROOT=Path(__file__).resolve().parents[1]
BASE='https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/'
D=Namespace(BASE+'dama-ontology.ttl#');M=Namespace(BASE+'dama-fair-mapping.ttl#')
P=Namespace(BASE+'dama-persona-ontology.ttl#');F=Namespace('https://w3id.org/fair/principles/terms/')
DC=Namespace('http://purl.org/dc/terms/');SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')
STAGE=ROOT/'outputs/dama-ontologies-v1.1.0'
WORK=ROOT/'outputs/ontology-update-20261116'
DOCNAME='DAMA_Segments_High_Level_v1.18.0.md'
DOC=URIRef(BASE+DOCNAME)
BOOK=URIRef(BASE+'outputs/dama-20261116/DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx')
FILES=['dama-ontology.ttl','dama-fair-mapping.ttl','dama-persona-ontology.ttl','fair-ontology.ttl']

def normalized(text):
 text=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',text).strip('-')

def annotation(g,prop,label):
 g.add((prop,RDF.type,OWL.AnnotationProperty));g.add((prop,RDFS.label,Literal(label,lang='en')))

def objprop(g,prop,label,domain,range_):
 g.add((prop,RDF.type,OWL.ObjectProperty));g.add((prop,RDFS.label,Literal(label,lang='en')))
 g.add((prop,RDFS.domain,domain));g.add((prop,RDFS.range,range_))

def cls(g,term,label,parent=None):
 g.add((term,RDF.type,OWL.Class));g.add((term,RDFS.label,Literal(label,lang='en')))
 if parent:g.add((term,RDFS.subClassOf,parent))

def individual(g,term,type_,label):
 g.add((term,RDF.type,OWL.NamedIndividual));g.add((term,RDF.type,type_));g.add((term,RDFS.label,Literal(label,lang='en')))

def revision(g,name):
 ontology=URIRef(BASE+name)
 g.set((ontology,OWL.versionInfo,Literal('1.1.0')))
 g.set((ontology,DC.modified,Literal('2026-11-16',datatype=XSD.date)))
 g.add((ontology,DC.source,DOC))

def build():
 STAGE.mkdir(exist_ok=True,parents=True);WORK.mkdir(exist_ok=True,parents=True)
 before=WORK/'before';before.mkdir(exist_ok=True)
 for name in FILES:
  if not (before/name).exists():shutil.copy2(ROOT/name,before/name)
 if not (before/'ontologies.md').exists():shutil.copy2(ROOT/'ontologies.md',before/'ontologies.md')
 graphs={name:Graph().parse(before/name,format='turtle') for name in FILES}
 for graph in graphs.values():
  for prefix,ns in [('dama',D),('map',M),('persona',P),('fair',F),('dcterms',DC),('skos',SKOS)]:graph.bind(prefix,ns)
 area=graphs['dama-ontology.ttl'];mapping=graphs['dama-fair-mapping.ttl'];persona=graphs['dama-persona-ontology.ttl']
 activities=json.loads((ROOT/'outputs/dama-20261116/new-areas.json').read_text(encoding='utf-8'))['areas']
 sankey=json.loads((ROOT/'outputs/dama-fair-sankey-v1.3.0/data.json').read_text(encoding='utf-8'))
 document=(ROOT/DOCNAME).read_text(encoding='utf-8')
 for name in FILES[:3]:revision(graphs[name],name)

 # A superclass admits additional topics without widening the closed 11-area
 # enumeration, hasPart list or AllDifferent list of the original vocabulary.
 cls(area,D.ManagementTopic,'Data management topic')
 area.add((D.KnowledgeArea,RDFS.subClassOf,D.ManagementTopic))
 cls(area,D.AdditionalTopic,'Additional DMBOK topic',D.ManagementTopic)
 area.add((D.AdditionalTopic,OWL.disjointWith,D.KnowledgeArea))
 objprop(area,D.hasAdditionalTopic,'has additional topic',D.FrameworkEdition,D.AdditionalTopic)
 extra={'Big Data & Data Science':D.BigDataAndDataScience,'Data Handling Ethics':D.DataHandlingEthics,'Data Management Maturity Assessment':D.DataManagementMaturityAssessment}
 for item in activities:
  node=extra[item['name']]
  individual(area,node,D.AdditionalTopic,item['name'])
  area.add((node,SKOS.definition,Literal(item['definition'].removeprefix('Working summary: '),lang='en')))
  heading=f'{item["number"]}. {item["name"]}'
  anchor=''.join(c for c in heading.lower() if c in '-_ ' or unicodedata.category(c)[0] in ('L','N','M')).replace(' ','-')
  area.add((node,DC.source,URIRef(str(DOC)+'#'+anchor)))
  area.add((node,DC.source,URIRef(BASE+'assets/'+item['image'])))
  area.add((node,RDFS.isDefinedBy,URIRef(BASE+'dama-ontology.ttl')))
  area.add((D['DMBOK2-2017'],D.hasAdditionalTopic,node))
 individual(area,D.DataManagementMaturityAssessment,D.AdditionalTopic,'Data Management Maturity Assessment')
 area.add((D.DataManagementMaturityAssessment,SKOS.definition,Literal('Assess data management capabilities against a maturity framework and prioritize, plan and monitor improvements.',lang='en')))
 area.add((D.DataManagementMaturityAssessment,DC.source,URIRef(str(DOC)+'#12-data-management-maturity-assessment')))
 area.add((D['DMBOK2-2017'],D.hasAdditionalTopic,D.DataManagementMaturityAssessment))
 distinct=BNode();members=BNode()
 area.add((distinct,RDF.type,OWL.AllDifferent));area.add((distinct,OWL.distinctMembers,members))
 Collection(area,members,list(extra.values()))
 area.set((URIRef(BASE+'dama-ontology.ttl'),DC.description,Literal('The eleven core DAMA-DMBOK2 knowledge areas and three explicitly separate supporting topics. The core enumeration remains unchanged.',lang='en')))

 # Update the persona catalog exactly from the current documentary table.
 block=document.split('## Persona\n',1)[1].split('## Appendix\n',1)[0]
 records=[]
 for line in block.splitlines():
  if not line.startswith('| ') or line.startswith('| Persona / source name |'):continue
  cells=[re.sub(r'\\([\\*_`\[\]|])',r'\1',c.strip()) for c in re.split(r'(?<!\\)\|',line)[1:-1]]
  if all(re.fullmatch(r':?-+:?',cell) for cell in cells):continue
  assert len(cells)==7
  records.append(cells)
 assert len(records)==123
 existing={str(persona.value(n,RDFS.label)):n for n in persona.subjects(RDF.type,P.Persona)}
 used=set(existing.values());profiles={}
 topics={str(persona.value(n,RDFS.label)):n for n in persona.subjects(RDF.type,P.SourceTopic)}
 objprop(persona,P.correspondsToTopic,'corresponds to management topic',P.SourceTopic,D.ManagementTopic)
 persona.add((P.correspondsToKnowledgeArea,RDFS.subPropertyOf,P.correspondsToTopic))
 objprop(persona,P.partiallyCorrespondsToKnowledgeArea,'partially corresponds to knowledge area',P.SourceTopic,D.KnowledgeArea)
 persona.add((P.partiallyCorrespondsToKnowledgeArea,RDFS.comment,Literal('A partial documentary correspondence; it is not identity or complete coverage.',lang='en')))
 for label,node in extra.items():
  topic=topics.setdefault(label,URIRef(str(P)+'topic/'+normalized(label)))
  individual(persona,topic,P.SourceTopic,label);persona.add((topic,P.correspondsToTopic,node))
 persona.add((topics['Data Development'],P.partiallyCorrespondsToKnowledgeArea,D.DataModelingAndDesign))
 for cells in records:
  label,definition=cells[:2]
  node=existing.get(label)
  if node is None:
   candidate=URIRef(str(P)+'profile/'+normalized(label))
   node=candidate if candidate not in used else URIRef(str(candidate)+'-'+hashlib.sha256(label.encode()).hexdigest()[:8])
  used.add(node);profiles[label]=node
  individual(persona,node,P.Persona,label)
  persona.set((node,SKOS.definition,Literal(definition,lang='en')))
  persona.set((node,DC.source,URIRef(str(DOC)+'#persona')))
  for column,property_ in [(2,P.supplierIn),(3,P.participantIn),(4,P.consumerIn),(5,P.reportedDirectFAIRPrinciple),(6,P.reportedIndirectFAIRPrinciple)]:
   persona.remove((node,property_,None))
   values=[v.strip() for v in re.split(';' if column<5 else ',',cells[column]) if v.strip()]
   for value in values:
    target=topics[value] if column<5 else F[value]
    persona.add((node,property_,target))
 persona.set((URIRef(BASE+'dama-persona-ontology.ttl'),DC.source,URIRef(str(DOC)+'#persona')))
 for prop in [P.reportedDirectFAIRPrinciple,P.reportedIndirectFAIRPrinciple]:
  persona.set((prop,RDFS.comment,Literal('Area-level relationship reported in the v1.18.0 persona table; inferred from listed topic membership, not individual responsibility or implementation evidence.',lang='en')))

 # Retain original practice semantics. A topic-level property is needed so the
 # new topics are not accidentally inferred to belong to the core area class.
 objprop(mapping,M.inTopic,'in management topic',M.Practice,D.ManagementTopic)
 mapping.add((M.inKnowledgeArea,RDFS.subPropertyOf,M.inTopic))
 cls(mapping,M.SourceActivity,'Source activity',M.Practice)
 for prop,label in [(M.alignmentBasis,'alignment basis'),(M.evidenceRequirement,'evidence requirement'),(M.assessmentStatus,'assessment status'),(M.sourceWorksheet,'source worksheet'),(M.sourceRow,'source row'),(M.lifecycleCode,'lifecycle code'),(M.deliverables,'deliverables'),(M.relevantDeliverables,'relevant deliverables'),(M.directSupportExplanation,'direct support explanation'),(M.indirectSupportExplanation,'indirect support explanation')]:annotation(mapping,prop,label)
 for prop,label in [(M.proposedResponsiblePersona,'proposed responsible persona'),(M.proposedApprovingPersona,'proposed approving persona'),(M.proposedContributingPersona,'proposed contributing persona')]:objprop(mapping,prop,label,M.SourceActivity,P.Persona)
 objprop(mapping,M.evidenceForPrinciple,'provides evidence for principle',M.Practice,F['FAIR-SubPrinciple'])
 target_practices={
  'A1.2':M.ConfigureRetrievalAuthorization,'R1.1':M.AttachUsageLicense,
  'I1':M.PublishSharedRepresentation,'R1.2':M.PublishProvenance,
  'F2':M.PublishRichDiscoveryMetadata,'A1':M.EnableIdentifierBasedRetrieval,
  'A1.1':M.ImplementOpenRetrievalProtocol,'I3':M.PublishQualifiedResourceReferences,
  'R1':M.PublishRichReuseDescriptions,'R1.3':M.ValidateCommunityStandards}
 practice_definitions={
  'F2':('Publish rich resource discovery descriptions',D.MetadataManagement),
  'A1':('Implement retrieval by identifier through a standardized protocol',D.DataIntegrationAndInteroperability),
  'A1.1':('Implement an open, free, universally implementable retrieval protocol',D.DataIntegrationAndInteroperability),
  'I3':('Publish explicit typed references to related identified resources',D.MetadataManagement),
  'R1':('Publish accurate and relevant resource descriptions for reuse',D.MetadataManagement),
  'R1.3':('Validate resources against applicable domain community standards',D.DataQualityManagement)}
 for pid,node in target_practices.items():
  if pid in practice_definitions:
   label,ka=practice_definitions[pid];individual(mapping,node,M.Practice,label)
   mapping.add((node,M.inKnowledgeArea,ka));mapping.add((node,M.assessmentStatus,Literal('Proposed evidence-producing practice; implementation not asserted',lang='en')))
  mapping.add((node,M.evidenceForPrinciple,F[pid]))
 activity_nodes={};assertions=[]
 for item in activities:
  for index,row in enumerate(item['rows'],2):
   node=URIRef(str(M)+f'activity/{item["sheet"]}/row-{index}')
   activity_nodes[(item['sheet'],index)]=node
   individual(mapping,node,M.SourceActivity,row[0]);mapping.add((node,M.inTopic,extra[item['name']]))
   mapping.add((node,M.sourceWorksheet,Literal(item['sheet'])))
   mapping.add((node,M.sourceRow,Literal(index,datatype=XSD.integer)))
   mapping.add((node,DC.identifier,Literal(f'{item["sheet"]}!A{index}:L{index}')))
   mapping.add((node,DC.source,URIRef(str(BOOK)+'#'+item['sheet']+f'!A{index}:L{index}')))
   mapping.add((node,DC.source,URIRef(BASE+'assets/'+item['image'])))
   for prop,col in [(M.deliverables,1),(M.lifecycleCode,5),(M.relevantDeliverables,6),(M.directSupportExplanation,8),(M.indirectSupportExplanation,9),(M.evidenceRequirement,10)]:mapping.add((node,prop,Literal(row[col],lang='en')))
   mapping.add((node,M.alignmentBasis,Literal('Activity-derived proposal; source image plus interpreted associations',lang='en')))
   mapping.add((node,M.assessmentStatus,Literal('Proposed; no implementation or compliance asserted',lang='en')))
   for col,prop in [(2,M.proposedResponsiblePersona),(3,M.proposedApprovingPersona),(4,M.proposedContributingPersona)]:
    for name in [v.strip() for v in row[col].split(';') if v.strip()]:
     assert name in profiles,name
     mapping.add((node,prop,profiles[name]))
   for col,type_,explanation in [(7,M.DirectContribution,8),(11,M.IndirectContribution,9)]:
    for pid in [v.strip() for v in row[col].split(';') if v.strip()]:
     assertion=URIRef(str(M)+f'contribution/{item["sheet"]}/row-{index}/'+('direct' if col==7 else 'indirect')+'/'+pid)
     individual(mapping,assertion,type_,row[0]+' → '+pid)
     mapping.add((assertion,M.fromPractice,node));mapping.add((assertion,M.targetsPrinciple,F[pid]))
     mapping.add((assertion,M.rationale,Literal(row[explanation],lang='en')))
     mapping.add((assertion,M.applicabilityCondition,Literal(row[10],lang='en')))
     mapping.add((assertion,M.evidenceRequirement,Literal(row[10],lang='en')))
     mapping.add((assertion,M.assessmentStatus,Literal('Proposed; no implementation or compliance asserted',lang='en')))
     mapping.add((assertion,M.alignmentBasis,Literal('Activity-derived proposal',lang='en')))
     mapping.add((assertion,DC.source,URIRef(str(BOOK)+'#'+item['sheet']+f'!A{index}:L{index}')))
     if col==11:mapping.add((assertion,M.viaPractice,target_practices[pid]))
     assertions.append(assertion)

 # Preserve the 74 Sankey links as a separate area-level assessment layer;
 # never type these as practice-level FAIRContribution assertions.
 cls(mapping,M.AreaAlignmentAssessment,'Proposed area-to-FAIR alignment assessment')
 mapping.add((M.AreaAlignmentAssessment,OWL.disjointWith,M.FAIRContribution))
 objprop(mapping,M.fromTopic,'from management topic',M.AreaAlignmentAssessment,D.ManagementTopic)
 objprop(mapping,M.alignedPrinciple,'aligned FAIR principle',M.AreaAlignmentAssessment,F['FAIR-SubPrinciple'])
 objprop(mapping,M.derivedFromActivity,'derived from source activity',M.AreaAlignmentAssessment,M.SourceActivity)
 annotation(mapping,M.alignmentType,'alignment type')
 terms={'Data Governance':D.DataGovernance,'Data Architecture':D.DataArchitecture,'Data Modeling & Design':D.DataModelingAndDesign,'Data Storage & Operations':D.DataStorageAndOperations,'Data Security':D.DataSecurity,'Data Integration & Interoperability':D.DataIntegrationAndInteroperability,'Documents & Content Management':D.DocumentsAndContentManagement,'Reference & Master Data Management':D.ReferenceAndMasterDataManagement,'Data Warehousing & Business Intelligence':D.DataWarehousingAndBusinessIntelligence,'Metadata Management':D.MetadataManagement,'Data Quality Management':D.DataQualityManagement,**extra}
 visual_source=URIRef(BASE+'DAMA_FAIR_Sankey_v1.3.0.zip')
 for link in sankey['links']:
  node=URIRef(str(M)+'area-alignment/'+normalized(link['source'])+'/'+link['kind'].lower()+'/'+link['target'])
  individual(mapping,node,M.AreaAlignmentAssessment,link['source']+' → '+link['target']+' ('+link['kind']+')')
  mapping.add((node,M.fromTopic,terms[link['source']]))
  mapping.add((node,M.alignedPrinciple,F[link['target']]))
  mapping.add((node,M.alignmentType,Literal(link['kind'])))
  mapping.add((node,M.alignmentBasis,Literal(link['basis'],lang='en')))
  mapping.add((node,M.rationale,Literal(link['description'],lang='en')))
  mapping.add((node,M.deliverables,Literal(link['deliverables'],lang='en')))
  mapping.add((node,M.assessmentStatus,Literal('Proposed; no implementation or compliance asserted',lang='en')))
  mapping.add((node,DC.source,visual_source))
  for evidence in link.get('activityEvidence',[]):
   match=re.match(r'([^!]+)!A(\d+):L\d+',evidence['worksheetRange']);key=(match[1],int(match[2]))
   mapping.add((node,M.derivedFromActivity,activity_nodes[key]))

 for name in FILES:
  if name=='fair-ontology.ttl':shutil.copy2(ROOT/name,STAGE/name)
  else:graphs[name].serialize(STAGE/name,format='turtle',encoding='utf-8')
 metadata={'version':'1.1.0','document':DOCNAME,'sankeyVersion':'1.3.0','coreAreas':11,'additionalTopics':3,'personas':123,'sourceActivities':16,'newActivityContributions':len(assertions),'newDirectActivityContributions':1,'newIndirectActivityContributions':30,'preservedExampleContributions':9,'areaAlignments':74,'sourceSha256':{str(path.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in [ROOT/DOCNAME,ROOT/'outputs/dama-fair-sankey-v1.3.0/data.json',ROOT/'outputs/dama-20261116/new-areas.json']}}
 (STAGE/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
 print(f'Staged {STAGE}: 11 core areas + 3 separate topics, 123 personas, 16 source activities, 31 new practice assertions and 74 separate area assessments.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source-root',type=Path,default=ROOT);args=parser.parse_args()
 ROOT=args.source_root.resolve();STAGE=ROOT/'outputs/dama-ontologies-v1.1.0';WORK=ROOT/'outputs/ontology-update-20261116'
 build()
