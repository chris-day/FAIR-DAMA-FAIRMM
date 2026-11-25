"""Create paired static and on-demand D3 Sankeys, plus an offline fallback."""
from collections import Counter, defaultdict
from html import escape
import hashlib
import json
from pathlib import Path
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/sankey'
DOC = ROOT / 'docs/sankey'
W, H = 1800, 1120
LEFT, RIGHT, BAR = 435, 1265, 16
TOP, BOTTOM = 205, 1005
COLORS = {'Direct': '#2463a7', 'Indirect': '#b75f08'}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def main(data=None):
    if data is None:
        data = json.loads((ROOT / 'artefacts/fairmm-crosswalk.json').read_text(encoding='utf-8'))
    areas = {s['id']: s for s in data['summaries'] if not s['aggregate']}
    dims = {f'D{i+1}': name for i, name in enumerate(['FAIR Data', 'FAIR Leadership', 'FAIR Strategy', 'FAIR Personas', 'FAIR Processes', 'FAIR Knowledge', 'FAIR Tools and infrastructures'])}
    grouped = defaultdict(list)
    for a in data['alignments']:
        if a.get('area_id'):
            grouped[a['area_id'], a['dimension'], a['proposed_dimension_contribution_type']].append(a)
    links = []
    for (area, dim, kind), records in sorted(grouped.items()):
        links.append(dict(id=f'{area}-{dim}-{kind}', source=area, target=dim, kind=kind, value=1, source_label=areas[area]['name'], target_label=dims[dim], underlying_record_count=len(records), activities=sorted({a['activity'] for a in records}), principles=sorted({a['principle'] for a in records if a.get('principle')}), original_fair_contribution_types=sorted({a['existing_contribution_type'] for a in records if a.get('existing_contribution_type')}), alignment_ids=[a['id'] for a in records], sources=sorted({a['source'] for a in records if a.get('source')}), conditions=sorted({a['condition'] for a in records}), descriptor_ids=sorted({d for a in records for d in a['descriptor_candidates']})))
        assertion_index = {a['id']: a for a in data['assertions']}
        links[-1]['rationales'] = sorted({assertion_index.get(a.get('source_assertion_id'), {}).get('rationale') or a['condition'] for a in records})
        links[-1]['deliverables'] = sorted({a['deliverable'] for a in records if a.get('deliverable')})
    counts = Counter(l['kind'] for l in links)
    degree = Counter()
    for l in links:
        degree[l['source']] += 1
        degree[l['target']] += 1
    unit = (BOTTOM - TOP - (len(areas)-1) * 24) / len(links)
    nodes = []
    for side, labels, gap in [('source', areas, 24), ('target', dims, 28)]:
        total = sum(degree[k] * unit for k in labels) + gap * (len(labels) - 1)
        y = TOP + (BOTTOM - TOP - total) / 2
        for key in labels:
            height = degree[key] * unit
            label = (str(areas[key]['number']) + '. ' + areas[key]['name']) if side == 'source' else key + ' · ' + dims[key]
            label_lines = textwrap.wrap(label, width=36 if side == 'source' else 34, break_long_words=False)
            documentation_url = ('../source-release.html#section-'+str(areas[key]['number']) if areas[key]['source'].startswith('file:') else 'https://fair-dama.perdl.com/dama/segments/' + areas[key]['source'].split('/')[-1].split('.md')[0] + '/') if side == 'source' else ('https://github.com/Pistoia-Alliance-Inc/FAIR-Maturity-Matrix/blob/' + data['sources']['fairmm_revision'] + '/docs/fmm-' + key.lower() + '.md')
            nodes.append(dict(id=key, side=side, label=label, lines=label_lines, x=LEFT if side == 'source' else RIGHT, y=y, height=height, degree=degree[key], documentation_url=documentation_url))
            y += height + gap
    node_index = {n['id']: n for n in nodes}
    source_offsets = Counter()
    target_offsets = Counter()
    for l in links:
        src, dst = node_index[l['source']], node_index[l['target']]
        l['geometry'] = dict(x0=LEFT + BAR, x1=RIGHT, y0=src['y'] + source_offsets[src['id']] * unit, y1=dst['y'] + target_offsets[dst['id']] * unit, thickness=unit)
        source_offsets[src['id']] += 1
        target_offsets[dst['id']] += 1
    model = dict(title='DAMA segments and FAIRMM dimensions', width=W, height=H, nodes=nodes, links=links, counts=dict(counts), basis='proposed_dimension_contribution_type', unit='One ribbon per distinct segment, dimension and contribution type; equal width', excluded=['Aggregate Data Management overview', 'Two proposed extensions without a DAMA area'], source_file='artefacts/fairmm-crosswalk.json', source_revisions=data['sources'], conditional=True)
    assert len(links) == len(grouped)
    underlying=sum(l['underlying_record_count'] for l in links)
    assert underlying == len([a for a in data['alignments'] if a.get('area_id')])
    assert all(abs(node_index[k]['height'] - count * unit) < 0.001 for k, count in degree.items())
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="chart-title chart-desc">', '<title id="chart-title">DAMA segments to FAIRMM dimensions: Direct and Indirect proposed alignment</title>', '<desc id="chart-desc">Twelve numbered DAMA segments connect to seven FAIRMM dimensions through 38 Direct and seven Indirect equal-width ribbons. Blue is Direct; amber with a dashed edge is Indirect. These are conditional dimension relationships, not maturity scores.</desc>', '<rect width="1800" height="1120" fill="#ffffff"/>', '<g font-family="Segoe UI,Arial,sans-serif" fill="#16283c">', '<text x="48" y="57" font-size="31" font-weight="600">DAMA segments and FAIRMM dimensions</text>', '<text x="48" y="94" font-size="19">Proposed dimension alignment · FAIRMM v1.2.5 · 14 November 2026</text>']
    for x, color, label, dash in [(48, COLORS['Direct'], 'Direct · 38', ''), (260, COLORS['Indirect'], 'Indirect · 7', ' stroke-dasharray="6 4" stroke="#783b00"')]:
        svg.append(f'<rect x="{x}" y="122" width="38" height="15" fill="{color}" fill-opacity="0.65"{dash}/><text x="{x+50}" y="136" font-size="18">{label}</text>')
    svg += ['<text x="480" y="136" font-size="18" fill="#475569">One equal-width ribbon per segment–dimension–type</text>', '<text x="48" y="183" font-size="17" font-weight="600">DAMA segments</text>', '<text x="1298" y="183" font-size="17" font-weight="600">FAIRMM dimensions</text>', '</g>', '<g class="ribbons">']
    for l in links:
        g = l['geometry']
        x0, x1, y0, y1, t = (g[k] for k in ['x0', 'x1', 'y0', 'y1', 'thickness'])
        c0, c1 = x0 + (x1 - x0) * .45, x1 - (x1 - x0) * .45
        path = f'M{x0:.3f},{y0:.3f} C{c0:.3f},{y0:.3f} {c1:.3f},{y1:.3f} {x1:.3f},{y1:.3f} L{x1:.3f},{y1+t:.3f} C{c1:.3f},{y1+t:.3f} {c0:.3f},{y0+t:.3f} {x0:.3f},{y0+t:.3f} Z'
        dash = ' stroke="#783b00" stroke-width="1.2" stroke-dasharray="6 4"' if l['kind'] == 'Indirect' else ''
        label = f"{l['source_label']} → {l['target_label']} · {l['kind']}"
        svg.append(f'<path d="{path}" fill="{COLORS[l["kind"]]}" fill-opacity="0.35"{dash} data-link="{l["id"]}" data-kind="{l["kind"]}" tabindex="0" role="button" aria-label="{escape(label)}"><title>{escape(label)}</title></path>')
    svg.append('</g><g font-family="Segoe UI,Arial,sans-serif" font-size="18" fill="#16283c">')
    for n in nodes:
        svg.append(f'<rect data-node="{n["id"]}" x="{n["x"]}" y="{n["y"]:.3f}" width="{BAR}" height="{n["height"]:.3f}" fill="#405468"/>')
        x, anchor = (LEFT - 16, 'end') if n['side'] == 'source' else (RIGHT + BAR + 18, 'start')
        center = n['y'] + n['height'] / 2
        for i, line in enumerate(n['lines']):
            y = center + (i - (len(n['lines']) - 1) / 2) * 23 + 6
            svg.append(f'<text data-node="{n["id"]}" x="{x}" y="{y:.3f}" text-anchor="{anchor}">{escape(line)}</text>')
    svg += ['<text x="48" y="1055" font-size="17" fill="#475569">Direct / Indirect describes dimension support, separately from the source FAIR-principle classification.</text>', '<text x="48" y="1085" font-size="17" fill="#475569">Conditional proposals; width is not strength or maturity. Topics 12–14 are additional to the 11 core knowledge areas.</text>', '</g></svg>']
    svg = '\n'.join(svg)
    svg=svg.replace('Direct · 38',f'Direct · {counts["Direct"]}').replace('Indirect · 7',f'Indirect · {counts["Indirect"]}').replace('Twelve numbered DAMA segments connect to seven FAIRMM dimensions through 38 Direct and seven Indirect equal-width ribbons.',f'{len(areas)} DAMA areas and additional topics connect to seven FAIRMM dimensions through {counts["Direct"]} Direct and {counts["Indirect"]} Indirect equal-width ribbons.').replace('14 November 2026','16 November 2026')
    ET.fromstring(svg)
    offline_html = (ROOT / 'scripts/templates/offline_dimension_sankey.html').read_text(encoding='utf-8').replace('__SVG__', svg).replace('__MODEL__', json.dumps(model, ensure_ascii=False).replace('</', '<\\/'))
    html = (ROOT / 'scripts/templates/dimension_sankey.html').read_text(encoding='utf-8').replace('__MODEL__', json.dumps(model, ensure_ascii=False).replace('</', '<\\/'))
    html=html.replace('Direct · 38',f'Direct · {counts["Direct"]}').replace('Indirect · 7',f'Indirect · {counts["Indirect"]}')
    serialized = json.dumps(model, ensure_ascii=False, indent=2) + '\n'
    for destination in [OUT, DOC]:
        write(destination / 'dama-fairmm-dimensions-sankey.svg', svg)
        write(destination / 'dama-fairmm-dimensions-sankey.html', html)
        write(destination / 'dama-fairmm-dimensions-sankey-offline.html', offline_html)
        write(destination / 'dama-fairmm-dimensions-sankey.json', serialized)
    dynamic_url = 'dama-fairmm-dimensions-sankey.html?v=' + hashlib.sha256(html.encode('utf-8')).hexdigest()[:12]
    loader = '''<button id="load-fairmm-sankey" type="button">Load interactive diagram</button>

<iframe id="fairmm-sankey-frame" title="Interactive DAMA segments and FAIRMM dimensions Sankey" width="100%" height="1350" loading="lazy" style="border:0;display:none;"></iframe>

<script>
(() => {
  const button=document.getElementById('load-fairmm-sankey'),frame=document.getElementById('fairmm-sankey-frame');
  button.addEventListener('click',()=>{frame.src='__DYNAMIC_URL__';frame.style.display='block';button.hidden=true;});
  window.addEventListener('message',event=>{if(event.source===frame.contentWindow&&event.data?.type==='fairmm-sankey-height'&&Number.isFinite(event.data.height)){frame.height=String(Math.max(600,Math.min(9000,event.data.height+20)));}});
})();
</script>'''.replace('__DYNAMIC_URL__', dynamic_url)
    md = '''# DAMA segments and FAIRMM dimensions

![Sankey of proposed Direct and Indirect dimension alignment](dama-fairmm-dimensions-sankey.svg)

The interactive diagram follows the FAIR–DAMA approach: hover or focus on a segment or dimension to highlight its connections, select a ribbon for rationale and deliverables, and select a label to open its documentation. DAMA labels open the corresponding FAIR–DAMA segment page; dimension labels open the pinned FAIRMM dimension page.

It uses the same pinned D3 and D3 Sankey libraries as FAIR–DAMA, loaded from jsDelivr only when you choose **Load interactive diagram** or open it directly.

__LOADER__

[Open the interactive diagram on its own](dama-fairmm-dimensions-sankey.html) · [Offline interactive fallback](dama-fairmm-dimensions-sankey-offline.html) · [SVG download](dama-fairmm-dimensions-sankey.svg) · [Source data](dama-fairmm-dimensions-sankey.json)

The diagram shows **38 Direct** and **7 Indirect** proposed relationships between 12 numbered DAMA segments and seven FAIRMM dimensions. One equal-width ribbon represents one distinct segment–dimension–type combination, grouping repeated activity records. Width does not indicate strength or maturity.

Direct and Indirect refer to **dimension support**, which is separate from the existing FAIR-principle classification. All seven Indirect dimension relationships target FAIR Data in the current crosswalk. Other dimension relationships can be Direct even when their source principle contribution is Indirect, because they address a workflow or infrastructure descriptor directly.

The aggregate Data Management overview and two extensions without a segment assignment are excluded. Maturity Assessment is included as supporting segment 12. The 45 ribbons group 397 activity/descriptor records; they remain conditional documentary proposals. Select a ribbon in the interactive version to inspect the original source classification, activities, conditions and pinned sources.
'''.replace('__LOADER__', loader)
    md = md.replace('](dama-fairmm-dimensions-sankey.html)', '](' + dynamic_url + ')')
    md=md.replace('**38 Direct** and **7 Indirect**',f'**{counts["Direct"]} Direct** and **{counts["Indirect"]} Indirect**').replace('12 numbered DAMA segments',f'{len(areas)} DAMA areas and additional topics').replace('All seven Indirect','All current Indirect').replace('45 ribbons group 397',f'{len(links)} ribbons group {underlying}').replace('pinned sources','versioned sources')
    write(DOC / 'index.md', md)
    landing = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DAMA and FAIRMM static and interactive Sankeys</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#16283c;background:#fff;max-width:1600px;margin:auto;padding:24px}h1{font-size:28px}img{width:100%;height:auto}button{font:inherit;padding:10px 16px;cursor:pointer}a{color:#2463a7}iframe{width:100%}</style></head><body><h1>DAMA segments and FAIRMM dimensions</h1><p>38 Direct and 7 Indirect proposed relationships. Each equal-width ribbon represents one segment–dimension–type relationship, not strength or maturity.</p><img src="dama-fairmm-dimensions-sankey.svg" alt="Static overview of proposed DAMA segment and FAIRMM dimension alignment"><p>Hover over nodes to highlight connections, select ribbons for rationale and deliverables, and select labels to open documentation. The interactive diagram loads D3 from jsDelivr only after you choose to load it.</p>__LOADER__<p><a href="dama-fairmm-dimensions-sankey.html">Open interactive diagram separately</a> · <a href="dama-fairmm-dimensions-sankey-offline.html">Offline interactive fallback</a> · <a href="dama-fairmm-dimensions-sankey.svg">Static SVG</a></p><p>Direct/Indirect describes dimension support, separately from source FAIR-principle classifications. All seven Indirect links target FAIR Data in the current crosswalk. Maturity Assessment is supporting segment 12; the aggregate overview and two extensions without a segment are excluded.</p></body></html>'''.replace('__LOADER__', loader)
    landing = landing.replace('href="dama-fairmm-dimensions-sankey.html"', 'href="' + dynamic_url + '"')
    landing=landing.replace('38 Direct and 7 Indirect',f'{counts["Direct"]} Direct and {counts["Indirect"]} Indirect').replace('All seven Indirect','All current Indirect')
    write(OUT / 'index.html', landing)
    write(OUT / 'validation.json', json.dumps(dict(status='passed', links=len(links), direct=counts['Direct'], indirect=counts['Indirect'], source_nodes=len(areas), target_nodes=len(dims), underlying_records=underlying, excluded_extensions=2, equal_width=True, conservation_checked=True, svg_xml_valid=True), indent=2) + '\n')
    print(json.dumps(dict(links=len(links), counts=dict(counts), underlying_records=underlying, output=str(OUT))))


if __name__ == '__main__':
    main()
