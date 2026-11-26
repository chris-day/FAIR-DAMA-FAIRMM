"""Executable CQ contracts and hand-authored synthetic expected results."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PREFIX='''PREFIX a: <urn:fair-dama-fairmm:alignment:>
PREFIX cap: <urn:capability-ontology:>
PREFIX dama: <https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-ontology.ttl#>
PREFIX persona: <https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl#>
PREFIX map: <https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-fair-mapping.ttl#>
PREFIX fair: <https://w3id.org/fair/principles/terms/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX i: <urn:fair-dama-fairmm:integrated:>
PREFIX ex: <urn:g4-fixture:>
'''
EX='urn:g4-fixture:'
gap='''OPTIONAL { ?real a cap:Realisation ; cap:forImplementation ?implementation ; cap:realisesCapability ?capability ; cap:inScope ?scope ; cap:verificationState cap:Verified ; cap:hasEvidence ?e ; cap:requiresCondition ?condition . ?e a cap:Evidence . ?condition a cap:ImplementationCondition . BIND("present" AS ?present) }
 OPTIONAL { ?notApplicable a cap:Realisation ; cap:realisesCapability ?capability ; cap:inScope ?scope ; cap:verificationState cap:NotApplicable . BIND("not applicable" AS ?na) }
 OPTIONAL { ?assessment cap:requiresCapability ?capability ; cap:inScope ?scope ; a:evidenceStatus "explicitly absent" . BIND("missing" AS ?absent) }
 BIND(IF(BOUND(?present), "present", IF(BOUND(?na), "not applicable", IF(BOUND(?absent), "missing", "unknown"))) AS ?gap)
 FILTER(?gap IN ("missing","unknown"))'''
specs={}
def add(n,query,pos,positive,neg='',negative=None,**kwargs):
 specs[f'CQ{n:02}']={'query':PREFIX+query,'cases':{'positive':{'data':PREFIX+pos,'expected':positive},'negative':{'data':PREFIX+neg,'expected':[] if negative is None else negative},'empty':{'data':PREFIX,'expected':[]}},**kwargs}
add(1,'''SELECT DISTINCT ?tool ?status ?condition WHERE { ?m a a:ToolPrincipleProposal ; a:forTool ?tool ; a:targetsPrinciple fair:F4 ; a:contributionType "Direct" ; a:normalizedMappingStatus ?status ; a:applicabilityCondition ?condition }''',
 'ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:F4; a:contributionType "Direct"; a:normalizedMappingStatus "proposed"; a:applicabilityCondition "condition" .',[[EX+'tool','proposed','condition']],
 'ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:F4; a:contributionType "Indirect"; a:normalizedMappingStatus "proposed"; a:applicabilityCondition "condition" .')
add(2,'''SELECT DISTINCT ?tool ?status ?condition WHERE { ?m a a:ToolPrincipleProposal ; a:forTool ?tool ; a:targetsPrinciple fair:R1.2 ; a:contributionType "Indirect" ; a:normalizedMappingStatus ?status ; a:applicabilityCondition ?condition }''',
 'ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:R1.2; a:contributionType "Indirect"; a:normalizedMappingStatus "proposed"; a:applicabilityCondition "condition" .',[[EX+'tool','proposed','condition']],
 'ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:R1.2; a:contributionType "Direct"; a:normalizedMappingStatus "proposed"; a:applicabilityCondition "condition" .')
add(3,'''SELECT DISTINCT ?tool ?scope WHERE { ?m a:forTool ?tool ; a:supportedByDescriptor ?cell ; cap:inScope ?scope . ?cell a:inDimension a:D7 ; a:atLevel a:L3 }''',
 'ex:m a:forTool ex:tool; a:supportedByDescriptor a:D7-L3; cap:inScope ex:scope . a:D7-L3 a:inDimension a:D7; a:atLevel a:L3 .',[[EX+'tool',EX+'scope']],
 'ex:m a a:MaturityRangeProposal; a:forTool ex:tool; a:targetsDimension a:D7; a:rangeSummary "L1–L5"; cap:inScope ex:scope .')
add(4,'''SELECT DISTINCT ?capability ?scope WHERE { ?m a:proposedCapability ?capability ; a:supportedByDescriptor ?cell ; cap:inScope ?scope ; a:normalizedMappingStatus "approved" . ?cell a:inDimension a:D7 ; a:atLevel a:L4 }''',
 'ex:m a:proposedCapability ex:capability; a:supportedByDescriptor a:D7-L4; cap:inScope ex:scope; a:normalizedMappingStatus "approved" . a:D7-L4 a:inDimension a:D7; a:atLevel a:L4 .',[[EX+'capability',EX+'scope']],
 'ex:m a a:CapabilityProgressionProposal; a:proposedCapability ex:capability; a:levelLabel "L4"; a:progressionCode "M" .')
profile='ex:profile a cap:Profile; cap:inScope ex:scope; a:normalizedMappingStatus "approved"; a:targetsLevel a:L4; cap:hasRequirement ex:req . ex:req cap:requiresCapability ex:capability . '
real='ex:real a cap:Realisation; cap:forImplementation ex:implementation; cap:realisesCapability ex:capability; cap:inScope ex:scope; cap:verificationState cap:Verified; cap:hasEvidence ex:evidence; cap:requiresCondition ex:condition . ex:evidence a cap:Evidence . ex:condition a cap:ImplementationCondition . '
add(5,'''SELECT DISTINCT ?capability ?gap WHERE { ?target a cap:Profile ; a:targetsLevel a:L4 ; cap:hasRequirement/cap:requiresCapability ?capability ; cap:inScope ?scope ; a:normalizedMappingStatus "approved" . FILTER NOT EXISTS { ?base a cap:Profile ; a:targetsLevel a:L3 ; cap:hasRequirement/cap:requiresCapability ?capability ; cap:inScope ?scope ; a:normalizedMappingStatus "approved" } '''+gap+' }',
 profile,[[EX+'capability','unknown']],profile+'ex:base a cap:Profile; a:targetsLevel a:L3; cap:hasRequirement ex:req; cap:inScope ex:scope; a:normalizedMappingStatus "approved" .')
add(6,'''SELECT DISTINCT ?activity ?tool WHERE { ?activity prov:used ?tool . ?m a a:ToolPrincipleProposal ; a:forTool ?tool ; a:targetsPrinciple fair:I1 ; a:applicabilityCondition ?condition }''',
 'ex:activity prov:used ex:tool . ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:I1; a:applicabilityCondition "condition" .',[[EX+'activity',EX+'tool']],
 'ex:activity map:inTopic dama:MetadataManagement . ex:m a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:I1; a:applicabilityCondition "condition" .')
add(7,'''SELECT DISTINCT ?principle WHERE { ?principle a fair:FAIR-SubPrinciple . FILTER NOT EXISTS { ?m a a:ToolPrincipleProposal ; a:targetsPrinciple ?principle ; a:contributionType "Direct" } }''',
 'fair:F4 a fair:FAIR-SubPrinciple . ex:m a a:ToolPrincipleProposal; a:targetsPrinciple fair:F4; a:contributionType "Indirect" .', [['https://w3id.org/fair/principles/terms/F4']],
 'fair:F4 a fair:FAIR-SubPrinciple . ex:m a a:ToolPrincipleProposal; a:targetsPrinciple fair:F4; a:contributionType "Direct" .')
add(8,'''SELECT ?tool (COUNT(DISTINCT ?dimension) AS ?dimensions) WHERE { ?m a:forTool ?tool ; a:targetsDimension ?dimension } GROUP BY ?tool HAVING(COUNT(DISTINCT ?dimension)>1)''',
 'ex:m1 a:forTool ex:tool; a:targetsDimension a:D1 . ex:m2 a:forTool ex:tool; a:targetsDimension a:D7 . ex:m3 a:forTool ex:tool; a:targetsDimension a:D7 .',[[EX+'tool','2']],
 'ex:m1 a:forTool ex:tool; a:targetsDimension a:D7 . ex:m2 a:forTool ex:tool; a:targetsDimension a:D7 .')
add(9,'''SELECT DISTINCT ?mapping ?source ?rationale ?digest WHERE { ?mapping a a:ToolPrincipleProposal ; dct:source ?source ; a:rationale ?rationale . GRAPH <urn:fair-dama-fairmm:graph:provenance:1.0.0> { ?graph i:role "asserted" ; i:sha256 ?digest } GRAPH ?graph { ?mapping dct:source ?source } }''',
 'ex:m a a:ToolPrincipleProposal; dct:source ex:source; a:rationale "reason" .',[[EX+'m',EX+'source','reason','fixture-hash']],
 'ex:m a a:ToolPrincipleProposal; dct:source ex:source; a:rationale "reason" .',fixture_named_source=True)
add(10,'''SELECT DISTINCT ?mapping ?status ?verification WHERE { { ?mapping a:normalizedMappingStatus ?status ; a:deploymentVerificationStatus ?verification . FILTER NOT EXISTS { ?mapping a a:LifecycleReview } } UNION { ?review a a:LifecycleReview ; a:sourceAssertion ?mapping ; a:normalizedMappingStatus ?status ; a:deploymentVerificationStatus ?verification } FILTER(?status="proposed" || ?verification IN ("unknown","unverified")) }''',
 'ex:m a:normalizedMappingStatus "proposed"; a:deploymentVerificationStatus "unknown" .',[[EX+'m','proposed','unknown']],
 'ex:m a:normalizedMappingStatus "approved"; a:deploymentVerificationStatus "verified" .')
add(11,'''SELECT DISTINCT ?implementation ?capability ?scope WHERE { ?real a cap:Realisation ; cap:forImplementation ?implementation ; cap:realisesCapability ?capability ; cap:inScope ?scope ; cap:verificationState cap:Verified ; cap:hasEvidence ?e ; cap:requiresCondition ?condition . ?e a cap:Evidence . ?condition a cap:ImplementationCondition }''',
 real,[[EX+'implementation',EX+'capability',EX+'scope']],
 'ex:capability a cap:Capability . ex:proposal a:forTool ex:tool; a:proposedCapability ex:capability .')
add(12,'''SELECT DISTINCT ?capability ?gap WHERE { ?profile a cap:Profile ; cap:hasRequirement/cap:requiresCapability ?capability ; cap:inScope ?scope ; a:normalizedMappingStatus "approved" . '''+gap+' }',
 profile+'ex:assessment cap:requiresCapability ex:capability; cap:inScope ex:scope; a:evidenceStatus "explicitly absent" .',[[EX+'capability','missing']],profile+real)
add(13,'''SELECT ?area (COUNT(DISTINCT ?assertion) AS ?assertions) WHERE { ?area a dama:DMBOK2-2017-KnowledgeArea . { ?assertion map:fromPractice ?practice ; map:targetsPrinciple ?principle . ?practice (map:inKnowledgeArea|map:inTopic) ?area } UNION { ?assertion a map:AreaAlignmentAssessment ; map:fromTopic ?area ; map:alignedPrinciple ?principle } } GROUP BY ?area''',
 'ex:area a dama:DMBOK2-2017-KnowledgeArea . ex:m map:fromPractice ex:p1,ex:p2; map:targetsPrinciple fair:F4 . ex:p1 map:inKnowledgeArea ex:area . ex:p2 map:inKnowledgeArea ex:area .',[[EX+'area','1']],
 'ex:area a dama:AdditionalTopic . ex:m map:fromPractice ex:p1; map:targetsPrinciple fair:F4 . ex:p1 map:inTopic ex:area .')
add(14,'''SELECT DISTINCT ?tool ?capability ?condition ?status WHERE { ?proposal a:forTool ?tool ; a:proposedCapability ?capability ; a:applicabilityCondition ?condition ; a:normalizedMappingStatus ?status . FILTER(?status IN ("proposed","approved")) }''',
 'ex:proposal a:forTool ex:tool; a:proposedCapability ex:capability; a:applicabilityCondition "condition"; a:normalizedMappingStatus "proposed" .',[[EX+'tool',EX+'capability','condition','proposed']],
 'ex:proposal a:forTool ex:tool; a:proposedCapability ex:capability; a:applicabilityCondition "condition"; a:normalizedMappingStatus "deprecated" .')
add(15,'''SELECT DISTINCT ?mapping ?status WHERE { { ?mapping a:normalizedMappingStatus ?status . FILTER NOT EXISTS { ?mapping a a:LifecycleReview } } UNION { ?review a a:LifecycleReview ; a:sourceAssertion ?mapping ; a:normalizedMappingStatus ?status } FILTER(?status IN ("approved","proposed","deprecated")) }''',
 'ex:m a:normalizedMappingStatus "proposed" . ex:old a:normalizedMappingStatus "deprecated" .',[[EX+'m','proposed'],[EX+'old','deprecated']],
 'ex:m a:normalizedMappingStatus "editorial text not normalised" .')
add(16,'''SELECT DISTINCT ?persona WHERE { ?persona a persona:Persona }''',
 'ex:p1 a persona:Persona . ex:p2 a persona:Persona .',[[EX+'p1'],[EX+'p2']],
 'ex:p1 a persona:Persona .',[[EX+'p1']],baseline_identity_check=True)
add(17,'''SELECT DISTINCT ?graph ?source ?digest ?path WHERE { GRAPH <urn:fair-dama-fairmm:graph:provenance:1.0.0> { ?graph prov:wasDerivedFrom ?source ; i:sha256 ?digest ; i:lockPath ?path ; i:role ?role } }''',
 '',[[EX+'source-graph',EX+'source','fixture-hash','fixture.ttl']],fixture_provenance=True)
context='''ex:p a a:ToolPrincipleProposal; a:forTool ex:tool; a:targetsPrinciple fair:F4; cap:forImplementation ex:implementation; cap:inScope ex:scope; a:inFrameworkVersion a:FAIRMM-v1.2.5; a:applicabilityCondition "condition"; a:deploymentVerificationStatus "verified"; cap:hasEvidence ex:ep .
ex:ep a cap:Evidence . ex:el a cap:Evidence .
ex:l a:forTool ex:tool; a:targetsDimension a:D7; a:targetsLevel a:L3; cap:forImplementation ex:implementation; cap:inScope ex:scope; a:inFrameworkVersion a:FAIRMM-v1.2.5; a:applicabilityCondition "condition"; a:deploymentVerificationStatus "verified"; cap:hasEvidence ex:el .'''
add(18,'''SELECT DISTINCT ?tool ?principle ?level WHERE { ?p a a:ToolPrincipleProposal ; a:forTool ?tool ; a:targetsPrinciple ?principle ; cap:forImplementation ?implementation ; cap:inScope ?scope ; a:inFrameworkVersion ?version ; a:applicabilityCondition ?condition ; a:deploymentVerificationStatus "verified" ; cap:hasEvidence ?ep . ?ep a cap:Evidence . ?l a:forTool ?tool ; a:targetsDimension a:D7 ; a:targetsLevel ?level ; cap:forImplementation ?implementation ; cap:inScope ?scope ; a:inFrameworkVersion ?version ; a:applicabilityCondition ?condition ; a:deploymentVerificationStatus "verified" ; cap:hasEvidence ?el . ?el a cap:Evidence }''',
 context,[[EX+'tool','https://w3id.org/fair/principles/terms/F4','urn:fair-dama-fairmm:alignment:L3']],context.replace('ex:l a:forTool ex:tool','ex:l a:forTool ex:tool').replace('ex:l a:forTool ex:tool; a:targetsDimension a:D7; a:targetsLevel a:L3; cap:forImplementation ex:implementation; cap:inScope ex:scope','ex:l a:forTool ex:tool; a:targetsDimension a:D7; a:targetsLevel a:L3; cap:forImplementation ex:implementation; cap:inScope ex:otherScope'))
for key,old,new in [('implementation','cap:forImplementation ex:implementation','cap:forImplementation ex:otherImplementation'),('version','a:inFrameworkVersion a:FAIRMM-v1.2.5','a:inFrameworkVersion ex:otherVersion'),('condition','a:applicabilityCondition "condition"','a:applicabilityCondition "other condition"')]:
 before,after=context.split('ex:l ',1);specs['CQ18']['cases']['incompatible-'+key]={'data':PREFIX+before+'ex:l '+after.replace(old,new),'expected':[]}
specs['CQ12']['cases']['unknown']={'data':PREFIX+profile,'expected':[[EX+'capability','unknown']]}
specs['CQ12']['cases']['different-scope-absence']={'data':PREFIX+profile+'ex:a cap:requiresCapability ex:capability; cap:inScope ex:otherScope; a:evidenceStatus "explicitly absent" .','expected':[[EX+'capability','unknown']]}
specs['CQ12']['cases']['unverified-not-absent']={'data':PREFIX+profile+'ex:r a cap:Realisation; cap:realisesCapability ex:capability; cap:inScope ex:scope; cap:verificationState cap:Unverified .','expected':[[EX+'capability','unknown']]}
specs['CQ12']['cases']['incomplete-verified-is-not-present']={'data':PREFIX+profile+real.replace('cap:requiresCondition ex:condition','cap:rationale "condition missing"'),'expected':[[EX+'capability','unknown']]}
specs['CQ12']['cases']['not-applicable']={'data':PREFIX+profile+'ex:r a cap:Realisation; cap:realisesCapability ex:capability; cap:inScope ex:scope; cap:verificationState cap:NotApplicable .','expected':[]}
specs['CQ18']['query']=specs['CQ18']['query'].rsplit('}',1)[0]+''' FILTER NOT EXISTS { ?p a:applicabilityCondition ?extra . FILTER NOT EXISTS { ?l a:applicabilityCondition ?extra } }
 FILTER NOT EXISTS { ?l a:applicabilityCondition ?extra . FILTER NOT EXISTS { ?p a:applicabilityCondition ?extra } } }'''
specs['CQ18']['cases']['overlapping-but-different-conditions']={'data':PREFIX+context+'\nex:p a:applicabilityCondition "additional incompatible condition" .','expected':[]}
specs['CQ02']['query']=specs['CQ02']['query'].replace('SELECT DISTINCT ?tool ?status ?condition','SELECT DISTINCT ?tool ?status ?condition ?intermediate').rsplit('}',1)[0]+' OPTIONAL { ?m a:viaPractice ?intermediate } }'
specs['CQ02']['cases']['positive']['expected']=[[EX+'tool','proposed','condition',None]]
specs['CQ02']['cases']['known-intermediate']={'data':specs['CQ02']['cases']['positive']['data']+'\nex:m a:viaPractice ex:pathway .','expected':[[EX+'tool','proposed','condition',EX+'pathway']]}
def write():
 (ROOT/'queries').mkdir(exist_ok=True);(ROOT/'fixtures').mkdir(exist_ok=True)
 for name,spec in specs.items():
  (ROOT/'queries'/(name+'.rq')).write_text('# Explicit asserted union view; CQ09/CQ17 also read the named provenance graph.\n'+spec['query'],encoding='utf-8')
  for case,data in spec['cases'].items():(ROOT/'fixtures'/(name+'-'+case+'.ttl')).write_text(data['data'],encoding='utf-8')
 (ROOT/'fixtures/expected-results.json').write_text(json.dumps({name:{'cases':{case:{'file':name+'-'+case+'.ttl','expected':v['expected']} for case,v in spec['cases'].items()},**{k:v for k,v in spec.items() if k not in ['query','cases']}} for name,spec in specs.items()},indent=2),encoding='utf-8')
if __name__=='__main__':write()
