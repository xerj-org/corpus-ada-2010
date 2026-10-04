#!/usr/bin/env python3
"""Extract per-section plain-text files from the ADA 2010 Standards for
Accessible Design page (ada.gov single-page HTML).

The current ada.gov publishes the 2010 Standards as ONE page
(/law-and-regs/design-standards/2010-stds/); the old per-section URLs are gone.
Section units are the page's own <h2>/<h3> structure with stable ids:
h3 = a numbered section (e.g. "603 Toilet and Bathing Rooms"), with
subsections ("603.2 Clearances.") as strong-lead paragraphs inside.
An h2 that contains h3 children becomes an index file; an h2 without h3
children becomes a content file. Figures carry rich technical alt text,
emitted as [Figure: caption — alt text] lines.
"""
import html as htmllib
import os
import re
import sys

FETCH_DATE = '2026-10-04'
PAGE = 'https://www.ada.gov/law-and-regs/design-standards/2010-stds/'

HEAD = re.compile(r'<(h[1-4])[^>]*\bid="([^"]+)"[^>]*>(.*?)</\1>', re.S)


def strip_tags(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    return s


def text_of(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'<[a-zA-Z/!][^>]*$', '', s)   # tag split across lines
    s = s.lstrip('>').strip()
    s = htmllib.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def render_figures(s):
    def fig(m):
        inner = m.group(0)
        alt = ''
        am = re.search(r'<img[^>]*\balt="([^"]*)"', inner)
        if am:
            alt = htmllib.unescape(am.group(1)).strip()
        cap = ''
        cm = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', inner, re.S)
        if cm:
            cap = text_of(cm.group(1))
        if alt and cap:
            return f'\n<p>__FIGURE__{cap} — {alt}</p>\n'
        if alt:
            return f'\n<p>__FIGURE__{alt}</p>\n'
        if cap:
            return f'\n<p>__FIGURE__{cap}</p>\n'
        return ''
    return re.sub(r'<figure[^>]*>.*?</figure>', fig, s, flags=re.S | re.I)


def render_tables(s):
    def tbl(m):
        out = []
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(1), re.S | re.I):
            cells = []
            for td in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.S | re.I):
                t = text_of(td)
                if t:
                    cells.append(t)
            if cells:
                out.append(' | '.join(cells))
        return '\n<p>__ROW__' + '\n__ROW__'.join(out) + '</p>\n' if out else ''
    return re.sub(r'<table[^>]*>(.*?)</table>', tbl, s, flags=re.S | re.I)


def render_list_items(s):
    return re.sub(r'<li[^>]*>', '\n<p>__LI__', s, flags=re.I)


def render_block(s, out):
    s = strip_tags(s)
    s = render_figures(s)
    s = render_tables(s)
    s = render_list_items(s)
    # block-level tags -> line breaks
    s = re.sub(r'</(p|div|li|ul|ol|details|summary|h[1-6]|blockquote)>', '\n', s, flags=re.I)
    s = re.sub(r'<(br|hr)\s*/?>', '\n', s, flags=re.I)
    for raw in s.split('\n'):
        line = re.sub(r'^\s*<[^>]+>', '', raw).strip()
        if line.startswith('__FIGURE__'):
            out.append('[Figure: ' + line[len('__FIGURE__'):] + ']')
            continue
        if line.startswith('__ROW__'):
            out.append(line[len('__ROW__'):])
            continue
        if line.startswith('__LI__'):
            t = text_of(line[len('__LI__'):])
            if t:
                out.append('- ' + t)
            continue
        t = text_of(line)
        if t:
            out.append(t)


def main(src, outdir):
    h = open(src, encoding='utf-8').read()
    os.makedirs(os.path.join(outdir, 'sections'), exist_ok=True)
    matches = [(m.start(), m.end(), m.group(1), m.group(2), text_of(m.group(3)))
               for m in HEAD.finditer(h)]
    manifest = []
    counts = {'h2_index': 0, 'h2_content': 0, 'h3': 0}
    for i, (s0, e0, tag, hid, title) in enumerate(matches):
        if tag not in ('h2', 'h3'):
            continue
        if hid == 'page-type-info-box-header':
            continue  # page-template help panel, not part of the Standards
        title = title.replace('**', '').strip()
        # slice to next h2/h3 heading
        nxt = None
        for j in range(i + 1, len(matches)):
            if matches[j][2] in ('h2', 'h3'):
                nxt = matches[j][0]
                break
        if nxt is not None:
            end = nxt
        else:
            # final slice: cut at the page template's help panel / footer
            cands = [p for p in (h.find('last updated', e0), h.find('touchpoints'),
                                 h.find('<footer'), h.find('class="usa-footer'))
                     if p > e0]
            end = min(cands) if cands else len(h)
        chunk = h[e0:end]
        path = f'sections/{hid}.txt'
        url = PAGE + '#' + hid
        lines = []
        render_block(chunk, lines)
        body = [x for x in lines if x.strip()]
        # h2 with h3 children -> index
        children = []
        if tag == 'h2':
            for j in range(i + 1, len(matches)):
                if matches[j][2] == 'h2':
                    break
                if matches[j][2] == 'h3':
                    children.append(matches[j][4].replace('**', '').strip())
        head = [title, f'ADA 2010 Standards for Accessible Design, 28 CFR Parts 35 & 36 (US DOJ)',
                f'Source: {url} (fetched {FETCH_DATE})']
        if tag == 'h2' and children:
            counts['h2_index'] += 1
            content = ['Index of subsections in this division:', ''] + \
                      [f'  {c}' for c in children]
        else:
            counts['h2_content' if tag == 'h2' else 'h3'] += 1
            content = body
        with open(os.path.join(outdir, path), 'w', encoding='utf-8') as f:
            f.write('\n'.join(head) + '\n\n' + '\n'.join(content) + '\n')
        manifest.append((path, url, title))
    with open(os.path.join(outdir, 'MANIFEST.tsv'), 'w', encoding='utf-8') as f:
        f.write('path\turl\tsection\n')
        for p, u, t in manifest:
            f.write(f'{p}\t{u}\t{t}\n')
    print('sections written:', len(manifest), counts)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
