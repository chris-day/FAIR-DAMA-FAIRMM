"""Shared offline RDF loading and vocabulary helpers. No inference or network imports."""
from pathlib import Path
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/ontology'
ART = ROOT / 'artefacts'
A = Namespace('urn:fair-dama-fairmm:alignment:')
MAP = Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-fair-mapping.ttl#')
PERSONA = Namespace('https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl#')
PROV = Namespace('http://www.w3.org/ns/prov#')
FAIR = Namespace('https://w3id.org/fair/principles/terms/')
MODULES = ['fairmm-core.ttl','fairmm-v1.2.5.ttl','fairmm-personas.ttl','fairmm-dama-alignment.ttl','fairmm-dama-derived.ttl']


def load(names=MODULES):
    graph = Graph()
    for name in names:
        graph.parse(ART / name, format='turtle')
    return graph


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
