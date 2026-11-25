"""Validate documentary fidelity, references and RDF without operational tests."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse
from zipfile import ZipFile
from html.parser import HTMLParser

from rdflib import Graph, Namespace, OWL, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / 'FAIR-DAMA'
X = Namespace('urn:fair-dama-fairmm:alignment:')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.hrefs.append(attrs['href'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fairmm', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--built-site', action='store_true')
    args = ap.parse_args()
    data_path = ROOT / 'artefacts/fairmm-crosswalk.json'
    data = json.loads(data_path.read_text(encoding='utf-8'))
    checks = []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def resolve_source(url):
        parts = urlparse(url)
        if parts.scheme=='file':return Path(unquote(parts.path).lstrip('/')),parts.fragment
        path = parts.path.split('/blob/', 1)[1].split('/', 1)[1]
        root = args.fairmm.resolve() if 'Pistoia-Alliance-Inc' in url else SOURCE_ROOT
        return root / path, parts.fragment

    for key in ['activities', 'assertions', 'dama_personas', 'persona_correspondences', 'descriptors', 'alignments']:
        records = data[key]
        check(key + ' unique IDs', len({a['id'] for a in records}) == len(records))
    expected_personas = {p.stem for p in (args.fairmm / 'docs/FAIR_personas').glob('*.md') if p.stem not in ['Overview_personas', 'X-template-FAIR_persona', 'file_list']}
    check('All upstream FAIRMM personas compared', {p['fairmm_persona'] for p in data['persona_correspondences']} == expected_personas)
    release=data['sources'].get('dama_source_release')
    check('All DAMA persona source entries retained', len(data['dama_personas']) == (123 if release else 108))
    check('All source activity rows retained', len(data['activities']) == (156 if release else 140))
    check('All 42 dimension and level cells retained', {d['id'] for d in data['descriptors']} == {f'D{i}-L{l}' for i in range(1, 8) for l in range(6)})
    if release:
        check('All ontology contribution records retained separately',sum(a['source_layer']=='ontology_contribution' for a in data['assertions'])==40)
        check('All ontology area assessments retained separately',sum(a['source_layer']=='ontology_area_assessment' for a in data['assertions'])==74)
        historical=json.loads((ROOT/'results/history/pre-2026-11-16-refresh/artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
        check('Earlier visualisation retained in historical corpus',sum(a['source_layer']=='visualisation' for a in historical['assertions'])==61)
    else:
        check('All nine ontology examples retained separately', sum(a['source_layer'] == 'ontology_example' for a in data['assertions']) == 9)
        with ZipFile(SOURCE_ROOT / 'artefacts/DAMA_FAIR_Sankey_v1.2.0.zip') as archive:
            original_visual = json.loads(archive.read('dama-fair-sankey-v1.2.0/data.json'))
        retained_visual = [a for a in data['assertions'] if a['source_layer'] == 'visualisation']
        check('All 61 Sankey records retained without rewriting', len(retained_visual) == 61 and [a['original_record'] for a in retained_visual] == original_visual['links'])
    for url, expected in data['sources']['input_sha256'].items():
        p, _ = resolve_source(url)
        check('Source digest: ' + p.name, hashlib.sha256(p.read_bytes()).hexdigest() == expected)
    activities = {a['id']: a for a in data['activities']}
    assertions = {a['id']: a for a in data['assertions']}
    personas = {p['id']: p for p in data['persona_correspondences']}
    descriptors = {d['id']: d for d in data['descriptors']}
    field_errors, source_errors = [], []
    for a in data['activities']:
        path, fragment = resolve_source(a['source'])
        line = path.read_text(encoding='utf-8-sig').splitlines()[int(fragment[1:]) - 1]
        fields = [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
        if list(a['source_fields'].values()) != fields:
            field_errors.append(a['id'])
        for kind, col in [('direct', 7), ('indirect', 11)]:
            original = set(re.findall(r'\b(?:F[1-4]|A[12](?:\.[12])?|I[1-3]|R1(?:\.[123])?)\b', fields[col]))
            if set(a[kind]) != original:
                source_errors.append(a['id'])
    check('All 12 activity fields equal the cited source row', not field_errors)
    check('No activity FAIR principle or Direct/Indirect label upgraded', not source_errors)
    descriptor_errors = []
    for d in data['descriptors']:
        p, fragment = resolve_source(d['source'])
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        if lines[int(fragment[1:]) - 1].strip() != '=== "' + d['dimension_label'] + '"':
            descriptor_errors.append(d['id'] + ' heading')
        if d['source_markdown'] not in p.read_text(encoding='utf-8-sig'):
            descriptor_errors.append(d['id'] + ' block')
    check('Every descriptor block and source line matches upstream text', not descriptor_errors)
    invalid = []
    missing_support = []
    for a in data['alignments']:
        if not a['descriptor_candidates'] or not a['descriptor_support']:
            missing_support.append(a['id'])
        for support in a['descriptor_support']:
            descriptor = descriptors[support['descriptor_id']]
            if not all(clause in descriptor['source_markdown'] for clause in support['source_clauses']):
                invalid.append(a['id'] + ' clause provenance')
        for d in a['descriptor_candidates']:
            if d not in descriptors or descriptors[d]['dimension'] != a['dimension']:
                invalid.append(a['id'] + ' dimension')
        source_id = a.get('source_assertion_id')
        if source_id:
            source = assertions[source_id]
            if (a['principle'], a['existing_contribution_type']) != (source['principle'], source['contribution_type']):
                invalid.append(a['id'] + ' source type')
        if a.get('existing_contribution_type') == 'Indirect' and not a.get('intermediate_practice'):
            invalid.append(a['id'] + ' missing intermediate practice')
        if a.get('proposed_dimension_contribution_type') == 'Indirect' and not a.get('dimension_intermediate_practice'):
            invalid.append(a['id'] + ' missing dimension intermediate practice')
        if a.get('assessed_level') is not None or a['operational_evidence_status'] != 'excluded by user' or a.get('local_reviewer') is not None:
            invalid.append(a['id'] + ' fabricated operational/local review result')
        for p in a['persona_candidates']:
            if p['persona_mapping_id'] not in personas:
                invalid.append(a['id'] + ' persona')
            if a.get('activity_id'):
                for occurrence in p.get('occurrences', []):
                    if occurrence['source_text'] != activities[a['activity_id']][occurrence['source_role_category']]:
                        invalid.append(a['id'] + ' role source')
    check('Every relationship has cited descriptor clauses', not missing_support)
    check('All crosswalk references and intermediate practices valid', not invalid)
    check('Gap rows never assert a functional equivalence', all(c['relationship'] == 'related counterpart; no equivalence asserted' for p in data['persona_correspondences'] if p['confidence'] == 'Gap' for c in p['candidates']))
    from fairmm_rdf import load, MODULES
    graph = load()
    check('RDF dimension alignments equal JSON alignments', len(set(graph.subjects(RDF.type, X.DimensionAlignment))) == len(data['alignments']))
    check('RDF persona correspondences equal JSON correspondences', len(set(graph.subjects(RDF.type, X.PersonaCorrespondence))) == 30)
    check('RDF descriptors equal JSON descriptors', len(set(graph.subjects(RDF.type, X.Descriptor))) == 42)
    check('Ontology avoids identity and exact equivalence assertions', not list(graph.triples((None, OWL.sameAs, None))) and not list(graph.triples((None, URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'), None))))
    check('JSON downloads identical to canonical artefact', (ROOT / 'docs/fairmm/data/crosswalk.json').read_bytes() == data_path.read_bytes() == (args.output / 'fairmm-crosswalk.json').read_bytes())
    check('Modular RDF downloads identical to canonical artefacts', all((ROOT/'docs/ontology-data'/name).read_bytes()==(ROOT/'artefacts'/name).read_bytes() for name in MODULES))
    broken = []
    for page in (ROOT / 'docs/fairmm').glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', page.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                path = (page.parent / unquote(target.split('#')[0])).resolve()
                if not path.exists():
                    broken.append(str(path))
    check('All crosswalk-page relative links resolve', not broken)
    if args.built_site:
        broken_html = []
        site = ROOT / 'site'
        rendered_pages = list((site / 'fairmm').rglob('index.html')) + [site / 'index.html']
        check('All 13 crosswalk pages built', len(list((site / 'fairmm').rglob('index.html'))) == 13)
        parsed = {}
        for page in rendered_pages:
            parser = Links()
            parser.feed(page.read_text(encoding='utf-8'))
            parsed[page.resolve()] = parser
        for page, parser in list(parsed.items()):
            for href in parser.hrefs:
                url = urlparse(href)
                if url.scheme or url.netloc:
                    continue
                dest = (site / unquote(url.path).lstrip('/')) if url.path.startswith('/') else page.parent / unquote(url.path) if url.path else page
                dest = dest.resolve()
                if dest.is_dir():
                    dest = dest / 'index.html'
                if not dest.exists():
                    broken_html.append(str(page) + ' → ' + href)
                elif url.fragment and dest.suffix == '.html':
                    if dest not in parsed:
                        other = Links()
                        other.feed(dest.read_text(encoding='utf-8'))
                        parsed[dest] = other
                    if unquote(url.fragment) not in parsed[dest].ids:
                        broken_html.append(str(page) + ' → ' + href)
        check('Rendered navigation, downloads and anchors resolve', not broken_html)
    report = {'status': 'passed', 'scope': 'documentary fidelity and structure; no operational pilot', 'checks': checks, 'rdf_triples': len(graph), 'alignment_count': len(data['alignments']), 'dimensions': dict(Counter(a['dimension'] for a in data['alignments'])), 'persona_confidence': dict(Counter(p['confidence'] for p in data['persona_correspondences']))}
    (args.output / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, indent=2))
    print(f'{len(checks)} documentary checks passed')


if __name__ == '__main__':
    main()
