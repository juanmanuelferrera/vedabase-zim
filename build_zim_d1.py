#!/usr/bin/env python3
"""Build vedabase_en_all from the vedabase.cc D1 export, so the ZIM matches what
vedabase.cc serves: one page per verse / chapter, linked tables of contents at
every level, full titles.

Inputs
  build/d1md/<book>.json   D1 export (vedabase-original/scripts/export_d1.sh)
  chapter-names.json       astro_vedabase/src/lib/chapter-names.json
  icon (PNG)

Usage
  python build_zim_d1.py OUT.zim ICON.png
"""
import datetime, html, io, json, os, posixpath, re, sys
from collections import defaultdict

import markdown
from PIL import Image
from libzim.writer import Creator, Item, StringProvider, Hint, Compression

HERE = os.path.dirname(os.path.abspath(__file__))
D1 = os.path.join(HERE, 'build', 'd1md')
ORIG = os.path.expanduser('~/git_projects/vedabase-original/scripts')
NAMES = os.path.expanduser('~/git_projects/astro_vedabase/src/lib/chapter-names.json')
sys.path.insert(0, ORIG)
from build_from_d1 import BOOKS, LILA, sort_key, render_transcript  # noqa: E402
from letters_format import format_letter                            # noqa: E402

OUT, ICON = sys.argv[1], sys.argv[2]
CH = json.load(open(NAMES))
SITE = 'https://vedabase.cc/en/library/'

# Short reference labels, as vedabase.cc uses them.
ABBR = {'bg': 'Bg.', 'sb': 'SB', 'cc': 'CC', 'iso': 'Īśo', 'noi': 'NoI'}
ORDER = ['bg', 'sb', 'cc', 'kb', 'nod', 'noi', 'iso', 'tlc', 'tqk', 'ssr', 'rv',
         'pop', 'pqpa', 'poy', 'bbd', 'ej', 'ekc', 'lcfl', 'lob', 'owk', 'krp',
         'ttp', 'transcripts', 'letters']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

CSS = """body{font-family:Georgia,'Times New Roman',serif;max-width:46em;margin:0 auto;
padding:1em 1.2em 3em;line-height:1.65;color:#222;background:#fffdf8}
h1{font-size:1.6em;color:#7a3b0c;border-bottom:2px solid #e3c9a0;padding-bottom:.3em;line-height:1.3}
h2{font-size:1.25em;color:#7a3b0c}h3{font-size:1.1em}
a{color:#8b4513}nav.crumbs{font-size:.9em;margin:.2em 0 1em;color:#666}
nav.pn{display:flex;justify-content:space-between;gap:1em;margin:2em 0 0;padding-top:.8em;
border-top:1px solid #e3c9a0;font-size:.95em}
.dev{font-size:1.25em;text-align:center;line-height:1.8;margin:1em 0}
.verse{text-align:center;font-style:italic;margin:1em 0}
.syn{font-size:.95em}.tr{font-weight:bold}
.meta{color:#666;font-style:italic}
ul.toc{list-style:none;padding-left:0}ul.toc li{margin:.35em 0}
ul.cols{columns:2 14em;margin-top:0}ul.cols li{margin:0;padding:.17em 0;break-inside:avoid}
table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:.2em .5em}
blockquote{margin:1em 2em;font-style:italic}
footer{margin-top:2em;font-size:.8em;color:#777}
@media (prefers-color-scheme:dark){body{background:#1b1915;color:#e6e0d4}
h1,h2{color:#e0a96d}a{color:#e0a96d}h1{border-color:#5a4630}nav.pn{border-color:#5a4630}}"""


# ---------- helpers ----------
def esc(s):
    return html.escape(s or '', quote=True)


def md(text):
    text = re.sub(r'\[#\w+\]\n?', '', text or '')            # scrape anchors
    # vedabase.cc links -> internal ZIM links (resolved per page in page())
    text = re.sub(r'\]\(https://vedabase\.cc/(?:en/library/)?([^)\s]+?)/?\)', r'](zim:\1)', text)
    # "[TEXT MISSING](e)": editorial brackets, not links
    text = re.sub(r'\]\((?!https?:|zim:)([^)]*)\)', r'] (\1)', text)
    return markdown.markdown(text, extensions=['tables', 'sane_lists'])


def strip_md(s):
    return re.sub(r'[*_`#>]', '', s or '').strip()


