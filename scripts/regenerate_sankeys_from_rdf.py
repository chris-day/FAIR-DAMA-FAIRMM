"""Extract diagram inputs exclusively from RDF; approved JSON is comparison-only."""
from collections import Counter
import json
import textwrap

from rdflib import RDF, RDFS
from rdflib.namespace import DCTERMS as DC
from fairmm_rdf import ROOT, OUT, A, FAIR, load, write


def value(g,n,p,default=None):
    values=sorted(g.objects(n,p),key=str)
    return str(values[0]) if values else default


def values(g,n,p):return sorted(str(v) for v in g.objects(n,p))


def identifier(g,n):return value(g,n,DC.identifier,str(n).split(':')[-1])


def label(g,n):return value(g,n,RDFS.label)


def source_metadata(g):
    result={}
    for repo,key in [('FAIR-DAMA','fair_dama_revision'),('FAIR-Maturity-Matrix','fairmm_revision')]:
        result[key]=value(g,A['snapshot-'+repo],A.sourceRevision)
    result['fairmm_branch']=value(g,A['snapshot-FAIR-Maturity-Matrix'],A.sourceBranch)
    result['input_sha256']={value(g,n,DC.source):value(g,n,A.sha256) for n in g.subjects(A.sha256,None)}
    return result


def topics(g):
    ns=set(g.subjects(RDF.type,A.SourceTopic))|set(g.subjects(RDF.type,A.SourceKnowledgeArea))
    return [dict(id=identifier(g,n),number=int(value(g,n,A.topicNumber)),name=label(g,n),aggregate=value(g,n,A.aggregate)=='true',source=value(g,n,A.primarySource)) for n in sorted(ns,key=lambda n:int(value(g,n,A.topicNumber)))]


def evidence(g,n):
    d=g.value(n,A.supportedByDescriptor)
    return dict(descriptor_id=identifier(g,d),phrase=value(g,n,A.matchingPhrase),clause=value(g,n,A.sourceText),source=value(g,n,A.primarySource))


def dimensions(g):
    alignments=[]
    for n in sorted(g.subjects(RDF.type,A.DimensionAlignment),key=str):
        p=g.value(n,A.fromPractice);area=g.value(n,A.sourceTopic);target=g.value(n,A.targetsDimension);principle=g.value(n,A.targetsPrinciple);source=g.value(n,A.sourceAssertion)
        deliverables=[label(g,d) for d in g.objects(n,A.hasDeliverable)]
        alignments.append(dict(id=identifier(g,n),activity_id=identifier(g,p) if identifier(g,p).startswith('ACT-') else None,area_id=identifier(g,area) if area else None,dimension=identifier(g,target),proposed_dimension_contribution_type=value(g,n,A.contributionType),activity=label(g,p),deliverable=deliverables[0],principle=str(principle).split('/')[-1] if principle else None,existing_contribution_type=value(g,n,A.existingContributionType),condition=value(g,n,A.applicabilityCondition),source=value(g,n,A.primarySource),source_assertion_id=identifier(g,source) if source else None,descriptor_candidates=sorted(identifier(g,d) for d in g.objects(n,A.supportedByDescriptor))))
    assertions=[dict(id=identifier(g,n),rationale=value(g,n,A.rationale)) for n in g.subjects(RDF.type,A.SourceAssertion)]
    return dict(summaries=topics(g),sources=source_metadata(g),alignments=alignments,assertions=assertions)


def get_onsets(g):
    result=[]
    for n in sorted(g.subjects(RDF.type,A.OnsetAlignment),key=str):
        bundle=g.value(n,A.fromPractice);area=g.value(n,A.sourceTopic)
        members=sorted(g.objects(bundle,DC.hasPart),key=lambda p:identifier(g,p))
        delivers=[label(g,next(g.objects(p,A.hasDeliverable))) for p in members]
        ev=next(g.objects(n,A.hasDescriptorEvidence));via=g.value(n,A.viaPractice)
        result.append(dict(id=identifier(g,n),area_id=identifier(g,area),area_name=label(g,area),kind=value(g,n,A.contributionType),first_supported_level=int(value(g,g.value(n,A.firstSupportedLevel),A.levelOrdinal)),rationale=value(g,n,A.rationale),intermediate_practice=label(g,via) if via else None,earliest_level_evidence=evidence(g,ev),activity_ids=[identifier(g,p) for p in members],activities=[label(g,p) for p in members],deliverables=delivers,source_references=values(g,n,DC.source),source_fair_direct=sorted(str(p).split('/')[-1] for p in g.objects(n,A.reportedDirectFAIRPrinciple)),source_fair_indirect=sorted(str(p).split('/')[-1] for p in g.objects(n,A.reportedIndirectFAIRPrinciple)),status=value(g,n,A.reviewStatus)))
    return result


