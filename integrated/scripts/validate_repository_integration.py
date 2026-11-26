"""Check graph-policy boundaries, host drift rejection and host/site copies."""
import json,tempfile,shutil,hashlib
from pathlib import Path
from rdflib import Graph,RDF,URIRef
from rdflib.compare import isomorphic
from graph_views import load,ROOT
import verify_host_sources

def main():
    checks=[]
    def check(name,ok):
        checks.append({'check':name,'passed':bool(ok)})
        if not ok:raise AssertionError(name)
    result=verify_host_sources.verify();check('All nine host source modules match pinned originals',result['checked']==9)
    asserted=load('integrated-asserted');check('Asserted graph equals accepted semantic baseline',len(asserted)==95008 and isomorphic(asserted,Graph().parse(ROOT/'baseline/g4-approved-asserted.ttl')))
    documentary=load('documentary');cumulative=URIRef('urn:fair-dama-fairmm:alignment:CumulativeAssociation')
    check('Historical documentary graph retains derived associations outside the asserted scope',len(set(documentary.subjects(RDF.type,cumulative)))==127 and not list(asserted.subjects(RDF.type,cumulative)))
    dataset=load('source-provenance');check('Released dataset default is empty and union disabled',not dataset.default_union and len(dataset.default_context)==0)
    manifest=json.loads((ROOT/'dist/merge-manifest.jsonld').read_text());check('Dataset preserves sixteen source graphs',len(manifest['source_graphs'])==16)
    baseline=ROOT.parent/'releases/integrated/1.0.0-rc.1/FAIR-DAMA-Integrated-1.0.0-rc.1.zip';expected=json.loads((ROOT/'integration-provenance.json').read_text())['accepted_candidate_sha256'];check('Accepted archive is unchanged',hashlib.sha256(baseline.read_bytes()).hexdigest()==expected)
    with tempfile.TemporaryDirectory() as directory:
        host=Path(directory);component=host/'integrated';component.mkdir()
        shutil.copytree(ROOT/'inputs/originals',component/'inputs/originals')
        shutil.copytree(ROOT/'.github',component/'.github');shutil.copytree(ROOT.parent/'artefacts',host/'artefacts')
        source=host/'sources/2026-11-16/dama-ontologies-v1.1.0';source.parent.mkdir(parents=True);shutil.copytree(ROOT/'inputs/originals/sources/2026-11-16/dama-ontologies-v1.1.0',source)
        (host/'.github/workflows').mkdir(parents=True);shutil.copyfile(ROOT/'.github/workflows/candidate.yml',host/'.github/workflows/integrated.yml')
        original=verify_host_sources.ROOT;verify_host_sources.ROOT=component
        try:
            verify_host_sources.verify();p=host/'artefacts/fairmm-core.ttl';p.write_bytes(p.read_bytes()+b'\n# drift\n')
            try:verify_host_sources.verify();rejected=False
            except ValueError:rejected=True
            check('Host source drift is rejected before candidate creation',rejected)
        finally:verify_host_sources.ROOT=original
    downloads=ROOT.parent/'docs/integrated/downloads';entries=json.loads((downloads/'manifest.json').read_text())['files']
    check('Every local site download matches its recorded checksum',all(hashlib.sha256((downloads/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in entries))
    report={'passed':len(checks),'failed':0,'checks':checks};(ROOT/'validation/repository-integration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
