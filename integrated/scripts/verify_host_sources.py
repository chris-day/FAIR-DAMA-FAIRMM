"""Fail on host source drift; relocated exports still enforce their own input locks."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def verify():
    host=ROOT.parent
    if not (host/'artefacts').is_dir():
        print('Standalone component: host comparison unavailable; embedded locks remain mandatory.')
        return {'host_available':False,'checked':0}
    pairs=[]
    for path in sorted((ROOT/'inputs/originals/artefacts').glob('*.ttl')):
        pairs.append((host/'artefacts'/path.name,path))
    for path in sorted((ROOT/'inputs/originals/sources/2026-11-16/dama-ontologies-v1.1.0').glob('*.ttl')):
        pairs.append((host/'sources/2026-11-16/dama-ontologies-v1.1.0'/path.name,path))
    assert len(pairs)==9,'Expected nine pinned source modules'
    for original,pinned in pairs:
        if not original.is_file() or original.read_bytes()!=pinned.read_bytes():
            raise ValueError('Host source drift requires a reviewed baseline update: '+str(original))
    hosted=host/'.github/workflows/integrated.yml'
    assert hosted.read_bytes()==(ROOT/'.github/workflows/candidate.yml').read_bytes(),'Workflow copies differ'
    result={'host_available':True,'checked':len(pairs),'sha256':{str(a.relative_to(host)).replace('\\','/'):hashlib.sha256(a.read_bytes()).hexdigest() for a,b in pairs}}
    print(json.dumps(result,indent=2));return result

if __name__=='__main__':verify()