def block(text):
    """'> a\\n> b' blockquote -> 'a<br>b'."""
    lines = [re.sub(r'^\s*>\s?', '', l).rstrip('\\ ').strip() for l in (text or '').split('\n')]
    return '<br>'.join(esc(l) if l else '' for l in lines).replace('<br><br>', '<br><br>')


def rel(src, dst):
    base = posixpath.dirname(src) or '.'
    return posixpath.relpath(dst, base)


def page(path, title, body, crumbs=(), prev=None, nxt=None, source=None):
    c = ' › '.join(f'<a href="{esc(rel(path, p))}">{esc(t)}</a>' for p, t in crumbs)
    pn = ''
    if prev or nxt:
        a = f'<a href="{esc(rel(path, prev[0]))}">← {esc(prev[1])}</a>' if prev else '<span></span>'
        b = f'<a href="{esc(rel(path, nxt[0]))}">{esc(nxt[1])} →</a>' if nxt else '<span></span>'
        pn = f'<nav class="pn">{a}{b}</nav>'
    body = re.sub(r'href="zim:([^"]+)"', lambda m: f'href="{esc(rel(path, m.group(1)))}"', body)
    foot = f'<footer>Original edition text from <a href="{esc(source)}">vedabase.cc</a></footer>' if source else ''
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><link rel="stylesheet" href="{esc(rel(path, "style.css"))}">'
            f'</head><body>{"<nav class=crumbs>" + c + "</nav>" if c else ""}'
            f'<h1>{esc(title)}</h1>{body}{pn}{foot}</body></html>')


def toc(path, items, cols=False):
    lis = ''.join(f'<li><a href="{esc(rel(path, p))}">{esc(t)}</a></li>' for p, t in items)
    return f'<ul class="toc{" cols" if cols else ""}">{lis}</ul>'


class Page(Item):
    def __init__(self, path, title, content, mime='text/html', front=True):
        super().__init__()
        self.p, self.t, self.c, self.m, self.f = path, title, content, mime, front

    def get_path(self): return self.p
    def get_title(self): return self.t
    def get_mimetype(self): return self.m
    def get_contentprovider(self): return StringProvider(self.c)
    def get_hints(self): return {Hint.FRONT_ARTICLE: self.f, Hint.COMPRESS: True}


PAGES = []          # (path, title, html)


def add(path, title, html_):
    PAGES.append((path, title, html_))


def rows(book):
    r = json.load(open(os.path.join(D1, f'{book}.json')))[0]['results']
    return sorted(r, key=lambda x: sort_key(x['ref']))


def is_verse(r):
    return bool((r.get('verse_text') or '').strip() or (r.get('devanagari') or '').strip())


def verse_label(book, ref):
    p = ref.split('/')
    if book == 'cc':
        return f'CC {LILA[p[1]][0].split("-")[0]} {p[2]}.{p[3]}'
    if book in ('bg', 'sb'):
        return f'{ABBR[book]} ' + '.'.join(p[1:])
    return f'{ABBR.get(book, BOOKS[book][1])} {p[-1]}'


def chapter_title(ref, fallback):
    t = CH.get(ref)
    return t if t else fallback


def verse_body(r):
    out = []
    if (r.get('devanagari') or '').strip():
        out.append(f'<p class="dev">{block(r["devanagari"])}</p>')
    if (r.get('verse_text') or '').strip():
        out.append(f'<p class="verse">{block(r["verse_text"])}</p>')
    if (r.get('synonyms') or '').strip():
        out.append('<h3>Synonyms</h3><div class="syn">' + md(r['synonyms']) + '</div>')
    if (r.get('translation') or '').strip():
        out.append('<h3>Translation</h3><div class="tr">' + md(r['translation']) + '</div>')
    if (r.get('purport') or '').strip():
        out.append('<h3>Purport</h3>' + md(r['purport']))
    return ''.join(out)


def prose_body(r, title):
    out = []
    tr = (r.get('translation') or '').strip()
    # In prose rows `translation` is either the chapter title (skip it) or a
    # bold lead paragraph (keep it).
    bare = lambda s: re.sub(r'^[\dIVXL]+\.\s*', '', strip_md(s)).lower()
    if tr and bare(tr) != bare(title):
        out.append(md(tr))
    out.append(md(r.get('purport') or ''))
    return ''.join(out)


# ---------- books ----------
def emit_sequence(book, seq, crumbs):
    """seq: list of (path, title, body). Adds pages with prev/next links."""
    for i, (p, t, b) in enumerate(seq):
        prev = seq[i - 1][:2] if i else None
        nxt = seq[i + 1][:2] if i + 1 < len(seq) else None
        add(p, t, page(p, t, b, crumbs, prev, nxt, SITE + p + '/'))


