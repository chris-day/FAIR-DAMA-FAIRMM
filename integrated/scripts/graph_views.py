"""Explicit graph scope for consumers; documentary remains separate from asserted."""
from pathlib import Path
import argparse,json
from rdflib import Graph,Dataset
ROOT=Path(__file__).resolve().parents[1]

def load(view):
    if view=='integrated-asserted':
        return Graph().parse(ROOT/'dist/merged-asserted.ttl',format='turtle')
    if view=='source-provenance':
        graph=Dataset(default_union=False);graph.parse(ROOT/'dist/merged.trig',format='trig');return graph
    if view=='documentary':
        graph=Graph()
        for directory in [ROOT/'inputs/originals/artefacts',ROOT/'inputs/originals/sources/2026-11-16/dama-ontologies-v1.1.0']:
            for path in sorted(directory.glob('*.ttl')):graph.parse(path,format='turtle')
        return graph
    raise ValueError('Choose documentary, integrated-asserted or source-provenance')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--view',required=True,choices=['documentary','integrated-asserted','source-provenance']);parser.add_argument('--query',type=Path);args=parser.parse_args()
    graph=load(args.view)
    if args.query:
        result=graph.query(args.query.read_text(encoding='utf-8'));print(result.serialize(format='json').decode())
    else:print(json.dumps({'view':args.view,'triples':len(graph),'default_union':getattr(graph,'default_union',False)}))
