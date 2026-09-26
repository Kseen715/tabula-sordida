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

# section glyphs from the sprite in PAGE, cycled in place of colours (the index is black and white)
GLYPHS = ['xs', 'sig', 'lat', 'brk', 'ring', 'phi', 'hx', 'chev', 'vf']
SEP = '<svg class="sx"><use href="#xs"/></svg>'
e = html.escape
sections, ticker = [], []
for i, (folder, pages) in enumerate(groups.items(), 1):
    lang = pages[0][2] or folder.lower()
    items = ''.join(
        f'<li><a href="{e(rel)}" hreflang="{e(l)}"><span class="no">{i:02}.{j}</span>'
        f'<span class="t" lang="{e(l)}">{e(t)}</span><span class="p">{e(rel)}</span><span class="go" aria-hidden="true">&#8599;</span></a></li>'
        for j, (rel, t, l) in enumerate(pages, 1))
    sections.append(
        f'<section><div class="in"><div class="rail" aria-hidden="true"><span>TS/{e(folder)}-{i:02} // offline // handle with care</span></div><div class="bd">'
        f'<h2><span class="idx">{i:02}</span><span class="code">{e(folder)}</span>'
        f'<span class="name" data-lang="{e(lang)}" lang="{e(lang)}">{e(folder)}</span>'
        f'<span class="cnt">&times;{len(pages):02}</span>'
        f'<svg class="gl" aria-hidden="true"><use href="#{GLYPHS[(i - 1) % len(GLYPHS)]}"/></svg></h2>'
        f'<p class="serial" aria-hidden="true">LNG-{e(folder)}/{i:04} &nbsp;//&nbsp; {e(lang)}</p><ul>{items}</ul></div></div></section>')
    ticker += [f'<b>{e(folder)}</b>'] + [e(t) for _, t, _ in pages]
total = sum(len(p) for p in groups.values())

