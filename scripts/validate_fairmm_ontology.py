"""Closed checks with RDFLib and SPARQL; OWL axioms alone do not check data completeness."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from rdflib import Graph, Literal, RDF, RDFS
from rdflib.namespace import DCTERMS as DC, OWL, SKOS
from fairmm_rdf import ROOT, OUT, ART, A, MAP, PERSONA, PROV, MODULES, load, write


def instances(g,cls):return set(g.subjects(RDF.type,cls))


def structural_errors(g):
    errors=[]
    def exact(n,p,count=1):
        if len(set(g.objects(n,p)))!=count:errors.append(('cardinality',str(n),str(p),count))
    for n in instances(g,A.Dimension):
        for p in [DC.identifier,RDFS.label,SKOS.definition,A.inFrameworkVersion]:exact(n,p)
    for n in instances(g,A.MaturityLevel):
        for p in [DC.identifier,RDFS.label,SKOS.definition,A.inFrameworkVersion,A.levelOrdinal]:exact(n,p)
    for n in instances(g,A.Descriptor):
        for p in [A.inDimension,A.atLevel,A.fullSourceBlock,DC.identifier,A.primarySource]:exact(n,p)
        if g.value(n,A.inDimension) not in instances(g,A.Dimension) or g.value(n,A.atLevel) not in instances(g,A.MaturityLevel):errors.append(('descriptor target',str(n)))
    for n in instances(g,A.Alignment):
        for p in [A.fromPractice,A.contributionType]:exact(n,p)
        for p in [A.rationale,A.applicabilityCondition,A.requiresEvidence,A.reviewStatus]:
            if not list(g.objects(n,p)):errors.append(('required field',str(n),str(p)))
        if g.value(n,A.fromPractice) not in instances(g,A.Practice):errors.append(('practice type',str(n)))
        dt=list(g.objects(n,A.targetsDimension));lt=list(g.objects(n,A.targetsLevel))
        if (n,RDF.type,A.DimensionAlignment) in g:
            if len(dt)!=1 or lt or dt[0] not in instances(g,A.Dimension):errors.append(('dimension target',str(n)))
        elif (n,RDF.type,A.LevelAlignment) in g:
            if len(lt)!=1 or dt or lt[0] not in instances(g,A.MaturityLevel):errors.append(('level target',str(n)))
            if A.L0 in lt:errors.append(('positive L0',str(n)))
        else:errors.append(('missing target class',str(n)))
        kind=str(g.value(n,A.contributionType))
        if kind not in ['Direct','Indirect']:errors.append(('unknown type',str(n)))
        if (n,RDF.type,A[kind+'Alignment']) not in g:errors.append(('type mismatch',str(n)))
        if (n,RDF.type,A.DirectAlignment) in g and (n,RDF.type,A.IndirectAlignment) in g:errors.append(('disjoint types',str(n)))
        if kind=='Indirect' and not list(g.objects(n,A.viaPractice)):errors.append(('missing via',str(n)))
        for v in g.objects(n,A.viaPractice):
            if (v,RDF.type,A.Practice) not in g:errors.append(('untyped via',str(n)))
    for n in instances(g,A.RoleAssignmentCandidate):
        for p in [A.inPractice,A.fairmmPersona,A.dataRole]:exact(n,p)
        if g.value(n,A.inPractice) not in instances(g,A.Practice):errors.append(('role context type',str(n)))
        if g.value(n,A.dataRole) not in instances(g,A.DataRole):errors.append(('data role type',str(n)))
    for n in instances(g,A.CumulativeAssociation):
        for p in [A.derivedFromOnset,A.firstSupportedLevel,A.inherited,A.derivationRule]:exact(n,p)
        o=g.value(n,A.derivedFromOnset)
        if o not in instances(g,A.OnsetAlignment):errors.append(('missing onset',str(n)));continue
        for p in [A.fromPractice,A.sourceTopic,A.contributionType,A.firstSupportedLevel]:
            if set(g.objects(n,p))!=set(g.objects(o,p)):errors.append(('inheritance mismatch',str(n),str(p)))
        target=g.value(n,A.targetsLevel);first=g.value(n,A.firstSupportedLevel)
        if target and first:
            ordinal=int(g.value(target,A.levelOrdinal));start=int(g.value(first,A.levelOrdinal))
            if ordinal<start or ordinal>5:errors.append(('invalid interval',str(n)))
            if bool(g.value(n,A.inherited).toPython())!=(ordinal>start):errors.append(('inherited flag',str(n)))
    return errors


def main():
    g=load();data=json.loads((ART/'fairmm-crosswalk.json').read_text(encoding='utf-8'))
    levels=json.loads((OUT/'baselines/levels-approved.json').read_text(encoding='utf-8'))
    dims=json.loads((OUT/'baselines/dimensions-approved.json').read_text(encoding='utf-8'))
    manifest=json.loads((OUT/'build-manifest.json').read_text(encoding='utf-8'))
    checks=[];failures=[]
    def check(name,test,detail=None):
        checks.append(dict(check=name,passed=bool(test)))
        if not test:failures.append(dict(check=name,detail=detail))
    check('Closed structural checks',not structural_errors(g),structural_errors(g)[:10])
    for cls,count in [(A.Dimension,7),(A.MaturityLevel,6),(A.Descriptor,42),(A.Persona,30),(A.DataRole,3)]:check('Count '+str(cls).split(':')[-1],len(instances(g,cls))==count)
    check('Framework has exactly the thirteen flat vocabulary members',set(g.objects(A['FAIRMM-v1.2.5'],DC.hasPart))==instances(g,A.Dimension)|instances(g,A.MaturityLevel))
    check('Descriptor cells complete',len({(g.value(n,A.inDimension),g.value(n,A.atLevel)) for n in instances(g,A.Descriptor)})==42)
    for n in instances(g,A.Dimension)|instances(g,A.MaturityLevel):
        check('No individual hierarchy '+str(n),not list(g.objects(n,RDFS.subClassOf)) and not list(g.objects(n,DC.hasPart)))
    check('Level ordinals exactly 0 through 5',sorted(int(g.value(n,A.levelOrdinal)) for n in instances(g,A.MaturityLevel))==list(range(6)))
    check('Immediate ordering exact',set(g.subject_objects(A.nextLevel))=={(A[f'L{i}'],A[f'L{i+1}']) for i in range(5)})
    check('Transitive ordering exact',set(g.subject_objects(A.precedes))=={(A[f'L{i}'],A[f'L{j}']) for i in range(6) for j in range(i+1,6)})
    for d in data['descriptors']:
        from descriptor_comments import COMMENTS
        check('Descriptor explanatory comment '+d['id'],list(g.objects(A[d['id']],RDFS.comment))==[Literal(COMMENTS[d['id']],lang='en')])
        n=A[d['id']]
        check('Descriptor source fidelity '+d['id'],str(g.value(n,A.fullSourceBlock))==d['source_markdown'] and str(g.value(n,A.primarySource))==d['source'])
    for p in data['persona_correspondences']:
        n=A['Persona-'+p['fairmm_persona']]
        check('Persona source fidelity '+p['fairmm_persona'],str(g.value(n,SKOS.definition))==p['fairmm_description'])
        if p['confidence']=='Gap':
            check('Gap is not equivalence '+p['id'],all(str(g.value(c,A.relationshipKind))=='related counterpart; no equivalence asserted' for c in g.objects(A[p['id']],A.hasCounterpart)))
    check('No identity or exact-match assertions',not list(g.triples((None,OWL.sameAs,None))) and not list(g.triples((None,SKOS.exactMatch,None))))
    check('Data roles are not attached globally to personas',not any(list(g.objects(p,A.dataRole)) for p in instances(g,A.Persona)))
    check('Area role occurrences preserved',len(instances(g,A.AreaRoleOccurrence))==sum(len(p[k]) for p in data['dama_personas'] for k in ['supplier_in','participant_in','consumer_in']))
    check('Source activity roles are separate objects',bool(instances(g,A.ActivityRoleOccurrence)) and not (instances(g,A.ActivityRoleOccurrence)&instances(g,A.AreaRoleOccurrence)))
    for a in data['activities']:
        fields=sorted(g.objects(A[a['id']],A.hasSourceField),key=lambda n:int(g.value(n,A.sourcePosition)))
        check('All original activity fields '+a['id'],[(str(g.value(f,A.fieldHeading)),str(g.value(f,A.sourceText))) for f in fields]==list(a['source_fields'].items()))
    check('All source assertions retained',len(instances(g,A.SourceAssertion))==len(data['assertions']))
    layer_counts=Counter(str(g.value(n,A.sourceLayer)) for n in instances(g,A.SourceAssertion))
    check('Source layers remain distinct',layer_counts==Counter(a['source_layer'] for a in data['assertions']))
    for a in data['assertions']:
        check('Original source classification '+a['id'],str(g.value(A[a['id']],A.existingContributionType))==a['contribution_type'])
    check('All dimension assertions retained',len(instances(g,A.DimensionAlignment))==len(data['alignments']))
    expected_dim={(l['source'],l['target'],l['kind'],l['underlying_record_count']) for l in dims['links']}
    dim_rows=list(g.query((ROOT/'scripts/queries/dimension-links.rq').read_text()))
    actual_dim={(str(r.areaID),str(r.dimensionID),str(r.kind),int(r.records)) for r in dim_rows}
    check('Dimension graph matches approved Sankey',actual_dim==expected_dim,dict(missing=list(expected_dim-actual_dim),extra=list(actual_dim-expected_dim)))
    check('Onset source-release baseline count',len(instances(g,A.OnsetAlignment))==len(levels['onsets']))
    check('Cumulative source-release baseline count',len(instances(g,A.CumulativeAssociation))==len(levels['links']))
    expected_levels={(l['source'],l['target'],l['kind'],l['first_supported_level'],l['inherited']) for l in levels['links']}
    level_rows=list(g.query((ROOT/'scripts/queries/level-links.rq').read_text()))
    actual_levels={(str(r.areaID),str(r.levelID),str(r.kind),int(str(r.firstLevel)[1:]),bool(r.inherited.toPython())) for r in level_rows}
    check('Cumulative graph matches approved Sankey',expected_levels==actual_levels,dict(missing=list(expected_levels-actual_levels),extra=list(actual_levels-expected_levels)))
    for o in instances(g,A.OnsetAlignment):
        start=int(g.value(g.value(o,A.firstSupportedLevel),A.levelOrdinal))
        related=set(g.subjects(A.derivedFromOnset,o))
        check('Complete cumulative closure '+str(o),{int(g.value(g.value(n,A.targetsLevel),A.levelOrdinal)) for n in related}==set(range(start,6)))
    constructed=g.query((ROOT/'scripts/queries/cumulative-construct.rq').read_text()).graph
    constructed_rel={(str(constructed.value(n,A.sourceTopic)).split(':')[-1],str(constructed.value(n,A.targetsLevel)).split(':')[-1],str(constructed.value(n,A.contributionType))) for n in constructed.subjects(RDF.type,A.CumulativeAssociation)}
    check('Independent SPARQL CONSTRUCT agrees with materializer',constructed_rel=={r[:3] for r in expected_levels})
    write(OUT/'sparql-derived-associations.ttl',constructed.serialize(format='turtle'))
    queries={}
    for path in sorted((ROOT/'scripts/queries').glob('*.rq')):
        if path.name=='cumulative-construct.rq':continue
        rows=list(g.query(path.read_text()))
        queries[path.name]=len(rows)
        check('SPARQL query executes '+path.name,bool(rows))
    check('No structured relationships serialized as JSON literals',not any(isinstance(o,Literal) and str(o).lstrip().startswith(('{','[{')) for _,_,o in g))
    check('Source text remains textual',all(isinstance(v,Literal) and isinstance(v.toPython(),str) for v in g.objects(None,A.sourceText)))
    declared={p for p in set(g.predicates()) if str(p).startswith(str(A)) and not any((p,RDF.type,t) in g for t in [OWL.ObjectProperty,OWL.DatatypeProperty,OWL.AnnotationProperty])}
    check('Every project predicate declared',not declared,[str(p) for p in declared])
    changed=[]
    for rel,digest in manifest['source_files_sha256'].items():
        path=ROOT.parent/rel
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:changed.append(rel)
    check('Both source checkouts unchanged',not changed,changed)
    check('Source Git revisions match pinned baselines',all(manifest['verified_git_revisions'][key]==data['sources'][key] for key in manifest['verified_git_revisions']))
    upstream_changes=[]
    for url,expected in data['sources']['input_sha256'].items():
        if url.startswith('file:'):
            from urllib.parse import urlparse,unquote
            path=Path(unquote(urlparse(url).path).lstrip('/'))
        else:
            root=ROOT.parent/('FAIR-Maturity-Matrix' if 'Pistoia-Alliance-Inc' in url else 'FAIR-DAMA')
            path=root/url.split('/blob/',1)[1].split('/',1)[1]
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:upstream_changes.append(url)
    check('Approved upstream input digests match',not upstream_changes,upstream_changes)
    for rel,digest in manifest['baseline_inputs'].items():check('Baseline input unchanged '+rel,hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest)
    for name in MODULES:check('Download copy identical '+name,(ART/name).read_bytes()==(ROOT/'docs/ontology-data'/name).read_bytes())
    # Negative cases ensure the closed checks detect real model failures.
    tests=[]
    for case in ['two descriptor levels','missing indirect pathway','changed inherited type','positive L0']:
        bad=Graph();bad+=g
        if case=='two descriptor levels':bad.add((A['D1-L1'],A.atLevel,A.L2))
        elif case=='missing indirect pathway':
            n=next(n for n in bad.subjects(RDF.type,A.DimensionAlignment) if str(bad.value(n,A.contributionType))=='Indirect');bad.remove((n,A.viaPractice,None))
        elif case=='changed inherited type':
            n=next(n for n in bad.subjects(RDF.type,A.CumulativeAssociation) if str(bad.value(n,A.contributionType))=='Indirect');bad.set((n,A.contributionType,Literal('Direct')))
        else:
            n=next(bad.subjects(RDF.type,A.CumulativeAssociation));bad.set((n,A.targetsLevel,A.L0))
        detected=bool(structural_errors(bad));tests.append(dict(case=case,rejected=detected));check('Negative case rejected: '+case,detected)
    counts={str(c).split(':')[-1]:len(instances(g,c)) for c in [A.Dimension,A.MaturityLevel,A.Descriptor,A.Persona,A.DataRole,A.DimensionAlignment,A.OnsetAlignment,A.CumulativeAssociation,A.RoleAssignmentCandidate,A.AreaRoleOccurrence,A.ActivityRoleOccurrence,A.SourceAssertion]}
    report=dict(status='passed' if not failures else 'failed',check_count=len(checks),checks=checks,failures=failures,counts=counts,source_layers=dict(layer_counts),query_rows=queries,negative_cases=tests,triples=len(g),validation_method='RDFLib structural checks, source comparisons and SPARQL; no SHACL')
    write(OUT/'validation.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','check_count','counts','triples','failures']},indent=2))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
