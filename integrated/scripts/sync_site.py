"""Publish local documentation assets only; never deploy the site."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]

def sync():
    host=ROOT.parent
    if not (host/'zensical.toml').is_file():raise ValueError('Run inside FAIR-DAMA-FAIRMM')
    out=host/'docs/integrated/downloads';out.mkdir(parents=True,exist_ok=True)
    config=json.loads((ROOT/'release-config.json').read_text());candidate=ROOT/'release'/('FAIR-DAMA-Integrated-'+config['candidate_version']+'.zip')
    sources=[ROOT/'dist/merged-asserted.ttl',ROOT/'dist/merged.trig',candidate]
    manifest={'policy':'Copied from validated component outputs; no publication performed','files':[]}
    for source in sources:
        target=out/source.name;shutil.copyfile(source,target)
        digest=hashlib.sha256(source.read_bytes()).hexdigest();assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        manifest['files'].append({'path':source.name,'sha256':digest,'bytes':target.stat().st_size})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    reference=host/'docs/integrated/reference';reference.mkdir(exist_ok=True)
    for source in (ROOT/'docs/generated').iterdir():
        if source.is_file():shutil.copyfile(source,reference/source.name)
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':sync()