def build_flat(book):
    """Books whose refs are <book>/<key> (prose chapters and/or verses)."""
    slug, btitle = BOOKS[book]
    rs = rows(book)
    seq, items = [], []
    for r in rs:
        key = r['ref'].split('/', 1)[1]
        if is_verse(r) and re.fullmatch(r'\d+(?:[-–]\d+)?', key):
            t = verse_label(book, r['ref'])
            name = CH.get(r['ref']) or ''
            name = re.sub(r'^(Text|Mantra)\s+\d+:?\s*', '', name)
            if name:
                t = f'{t}: {name}'
            seq.append((r['ref'], t, verse_body(r)))
            items.append((r['ref'], t))
        elif is_verse(r):
            t = chapter_title(r['ref'], key)
            seq.append((r['ref'], t, verse_body(r)))
            items.append((r['ref'], t))
        else:
            fb = strip_md(r.get('translation') or '') if len(strip_md(r.get('translation') or '')) < 120 else key
            t = chapter_title(r['ref'], fb or key)
            seq.append((r['ref'], t, prose_body(r, t)))
            items.append((r['ref'], t))
    crumbs = [('index', 'Home'), (book, btitle)]
    emit_sequence(book, seq, crumbs)
    add(book, btitle, page(book, btitle, toc(book, items), [('index', 'Home')], source=SITE + book + '/'))
    return len(seq)


def build_bg():
    book, (slug, btitle) = 'bg', BOOKS['bg']
    rs = rows(book)
    chapters = defaultdict(list)
    front, n = [], 0
    for r in rs:
        p = r['ref'].split('/')
        (chapters[p[1]].append(r) if len(p) == 3 else front.append(r))
    items = []
    for r in front:
        t = chapter_title(r['ref'], r['ref'])
        items.append((r['ref'], t))
    seq = [(r['ref'], chapter_title(r['ref'], r['ref']), prose_body(r, chapter_title(r['ref'], ''))) for r in front]
    for ch in sorted(chapters, key=int):
        cref = f'bg/{ch}'
        ct = chapter_title(cref, f'Chapter {ch}')
        items.append((cref, ct))
        vitems = []
        for r in chapters[ch]:
            seq.append((r['ref'], verse_label(book, r['ref']), verse_body(r)))
            vitems.append((r['ref'], verse_label(book, r['ref'])))
        add(cref, ct, page(cref, ct, toc(cref, vitems, cols=True),
                           [('index', 'Home'), (book, btitle)], source=SITE + cref + '/'))
    crumbs = [('index', 'Home'), (book, btitle)]
    emit_sequence(book, seq, crumbs)
    add(book, btitle, page(book, btitle, toc(book, items), [('index', 'Home')], source=SITE + book + '/'))
    return len(seq)


def build_nested(book):
    """SB (sb/canto/chapter/verse) and CC (cc/lila/chapter/verse)."""
    slug, btitle = BOOKS[book]
    rs = rows(book)
    tree = defaultdict(lambda: defaultdict(list))
    tops, front = [], []
    for r in rs:
        p = r['ref'].split('/')
        if len(p) == 4:
            tree[p[1]][p[2]].append(r)
        elif len(p) == 3:                 # front matter inside a canto/lila (cc/adi/0a)
            tree[p[1]]['__front__'].append(r)
        else:
            front.append(r)
    for t in tree:
        if t not in tops:
            tops.append(t)
    tops.sort(key=lambda s: (0, LILA[s][1]) if s in LILA else (0, int(s)) if s.isdigit() else (1, s))
    seq, top_items = [], []
    for r in front:
        t = chapter_title(r['ref'], r['ref'])
        seq.append((r['ref'], t, prose_body(r, t)))
        top_items.append((r['ref'], t))
    for top in tops:
        tref = f'{book}/{top}'
        tt = chapter_title(tref, LILA[top][0] if top in LILA else f'Canto {top}')
        top_items.append((tref, tt))
        ch_items = []
        for r in tree[top].get('__front__', []):
            t = chapter_title(r['ref'], r['ref'])
            seq.append((r['ref'], f'{tt} — {t}', prose_body(r, t)))
            ch_items.append((r['ref'], t))
        for ch in sorted((c for c in tree[top] if c != '__front__'), key=lambda c: int(re.match(r'\d+', c).group())):
            cref = f'{book}/{top}/{ch}'
            ctn = chapter_title(cref, f'Chapter {ch}')
            label = (f'{LILA[top][0]} {ch}' if top in LILA else f'SB {top}.{ch}')
            ct = f'{label}: {ctn}'
            ch_items.append((cref, f'Chapter {ch}: {ctn}'))
            vitems = []
            for r in tree[top][ch]:
                vl = verse_label(book, r['ref'])
                seq.append((r['ref'], vl, verse_body(r)))
                vitems.append((r['ref'], vl))
            add(cref, ct, page(cref, ct, toc(cref, vitems, cols=True),
                               [('index', 'Home'), (book, btitle), (tref, tt)], source=SITE + cref + '/'))
        add(tref, f'{btitle} — {tt}', page(tref, f'{btitle} — {tt}', toc(tref, ch_items),
                                           [('index', 'Home'), (book, btitle)], source=SITE + tref + '/'))
    emit_sequence(book, seq, [('index', 'Home'), (book, btitle)])
    add(book, btitle, page(book, btitle, toc(book, top_items), [('index', 'Home')], source=SITE + book + '/'))
    return len(seq)


