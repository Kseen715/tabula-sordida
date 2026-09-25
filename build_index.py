"""Write index.html listing every <LANG>/*.html page, grouped by language folder.

Usage: python3 build_index.py
(safe to rerun; CI runs it before every Pages deploy)
Styles, fonts and favicon live in assets/; edit them there.
"""
import glob, html, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
def meta(path):
    src = open(path, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', src, re.S)
    lang = re.search(r'<html[^>]*\blang="([^"]+)"', src)
    return html.unescape(title[1].strip()) if title else os.path.basename(path), lang[1] if lang else ''

groups = {}
for path in sorted(glob.glob(os.path.join(ROOT, '*', '*.html'))):
    groups.setdefault(os.path.basename(os.path.dirname(path)), []).append((os.path.relpath(path, ROOT), *meta(path)))

ACCENTS = ['#d4ff00', '#ff4d1a', '#00d9ff', '#ff3df2', '#ffd400']
e = html.escape
sections, ticker = [], []
for i, (folder, pages) in enumerate(groups.items(), 1):
    lang = pages[0][2] or folder.lower()
    items = ''.join(
        f'<li><a href="{e(rel)}" hreflang="{e(l)}"><span class="no">{i:02}.{j}</span>'
        f'<span class="t" lang="{e(l)}">{e(t)}</span><span class="p">{e(rel)}</span><span class="go" aria-hidden="true">&#8599;</span></a></li>'
        for j, (rel, t, l) in enumerate(pages, 1))
    sections.append(
        f'<section style="--a:{ACCENTS[(i - 1) % len(ACCENTS)]}"><div class="in">'
        f'<h2><span class="idx">{i:02}</span><span class="code">{e(folder)}</span>'
        f'<span class="name" data-lang="{e(lang)}" lang="{e(lang)}">{e(folder)}</span>'
        f'<span class="cnt">&times;{len(pages):02}</span></h2>'
        f'<p class="serial" aria-hidden="true">LNG-{e(folder)}/{i:04} &nbsp;//&nbsp; {e(lang)}</p><ul>{items}</ul></div></section>')
    ticker += [f'<b>{e(folder)}</b>'] + [e(t) for _, t, _ in pages]
total = sum(len(p) for p in groups.values())

PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tabula Sordida</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/index.css">
</head>
<body>
<div class="top"><span><span class="dot"></span>SYS.IDX // ONLINE</span><span>TS-01 / PAGE DIRECTORY</span><span class="bar" aria-hidden="true"></span><a href="https://github.com/Kseen715/tabula-sordida">GitHub &#8599;</a></div>
<main>
<div class="hero">
<h1><span>Tabula</span><span class="o">Sordida</span></h1>
<p class="tag">Offline page archive <span>&#9656;</span> sorted by language</p>
</div>
<div class="stats"><div><b>@TOTAL@</b>pages</div><div><b>@LANGS@</b>languages</div></div>
<div class="ticker" aria-hidden="true"><div>@TICK@ <i>///</i> @TICK@ <i>///</i> </div></div>
<div class="grid">
@SECTIONS@
</div>
<footer><span class="stripe" aria-hidden="true"></span><span>Tabula Sordida // index</span><a href="https://github.com/Kseen715/tabula-sordida">github.com/Kseen715/tabula-sordida</a><span>&#9632; &#9632; &#9632; EOF</span></footer>
</main>
<script>
// native language names ("de" -> "Deutsch"); folder code stays as fallback
for (const el of document.querySelectorAll('[data-lang]')) {
  try { el.textContent = new Intl.DisplayNames([el.dataset.lang], {type: 'language'}).of(el.dataset.lang); } catch {}
}
</script>
</body>
</html>
'''
page = (PAGE.replace('@TOTAL@', f'{total:02}').replace('@LANGS@', f'{len(groups):02}')
        .replace('@TICK@', ' <i>///</i> '.join(ticker)).replace('@SECTIONS@', '\n'.join(sections)))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print(f'index.html: {total} pages in {len(groups)} languages')
