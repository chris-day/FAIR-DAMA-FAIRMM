"""Independently check supplied source fidelity and the combined nine-module graph."""
import json,hashlib
from pathlib import Path
from rdflib import Graph,RDF,RDFS,Namespace,URIRef
from fairmm_rdf import A,MAP,MODULES,load,write

ROOT=Path(__file__).resolve().parents[1]
def main():
    corpus=json.loads((ROOT/'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    package=ROOT/corpus['sources']['ontology_directory']
    g=Graph();checks=[]
    def check(label,condition):
        if not condition:raise AssertionError(label)
        checks.append(label)
    for name in ['fair-ontology.ttl','dama-ontology.ttl','dama-fair-mapping.ttl','dama-persona-ontology.ttl']:
        g.parse(package/name,format='turtle')
        check('Byte-identical source dependency '+name,(package/name).read_bytes()==(ROOT/'docs/ontology-data/dama-source-v1.1.0'/name).read_bytes())
    source=Graph().parse(package/'dama-fair-mapping.ttl',format='turtle')
    for a in corpus['assertions']:
        if not a.get('source_node'):continue
        node=URIRef(a['source_node'])
        check('Exact source predicates retained '+a['id'],a['source_fields']=={str(p):[str(o) for o in source.objects(node,p)] for p in sorted(set(source.predicates(node)),key=str)})
    for name in MODULES:g.parse(ROOT/'artefacts'/name,format='turtle')
    dama=Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-ontology.ttl#')
    check('Source core enumeration stays eleven',len(set(g.subjects(RDF.type,dama['DMBOK2-2017-KnowledgeArea'])))==11)
    check('Source additional topics stay three',len(set(g.subjects(RDF.type,dama.AdditionalTopic)))==3)
    check('Alignment core knowledge areas stay eleven',len(set(g.subjects(RDF.type,A.SourceKnowledgeArea)))==11)
    check('New topics are not classified as core areas',all((A[f'AREA-{i}'],RDF.type,A.SourceTopic) in g and (A[f'AREA-{i}'],RDF.type,A.SourceKnowledgeArea) not in g for i in [12,13,14]))
    activities={a['coordinate']:a for a in corpus['activities']}
    new_source_nodes=set(source.subjects(RDF.type,MAP.SourceActivity))
    for n in new_source_nodes:
        sheet=str(source.value(n,MAP.sourceWorksheet));row=int(source.value(n,MAP.sourceRow));coord=f'{sheet}!A{row}:L{row}'
        check('Ontology source activity matches workbook label '+coord,str(source.value(n,RDFS.label))==activities[coord]['activity'])
        expected={(str(source.value(c,MAP.targetsPrinciple)).rsplit('/',1)[-1],kind) for kind in ['Direct','Indirect'] for c in source.subjects(MAP.fromPractice,n) if (c,RDF.type,MAP[kind+'Contribution']) in source}
        actual={(p,kind.title()) for kind in ['direct','indirect'] for p in activities[coord][kind]}
        check('Ontology new activity classifications match document/workbook '+coord,actual==expected)
    new_counts={str(c).split(':')[-1]:len(set(g.subjects(RDF.type,c))) for c in [A.DimensionAlignment,A.OnsetAlignment,A.CumulativeAssociation,A.SourceAssertion]}
    check('No unsupported Big Data FAIR Knowledge link',not any(g.value(n,A.sourceTopic)==A['AREA-13'] and g.value(n,A.targetsDimension)==A.D6 for n in g.subjects(RDF.type,A.DimensionAlignment)))
    for original,copy in [('DAMA_Segments_High_Level_v1.18.0.md','DAMA_Segments_High_Level_v1.18.0.md'),('DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx','DAMA-PDOC_FAIR-MASTER_2026-11-16_V3.xlsx'),('outputs/DAMA_FAIR_Ontologies_v1.1.0.zip','DAMA_FAIR_Ontologies_v1.1.0.zip')]:
        check('Original input preserved '+original,(ROOT.parents[1]/original).read_bytes()==(ROOT/'sources/2026-11-16'/copy).read_bytes())
    report=dict(status='passed',check_count=len(checks),checks=checks,combined_nine_module_triples=len(g),counts=new_counts)
    write(ROOT/'results/ontology/source-union-validation.json',json.dumps(report,indent=2)+'\n')
    print(f'{len(checks)} independent supplied-source/union checks passed')

if __name__=='__main__':main()
