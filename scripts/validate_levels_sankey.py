"""Independent fidelity and cumulative-association validation for the level diagram."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse,unquote

ROOT=Path(__file__).resolve().parents[1]
PREFIX='dama-fairmm-levels-sankey'


def main():
    data=json.loads((ROOT/'results/levels'/(PREFIX+'.json')).read_text(encoding='utf-8'))
    corpus=json.loads((ROOT/'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    desc={d['id']:d for d in corpus['descriptors']}
    acts={a['id']:a for a in corpus['activities']}
    checks=[]
    def check(name,test):
        if not test:raise AssertionError(name)
        checks.append(name)
    areas={o['area_id'] for o in data['onsets']}
    check('Source areas match onset judgements', {n['id'] for n in data['nodes'] if n['side']=='source'}==areas)
    check('All six level nodes',{n['id'] for n in data['nodes'] if n['side']=='target'}=={f'L{i}' for i in range(6)})
    check('All 42 descriptor references reviewed',set(data['reviewed_descriptor_ids'])==set(desc))
    check('All positive-level area reviews',len(data['level_review'])==5*len(areas))
    check('All L0 diagnostics retained',len(data['diagnostic_baseline'])==len(areas))
    check('L0 is unconnected baseline',not any(l['target']=='L0' for l in data['links']))
    check('Unique area-level-type relations',len(data['links'])==len({(l['source'],l['target'],l['kind']) for l in data['links']}))
    for o in data['onsets']:
        evidence=o['earliest_level_evidence']
        check('Onset source clause '+o['id'],evidence['clause'] in desc[evidence['descriptor_id']]['source_markdown'] and evidence['phrase'].lower() in evidence['clause'].lower())
        check('Onset deliverables '+o['id'],o['deliverables']==[acts[a]['deliverables'] for a in o['activity_ids']])
        check('Indirect pathway '+o['id'],o['kind']!='Indirect' or bool(o['intermediate_practice']))
        links=[l for l in data['links'] if l['onset_id']==o['id']]
        check('Full inheritance closure '+o['id'],{int(l['target'][1:]) for l in links}==set(range(o['first_supported_level'],6)))
        check('Type retained '+o['id'],all(l['kind']==o['kind'] for l in links))
        check('Correct inherited flags '+o['id'],all(l['inherited']==(int(l['target'][1:])>o['first_supported_level']) for l in links))
    for review in data['level_review']:
        for e in review['descriptor_evidence']:
            check('Progression source '+review['area_id']+' L'+str(review['level'])+' '+e['descriptor_id'],e['clause'] in desc[e['descriptor_id']]['source_markdown'])
    check('Every ribbon has equal unit weight',all(l['value']==1 for l in data['links']))
    for level in range(1,5):
        before={(l['source'],l['kind']) for l in data['links'] if l['target']==f'L{level}'}
        after={(l['source'],l['kind']) for l in data['links'] if l['target']==f'L{level+1}'}
        check('Monotone L'+str(level),before<=after)
    ns={'s':'http://www.w3.org/2000/svg'}
    xml=ET.parse(ROOT/'results/levels'/(PREFIX+'.svg'))
    check('One SVG ribbon per relationship',len(xml.findall('.//s:path[@data-link]',ns))==len(data['links']))
    for ext in ['svg','json','html','png']:
        check('Matching distributed '+ext,(ROOT/'results/levels'/(PREFIX+'.'+ext)).read_bytes()==(ROOT/'docs/levels'/(PREFIX+'.'+ext)).read_bytes())
    html=(ROOT/'results/levels'/(PREFIX+'.html')).read_text(encoding='utf-8')
    check('No dropdown selectors','<select' not in html)
    check('L0 forced to target column',"nodeAlign(d=>d.side==='source'?0:1)" in html)
    md=(ROOT/'docs/levels/index.md').read_text(encoding='utf-8')
    check('Interactive iframe loads on demand',not re.search(r'<iframe[^>]+\bsrc=',md) and 'Load interactive diagram' in md)
    for page in (ROOT/'docs/levels').glob('*.md'):
        for href in re.findall(r'\]\(([^)]+)\)',page.read_text(encoding='utf-8')):
            u=urlparse(href)
            if not u.scheme and u.path:
                check('Local link '+href,(page.parent/unquote(u.path)).exists())
    built=ROOT/'site/levels/index.html'
    check('Built levels page exists',built.exists())
    report=dict(status='passed',scope='documentary fidelity and cumulative graph semantics; no operational maturity assessment',checks=checks,check_count=len(checks),onsets=len(data['onsets']),cumulative_links=len(data['links']),counts=data['counts'],level_counts=data['level_counts'])
    (ROOT/'results/levels/dama-fairmm-levels-independent-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(str(len(checks))+' independent level checks passed')


if __name__=='__main__':main()
