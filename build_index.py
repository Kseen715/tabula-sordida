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

# graduated line fields (the wing and hood stripes): pitch 3, lines thicken toward one end
def gradbars(n, vertical):
    t = lambda k: 0.3 + 2.4 * (k / (n - 1)) ** 1.6
    return ''.join(f'<rect x="{k * 3}" width="{t(n - 1 - k):.2f}" height="10"/>' if vertical
                   else f'<rect y="{k * 3}" width="100" height="{t(k):.2f}"/>' for k in range(n))

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
<symbol id="tb" viewBox="0 0 16 40" preserveAspectRatio="none"><path d="M16 2H8L2 8V32L8 38H16" fill="none" stroke="currentColor" stroke-width="3"/><path d="M6 15H9V25H6Z"/></symbol>
<symbol id="bh" viewBox="0 0 100 120" preserveAspectRatio="none" shape-rendering="crispEdges">@BH@</symbol>
<symbol id="bv" viewBox="0 0 240 10" preserveAspectRatio="none" shape-rendering="crispEdges">@BV@</symbol>
<symbol id="sigil" viewBox="-100 -150 200 300"><!-- cybersigil: right half of thorns, mirrored across the spine -->
<g id="sh">
<path d="M0 -150L5 -44L2 0L5 44L0 150Z"/>
<path d="M3 -28C34 -38 62 -72 70 -134C60 -84 36 -52 3 -16Z"/>
<path d="M44 -66L92 -80L50 -56Z"/>
<path d="M3 -96C16 -100 26 -114 24 -140C20 -118 12 -106 3 -102Z"/>
<path d="M5 -3C40 -10 70 -6 99 -24C74 4 42 8 5 7Z"/>
<path d="M60 -6L84 18L66 0Z"/>
<path d="M3 26C32 36 58 70 52 124C46 88 26 58 3 42Z"/>
<path d="M36 50L78 44L40 60Z"/>
<path d="M3 104C14 108 20 122 16 140C12 124 8 116 3 114Z"/>
<path d="M0 -20L12 0L0 20Z"/>
</g><use href="#sh" transform="scale(-1 1)"/></symbol>
</defs></svg>'''.replace('@BH@', gradbars(40, False)).replace('@BV@', gradbars(80, True))

PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tabula Sordida</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/index.css">
<script>try { const t = localStorage.getItem('theme'); if (t) document.documentElement.dataset.theme = t; } catch {}</script>
</head>
<body>
@SPRITE@
<div class="top"><span><span class="dot"></span>SYS.IDX // ONLINE</span><span>TS-01 / PAGE DIRECTORY</span><span>REV 0x@HEX@</span>@BARCODE@<button class="theme" type="button" aria-pressed="false">Dark</button><a href="https://github.com/Kseen715/tabula-sordida">GitHub &#8599;</a></div>
<div class="ruler" aria-hidden="true">@RULER@</div>
<main>
<div class="hero">
<svg class="sigil" aria-hidden="true"><use href="#sigil"/></svg>
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
<div class="c3"><span class="vt">Not a tabula rasa</span><svg class="bars bh"><use href="#bh"/></svg><svg class="bars bv"><use href="#bv"/></svg><svg class="g"><use href="#vf"/></svg><svg class="g"><use href="#vf"/></svg></div>
</div>
</div>
<div class="tape" aria-hidden="true"><svg class="tb"><use href="#tb"/></svg><div class="ticker"><div>@TICK@ @SEP@ @TICK@ @SEP@ </div></div><svg class="tb r"><use href="#tb"/></svg></div>
<div class="legend" aria-hidden="true"><span>[+] IDX.@LANGS@</span><span class="rule"></span><span>SORT &#9656; LANG / TITLE</span><span class="rule"></span><span>N&deg;@TOTAL@</span></div>
<div class="grid">
@SECTIONS@
</div>
<footer><svg class="stripe" aria-hidden="true"><use href="#bv"/></svg><span>Tabula Sordida // index</span><a href="https://github.com/Kseen715/tabula-sordida">github.com/Kseen715/tabula-sordida</a><span>+ + + EOF</span></footer>
</main>
<script>
// native language names ("de" -> "Deutsch"); folder code stays as fallback
for (const el of document.querySelectorAll('[data-lang]')) {
  try { el.textContent = new Intl.DisplayNames([el.dataset.lang], {type: 'language'}).of(el.dataset.lang); } catch {}
}
// theme toggle: flips whatever is showing now and remembers the choice
const root = document.documentElement, btn = document.querySelector('.theme');
const isDark = () => (root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')) === 'dark';
const sync = () => btn.setAttribute('aria-pressed', isDark());
btn.onclick = () => { root.dataset.theme = isDark() ? 'light' : 'dark'; try { localStorage.setItem('theme', root.dataset.theme); } catch {} sync(); };
matchMedia('(prefers-color-scheme: dark)').onchange = sync;
sync();
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
