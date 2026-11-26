"""Generate modular OWL/RDFS from approved documentary baselines, without SHACL."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS as DC, OWL, SKOS, XSD
from fairmm_rdf import ROOT, OUT, ART, A, MAP, PERSONA, PROV, FAIR, MODULES, write
from descriptor_comments import COMMENTS

CORPUS = ART / 'fairmm-crosswalk.json'
LEVEL_DATA = OUT / 'baselines/levels-approved.json'
DAMA_ROOT = ROOT.parent / 'FAIR-DAMA'
MM_ROOT = ROOT.parent / 'FAIR-Maturity-Matrix'


def ident(text):
    return hashlib.sha256(str(text).encode('utf-8')).hexdigest()[:24]


def node(g, uri, cls, label=None):
    g.add((uri, RDF.type, cls))
    g.add((uri, RDF.type, OWL.NamedIndividual))
    if label is not None:
        g.add((uri, RDFS.label, Literal(label, lang='en')))
    return uri


def lit(g, s, p, value):
    if value is not None:
        g.add((s, p, Literal(value)))


def src(g, n, url, primary=False):
    if url:
        g.add((n, DC.source, URIRef(url)))
        if primary:
            g.add((n, A.primarySource, URIRef(url)))


def graph(name, data):
    g = Graph()
    for p, ns in [('align',A),('map',MAP),('persona',PERSONA),('prov',PROV),('fair',FAIR),('owl',OWL),('rdfs',RDFS),('rdf',RDF),('dcterms',DC),('skos',SKOS),('xsd',XSD)]:
        g.bind(p,ns)
    ontology = A['ontology:'+name]
    g.add((ontology,RDF.type,OWL.Ontology))
    g.add((ontology,DC.title,Literal('FAIRMM '+name+' ontology',lang='en')))
    release=data.get('schema_version','1.0.0')
    g.add((ontology,OWL.versionInfo,Literal(release)))
    g.add((ontology,OWL.versionIRI,A['ontology:'+name+':'+release]))
    if name!='core':g.add((ontology,OWL.imports,A['ontology:core']))
    for dep in {'alignment':['version','personas'],'derived':['alignment'],'personas':['version']}.get(name,[]):
        g.add((ontology,OWL.imports,A['ontology:'+dep]))
    for key,owner,repo in [('fair_dama_revision','chris-day','FAIR-DAMA'),('fairmm_revision','Pistoia-Alliance-Inc','FAIR-Maturity-Matrix')]:
        src(g,ontology,f'https://github.com/{owner}/{repo}/tree/{data["sources"][key]}')
    if data['sources'].get('dama_source_release'):
        lit(g,ontology,DC.description,data['sources']['dama_source_release']+'. '+data['sources']['source_authority'])
        for url in data['sources']['input_sha256']:
            if url.endswith(('v1.18.0.md','V3.xlsx','v1.1.0.zip')):src(g,ontology,url)
    g.add((ontology,DC.description,Literal('Independent local ontology. Source definitions, proposed alignments and materialized associations remain distinct. No operational maturity assessment.')))
    return g


def restriction(g, cls, prop, count, maximum=False):
    b=BNode();g.add((cls,RDFS.subClassOf,b));g.add((b,RDF.type,OWL.Restriction));g.add((b,OWL.onProperty,prop));g.add((b,OWL.maxCardinality if maximum else OWL.cardinality,Literal(count,datatype=XSD.nonNegativeInteger)))


def core(data):
    g=graph('core',data)
    definitions={
      'FrameworkVersion':'An identified edition of the FAIR Maturity Matrix.',
      'Dimension':'A complementary FAIRMM perspective. Individual dimensions form a flat vocabulary.',
      'MaturityLevel':'An ordered FAIRMM stage. Individual levels form a flat vocabulary, not a class hierarchy.',
      'Descriptor':'The source description at one dimension and one maturity level; not a subprinciple.',
      'CapabilityInterpretation':'A separately identified proposed interpretation of descriptor text.',
      'Practice':'A DAMA-related or explicitly proposed implementation practice.',
      'PracticeBundle':'A composite practice comprising the source activities behind a level-onset judgement.',
      'SourceTopic':'A topic in the source catalogue, retaining its source terminology.',
      'SourceKnowledgeArea':'A numbered core knowledge area in the source catalogue; not an identity assertion with another edition.',
      'Alignment':'A qualified proposed assertion connecting a practice to a dimension or maturity level.',
      'DimensionAlignment':'An alignment with exactly one dimension target.',
      'LevelAlignment':'An alignment with exactly one maturity-level target.',
      'OnsetAlignment':'A source-backed judgement of the first supported level for a practice contribution.',
      'CumulativeAssociation':'A materialized area-level-type association derived from an onset judgement.',
      'DirectAlignment':'The practice directly produces or verifies evidence relevant to the target capability.',
      'IndirectAlignment':'The practice enables an intermediate practice that provides or verifies the relevant evidence.',
      'SourceAssertion':'An original FAIR-principle assertion retained in its own source layer.',
      'Deliverable':'A named practice output, preserving the source wording.',
      'EvidenceRequirement':'A requirement for evidence, not an observed test result.',
      'DescriptorEvidence':'A source-cited descriptor clause supporting a proposed interpretation.',
      'SourceField':'An original table field, retaining its heading, position and exact text.',
      'Persona':'A FAIRMM archetypal actor; not an appointed individual.',
      'DataRole':'Producer, Consumer or Enabler in the context of data work.',
      'PersonaCorrespondence':'A qualified proposed comparison between FAIRMM and DAMA persona entries.',
      'CounterpartCandidate':'A proposed DAMA counterpart with its own match qualification and source.',
      'AreaRoleOccurrence':'A supplier, participant or consumer occurrence in a source topic.',
      'ActivityRoleOccurrence':'A responsible, approving or contributing role occurrence in an activity source.',
      'RoleAssignmentCandidate':'A proposed data role for a persona in a specific practice, not an appointment.',
      'SourceSnapshot':'A pinned source revision or file digest.',
      'DerivationRule':'An explicit reproducible rule for materialized relationships.',
      'LevelReview':'A documentary review of a knowledge area at a specified level.',
      'DiagnosticReview':'A baseline review that does not assert positive alignment.',
      'RoleCategory':'A source involvement category, separate from a data role.',
      'UnresolvedAlignmentCandidate':'A documentary candidate with no sufficiently matched descriptor; not an asserted alignment.',
    }
    for name,definition in definitions.items():
        g.add((A[name],RDF.type,OWL.Class));g.add((A[name],RDFS.label,Literal(name,lang='en')));g.add((A[name],SKOS.definition,Literal(definition,lang='en')))
    parents={'Practice':MAP.Practice,'PracticeBundle':A.Practice,'SourceKnowledgeArea':A.SourceTopic,'DimensionAlignment':A.Alignment,'LevelAlignment':A.Alignment,'OnsetAlignment':A.LevelAlignment,'CumulativeAssociation':A.LevelAlignment,'DirectAlignment':A.Alignment,'IndirectAlignment':A.Alignment,'DiagnosticReview':A.LevelReview}
    for c,p in parents.items():g.add((A[c],RDFS.subClassOf,p))
    for a,b in [('Dimension','MaturityLevel'),('Dimension','Descriptor'),('MaturityLevel','Descriptor'),('DimensionAlignment','LevelAlignment'),('DirectAlignment','IndirectAlignment'),('OnsetAlignment','CumulativeAssociation')]:g.add((A[a],OWL.disjointWith,A[b]))
    ranges={
      'inDimension':A.Dimension,'atLevel':A.MaturityLevel,'targetsDimension':A.Dimension,'targetsLevel':A.MaturityLevel,'firstSupportedLevel':A.MaturityLevel,
      'fromPractice':A.Practice,'viaPractice':A.Practice,'sourceIntermediatePractice':A.Practice,'inPractice':A.Practice,'concernsPractice':A.Practice,'hasPractice':A.Practice,
      'sourceTopic':A.SourceTopic,'inKnowledgeArea':A.SourceKnowledgeArea,'inSourceTopic':A.SourceTopic,
      'hasDeliverable':A.Deliverable,'requiresEvidence':A.EvidenceRequirement,'supportedByDescriptor':A.Descriptor,'hasDescriptor':A.Descriptor,'hasDescriptorEvidence':A.DescriptorEvidence,'hasInterpretation':A.CapabilityInterpretation,
      'sourceAssertion':A.SourceAssertion,'fairmmPersona':A.Persona,'dataRole':A.DataRole,'hasCounterpart':A.CounterpartCandidate,'candidatePersona':A.PersonaCorrespondence,'hasRoleOccurrence':A.ActivityRoleOccurrence,'hasRoleAssignmentCandidate':A.RoleAssignmentCandidate,'derivationRule':A.DerivationRule,'derivedFromOnset':A.OnsetAlignment,'reviewOfOnset':A.OnsetAlignment,
      'nextLevel':A.MaturityLevel,'precedes':A.MaturityLevel,'inFrameworkVersion':A.FrameworkVersion,'hasSourceField':A.SourceField,
    }
    for prop,target in ranges.items():g.add((A[prop],RDF.type,OWL.ObjectProperty));g.add((A[prop],RDFS.range,target))
    for prop in ['primarySource','damaCounterpart','sourcePersona','sourceRoleCategory','areaRoleCategory','roleSuggestion','frameworkPart','sourceSnapshot','supportsInterpretation','reportedDirectFAIRPrinciple','reportedIndirectFAIRPrinciple','candidateDimension']:
        g.add((A[prop],RDF.type,OWL.ObjectProperty))
    g.add((A.precedes,RDF.type,OWL.TransitiveProperty))
    g.add((A.nextLevel,RDFS.subPropertyOf,A.precedes));g.add((A.nextLevel,RDF.type,OWL.FunctionalProperty))
    for prop in ['levelOrdinal','topicNumber','sourcePosition']:
        g.add((A[prop],RDF.type,OWL.DatatypeProperty));g.add((A[prop],RDFS.range,XSD.nonNegativeInteger))
    for prop in ['contributionType','existingContributionType','originalContributionType','rationale','applicabilityCondition','reviewStatus','sourceLayer','sourceText','fullSourceBlock','sourceColumn','sourceCoordinate','qualification','confidence','matchStatus','matchLimitation','relationshipKind','evidenceStatus','sourceRevision','sourceBranch','sha256','sourceIdentifier','fieldHeading','scope','ruleText','onsetStatus','matchingPhrase']:
        g.add((A[prop],RDF.type,OWL.DatatypeProperty));g.add((A[prop],RDFS.range,XSD.string))
    for prop in ['inherited','aggregate','requiresActivityContext']:
        g.add((A[prop],RDF.type,OWL.DatatypeProperty));g.add((A[prop],RDFS.range,XSD.boolean))
    g.add((A.numericValue,RDF.type,OWL.DatatypeProperty));g.add((A.numericValue,RDFS.range,XSD.decimal))
    for prop in ['targetsPrinciple','derivedFromSourceNode']:
        g.add((A[prop],RDF.type,OWL.ObjectProperty))
    for cls,prop in [('Descriptor','inDimension'),('Descriptor','atLevel'),('Alignment','fromPractice'),('DimensionAlignment','targetsDimension'),('LevelAlignment','targetsLevel'),('OnsetAlignment','firstSupportedLevel'),('CumulativeAssociation','firstSupportedLevel'),('CumulativeAssociation','derivedFromOnset'),('RoleAssignmentCandidate','inPractice'),('RoleAssignmentCandidate','fairmmPersona'),('RoleAssignmentCandidate','dataRole')]:restriction(g,A[cls],A[prop],1)
    restriction(g,A.DimensionAlignment,A.targetsLevel,0,True);restriction(g,A.LevelAlignment,A.targetsDimension,0,True)
    b=BNode();g.add((A.IndirectAlignment,RDFS.subClassOf,b));g.add((b,RDF.type,OWL.Restriction));g.add((b,OWL.onProperty,A.viaPractice));g.add((b,OWL.someValuesFrom,A.Practice))
    g.add((A.Alignment,RDFS.comment,Literal('Pattern reuse does not reuse map:fromPractice or map:targetsPrinciple: their FAIR-specific domains and ranges must not classify FAIRMM targets as FAIR subprinciples.')))
    for prop in ['nextLevel','precedes']:
        g.add((A[prop],RDFS.comment,Literal('Ordering only. This property does not propagate capabilities, establish organisational maturity, or turn levels into subclasses.')))
    return g


def plain(text):
    text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',text)
    return re.sub(r'[*`#]','',text).strip()


def source_version(g,data):
    version=node(g,A['FAIRMM-v1.2.5'],A.FrameworkVersion,'FAIR Maturity Matrix v1.2.5')
    lit(g,version,OWL.versionInfo,'1.2.5');lit(g,version,DC.identifier,'FAIR-MM-V1.2.5')
    for key,folder,owner,repo in [('fair_dama_revision',DAMA_ROOT,'chris-day','FAIR-DAMA'),('fairmm_revision',MM_ROOT,'Pistoia-Alliance-Inc','FAIR-Maturity-Matrix')]:
        n=node(g,A['snapshot-'+repo],A.SourceSnapshot,repo+' source snapshot')
        lit(g,n,A.sourceRevision,data['sources'][key]);lit(g,n,A.sourceBranch,'FAIR-MM-V1.2.5' if repo=='FAIR-Maturity-Matrix' else 'main')
        src(g,n,f'https://github.com/{owner}/{repo}/tree/{data["sources"][key]}');g.add((version,A.sourceSnapshot,n))
    for url,digest in data['sources']['input_sha256'].items():
        n=node(g,A['file-'+ident(url)],A.SourceSnapshot);src(g,n,url);lit(g,n,A.sha256,digest);g.add((version,A.sourceSnapshot,n))
    if data['sources'].get('dama_source_release'):
        lit(g,version,DC.description,data['sources']['dama_source_release']+'. '+data['sources']['source_authority'])
    g.add((version,DC.rights,Literal('FAIRMM repository source: Pistoia Alliance contributors, GPL-3.0; persona overview separately states CC BY 4.0. FAIR-DAMA: Chris Day, CC0. Preserve these component-specific notices.')))
    return version


def version_data(data):
    g=graph('version',data);version=source_version(g,data)
    mm_base='https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/'+data['sources']['fairmm_revision']+'/'
    dimnames=[next(d['dimension_label'] for d in data['descriptors'] if d['dimension']==f'D{i}') for i in range(1,8)]
    for i,label in enumerate(dimnames,1):
        n=node(g,A[f'D{i}'],A.Dimension,label);g.add((n,RDF.type,A.Version125Dimension));lit(g,n,DC.identifier,f'D{i}')
        raw=(MM_ROOT/f'docs/fmm-d{i}.md').read_text(encoding='utf-8-sig')
        paras=[p.strip() for p in re.split(r'\n\s*\n',raw) if p.strip() and not p.lstrip().startswith(('#','<','!','|','**[','---'))]
        definition=paras[0]
        lit(g,n,SKOS.definition,plain(definition));lit(g,n,A.sourceText,definition);src(g,n,mm_base+f'docs/fmm-d{i}.md',True)
        g.add((version,DC.hasPart,n));g.add((n,A.inFrameworkVersion,version))
    levels={}
    for line in (MM_ROOT/'docs/FMMlevels.md').read_text(encoding='utf-8-sig').splitlines():
        cells=[s.strip() for s in line.split('|')[1:-1]]
        if len(cells)==4 and cells[0].isdigit() and int(cells[0])<=5 and int(cells[0]) not in levels:levels[int(cells[0])]=cells
    for i,cells in levels.items():
        n=node(g,A[f'L{i}'],A.MaturityLevel,'L'+str(i)+' '+cells[1].strip('" '));g.add((n,RDF.type,A.Version125MaturityLevel))
        lit(g,n,DC.identifier,f'L{i}');lit(g,n,A.levelOrdinal,i);lit(g,n,SKOS.definition,cells[3]);lit(g,n,A.sourceText,cells[3])
        src(g,n,mm_base+'docs/FMMlevels.md',True);src(g,n,mm_base+f'docs/level{i}.md')
        g.add((version,DC.hasPart,n));g.add((n,A.inFrameworkVersion,version))
        if i<5:g.add((n,A.nextLevel,A[f'L{i+1}']))
        for j in range(i+1,6):g.add((n,A.precedes,A[f'L{j}']))
    for cls,base,ids in [('Version125Dimension',A.Dimension,[A[f'D{i}'] for i in range(1,8)]),('Version125MaturityLevel',A.MaturityLevel,[A[f'L{i}'] for i in range(6)])]:
        g.add((A[cls],RDF.type,OWL.Class));g.add((A[cls],RDFS.subClassOf,base))
        enum=BNode();head=BNode();g.add((A[cls],OWL.equivalentClass,enum));g.add((enum,RDF.type,OWL.Class));g.add((enum,OWL.oneOf,head));Collection(g,head,ids)
        diff=BNode();h=BNode();g.add((diff,RDF.type,OWL.AllDifferent));g.add((diff,OWL.distinctMembers,h));Collection(g,h,ids)
    for d in data['descriptors']:
        n=node(g,A[d['id']],A.Descriptor,d['dimension_label']+' at L'+str(d['level']))
        g.add((n,A.inDimension,A[d['dimension']]));g.add((n,A.atLevel,A[f'L{d["level"]}']));g.add((n,A.inFrameworkVersion,version));g.add((version,A.hasDescriptor,n))
        lit(g,n,DC.identifier,d['id']);lit(g,n,A.fullSourceBlock,d['source_markdown']);src(g,n,d['source'],True);lit(g,n,A.evidenceStatus,'not assessed')
        g.add((n,RDFS.comment,Literal(COMMENTS[d['id']],lang='en')))
    return g


def topic(g,s):
    n=node(g,A[s['id']],A.SourceKnowledgeArea if 1<=s['number']<=11 else A.SourceTopic,s['name'])
    lit(g,n,DC.identifier,s['id']);lit(g,n,A.topicNumber,s['number']);lit(g,n,A.aggregate,s['aggregate']);src(g,n,s['source'],True)
    return n


def deliverable(g,owner,label):
    if not label:return
    n=node(g,A['deliverable-'+ident(label)],A.Deliverable,label);g.add((owner,A.hasDeliverable,n))


def practice(g,identifier,label,topic_id=None):
    n=node(g,A[identifier],A.Practice,label);g.add((n,RDF.type,MAP.Practice));lit(g,n,DC.identifier,identifier)
    if topic_id:
        g.add((n,A.inSourceTopic,A[topic_id]))
        if 1<=int(topic_id[-2:])<=11:g.add((n,A.inKnowledgeArea,A[topic_id]))
    return n


def evidence(g,owner,record):
    did=record.get('descriptor_id');clauses=record.get('source_clauses') or [record['clause']]
    if did:g.add((owner,A.supportedByDescriptor,A[did]))
    for clause in clauses:
        n=node(g,A['evidence-'+ident((did,clause,record['source'],record.get('phrase'),record.get('rationale')))],A.DescriptorEvidence)
        g.add((owner,A.hasDescriptorEvidence,n))
        if did:g.add((n,A.supportedByDescriptor,A[did]))
        lit(g,n,A.sourceText,clause);lit(g,n,A.rationale,record.get('rationale'));lit(g,n,A.matchLimitation,record.get('limitation'))
        lit(g,n,A.matchingPhrase,record.get('phrase'));src(g,n,record['source'],True)
        if record.get('rationale'):
            interp=node(g,A['interpretation-'+ident((did,record['rationale']))],A.CapabilityInterpretation)
            lit(g,interp,A.rationale,record['rationale']);lit(g,interp,A.reviewStatus,'proposed interpretation')
            g.add((A[did],A.hasInterpretation,interp));g.add((n,A.supportsInterpretation,interp))


def qualified(g,n,kind,practice_uri,area_id,rationale,conditions,evidence_text,status):
    g.add((n,RDF.type,A.Alignment));g.add((n,RDF.type,A[kind+'Alignment']));g.add((n,A.fromPractice,practice_uri))
    lit(g,n,A.contributionType,kind);lit(g,n,A.rationale,rationale);lit(g,n,A.reviewStatus,status)
    if area_id:
        g.add((n,A.sourceTopic,A[area_id]))
        if 1<=int(area_id[-2:])<=11:g.add((n,A.inKnowledgeArea,A[area_id]))
    for condition in conditions:lit(g,n,A.applicabilityCondition,condition)
    req=node(g,A['requirement-'+ident(evidence_text)],A.EvidenceRequirement,evidence_text)
    lit(g,req,A.evidenceStatus,'requirement only; no operational test');g.add((n,A.requiresEvidence,req))


def alignment_data(data,levels):
    g=graph('alignment',data)
    ontology_root=ROOT/data['sources']['ontology_directory'] if data['sources'].get('ontology_directory') else DAMA_ROOT/'artefacts'
    pg=Graph().parse(ontology_root/'dama-persona-ontology.ttl',format='turtle')
    for s in data['summaries']:
        t=topic(g,s)
        for p,label in pg.subject_objects(RDFS.label):
            if str(label)==s['name']:
                for area in pg.objects(p,PERSONA.correspondsToKnowledgeArea):g.add((t,PERSONA.correspondsToKnowledgeArea,area))
    for a in data['activities']:
        p=practice(g,a['id'],a['activity'],a['area_id']);src(g,p,a['source'],True);lit(g,p,A.sourceCoordinate,a['coordinate']);deliverable(g,p,a['deliverables'])
        for i,(heading,text) in enumerate(a['source_fields'].items(),1):
            f=node(g,A[a['id']+'-field-'+str(i)],A.SourceField,heading);lit(g,f,A.sourceText,text);lit(g,f,A.fieldHeading,heading);lit(g,f,A.sourcePosition,i);g.add((p,A.hasSourceField,f));src(g,f,a['source'])
    for a in data['assertions']:
        n=node(g,A[a['id']],A.SourceAssertion);lit(g,n,DC.identifier,a['id']);lit(g,n,A.sourceLayer,a['source_layer']);lit(g,n,A.existingContributionType,a['contribution_type']);lit(g,n,A.originalContributionType,a.get('original_contribution_type',a['contribution_type']));g.add((n,A.targetsPrinciple,FAIR[a['principle']]));src(g,n,a['source'],True)
        lit(g,n,A.rationale,a.get('rationale'));lit(g,n,A.applicabilityCondition,a.get('condition'));lit(g,n,A.sourceCoordinate,a.get('coordinate'));lit(g,n,A.aggregate,a.get('aggregate'))
        if a.get('area_id'):g.add((n,A.inSourceTopic,A[a['area_id']]))
        if a.get('activity_id'):g.add((n,A.hasPractice,A[a['activity_id']]))
        if a.get('source_node'):g.add((n,A.derivedFromSourceNode,URIRef(a['source_node'])))
        if a.get('practice'):g.add((n,A.hasPractice,URIRef(a['practice'])))
        if a.get('intermediate_practice'):
            via=a['intermediate_practice'];v=URIRef(via) if via.startswith(('http:','https:','urn:')) else practice(g,'practice-'+ident(via),via)
            g.add((n,A.sourceIntermediatePractice,v))
        if a.get('original_record'):
            for i,(key,value) in enumerate(a['original_record'].items(),1):
                f=node(g,A[a['id']+'-field-'+key],A.SourceField,key);lit(g,f,A.fieldHeading,key);lit(g,f,A.sourceText,str(value));lit(g,f,A.sourcePosition,i);g.add((n,A.hasSourceField,f))
                if isinstance(value,(int,float)) and not isinstance(value,bool):lit(g,f,A.numericValue,value)
            lit(g,n,A.sourceCoordinate,a['source_member']+' links['+str(a['source_record_index'])+']')
    activity_by_id={a['id']:a for a in data['activities']}
    persona_by_name={p['name']:p for p in data['dama_personas']}
    corr={p['id']:p for p in data['persona_correspondences']}
    for a in data['alignments']:
        n=node(g,A[a['id']],A.DimensionAlignment,a['activity']);lit(g,n,DC.identifier,a['id'])
        p=A[a['activity_id']] if a.get('activity_id') else practice(g,a['id']+'-practice',a['activity'])
        qualified(g,n,a['proposed_dimension_contribution_type'],p,a.get('area_id'),a.get('descriptor_match_status',a['condition']),[a['condition']],a['evidence_test'],a['review_status'])
        g.add((n,A.targetsDimension,A[a['dimension']]));deliverable(g,n,a['deliverable']);src(g,n,a.get('source'),True)
        lit(g,n,A.sourceCoordinate,a.get('source_coordinate'));lit(g,n,A.existingContributionType,a.get('existing_contribution_type'));lit(g,n,A.matchStatus,a.get('descriptor_match_status'));lit(g,n,A.evidenceStatus,'operational pilot excluded')
        if a.get('source_assertion_id'):g.add((n,A.sourceAssertion,A[a['source_assertion_id']]))
        if a.get('principle'):g.add((n,A.targetsPrinciple,FAIR[a['principle']]))
        if a.get('intermediate_practice'):g.add((n,A.sourceIntermediatePractice,practice(g,'practice-'+ident(a['intermediate_practice']),a['intermediate_practice'])))
        if a['proposed_dimension_contribution_type']=='Indirect':g.add((n,A.viaPractice,practice(g,'practice-'+ident(a['dimension_intermediate_practice']),a['dimension_intermediate_practice'])))
        for support in a['descriptor_support']:evidence(g,n,support)
        for candidate in a['persona_candidates']:
            correspondence=A[candidate['persona_mapping_id']];g.add((n,A.candidatePersona,correspondence))
            for occurrence in candidate.get('occurrences',[]):
                original=persona_by_name[occurrence['dama_persona']]
                o=node(g,A['role-occurrence-'+ident((a.get('activity_id'),original['source_iri'],occurrence['source_role_category']))],A.ActivityRoleOccurrence)
                g.add((o,A.sourcePersona,URIRef(original['source_iri'])));g.add((o,A.concernsPractice,p));lit(g,o,A.sourceText,occurrence['source_text']);g.add((o,A.sourceRoleCategory,A[occurrence['source_role_category']]));src(g,o,a.get('source'))
                g.add((n,A.hasRoleOccurrence,o))
                for role in corr[candidate['persona_mapping_id']]['proposed_data_roles']:
                    assignment=node(g,A['role-candidate-'+ident((str(o),corr[candidate['persona_mapping_id']]['fairmm_persona'],role))],A.RoleAssignmentCandidate)
                    g.add((assignment,A.inPractice,p));g.add((assignment,A.fairmmPersona,A['Persona-'+corr[candidate['persona_mapping_id']]['fairmm_persona']]));g.add((assignment,A.dataRole,A[role]));g.add((assignment,A.hasRoleOccurrence,o));g.add((assignment,A.candidatePersona,correspondence));lit(g,assignment,A.reviewStatus,'proposed; no local appointment or authority inferred');g.add((n,A.hasRoleAssignmentCandidate,assignment))
    for o in levels['onsets']:
        n=node(g,A[o['id']],A.OnsetAlignment,o['area_name']+' '+o['kind']+' onset')
        g.add((n,RDF.type,A.LevelAlignment))
        lit(g,n,DC.identifier,o['id']);bundle=practice(g,o['id']+'-practice',' / '.join(o['activities']),o['area_id']);g.add((bundle,RDF.type,A.PracticeBundle))
        for aid in o['activity_ids']:g.add((bundle,DC.hasPart,A[aid]))
        for d in o['deliverables']:deliverable(g,bundle,d);deliverable(g,n,d)
        condition='The source practice must address the cited FAIRMM capability; area association does not establish an organisational maturity level.'
        qualified(g,n,o['kind'],bundle,o['area_id'],o['rationale'],[condition],'Inspect the named deliverables and the cited descriptor clauses at the stated scope.',o['status'])
        level=A['L'+str(o['first_supported_level'])];g.add((n,A.targetsLevel,level));g.add((n,A.firstSupportedLevel,level));evidence(g,n,o['earliest_level_evidence'])
        for url in o['source_references']:src(g,n,url)
        if o['intermediate_practice']:g.add((n,A.viaPractice,practice(g,'practice-'+ident(o['intermediate_practice']),o['intermediate_practice'])))
        for pid in o['source_fair_direct']:g.add((n,A.reportedDirectFAIRPrinciple,FAIR[pid]))
        for pid in o['source_fair_indirect']:g.add((n,A.reportedIndirectFAIRPrinciple,FAIR[pid]))
    for candidate in data.get('unresolved_descriptor_candidates',[]):
        n=node(g,A['unresolved-'+candidate['id']],A.UnresolvedAlignmentCandidate,candidate['activity']);g.add((n,A.candidateDimension,A[candidate['dimension']]));g.add((n,A.hasPractice,A[candidate['activity_id']]));g.add((n,A.sourceAssertion,A[candidate['source_assertion_id']]));lit(g,n,A.reviewStatus,candidate['review_status']);src(g,n,candidate['source'])
    for review in levels['level_review']:
        n=node(g,A['review-'+review['area_id']+'-L'+str(review['level'])],A.LevelReview)
        g.add((n,A.sourceTopic,A[review['area_id']]));g.add((n,A.atLevel,A['L'+str(review['level'])]));lit(g,n,A.rationale,review['interpretation'])
        for item in review['descriptor_evidence']:evidence(g,n,item)
    for review in levels['diagnostic_baseline']:
        n=node(g,A['diagnostic-'+review['area_id']],A.DiagnosticReview);g.add((n,A.sourceTopic,A[review['area_id']]));g.add((n,A.atLevel,A.L0));g.add((n,A.supportedByDescriptor,A[review['descriptor']]));src(g,n,review['source']);lit(g,n,A.rationale,review['rationale'])
    return g


def personas(data):
    g=graph('personas',data);version=A['FAIRMM-v1.2.5']
    for category in ['supplier_in','participant_in','consumer_in','responsible_roles','approving_roles','contributing_roles']:
        node(g,A[category],A.RoleCategory,category.replace('_',' '))
    for role in ['Producer','Consumer','Enabler']:
        n=node(g,A[role],A.DataRole,role)
        raw=(MM_ROOT/f'docs/FAIR_roles/Data_{role}.md').read_text(encoding='utf-8-sig')
        definition=raw.split('## Role definition',1)[1].split('## Sources',1)[0].strip()
        lit(g,n,SKOS.definition,definition);src(g,n,'https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/'+data['sources']['fairmm_revision']+f'/docs/FAIR_roles/Data_{role}.md');g.add((n,A.inFrameworkVersion,version))
    for p in data['persona_correspondences']:
        n=node(g,A['Persona-'+p['fairmm_persona']],A.Persona,p['fairmm_persona']);lit(g,n,DC.identifier,p['fairmm_persona']);lit(g,n,SKOS.definition,p['fairmm_description']);lit(g,n,A.sourceText,p['fairmm_description']);src(g,n,p['fairmm_source'],True);g.add((n,A.inFrameworkVersion,version))
        c=node(g,A[p['id']],A.PersonaCorrespondence,p['fairmm_persona']+' comparison');g.add((c,A.fairmmPersona,n));lit(g,c,DC.identifier,p['id']);lit(g,c,A.confidence,p['confidence']);lit(g,c,A.qualification,p['qualification']);lit(g,c,A.rationale,p['rationale']);lit(g,c,A.reviewStatus,p['status']);lit(g,c,A.requiresActivityContext,True);src(g,c,p['fairmm_source'])
        for role in p['proposed_data_roles']:g.add((c,A.roleSuggestion,A[role]))
        for i,candidate in enumerate(p['candidates'],1):
            q=node(g,A[p['id']+'-counterpart-'+str(i)],A.CounterpartCandidate,candidate['name']);g.add((c,A.hasCounterpart,q));g.add((q,A.damaCounterpart,URIRef(candidate['source_iri'])));lit(g,q,A.relationshipKind,candidate['relationship']);lit(g,q,A.confidence,p['confidence']);src(g,q,candidate['source'])
    for p in data['dama_personas']:
        original=URIRef(p['source_iri']);g.add((original,RDFS.label,Literal(p['name'],lang='en')));src(g,original,p['source'])
        for key in ['supplier_in','participant_in','consumer_in']:
            for area in p[key]:
                n=node(g,A['area-occurrence-'+ident((p['id'],key,area))],A.AreaRoleOccurrence)
                g.add((n,A.sourcePersona,original));g.add((n,A.areaRoleCategory,A[key]));src(g,n,p['source']);lit(g,n,A.sourceText,area)
                topic_id=next((s['id'] for s in data['summaries'] if s['name']==area),None)
                if topic_id:g.add((n,A.inSourceTopic,A[topic_id]))
                else:lit(g,n,RDFS.comment,'Source topic label preserved; no automatic alias merge.')
        for prop,key in [(PERSONA.reportedDirectFAIRPrinciple,'inherited_direct'),(PERSONA.reportedIndirectFAIRPrinciple,'inherited_indirect')]:
            for pid in p[key]:g.add((original,prop,FAIR[pid]))
    return g


def derive(data,alignment):
    """Materialize closure from RDF onsets and RDF ordinal values, never baseline links."""
    g=graph('derived',data);rule=node(g,A.CumulativeLevelRule,A.DerivationRule,'Cumulative knowledge-area association')
    lit(g,rule,A.ruleText,'For each OnsetAlignment at ordinal k, emit one CumulativeAssociation at each level n with k <= n <= 5. Preserve practice, area and type. n=k is introduced; n>k is inherited. This is association, not capability or maturity inheritance.')
    combined=alignment+version_data(data)
    for onset in sorted(alignment.subjects(RDF.type,A.OnsetAlignment),key=str):
        start=alignment.value(onset,A.firstSupportedLevel);k=int(combined.value(start,A.levelOrdinal));kind=str(alignment.value(onset,A.contributionType));area=alignment.value(onset,A.sourceTopic);p=alignment.value(onset,A.fromPractice)
        for target in sorted(combined.subjects(RDF.type,A.MaturityLevel),key=lambda n:int(combined.value(n,A.levelOrdinal))):
            ordinal=int(combined.value(target,A.levelOrdinal))
            if ordinal<k:continue
            ident_str=str(area).split(':')[-1]+'-L'+str(ordinal)+'-'+kind
            n=node(g,A['cumulative-'+ident_str],A.CumulativeAssociation,ident_str);lit(g,n,DC.identifier,ident_str)
            g.add((n,RDF.type,A.LevelAlignment))
            conditions=['The named practice must explicitly support the cited FAIRMM capability at the stated scope.','Cumulative association retains the area and contribution type; it is not a claim that a complete higher maturity level is achieved.','Higher-level implementation, resources and competence remain to be established.']
            qualified(g,n,kind,p,str(area).split(':')[-1],str(alignment.value(onset,A.rationale)),conditions,'Inspect onset and progression descriptor evidence separately from actual implementation.','derived from proposed onset; not an assessed maturity level')
            g.add((n,A.targetsLevel,target));g.add((n,A.firstSupportedLevel,start));g.add((n,A.derivedFromOnset,onset));g.add((n,PROV.wasDerivedFrom,onset));g.add((n,A.derivationRule,rule));lit(g,n,A.inherited,ordinal>k);lit(g,n,A.onsetStatus,'inherited' if ordinal>k else 'introduced')
            for prop in [A.viaPractice,A.hasDeliverable,A.supportedByDescriptor,A.hasDescriptorEvidence,DC.source]:
                for value in alignment.objects(onset,prop):g.add((n,prop,value))
            review=A['review-'+str(area).split(':')[-1]+'-L'+str(ordinal)]
            for prop in [A.supportedByDescriptor,A.hasDescriptorEvidence]:
                for value in alignment.objects(review,prop):g.add((n,prop,value))
    return g


def source_files_snapshot():
    """Read-only source checkout fingerprint, excluding internal Git state."""
    return {str(path.relative_to(ROOT.parent)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for folder in [DAMA_ROOT,MM_ROOT] for path in sorted(folder.rglob('*')) if path.is_file() and '.git' not in path.relative_to(folder).parts}


def git_revision(folder):
    """Read refs without invoking Git or writing its index."""
    gitdir=folder/'.git'
    if gitdir.is_file():gitdir=(folder/gitdir.read_text().strip().split('gitdir:',1)[1].strip()).resolve()
    head=(gitdir/'HEAD').read_text().strip()
    if not head.startswith('ref: '):return head
    ref=head[5:];path=gitdir/ref
    if path.exists():return path.read_text().strip()
    common=gitdir
    if (gitdir/'commondir').exists():common=(gitdir/(gitdir/'commondir').read_text().strip()).resolve()
    if (common/ref).exists():return (common/ref).read_text().strip()
    packed=common/'packed-refs'
    if packed.exists():
        for line in packed.read_text().splitlines():
            if line.endswith(' '+ref):return line.split()[0]
    raise ValueError('Cannot resolve source Git revision: '+str(folder))


def main():
    for destination,source in [(LEVEL_DATA,ROOT/'results/levels/dama-fairmm-levels-sankey.json'),(OUT/'baselines/dimensions-approved.json',ROOT/'results/sankey/dama-fairmm-dimensions-sankey.json')]:
        if not destination.exists():write(destination,source.read_text(encoding='utf-8'))
    data=json.loads(CORPUS.read_text(encoding='utf-8'));levels=json.loads(LEVEL_DATA.read_text(encoding='utf-8'))
    actual_revisions={key:git_revision(folder) for key,folder in [('fair_dama_revision',DAMA_ROOT),('fairmm_revision',MM_ROOT)]}
    if any(data['sources'][key]!=revision for key,revision in actual_revisions.items()):raise ValueError('Source checkout revisions differ from the approved baselines: '+str(actual_revisions))
    before=source_files_snapshot()
    expected_branch='ref: refs/heads/FAIR-MM-V1.2.5'
    if (MM_ROOT/'.git/HEAD').read_text().strip()!=expected_branch:raise ValueError('FAIRMM source is not on the requested branch')
    pg=personas(data);ag=alignment_data(data,levels)
    modules=[core(data),version_data(data),pg,ag,derive(data,ag)]
    for filename,g in zip(MODULES,modules):
        # Retain pinned source bytes when regeneration changes only Turtle ordering.
        from rdflib.compare import isomorphic
        canonical=ART/filename
        if canonical.exists() and isomorphic(g,Graph().parse(canonical,format='turtle')):
            payload=canonical.read_bytes()
        else:
            payload=g.serialize(format='turtle').encode('utf-8')
            canonical.write_bytes(payload)
        download=ROOT/'docs/ontology-data'/filename
        download.parent.mkdir(parents=True,exist_ok=True)
        download.write_bytes(payload)
    manifest=dict(modules={name:len(g) for name,g in zip(MODULES,modules)},namespace=str(A),source_revisions=data['sources'],source_files_sha256=before,baseline_inputs={str(path.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in [CORPUS,LEVEL_DATA,OUT/'baselines/dimensions-approved.json']},source_checkouts_unchanged=before==source_files_snapshot(),validation_method='Python/RDFLib and SPARQL only; no SHACL')
    manifest['verified_git_revisions']=actual_revisions
    comment_script=ROOT/'scripts/descriptor_comments.py'
    manifest['descriptor_comments']=dict(count=len(COMMENTS),kind='Project-authored explanatory paraphrases of pinned FAIRMM descriptor blocks; not verbatim source definitions or assessment results',generator='scripts/descriptor_comments.py',generator_sha256=hashlib.sha256(comment_script.read_bytes()).hexdigest(),source_block_sha256={d['id']:hashlib.sha256(d['source_markdown'].encode('utf-8')).hexdigest() for d in data['descriptors']})
    write(OUT/'build-manifest.json',json.dumps(manifest,indent=2)+'\n')
    if not manifest['source_checkouts_unchanged']:raise AssertionError('Source checkout changed during generation')
    print(json.dumps({k:v for k,v in manifest.items() if k in ['modules','namespace','source_checkouts_unchanged']},indent=2))


if __name__=='__main__':main()