def parse_date(s):
    m = re.match(r'([A-Z][a-z]+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})', s or '')
    if not m or m.group(1) not in MONTHS:
        return None
    return int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2))


def nice_date(d):
    return f'{d[2]} {MONTHS[d[1] - 1][:3]} {d[0]}' if d else ''


def build_transcripts():
    rs = rows('transcripts')
    by_year, n = defaultdict(list), 0
    for r in rs:
        parts = render_transcript(r)
        title = parts[0].lstrip('# ').strip()
        meta = parts[1].strip('*\n ') if len(parts) > 2 else ''
        body_md = parts[-1]
        typ = re.search(r'Type:\s*(.*?)\s*(?=Dated:|Location:|Audio file:|$)', meta)
        dt = re.search(r'Dated:\s*(.*?)\s*(?=Location:|Audio file:|$)', meta)
        loc = re.search(r'Location:\s*(.*?)\s*(?=Audio file:|$)', meta)
        d = parse_date(dt.group(1) if dt else '')
        where = ', '.join(x for x in [loc.group(1).strip() if loc else '', nice_date(d)] if x)
        full = f'{title} — {where}' if where else title
        year = str(d[0]) if d else (('19' + r['ref'].split('/')[1][:2]) if r['ref'].split('/')[1][:2].isdigit() else 'Undated')
        body = (f'<p class="meta">{esc(meta)}</p>' if meta else '') + md(body_md)
        by_year[year].append((r['ref'], full, body, d or (9999, 0, 0)))
    years = sorted(by_year)
    seq = []
    for y in years:
        lst = sorted(by_year[y], key=lambda x: (x[3], x[0]))
        yp = f'transcripts/year-{y}'
        add(yp, f'Lectures & Conversations — {y}',
            page(yp, f'Lectures & Conversations — {y}', toc(yp, [(p, t) for p, t, _, _ in lst]),
                 [('index', 'Home'), ('transcripts', BOOKS['transcripts'][1])]))
        seq += [(p, t, b) for p, t, b, _ in lst]
    emit_sequence('transcripts', seq, [('index', 'Home'), ('transcripts', BOOKS['transcripts'][1])])
    yitems = [(f'transcripts/year-{y}', f'{y} ({len(by_year[y])})') for y in years]
    add('transcripts', BOOKS['transcripts'][1], page('transcripts', BOOKS['transcripts'][1],
        toc('transcripts', yitems, cols=True), [('index', 'Home')]))
    return len(seq)


def build_letters():
    rs = rows('letters')
    by_year = defaultdict(list)
    for r in rs:
        text = format_letter(r.get('translation'), r.get('purport'))
        name = re.sub(r'^Letter to:\s*', '', (r.get('translation') or '').strip())
        dm = re.search(r'Dated:\s*([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})', r.get('purport') or '')
        lm = re.search(r'Location:\s*([A-Z][a-zA-Z.]*(?: [A-Z][a-zA-Z.]*){0,2})', r.get('purport') or '')
        d = parse_date(dm.group(1) if dm else '')
        where = ', '.join(x for x in [lm.group(1).strip() if lm else '', nice_date(d)] if x)
        title = f'Letter to {name}' + (f' — {where}' if where else '')
        body = md(re.sub(r'^#.*\n', '', text, count=1))
        by_year[str(d[0]) if d else 'Undated'].append((r['ref'], title, body, d or (9999, 0, 0)))
    years = sorted(by_year)
    seq = []
    for y in years:
        lst = sorted(by_year[y], key=lambda x: (x[3], x[1]))
        yp = f'letters/year-{y}'
        add(yp, f'Letters — {y}', page(yp, f'Letters — {y}', toc(yp, [(p, t) for p, t, _, _ in lst]),
                                       [('index', 'Home'), ('letters', 'Letters')]))
        seq += [(p, t, b) for p, t, b, _ in lst]
    emit_sequence('letters', seq, [('index', 'Home'), ('letters', 'Letters')])
    add('letters', 'Letters', page('letters', 'Letters',
        toc('letters', [(f'letters/year-{y}', f'{y} ({len(by_year[y])})') for y in years], cols=True),
        [('index', 'Home')]))
    return len(seq)