# Code 39: 5 bars (2 wide) + 4 spaces (1 wide); rows of 10 chars share the wide-space slot
C39_CHARS = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-. *'
C39_BARS = ['10001', '01001', '11000', '00101', '10100', '01100', '00011', '10010', '01010', '00110']
def code39(text, narrow=1, wide=3, h=14):
    x, rects = 0, []
    for ch in f'*{text}*':
        k = C39_CHARS.index(ch)
        spaces = ['0'] * 4
        spaces[(k // 10 + 1) % 4] = '1'
        for n, w in enumerate(''.join(b + s for b, s in zip(C39_BARS[k % 10], spaces + ['']))):
            width = wide if w == '1' else narrow
            if n % 2 == 0:
                rects.append(f'<rect x="{x}" width="{width}" height="{h}"/>')
            x += width
        x += narrow  # inter-character gap
    x -= narrow
    return f'<svg class="bar" width="{x}" height="{h}" viewBox="0 0 {x} {h}" aria-hidden="true">{"".join(rects)}</svg>'

# glyph sprite: Printstream-style marks drawn once, reused through <use> so they follow currentColor
SPRITE = '''<svg class="sprite" aria-hidden="true"><defs>
<symbol id="xs" viewBox="0 0 124 100"><path d="M0 0H24L62 38L100 0H124L74 50L124 100H100L62 62L24 100H0L50 50Z"/></symbol>
<symbol id="xo" viewBox="-5 -5 134 110"><path d="M0 0H24L62 38L100 0H124L74 50L124 100H100L62 62L24 100H0L50 50Z" fill="none" stroke="currentColor" stroke-width="7"/></symbol>
<symbol id="vf" viewBox="0 0 100 100"><path d="M4 30V4H30M70 4H96V30M96 70V96H70M30 96H4V70M50 38V62M38 50H62" fill="none" stroke="currentColor" stroke-width="7"/></symbol>
<symbol id="vfh" viewBox="0 0 100 100"><path d="M4 30V4H30M70 4H96V30M96 70V96H70M30 96H4V70" fill="none" stroke="currentColor" stroke-width="7"/><path d="M32 36H46L50 43L54 36H68L50 64Z"/></symbol>
<symbol id="hx" viewBox="0 0 80 100"><path d="M40 5H75V80L62 95H5V20L18 5H26M40 42V58M32 50H48" fill="none" stroke="currentColor" stroke-width="6"/></symbol>
<symbol id="tri" viewBox="0 0 80 100"><path d="M16 8H80V24H0ZM16 42H80V58H0ZM16 76H80V92H0Z"/></symbol>
<symbol id="sig" viewBox="0 0 100 100"><g fill="none" stroke="currentColor" stroke-width="4"><path d="M50 4L57 43L96 50L57 57L50 96L43 57L4 50L43 43ZM18 18L32 32M82 18L68 32M82 82L68 68M18 82L32 68"/><circle cx="50" cy="50" r="13"/></g><circle cx="50" cy="50" r="5"/></symbol>
<symbol id="lat" viewBox="0 0 100 100"><path d="M50 3L97 50L50 97L3 50ZM17 34L66 83M34 17L83 66M66 17L17 66M83 34L34 83" fill="none" stroke="currentColor" stroke-width="5"/></symbol>
<symbol id="brk" viewBox="0 0 100 100"><path d="M4 24V4H24M76 4H96V24M96 76V96H76M24 96H4V76M22 22L34 34M78 22L66 34M78 78L66 66M22 78L34 66M42 36L50 44L58 36M42 64L50 56L58 64M36 42L44 50L36 58M64 42L56 50L64 58" fill="none" stroke="currentColor" stroke-width="6"/></symbol>
<symbol id="ring" viewBox="0 0 100 100"><circle cx="50" cy="50" r="38" fill="none" stroke="currentColor" stroke-width="13" pathLength="100" stroke-dasharray="20 5" stroke-dashoffset="22.5"/></symbol>
<symbol id="chev" viewBox="0 0 100 72"><path d="M0 0H32L50 28L68 0H100L50 72Z"/></symbol>
<symbol id="phi" viewBox="0 0 100 100"><path d="M22 92L78 8" stroke="currentColor" stroke-width="7"/><circle cx="50" cy="50" r="28" fill="none" stroke="currentColor" stroke-width="7"/></symbol>
</defs></svg>'''

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
@SPRITE@
<div class="top"><span><span class="dot"></span>SYS.IDX // ONLINE</span><span>TS-01 / PAGE DIRECTORY</span><span>REV 0x@HEX@</span>@BARCODE@<a href="https://github.com/Kseen715/tabula-sordida">GitHub &#8599;</a></div>
<div class="ruler" aria-hidden="true">@RULER@</div>
<main>
<div class="hero">
<div class="htxt">
<p class="kick" aria-hidden="true"><b>[+]</b><span>ARCHIVE // N&deg;@TOTAL@</span><span>SEC.01&ndash;@LANGS@</span><span>DIRTY SLATE</span></p>
<h1><span data-n="01">Tabula</span><span class="o" data-n="02">Sordida</span></h1>
<div class="brand"><svg class="g" aria-hidden="true"><use href="#vfh"/></svg><span class="bn">Offline<br>archive</span><span class="hw" aria-hidden="true">Handle<br>with care</span></div>
<p class="tag">Offline page archive <span>&#9656;</span> sorted by language</p>
<div class="stats"><div><b>@TOTAL@</b>pages</div><div><b>@LANGS@</b>languages</div><div><b>00</b>network refs</div></div>
</div>
<div class="spine" aria-hidden="true">
<div class="c1"><svg class="g"><use href="#hx"/></svg><svg class="g"><use href="#tri"/></svg><svg class="g"><use href="#tri"/></svg><svg class="g"><use href="#hx"/></svg><span class="vt">Handle with care // 0x@HEX@</span></div>
<div class="c2"><svg class="g"><use href="#xs"/></svg><svg class="g"><use href="#xo"/></svg><svg class="g"><use href="#xo"/></svg><svg class="g"><use href="#xs"/></svg><svg class="g"><use href="#sig"/></svg></div>
<div class="c3"><span class="vt">Not a tabula rasa</span><span class="bars"></span><svg class="g"><use href="#vf"/></svg><svg class="g"><use href="#vf"/></svg></div>
</div>
</div>
<div class="ticker" aria-hidden="true"><div>@TICK@ @SEP@ @TICK@ @SEP@ </div></div>
<div class="legend" aria-hidden="true"><span>[+] IDX.@LANGS@</span><span class="rule"></span><span>SORT &#9656; LANG / TITLE</span><span class="rule"></span><span>N&deg;@TOTAL@</span></div>
<div class="grid">
@SECTIONS@
</div>
<footer><span class="stripe" aria-hidden="true"></span><span>Tabula Sordida // index</span><a href="https://github.com/Kseen715/tabula-sordida">github.com/Kseen715/tabula-sordida</a><span>+ + + EOF</span></footer>
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
page = (PAGE.replace('@SPRITE@', SPRITE).replace('@TOTAL@', f'{total:02}').replace('@LANGS@', f'{len(groups):02}')
        .replace('@HEX@', f'{total:02X}{len(groups):02X}')
        .replace('@BARCODE@', code39(f'TS-{total:02}-{len(groups):02}'))
        .replace('@RULER@', ''.join(f'<span>{k * 64:04}</span>' for k in range(32)))
        .replace('@TICK@', f' {SEP} '.join(ticker)).replace('@SEP@', SEP).replace('@SECTIONS@', '\n'.join(sections)))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print(f'index.html: {total} pages in {len(groups)} languages')