def get_reviews(g,onsets):
    result=[]
    for n in sorted(g.subjects(RDF.type,A.LevelReview),key=str):
        if (n,RDF.type,A.DiagnosticReview) in g:continue
        area=identifier(g,g.value(n,A.sourceTopic));level=int(value(g,g.value(n,A.atLevel),A.levelOrdinal))
        related={o['kind']:o['first_supported_level'] for o in onsets if o['area_id']==area}
        result.append(dict(area_id=area,level=level,descriptor_evidence=[evidence(g,e) for e in sorted(g.objects(n,A.hasDescriptorEvidence),key=str)],direct_active=level>=related['Direct'],indirect_active=level>=related['Indirect'],interpretation=value(g,n,A.rationale)))
    return result


def levels(g):
    onsets=get_onsets(g);oi={o['id']:o for o in onsets};reviews=get_reviews(g,onsets)
    links=[]
    for n in sorted(g.subjects(RDF.type,A.CumulativeAssociation),key=str):
        onset=oi[identifier(g,g.value(n,A.derivedFromOnset))];target=g.value(n,A.targetsLevel);level=int(value(g,target,A.levelOrdinal));area=g.value(n,A.sourceTopic);kind=value(g,n,A.contributionType);start=onset['first_supported_level'];inherited=value(g,n,A.inherited)=='true'
        progress=next(r for r in reviews if r['area_id']==identifier(g,area) and r['level']==level)
        ev=[evidence(g,e) for e in sorted(g.objects(n,A.hasDescriptorEvidence),key=str)]
        rationale=[onset['rationale'],f'First supported at L{start}; '+(f'carried forward to L{level} under the requested cumulative association.' if inherited else 'introduced at this level.')]
        if onset['intermediate_practice']:rationale.append('Indirect pathway via: '+onset['intermediate_practice'])
        rationale += [e['descriptor_id']+': '+e['clause'] for e in progress['descriptor_evidence']]
        target_label=label(g,target);target_label=target_label.replace('L'+str(level)+' ','L'+str(level)+' · ',1)
        links.append(dict(id=identifier(g,n),source=identifier(g,area),target=identifier(g,target),kind=kind,value=1,source_label=label(g,area),target_label=target_label,onset_id=onset['id'],first_supported_level=start,inherited=inherited,inheritance_path=list(range(start,level+1)),intermediate_practice=onset['intermediate_practice'],rationales=rationale,deliverables=onset['deliverables'],activities=onset['activities'],underlying_record_count=1,principles=sorted(set(onset['source_fair_direct']+onset['source_fair_indirect'])),original_fair_contribution_types=[kind for kind,key in [('Direct','source_fair_direct'),('Indirect','source_fair_indirect')] if onset[key]],conditions=values(g,n,A.applicabilityCondition),descriptor_ids=sorted(identifier(g,d) for d in g.objects(n,A.supportedByDescriptor)),sources=sorted(set(onset['source_references']+[e['source'] for e in ev])),evidence=ev))
    counts=Counter(l['kind'] for l in links);degree=Counter()
    for l in links:degree[l['source']]+=1;degree[l['target']]+=1
    W,H,left,right,bar,top,bottom=1800,1120,435,1265,16,205,1005
    onset_areas={o['area_id'] for o in onsets}
    areas={s['number']:s for s in topics(g) if s['id'] in onset_areas}
    unit=(bottom-top-(len(areas)-1)*24)/len(links)
    nodes=[]
    items=[('source',[(a['id'],str(i)+'. '+a['name']) for i,a in areas.items()],24),('target',[(identifier(g,n),label(g,n).replace(identifier(g,n)+' ',identifier(g,n)+' · ',1)+(' (baseline)' if identifier(g,n)=='L0' else '')) for n in sorted(g.subjects(RDF.type,A.MaturityLevel),key=lambda n:int(value(g,n,A.levelOrdinal)))],28)]
    meta=source_metadata(g)
    for side,labels,gap in items:
        total=sum(degree[k]*unit for k,_ in labels)+gap*(len(labels)-1);y=top+(bottom-top-total)/2
        for key,lab in labels:
            href=('../source-release.html#section-'+str(int(key[-2:])) if areas[int(key[-2:])]['source'].startswith('file:') else 'https://fair-dama.perdl.com/dama/segments/'+areas[int(key[-2:])]['source'].split('/')[-1].split('.md')[0]+'/') if side=='source' else ('https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/'+meta['fairmm_revision']+'/docs/level'+key[1:]+'.md')
            nodes.append(dict(id=key,side=side,label=lab,lines=textwrap.wrap(lab,36 if side=='source' else 34),x=left if side=='source' else right,y=y,height=degree[key]*unit,degree=degree[key],documentation_url=href));y+=degree[key]*unit+gap
    ni={n['id']:n for n in nodes};so=Counter();to=Counter()
    links.sort(key=lambda l:(l['source'],l['target'],l['kind']))
    for l in links:
        l['geometry']=dict(x0=left+bar,x1=right,y0=ni[l['source']]['y']+so[l['source']]*unit,y1=ni[l['target']]['y']+to[l['target']]*unit,thickness=unit);so[l['source']]+=1;to[l['target']]+=1
    baseline=[]
    for n in sorted(g.subjects(RDF.type,A.DiagnosticReview),key=str):baseline.append(dict(area_id=identifier(g,g.value(n,A.sourceTopic)),level=0,classification='diagnostic only',source=value(g,n,DC.source),descriptor=identifier(g,g.value(n,A.supportedByDescriptor)),rationale=value(g,n,A.rationale)))
    level_counts={f'L{i}':dict(Counter(l['kind'] for l in links if l['target']==f'L{i}')) for i in range(6)}
    model=dict(title='DAMA knowledge areas and FAIRMM maturity levels',width=W,height=H,nodes=nodes,links=links,counts=dict(counts),onsets=onsets,level_review=reviews,diagnostic_baseline=baseline,reviewed_descriptor_ids=sorted(identifier(g,n) for n in g.subjects(RDF.type,A.Descriptor)),level_counts=level_counts,source_revisions=meta,unit='One equal-width ribbon per knowledge area, level and contribution type',method='RDF onset assertions and explicitly derived cumulative RDF associations; no maturity scores',excluded=['Aggregate Data Management overview','Supporting Maturity Assessment discipline'],conditional=True)
    return model,areas,dict(sources=meta)


