"""Build a source-traceable documentary FAIRMM crosswalk. No maturity scoring.

Requires rdflib; run from any directory with --fairmm pointing to the pinned clone.
Generated JSON preserves source text; Markdown presents the documentary findings.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, OWL

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / 'FAIR-DAMA'
DAMA_SHA = "438ad2d0c6be3c336254fe3ce6a5d93f111db8a0"
MM_SHA = "8ff4676eb340b0da5034ffb3d0e901c594c3cfc4"
DB = f"https://github.com/chris-day/FAIR-DAMA/blob/{DAMA_SHA}/"
MB = f"https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/{MM_SHA}/"
BASE = "urn:fair-dama-fairmm:alignment:"
X = Namespace(BASE)
MAP = Namespace("https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-fair-mapping.ttl#")
PERSONA = Namespace("https://github.com/chris-day/FAIR-DAMA/blob/main/artefacts/dama-persona-ontology.ttl#")
FAIR = Namespace("https://w3id.org/fair/principles/terms/")
IDS = ['F1', 'F2', 'F3', 'F4', 'A1', 'A1.1', 'A1.2', 'A2', 'I1', 'I2', 'I3', 'R1', 'R1.1', 'R1.2', 'R1.3']
DIMENSIONS = ['FAIR Data', 'FAIR Leadership', 'FAIR Strategy', 'FAIR Personas', 'FAIR Processes', 'FAIR Knowledge', 'FAIR Tools and Infrastructures']


def read(p):
    return p.read_text(encoding='utf-8-sig')


def save(p, content):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8', newline='\n')


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def ids(s):
    return sorted(set(re.findall(r'\b(?:F[1-4]|A[12](?:\.[12])?|I[1-3]|R1(?:\.[123])?)\b', s)), key=IDS.index)


def rows(text):
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.startswith('|'):
            cells = [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
            if cells and not re.fullmatch(r'[-: ]+', cells[0]):
                yield line_no, cells


def table(headers, records):
    def esc(v):
        if isinstance(v, list):
            v = '; '.join(str(x) for x in v)
        return str(v or '—').replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(esc(x) for x in r) + ' |' for r in records])


TESTS = {
    'F1': 'Inspect globally unique persistent identifiers for data and metadata, persistence commitments and resolution arrangements.',
    'F2': 'Inspect rich resource-linked metadata against an explicit discovery profile.',
    'F3': 'Check that metadata explicitly contains the identifier of the data it describes.',
    'F4': 'Search a catalogue/index and confirm representative data or metadata records are returned.',
    'A1': 'Retrieve data and metadata by identifier through a standard communications protocol.',
    'A1.1': 'Inspect the retrieval protocol specification for openness, absence of fees and universal implementability.',
    'A1.2': 'Test that the retrieval protocol supports authentication and authorization where necessary.',
    'A2': 'Retrieve metadata after the underlying data is no longer available.',
    'I1': 'Parse the actual data/metadata representation and inspect its formal, accessible, shared language.',
    'I2': 'Inspect identifiers, access, representation, provenance and licensing of the vocabularies actually used.',
    'I3': 'Inspect qualified references identifying related resources and the meanings of the relations.',
    'R1': 'Validate multiple accurate and relevant descriptive attributes needed for reuse.',
    'R1.1': 'Inspect a clear accessible usage licence applicable to the resource.',
    'R1.2': 'Trace linked provenance to sources, agents, transformations, dates and versions.',
    'R1.3': 'Compare data and metadata with relevant community standards and document conformance.',
}
VIA = {
    'F1': 'Implement and operate a persistent identifier service for data and metadata',
    'F2': 'Publish and validate resource-linked discovery metadata',
    'F3': 'Include the described data identifier explicitly in metadata',
    'F4': 'Register and index identified resources in a searchable catalogue',
    'A1': 'Implement identifier-based retrieval through a standard protocol',
    'A1.1': 'Select and implement an open free universally implementable retrieval protocol',
    'A1.2': 'Configure and test protocol authentication and authorization',
    'A2': 'Preserve and serve metadata independently of data availability',
    'I1': 'Publish data or metadata in a formal accessible shared representation',
    'I2': 'Publish and maintain FAIR vocabularies used by resources',
    'I3': 'Publish qualified references between identifiable resources',
    'R1': 'Publish and validate accurate relevant reuse descriptions',
    'R1.1': 'Attach an applicable clear accessible usage licence to the resource',
    'R1.2': 'Capture and publish detailed resource-linked provenance',
    'R1.3': 'Implement and validate relevant community standards',
}

# Explicit many-to-many candidate names from the plan, resolved to source catalogue
# entries. Gap rows retain counterparts without asserting an equivalence.
CANDIDATES = {
    'Business_Analyst': ['Business and Data Analysts', 'BI Analysts'],
    'Business_Leader': ['Business Executives', 'Executives', 'Senior management'],
    'Business_Owner': ['Business Executives and Managers', 'Managers and Executives'],
    'Citizen_Data_Scientist': ['Business Users', 'BI and Reporting Users'],
    'Clinical_Data_Manager': ['Data Stewards', 'Data Quality Analysts'],
    'Curator': ['Meta-data Specialist', 'Records Management Staff', 'Data Stewards'],
    'Data_Analyst': ['BI Analysts', 'Data Analysts', 'BI Specialists'],
    'Data_Engineer': ['Software Developers', 'Database Administrators', 'ETL, Service, Interface Developers'],
    'Data_Integration_Specialist': ['Data Integration (ETL) Specialists', 'ETL, Service, Interface Developers'],
    'Data_Owner': ['Executive Data Stewards', 'Business Data Stewards', 'Data Governance Council'],
    'Data_Protection_Officer': ['Data Security Administrators', 'Audit / Compliance'],
    'Data_Quality_Manager': ['Data Quality Analysts', 'Data Stewardship Council'],
    'Data_Scientist': ['Data Analysts', 'Knowledge Workers'],
    'Data_Standards_and_Governance_Expert': ['Business Data Stewards', 'Coordinating Data Stewards', 'Data Governance Office', 'Standards Organizations'],
    'Data_Steward': ['Data Stewards', 'Business Data Stewards', 'Data Stewards and SMEs'],
    'Data_Strategy_Owner': ['DM Executive', 'Data Management Executive', 'CDO/CIO'],
    'FAIR_Community_Manager': ['Coordinating Data Stewards', 'Organizational Effectiveness Group'],
    'FAIR_Data_Architect': ['Data Architects', 'Data Architects and Modelers', 'Other Enterprise Architects'],
    'FAIR_Trainer': ['Subject Matter Experts', 'Organizational Effectiveness Group'],
    'Knowledge-Enabled_Citizen': ['Knowledge Workers', 'Business Users'],
    'Lab_Manager': ['Managers', 'Data Producers'],
    'Legal_Data_Expert': ['Audit / Compliance', 'Government and Industry Regulators'],
    'Master_Data_Manager': ['Business Data Stewards', 'Data Providers', 'Data Stewards'],
    'Ontologist': ['Data Modelers', 'Meta-data Specialist', 'Data Architects'],
    'Project_Manager': ['Project Managers', 'Project and Program Managers'],
    'Reference_Data_Manager': ['Data Stewards', 'Data Providers'],
    'Researcher': ['Data Creators', 'Data Producers', 'Knowledge Workers'],
    'Subject_Matter_Expert': ['Subject Matter Experts', 'Subject Matter Experts (SMEs)', 'Business Subject Matter Experts'],
    'Technology_Leader': ['CIO', 'Chief Information Officer', 'CIO/CTO', 'CDO/CIO'],
    'Autonomous_AI_Agent': ['Internal Customers and Systems'],
}

# These mappings select relevant organisational functions rather than assigning
# every governance or assessment row to every dimension.
ORG_TARGETS = {
    'ACT-01-001': ['D3'], 'ACT-01-002': ['D3'],
    'ACT-01-003': ['D4'], 'ACT-01-004': ['D2', 'D4'],
    'ACT-01-005': ['D4'], 'ACT-01-006': ['D3', 'D5'],
    'ACT-01-007': ['D3', 'D7'], 'ACT-01-008': ['D2', 'D3'],
    'ACT-01-009': ['D3'], 'ACT-01-010': ['D2', 'D4'],
    'ACT-01-011': ['D5'], 'ACT-01-012': ['D5'],
    'ACT-01-013': ['D5'], 'ACT-01-014': ['D5'],
    'ACT-01-015': ['D2', 'D5'], 'ACT-01-016': ['D2', 'D6'],
    'ACT-12-001': ['D3'], 'ACT-12-002': ['D5'],
    'ACT-12-003': ['D3', 'D4'], 'ACT-12-004': ['D5'],
    'ACT-12-005': ['D6'], 'ACT-12-006': ['D5'],
    'ACT-12-007': ['D5'], 'ACT-12-008': ['D3'],
    'ACT-12-009': ['D2', 'D3'], 'ACT-12-010': ['D3'],
    'ACT-12-011': ['D5'],
}
CLAUSE_TERMS = {
    'F1': ['identif', 'persistent', 'pid', 'gup'],
    'F2': ['metadata', 'catalog', 'description'],
    'F3': ['metadata', 'identif'], 'F4': ['find', 'catalog', 'search'],
    'A1': ['access', 'protocol', 'resolv'],
    'A1.1': ['protocol', 'open', 'standard'],
    'A1.2': ['access', 'control', 'auth'], 'A2': ['metadata', 'lifecycle', 'maintain'],
    'I1': ['model', 'machine', 'semantic', 'represent'],
    'I2': ['vocabular', 'ontolog', 'semantic'],
    'I3': ['integrat', 'interoperab', 'connect'],
    'R1': ['reuse', 're-use', 'metadata', 'context'],
    'R1.1': ['licen', 'reuse', 're-use'],
    'R1.2': ['lineage', 'provenance', 'metadata'],
    'R1.3': ['standard', 'domain', 'community'],
    'D2': ['leadership', 'budget', 'fund', 'champion', 'value'],
    'D3': ['strateg', 'vision', 'plan', 'value'],
    'D4': ['role', 'steward', 'team', 'persona'],
    'D5': ['process', 'workflow', 'governance', 'procedure'],
    'D6': ['training', 'knowledge', 'learn', 'community'],
    'D7': ['tool', 'infrastructure', 'architect', 'system'],
}


def descriptor_support(record, descriptor_index):
    """Identify exact source clauses and label limited thematic support explicitly."""
    supports = []
    for descriptor_id in record['descriptor_candidates']:
        descriptor = descriptor_index[descriptor_id]
        terms = CLAUSE_TERMS.get(record.get('principle'), CLAUSE_TERMS.get(record['dimension'], ['data']))
        if record['dimension'] != 'D1':
            terms = terms + CLAUSE_TERMS.get(record['dimension'], [])
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', descriptor['source_markdown']) if p.strip()]
        ranked = sorted(enumerate(paragraphs), key=lambda v: (-sum(t in v[1].lower() for t in terms), v[0]))
        chosen = [p for _, p in ranked if any(t in p.lower() for t in terms) and not p.lstrip().startswith(('===', '![', '**[', '!('))][:2]
        if chosen:
            supports.append(dict(descriptor_id=descriptor_id, source=descriptor['source'], source_clauses=chosen, rationale=f"The named deliverable may address the {record['principle'] or record['dimension']} aspect of these clauses when its applicability condition is met.", limitation='Thematic documentary support only. Remaining descriptor clauses, deployment scope and operational capability are not established.'))
    return supports


def extract(fairmm, plan):
    # Source checkout is read only. All generated files use the project ROOT.
    ROOT = SOURCE_ROOT
    summaries, activities, assertions, inputs = [], [], [], {}
    def source(path, base, repo_root):
        rel = path.relative_to(repo_root).as_posix()
        inputs[base + rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        return base + rel
    for path in sorted((ROOT / 'docs/dama/segments').glob('*.md')):
        text = read(path)
        url = source(path, DB, ROOT)
        number = int(path.name[:2])
        rs = list(rows(text))
        s = next((r for r in rs if len(r[1]) == 3 and r[1][0].startswith(str(number) + '.')), None)
        assert s, path
        label = s[1][0].split('. ', 1)[1]
        summary = dict(id=f'AREA-{number:02}', number=number, name=label, source=url + f'#L{s[0]}', source_layer='segment_summary', direct=ids(s[1][1]), indirect=ids(s[1][2]), aggregate=number == 0)
        summaries.append(summary)
        for kind in ['direct', 'indirect']:
            for principle in summary[kind]:
                assertions.append(dict(id=f'S-{number:02}-{kind}-{principle}', area_id=summary['id'], source_layer='segment_summary', source=summary['source'], contribution_type=kind.title(), principle=principle, aggregate=number == 0))
        header = None
        for ln, cells in rs:
            if cells[0] == 'Activities' and len(cells) == 12:
                header = cells
                continue
            if header and len(cells) == 12:
                aid = f'ACT-{number:02}-{len([a for a in activities if a["area_id"] == summary["id"]]) + 1:03}'
                coord = re.search(r'\[source:\s*([^\]\\]+)', cells[8])
                a = dict(id=aid, area_id=summary['id'], area=label, source=url + f'#L{ln}', source_layer='activity_table', coordinate=coord.group(1) if coord else None, source_fields=dict(zip(header, cells)), activity=cells[0], deliverables=cells[1], responsible_roles=cells[2], approving_roles=cells[3], contributing_roles=cells[4], direct=ids(cells[7]), indirect=ids(cells[11]), rationale=cells[8], indirect_rationale=cells[9], source_evidence_test=cells[10])
                activities.append(a)
                for kind in ['direct', 'indirect']:
                    for principle in a[kind]:
                        assertions.append(dict(id=f'{aid}-{kind}-{principle}', activity_id=aid, area_id=summary['id'], source_layer='activity_table', source=a['source'], coordinate=a['coordinate'], contribution_type=kind.title(), principle=principle, rationale=a['rationale'] if kind == 'direct' else a['indirect_rationale'], source_evidence_test=a['source_evidence_test'], intermediate_practice=VIA[principle] if kind == 'indirect' else None, intermediate_practice_status='proposed bridge' if kind == 'indirect' else None))
    ontology_path = ROOT / 'artefacts/dama-fair-mapping.ttl'
    source(ontology_path, DB, ROOT)
    g = Graph().parse(ontology_path, format='turtle')
    for kind in ['Direct', 'Indirect']:
        for node in sorted(g.subjects(RDF.type, MAP[kind + 'Contribution']), key=str):
            practice = g.value(node, MAP.fromPractice)
            assertions.append(dict(id='ONT-' + str(node).split('#')[-1], source_layer='ontology_example', source=DB + 'artefacts/dama-fair-mapping.ttl', source_node=str(node), contribution_type=kind, principle=str(g.value(node, MAP.targetsPrinciple)).split('/')[-1], practice=str(practice), practice_label=str(g.value(practice, RDFS.label)), area_iri=str(g.value(practice, MAP.inKnowledgeArea)), intermediate_practice=str(g.value(node, MAP.viaPractice)) if kind == 'Indirect' else None, rationale=str(g.value(node, MAP.rationale)), condition=str(g.value(node, MAP.applicabilityCondition) or '')))
    package = ROOT / 'artefacts/DAMA_FAIR_Sankey_v1.2.0.zip'
    package_url = source(package, DB, ROOT)
    prefix = 'dama-fair-sankey-v1.2.0/'
    with ZipFile(package) as archive:
        visual = json.loads(archive.read(prefix + 'data.json'))
        anchors = json.loads(archive.read(prefix + 'section-links.json'))
    for i, link in enumerate(visual['links']):
        # The package itself associates edition-specific labels with numbered
        # source sections. This is navigation correspondence, not area identity.
        number = int(re.match(r'^(\d+)-', anchors[link['source']])[1])
        assertions.append(dict(id=f'VIS-{i + 1:03}', source_layer='visualisation', source=package_url, source_member=prefix + 'data.json', source_record_index=i, source_area=link['source'], area_id=f'AREA-{number:02}', area_correspondence_basis='packaged section-links.json navigation anchor; labels differ by framework edition', principle=link['target'], contribution_type='Indirect' if link['kind'] == 'Enabling' else link['kind'], original_contribution_type=link['kind'], classification_note='Enabling is normalized to Indirect for comparison; original label is preserved', rationale=link['description'], deliverables=link['deliverables'], original_record=link))
    persona_path = ROOT / 'docs/dama/personas.md'
    purl = source(persona_path, DB, ROOT)
    dama_personas = []
    for ln, cells in rows(read(persona_path)):
        if len(cells) == 7 and cells[0] != 'Persona / source name':
            dama_personas.append(dict(id=slug(cells[0]), name=cells[0], description=cells[1], supplier_in=[x.strip() for x in cells[2].split(';') if x.strip()], participant_in=[x.strip() for x in cells[3].split(';') if x.strip()], consumer_in=[x.strip() for x in cells[4].split(';') if x.strip()], inherited_direct=ids(cells[5]), inherited_indirect=ids(cells[6]), source=purl + f'#L{ln}'))
    pg = Graph().parse(ROOT / 'artefacts/dama-persona-ontology.ttl', format='turtle')
    for p in dama_personas:
        matches = [n for n, label in pg.subject_objects(RDFS.label) if str(label) == p['name'] and (n, RDF.type, PERSONA.Persona) in pg]
        assert len(matches) == 1, p['name']
        p['source_iri'] = str(matches[0])
    descriptions, descriptor_index = [], {}
    for level in range(6):
        path = fairmm / f'docs/level{level}.md'
        text = read(path)
        url = source(path, MB, fairmm)
        blocks = list(re.finditer(r'^=== "([^"]+)"\s*$', text, re.M))
        for i, block in enumerate(blocks):
            if block[1] not in DIMENSIONS:
                continue
            dim = 'D' + str(DIMENSIONS.index(block[1]) + 1)
            start, end = block.end(), blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
            body = text[start:end].strip()
            # Preserve the entire source block; extracted text is an assessment reference.
            ident = f'{dim}-L{level}'
            record = dict(id=ident, dimension=dim, dimension_label=block[1], level=level, source=url + f'#L{text[:block.start()].count(chr(10)) + 1}', source_markdown=body, evidence_status='not assessed', scope='documentary crosswalk; operational pilot excluded')
            descriptions.append(record)
            descriptor_index[ident] = record
    mm_personas = {}
    for path in sorted((fairmm / 'docs/FAIR_personas').glob('*.md')):
        if path.stem in ['Overview_personas', 'file_list', 'X-template-FAIR_persona']:
            continue
        text = read(path)
        description = re.search(r'=== "Description"(.*?)(?=^=== |^!!! |\Z)', text, re.S | re.M)
        assert description, path
        mm_personas[path.stem] = dict(name=path.stem, source=source(path, MB, fairmm), description=description[1].strip())
    proposal_rows = {c[0]: c for _, c in rows(read(plan)) if len(c) == 4 and c[0] in CANDIDATES}
    assert set(proposal_rows) == set(mm_personas) == set(CANDIDATES)
    names = {p['name']: p for p in dama_personas}
    correspondences = []
    for name, candidates in CANDIDATES.items():
        c = proposal_rows[name]
        category = 'Gap' if c[2].startswith('Gap') else 'Close' if c[2].startswith('Close') else 'Partial'
        roles = {'P': 'Producer', 'C': 'Consumer', 'E': 'Enabler'}
        proposed_roles = [roles[x] for x in re.findall(r'\b[PEC]\b', c[2].split(';')[-1])]
        if name == 'Autonomous_AI_Agent':
            proposed_roles = ['Producer', 'Consumer', 'Enabler']
        links = []
        for candidate in candidates:
            assert candidate in names, candidate
            p = names[candidate]
            links.append(dict(dama_persona_id=p['id'], name=candidate, source=p['source'], source_iri=p['source_iri'], occurrence_categories={k: p[k] for k in ['supplier_in', 'participant_in', 'consumer_in']}, relationship='related counterpart; no equivalence asserted' if category == 'Gap' else 'proposed functional correspondence', inherited_direct=p['inherited_direct'], inherited_indirect=p['inherited_indirect']))
        correspondences.append(dict(id='PM-' + slug(name), fairmm_persona=name, fairmm_source=mm_personas[name]['source'], fairmm_description=mm_personas[name]['description'], confidence=category, qualification=c[2], rationale=c[3], proposed_data_roles=proposed_roles, candidates=links, status='proposed; documentary comparison completed', local_reviewer=None, local_assignment_status='not assigned'))
    return summaries, activities, assertions, dama_personas, correspondences, descriptions, inputs


def role_candidates(activity, correspondences):
    result = []
    for p in correspondences:
        hits = []
        for candidate in p['candidates']:
            for field in ['responsible_roles', 'approving_roles', 'contributing_roles']:
                text = activity[field]
                tokens = [s.strip() for s in text.split(';')]
                tokens += [s.strip() for s in re.split(r';|,(?![^()]*\))', text)]
                if candidate['name'] in tokens:
                    hits.append(dict(dama_persona=candidate['name'], source_role_category=field, source_text=text))
        if hits:
            result.append(dict(persona_mapping_id=p['id'], equivalence_confidence=p['confidence'], occurrences=hits, assignment_status='candidate; requires task-specific confirmation'))
    return result


def align(activities, assertions, correspondences, descriptions):
    alignments = []
    dm = {r['id']: r for r in descriptions}
    by_name = {p['fairmm_persona']: p for p in correspondences}
    for a in activities:
        for kind in ['direct', 'indirect']:
            for principle in a[kind]:
                # D1 is the resource evidence bridge. D5/D7 are separately conditional
                # workflow/infrastructure relationships rather than inherited FAIR grades.
                artifact = a['source_fields'].get('Relevant deliverables') or a['deliverables']
                dimensions = ['D1', 'D5']
                if re.search(r'repositor|tool|system|model|architect|service|catalog|interface|database|etl|metadata|specification|software|protocol|platform|warehouse', artifact, re.I):
                    dimensions.append('D7')
                for dim in dimensions:
                    dimension_kind = kind.title() if dim == 'D1' else 'Direct'
                    artifact = a['source_fields'].get('Relevant deliverables') or a['deliverables']
                    condition = {'D1': 'Resource evidence must address the principle and the selected descriptor; a practice description alone is insufficient.', 'D5': 'The deliverable must include a repeatable FAIR-specific workflow, procedure or control addressing this descriptor.', 'D7': 'The deliverable must include implemented FAIR infrastructure or tooling addressing this descriptor; a tool inventory alone is insufficient.'}[dim]
                    candidate_links = role_candidates(a, correspondences)
                    alignments.append(dict(id=f'AL-{a["id"]}-{kind}-{principle}-{dim}', source_assertion_id=f'{a["id"]}-{kind}-{principle}', activity_id=a['id'], source=a['source'], source_coordinate=a['coordinate'], area_id=a['area_id'], activity=a['activity'], deliverable=artifact, principle=principle, existing_contribution_type=kind.title(), dimension=dim, proposed_dimension_contribution_type=dimension_kind, descriptor_candidates=[dm[f'{dim}-L{l}']['id'] for l in [2, 3]], descriptor_match_status='candidate thematic support; full descriptor not established', condition=condition, intermediate_practice=VIA[principle] if kind == 'indirect' else None, dimension_intermediate_practice=VIA[principle] if dimension_kind == 'Indirect' else None, evidence_test=TESTS[principle], source_evidence_test=a['source_evidence_test'], persona_candidates=candidate_links, review_status='documentary trace checked; proposal', operational_evidence_status='excluded by user', assessed_level=None, local_reviewer=None))
    # Organisational contributions do not manufacture principle IDs for governance
    # and assessment rows whose source principle columns are blank.
    for a in activities:
        targets = ORG_TARGETS.get(a['id'], [])
        for dim in targets:
            alignments.append(dict(id=f'ORG-{a["id"]}-{dim}', activity_id=a['id'], area_id=a['area_id'], activity=a['activity'], deliverable=a['source_fields'].get('Relevant deliverables') or a['deliverables'], source=a['source'], source_coordinate=a['coordinate'], source_assertion_id=None, principle=None, existing_contribution_type=None, dimension=dim, proposed_dimension_contribution_type='Direct', descriptor_candidates=[f'{dim}-L2', f'{dim}-L3'], descriptor_match_status='candidate organisational support; FAIR-specific content required', condition='The activity deliverable must explicitly address the referenced FAIRMM dimension and selected descriptor. Assessment-process evidence does not establish the assessed capability.', evidence_test='Inspect the FAIR-specific deliverable, decisions, role mandates and dated review records against the selected descriptor.', persona_candidates=[], review_status='documentary trace checked; proposal', operational_evidence_status='excluded by user', assessed_level=None, local_reviewer=None))
    extensions = [
        ('EXT-TRAINING', 'D6', 'FAIR_Trainer', 'Design role-specific FAIR training and assess practical competence', 'Curriculum, exercises and competence assessment records', 'Inspect learning objectives, practical tasks and competence results; attendance alone is insufficient.'),
        ('EXT-ROLES', 'D4', 'Data_Steward', 'Define FAIR responsibilities and interactions for each data product', 'Role mandates, interaction model and capacity allocation', 'Inspect documented decision rights, task assignments, handoffs and allocated capacity.'),
    ]
    for ident, dim, pname, practice, deliverable, test in extensions:
        alignments.append(dict(id=ident, source_assertion_id=None, activity_id=None, area_id=None, source=None, principle=None, existing_contribution_type=None, dimension=dim, proposed_dimension_contribution_type='Direct', descriptor_candidates=[f'{dim}-L{l}' for l in [2, 3, 4]], activity=practice, deliverable=deliverable, condition='New FAIR-specific practice proposed to fill an explicit operating-model gap; not an existing DAMA principle mapping.', evidence_test=test, persona_candidates=[dict(persona_mapping_id=by_name[pname]['id'], assignment_status='proposed')], review_status='proposed extension', operational_evidence_status='excluded by user', assessed_level=None, local_reviewer=None))
    for a in alignments:
        if a.get('activity_id') and not a['persona_candidates']:
            a['persona_candidates'] = role_candidates(next(row for row in activities if row['id'] == a['activity_id']), correspondences)
        a['descriptor_support'] = descriptor_support(a, dm)
        a['descriptor_candidates'] = [s['descriptor_id'] for s in a['descriptor_support']]
    return alignments


def pages(data, plan, out):
    sums, acts, links = data['summaries'], data['activities'], data['alignments']
    counts = Counter(a['source_layer'] for a in data['assertions'])
    total = len(links)
    overview = f'''# FAIRMM alignment

The documentary crosswalk connects DAMA activities and their existing Direct and Indirect FAIR relationships to the seven FAIR Maturity Matrix dimensions. It preserves the source classifications and adds conditional dimension relationships and persona correspondences.

The baseline is FAIR–DAMA `{DAMA_SHA[:12]}` and FAIRMM branch **FAIR-MM-V1.2.5**, revision `{MM_SHA[:12]}`. The crosswalk contains **{len(acts)} activity rows**, **{len(data['persona_correspondences'])} FAIRMM persona comparisons**, **42 dimension and level references**, and **{total} proposed dimension relationships**. Counts describe documentary records, not maturity or implementation.

## Explore the alignment

- [Knowledge areas and source reconciliation](areas.md)
- [Persona correspondences](personas.md)
- [Persona links to Direct and Indirect FAIR contributions](persona-relationships.md)
- [Dimensions and maturity references](dimensions.md)
- [Documentary review and remaining decisions](review.md)
- [Download the complete crosswalk](data/crosswalk.json)
- [Modular FAIRMM ontologies](../ontology.md)

## Interpreting relationships

**Direct FAIR contribution** retains the source assertion that a practice can produce or verify relevant resource evidence. **Indirect FAIR contribution** retains enabling support and names a proposed intermediate practice. Both remain conditional on implementation.

**Dimension support** is a separate proposal. Governance can directly address Leadership or Strategy while having no specific principle ID in the source summary. A tool list alone cannot establish Tools and infrastructures, and a policy alone cannot establish resource FAIRness.

Persona correspondences are functional candidates. Close, Partial and Gap express the result of comparing the documentary roles; they do not appoint people or confer decision rights. Producer, Consumer and Enabler depend on the actual activity. An Enabler may contribute directly to FAIR evidence.

The operational pilot was excluded at the user's request. No operational test results or maturity levels are assigned. All descriptor links are candidate support requiring the full descriptor to be assessed in context.

## Source layers

{table(['Layer', 'Principle assertion records', 'Interpretation'], [(k, v, 'Separate source scope; do not sum as maturity coverage') for k, v in counts.items()])}

The segment summaries, activity tables, ontology examples and visualisation have different scopes. The Data Management overview is an aggregate and is excluded from primary coverage totals. The inherited persona principle lists remain separate from activity responsibilities.

## Sources and attribution

FAIRMM source material is attributed to the **Pistoia Alliance FAIR Maturity Matrix contributors**, [FAIR-MM-V1.2.5 source](https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/tree/{MM_SHA}). Its repository carries [GPL-3.0](data/FAIRMM-LICENSE.txt); the persona overview separately states [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These source notices are preserved rather than applying one licence to every component. The crosswalk adds proposed correspondences and conditional dimension relationships; the extracted source blocks retain their upstream notices. FAIR–DAMA source classifications are attributed to Chris Day and [the pinned repository](https://github.com/chris-day/FAIR-DAMA/tree/{DAMA_SHA}) under its CC0 licence. The JSON manifest records SHA-256 digests of the source inputs.
'''
    save(out / 'index.md', overview)
    area_rows = []
    for s in sums:
        if s['aggregate']:
            continue
        supported = [a for a in links if a['area_id'] == s['id']]
        dimension_types = []
        for dim in [f'D{i}' for i in range(1, 8)]:
            types = sorted({a['proposed_dimension_contribution_type'] for a in supported if a['dimension'] == dim})
            if types:
                dimension_types.append(dim + ': ' + '/'.join(types))
        area_rows.append((s['name'], s['direct'], s['indirect'], dimension_types, f"[Source]({s['source']})"))
    reconciliations = []
    for s in sums:
        if s['aggregate']:
            continue
        related = [a for a in acts if a['area_id'] == s['id']]
        for kind in ['direct', 'indirect']:
            union = set(x for a in related for x in a[kind])
            if union != set(s[kind]):
                reconciliations.append(dict(area=s['name'], kind=kind, summary=s[kind], activity_union=sorted(union, key=IDS.index)))
    data['reconciliation']['summary_activity_differences'] = reconciliations
    visual_differences = []
    summary_index = {s['id']: s for s in sums}
    for a in data['assertions']:
        if a['source_layer'] != 'visualisation':
            continue
        s = summary_index[a['area_id']]
        kind = a['contribution_type'].lower()
        if a['principle'] not in s[kind]:
            visual_differences.append(dict(assertion_id=a['id'], source_area=a['source_area'], section_area=s['name'], principle=a['principle'], visualisation_type=a['original_contribution_type'], summary_direct=s['direct'], summary_indirect=s['indirect']))
    data['reconciliation']['visualisation_summary_differences'] = visual_differences
    save(out / 'areas.md', '# Knowledge areas and source reconciliation\n\nD1 Data; D2 Leadership; D3 Strategy; D4 Personas; D5 Processes; D6 Knowledge; D7 Tools and infrastructures. Dimension support is a separate conditional proposal, not a change to the existing FAIR contribution type.\n\n' + table(['DAMA area', 'Existing Direct IDs', 'Existing Indirect IDs', 'Proposed dimension support', 'Evidence'], area_rows) + '''

## Differences retained

The segment summaries provide direct support somewhere for ten principles. F1, F3, A1.1, A2 and R1.1 have indirect support only at this summary layer. The ontology includes specific proposed Direct examples for F3 and R1.1 and a specific integration I1 practice. Governance has ontology examples for Indirect R1.1 and R1.2 while its segment summary has no IDs. These are distinct assertions with source-layer provenance, not corrections silently applied to the summaries.

The Sankey states 51 direct and 10 enabling links for its own presentation scope. Those counts are not activity or persona counts. Its original data remains unchanged.

''' + ('Summary/activity union differences found: ' + json.dumps(reconciliations, ensure_ascii=False) if reconciliations else 'The union of activity-table principle IDs matches each non-aggregate segment summary in both categories.') + '\n\n## Visualisation assertions outside the summary classification\n\nThe 61 packaged links are extracted separately with their original labels and records. Enabling is normalized to Indirect only for comparison. Edition-specific area labels are associated using the package navigation anchors; this is not an assertion that the knowledge areas are identical. The following links are not present in the corresponding summary category and require an explicit reconciliation decision.\n\n' + table(['Sankey area label', 'Linked source section', 'FAIR ID', 'Sankey type', 'Summary Direct IDs', 'Summary Indirect IDs'], [(a['source_area'], a['section_area'], a['principle'], a['visualisation_type'], a['summary_direct'], a['summary_indirect']) for a in visual_differences]) + '\n\n[Download every activity, original role field, source coordinate and principle assertion](data/crosswalk.json).\n')
    persona_rows = []
    for p in data['persona_correspondences']:
        persona_rows.append((f"[{p['fairmm_persona']}]({p['fairmm_source']})", [c['name'] for c in p['candidates']], p['confidence'], p['proposed_data_roles'], p['rationale']))
    matched = {c['dama_persona_id'] for p in data['persona_correspondences'] if p['confidence'] != 'Gap' for c in p['candidates']}
    reverse = [p for p in data['dama_personas'] if p['id'] not in matched]
    save(out / 'personas.md', '# Persona correspondences\n\nEach row compares FAIRMM tasks with DAMA role descriptions. Gap candidates are related counterparts only; no equivalence is asserted. All assignments and data roles remain proposed.\n\n' + table(['FAIRMM persona', 'DAMA candidates', 'Match', 'Proposed data roles', 'Contribution and condition'], persona_rows) + '\n\n## DAMA entries without an asserted correspondence\n\nThe catalogue includes collective bodies, systems and title variants. Preserve them as separate source entries. The following have no Close or Partial correspondence in this crosswalk; some occur as counterparts in Gap rows.\n\n' + table(['DAMA source entry', 'Description', 'Source'], [(p['name'], p['description'], f"[Source]({p['source']})") for p in reverse]) + '\n\n## Role evidence\n\nThe JSON retains supplier, participant and consumer appearances alongside the inherited area-level principle lists. Activity links use literal matches against responsible, approving or contributing source-role fields. A missing literal match means unresolved terminology, not absence of a possible contribution. No title aliases are silently merged.\n')
    detail = '# Persona links to FAIR contributions\n\nThese tables retain the DAMA area-level Direct and Indirect principle lists for each proposed counterpart. They do not transfer those lists into individual responsibility. Activity evidence below each table comes only from literal source-role occurrences. Gap counterparts do not assert an equivalence.\n\n'
    for p in data['persona_correspondences']:
        detail += f"## {p['fairmm_persona']}\n\nMatch: **{p['confidence']}**. {p['rationale']}\n\n"
        detail += table(['DAMA counterpart', 'Occurrence categories and areas', 'Inherited Direct IDs', 'Inherited Indirect IDs'], [(f"[{c['name']}]({c['source']})", '; '.join(k.replace('_', ' ') + ': ' + ', '.join(v) for k, v in c['occurrence_categories'].items() if v), c['inherited_direct'], c['inherited_indirect']) for c in p['candidates']]) + '\n\n'
        seen, activity_links = set(), []
        for a in links:
            if a.get('principle') and a['dimension'] != 'D1':
                continue
            for pm in a['persona_candidates']:
                if pm['persona_mapping_id'] != p['id']:
                    continue
                key = (a['activity_id'], a['principle'], a['existing_contribution_type'], a['dimension'] if not a.get('principle') else None)
                if key in seen:
                    continue
                seen.add(key)
                if not a.get('source'):
                    continue
                activity_links.append((f"[{a['activity']}]({a['source']})", a['principle'], a['existing_contribution_type'], a['dimension'], [h['dama_persona'] + ' (' + h['source_role_category'].replace('_', ' ') + ')' for h in pm.get('occurrences', [])], a.get('intermediate_practice') or ('Produces/verifies evidence when implemented' if a.get('principle') else 'Organisational dimension support; no FAIR ID inferred')))
        detail += (table(['Activity source', 'FAIR ID', 'Existing type', 'Dimension', 'Literal role evidence', 'Evidence pathway'], activity_links) if activity_links else 'No literal activity-role occurrence was resolved for this counterpart set. Area-level candidates remain available above.') + '\n\n'
    save(out / 'persona-relationships.md', detail)
    dim_rows = []
    for i, label in enumerate(DIMENSIONS, 1):
        dim = f'D{i}'
        dim_rows.append((dim, label, sum(a['dimension'] == dim for a in links), f'[References]({dim.lower()}.md)'))
        ds = [d for d in data['descriptors'] if d['dimension'] == dim]
        contents = f'# {label}\n\nDimension relationships below are conditional documentary candidates. The source block for each level is preserved in the JSON; none establishes an assessed level.\n\n'
        for d in ds:
            # A concise navigable reference; full copyrighted source blocks are in the
            # attributed, licensed data export rather than repeated as page text.
            contents += f"## Level {d['level']}\n\n[Read the exact FAIRMM descriptor]({d['source']}). Assessment status: **not assessed**; operational pilot excluded.\n\n"
        contents += '## Proposed activity relationships\n\n' + table(['Activity', 'FAIR ID', 'Existing FAIR type', 'Dimension type', 'Condition'], [(a['activity'], a.get('principle'), a.get('existing_contribution_type'), a['proposed_dimension_contribution_type'], a['condition']) for a in links if a['dimension'] == dim]) + '\n'
        save(out / f'{dim.lower()}.md', contents)
    save(out / 'dimensions.md', '''# Dimensions and maturity references

The seven dimensions offer complementary perspectives. Their maturity can differ within the same organisation. The crosswalk preserves all six level descriptions for each dimension and links candidate activity support primarily to L2 and L3. L0, L1, L4 and L5 remain available as full assessment references. L5 is aspirational in FAIRMM.

No arithmetic score is inferred from the number of relationships or personas. An activity supports only the relevant part of a descriptor; all other elements remain to be established. Leadership, strategy, responsibilities, training and capacity require their own evidence.

''' + table(['ID', 'Dimension', 'Proposed relationships', 'Level references and activity detail'], dim_rows) + '\n\nTwo extensions explicitly address FAIR role mandates and practical FAIR training. They are proposed new practices and do not manufacture missing FAIR IDs in DAMA source rows.\n')
    save(out / 'review.md', '''# Documentary review and remaining decisions

The documentary execution completes source extraction, source-layer reconciliation, the 30 persona comparisons, conditional dimension relationships and the ontology export. The operational pilot is excluded at the user's request.

## Completed documentary checks

- Each numbered segment summary and each activity-table row has a pinned source and line coordinate.
- Existing Direct and Indirect labels are retained per source layer; aggregate overview assertions are identifiable.
- Every FAIRMM persona is compared, and every DAMA source persona is retained for reverse lookup.
- All 42 dimension and level descriptions are preserved with source provenance.
- Indirect activity bridges name a proposed intermediate practice.
- No operational evidence, local reviewer approval, local accountability or assessed maturity level is fabricated.

## Review decisions

| Decision | Documentary disposition | Remaining organisational decision |
| --- | --- | --- |
| Persona equivalence | Close, Partial or Gap assigned by functional comparison | Confirm local job scope, competence and mandate |
| Data role | Producer, Consumer and Enabler suggested | Confirm for each task and data product |
| Principle contribution | Existing labels retained | Confirm applicability to actual resources |
| Dimension support | Conditional candidate descriptor relationships recorded | Confirm the relevant descriptor clauses and scope |
| Ontology and summary differences | Preserved as separate source assertions | Decide whether to revise upstream summaries in a later change |
| Governance and training | Organisational relationships and explicit extensions recorded | Adopt roles, training and capacity arrangements |

## Terminology requiring attention

Activity-level role names and area-level persona names are not consistently identical. Literal matching avoids silently expanding responsibility. The full original role fields remain available for a later, explicit alias review.

FAIRMM persona benefit text sometimes uses principle IDs loosely. For example, the Data Steward page associates R1.1 with reproducible governance evidence, while R1.1 addresses usage licensing; the Autonomous AI Agent page associates F3 with semantic search, while F3 requires the data identifier in metadata. The crosswalk uses the actual FAIR requirement for its evidence tests and does not transfer those benefit statements into equivalence or implementation claims.

## Publication state

The documentation source, data downloads and ontology are maintained independently in `research-repos/FAIR-DAMA-FAIRMM`. The sibling FAIR–DAMA checkout is a read-only source. Build and structural validation results are recorded in the execution report. The public website has not changed.
''')
    unresolved = data['unresolved_descriptor_candidates']
    with (out / 'review.md').open('a', encoding='utf-8') as f:
        f.write('\n## Unresolved descriptor candidates\n\nThe following source assertions remain intact, but no relevant D1 clause was resolved in the selected L2/L3 blocks. Other dimension relationships may remain. This prevents keyword-based inference from becoming a forced descriptor mapping.\n\n' + table(['Activity', 'FAIR ID', 'Existing type', 'Unresolved dimension'], [(a['activity'], a['principle'], a['existing_contribution_type'], a['dimension']) for a in unresolved]) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fairmm', type=Path, required=True)
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    fairmm, plan = args.fairmm.resolve(), args.plan.resolve()
    summaries, activities, assertions, personas, correspondences, descriptors, inputs = extract(fairmm, plan)
    assert len(descriptors) == 42
    data = dict(schema_version='1.0.0', execution_date='2026-11-14', scope='documentary alignment; operational pilot excluded by user', sources={'fair_dama_revision': DAMA_SHA, 'fairmm_revision': MM_SHA, 'fairmm_branch': 'FAIR-MM-V1.2.5', 'input_sha256': inputs, 'proposal_sha256': hashlib.sha256(plan.read_bytes()).hexdigest()}, summaries=summaries, activities=activities, assertions=assertions, dama_personas=personas, persona_correspondences=correspondences, descriptors=descriptors, reconciliation={'policy': 'retain source layers independently; no silent upgrades'}, attribution={'FAIRMM': 'Pistoia Alliance FAIR Maturity Matrix contributors; repository GPL-3.0; persona overview separately states CC BY 4.0; source notices retained', 'FAIR_DAMA': 'Chris Day; CC0; see repository LICENSE'})
    candidates = align(activities, assertions, correspondences, descriptors)
    data['alignments'] = [a for a in candidates if a['descriptor_support']]
    data['unresolved_descriptor_candidates'] = [dict(a, review_status='no relevant clause resolved in L2/L3; retain source assertion without a descriptor link') for a in candidates if not a['descriptor_support']]
    docs = ROOT / 'docs/fairmm'
    save(docs / 'data/FAIRMM-LICENSE.txt', read(fairmm / 'LICENSE'))
    save(args.output / 'FAIRMM-LICENSE.txt', read(fairmm / 'LICENSE'))
    pages(data, plan, docs)
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    save(ROOT / 'artefacts/fairmm-crosswalk.json', serialized)
    save(docs / 'data/crosswalk.json', serialized)
    save(args.output / 'fairmm-crosswalk.json', serialized)
    stats = {k: len(data[k]) for k in ['summaries', 'activities', 'assertions', 'dama_personas', 'persona_correspondences', 'descriptors', 'alignments']}
    stats['assertions_by_layer'] = dict(Counter(a['source_layer'] for a in assertions))
    stats['persona_confidence'] = dict(Counter(p['confidence'] for p in correspondences))
    stats['rdf_output'] = 'Generated separately by build_fairmm_ontology.py as five modular Turtle files'
    save(args.output / 'execution-stats.json', json.dumps(stats, indent=2) + '\n')
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
