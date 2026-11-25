"""Render the ontology structure with the existing Graphviz installation."""
from pathlib import Path
import subprocess
from rdflib import RDF
from fairmm_rdf import ROOT, OUT, A, load, write


def main():
    g=load();template=(ROOT/'scripts/templates/fairmm-model.dot').read_text(encoding='utf-8')
    for key,cls in [('DIMENSIONS',A.Dimension),('LEVELS',A.MaturityLevel),('DESCRIPTORS',A.Descriptor),('DIMENSION_ASSERTIONS',A.DimensionAlignment),('ONSETS',A.OnsetAlignment),('CUMULATIVE',A.CumulativeAssociation),('PERSONAS',A.Persona),('SOURCE_ASSERTIONS',A.SourceAssertion)]:
        template=template.replace('__'+key+'__',str(len(set(g.subjects(RDF.type,cls)))))
    dot=OUT/'fairmm-ontology.dot';write(dot,template)
    for ext in ['svg']:
        dest=OUT/('fairmm-ontology.'+ext)
        subprocess.run(['dot','-T'+ext,str(dot),'-o',str(dest)],check=True)
        copy=ROOT/'docs/assets/images'/dest.name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(dest.read_bytes())
    print('Rendered ontology SVG from module counts')


if __name__=='__main__':main()