def main():
    graph=load();d=dimensions(graph);l,areas,corpus=levels(graph)
    approved_d=json.loads((OUT/'baselines/dimensions-approved.json').read_text(encoding='utf-8'));approved_l=json.loads((OUT/'baselines/levels-approved.json').read_text(encoding='utf-8'))
    expected_d={(x['source'],x['target'],x['kind']):x['underlying_record_count'] for x in approved_d['links']}
    actual_d=Counter((a['area_id'],a['dimension'],a['proposed_dimension_contribution_type']) for a in d['alignments'] if a['area_id'])
    expected_l={(x['source'],x['target'],x['kind'],x['first_supported_level'],x['inherited']) for x in approved_l['links']}
    actual_l={(x['source'],x['target'],x['kind'],x['first_supported_level'],x['inherited']) for x in l['links']}
    report=dict(status='passed' if actual_d==expected_d and actual_l==expected_l else 'failed',dimensions=dict(expected=len(expected_d),actual=len(actual_d),relationships_equal=actual_d==expected_d),levels=dict(expected=len(expected_l),actual=len(actual_l),relationships_equal=actual_l==expected_l),input='five modular Turtle files; no JSON relationship literals',approved_json_use='regression comparison only')
    write(OUT/'rdf-sankey-regression.json',json.dumps(report,indent=2)+'\n')
    if report['status']!='passed':raise AssertionError(report)
    write(OUT/'rdf-dimensions-input.json',json.dumps(d,ensure_ascii=False,indent=2)+'\n');write(OUT/'rdf-levels-model.json',json.dumps(l,ensure_ascii=False,indent=2)+'\n')
    from build_dimension_sankey import main as render_dimensions
    from build_levels_sankey import render_model as render_levels
    render_dimensions(d);render_levels(l,areas,corpus)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