def main():
    counts = {}
    for b in ORDER:
        if b == 'bg':
            counts[b] = build_bg()
        elif b in ('sb', 'cc'):
            counts[b] = build_nested(b)
        elif b == 'transcripts':
            counts[b] = build_transcripts()
        elif b == 'letters':
            counts[b] = build_letters()
        else:
            counts[b] = build_flat(b)
    books = [(b, BOOKS[b][1]) for b in ORDER if b not in ('transcripts', 'letters')]
    body = ('<p>The complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda '
            'in their original editions, as published during his lifetime.</p>'
            '<h2>Books</h2>' + toc('index', books) +
            '<h2>Lectures, conversations and letters</h2>' +
            toc('index', [('transcripts', BOOKS['transcripts'][1]), ('letters', 'Letters')]))
    add('index', 'Vedabase Original Edition', page('index', 'Vedabase Original Edition', body,
        source='https://vedabase.cc/'))

    # Unique entry titles (for Kiwix search/suggestions): front matter shared by
    # several books gets the book name; same-day transcripts get (2), (3)...
    groups = defaultdict(list)
    for i, (p, t, _) in enumerate(PAGES):
        groups[t].append(i)
    for t, idx in groups.items():
        if len(idx) < 2:
            continue
        for k, i in enumerate(idx):
            p, _, h = PAGES[i]
            top = p.split('/')[0]
            if top in BOOKS and top not in ('transcripts', 'letters') and len({PAGES[j][0].split('/')[0] for j in idx}) == len(idx):
                PAGES[i] = (p, f'{BOOKS[top][1]}: {t}', h)
            elif k:
                PAGES[i] = (p, f'{t} ({k + 1})', h)
    paths = [p for p, _, _ in PAGES]
    assert len(paths) == len(set(paths)), 'duplicate paths'
    img = Image.open(ICON).convert('RGBA').resize((48, 48), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, format='PNG')
    meta = {
        'Name': 'vedabase_en_all',
        'Title': 'Vedabase Original Edition',
        'Description': 'Complete works of Srila Prabhupada - Original Edition',
        'LongDescription': (
            'The complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupada in their '
            'original, unrevised editions as published during his lifetime: Bhagavad-gita As It Is, '
            'Srimad-Bhagavatam, Sri Caitanya-caritamrta, Krsna Book, Nectar of Devotion and other '
            'books, plus lectures, conversations and letters, with full Sanskrit diacritics. '
            'One page per verse, with linked tables of contents. Source: https://vedabase.cc'),
        'Language': 'eng',
        'Creator': 'A.C. Bhaktivedanta Swami Prabhupada',
        'Publisher': 'Vedic Vault',
        'Date': datetime.date.today().isoformat(),
        'Tags': 'religion;philosophy;hinduism;vaishnavism;_category:religion;_ftindex:yes;_pictures:no;_videos:no;_details:yes',
        'Scraper': 'vedabase-zim 2.0 (python-libzim, from vedabase.cc D1)',
        'Source': 'https://vedabase.cc',
    }
    assert len(meta['Title']) <= 30 and len(meta['Description']) <= 80 and len(meta['LongDescription']) <= 4000
    with Creator(OUT).config_compression(Compression.zstd).config_indexing(True, 'eng') as c:
        for k, v in meta.items():
            c.add_metadata(k, v)
        c.add_illustration(48, buf.getvalue())
        c.add_item(Page('style.css', 'style', CSS, 'text/css', False))
        for p, t, h in PAGES:
            c.add_item(Page(p, t, h))
        c.set_mainpath('index')
    print(json.dumps(counts), 'pages:', len(PAGES), '->', OUT)


if __name__ == '__main__':
    main()
