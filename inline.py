"""Embed Google Fonts and Unsplash images into HTML files so they open offline.

Usage: python3 inline.py */*.html  (rewrites files in place; safe to rerun)
"""
import base64, re, sys, urllib.error, urllib.request
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
cache = {}
def get(url):
    if url not in cache:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
            cache[url] = (r.headers.get_content_type(), r.read())
    return cache[url]
def data_uri(url):
    ctype, body = get(url)
    return f'data:{ctype};base64,{base64.b64encode(body).decode()}'
def photo(pid, w):
    # webp keeps the embedded size down; all modern browsers render it
    try:
        return data_uri(f'https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w={w}&q=75&fm=webp')
    except urllib.error.HTTPError as e:
        # a dead photo must be replaced in the page source, not papered over with a duplicate
        sys.exit(f'photo-{pid}: HTTP {e.code}; pick another Unsplash photo id (file left unchanged)')

SUBSETS = {'latin', 'latin-ext', 'cyrillic', 'cyrillic-ext'}
def covers(rng, chars):
    for a, b in re.findall(r'U\+([\da-f?]+)(?:-([\da-f]+))?', rng, re.I):
        lo, hi = int(a.replace('?', '0'), 16), int((b or a).replace('?', 'f'), 16)
        if any(lo <= c <= hi for c in chars):
            return True
    return False
def fonts_style(href, text):
    css = get(href.replace('&amp;', '&'))[1].decode()
    # CJK fonts ship as ~100 unnamed numbered slices; keep only slices holding characters the page uses
    chars = {ord(c) for c in text if ord(c) > 0x2ff}
    blocks = re.findall(r'(?:/\* ([\w-]+) \*/\s*)?(@font-face \{.*?\})', css, re.S)
    keep = [b for sub, b in blocks if sub in SUBSETS or not sub and covers(re.search(r'unicode-range:([^;]*)', b)[1], chars)]
    out = [re.sub(r'url\((.*?)\)', lambda m: f'url({data_uri(m[1])})', b) for b in keep]
    return '<style>\n' + '\n'.join(out) + '\n</style>'

for p in sys.argv[1:]:
    s = open(p).read()
    used = re.findall(r'(?:img: "|images\.unsplash\.com/photo-)([\da-f-]+)', s)
    dups = sorted({i for i in used if used.count(i) > 1})
    if dups:
        print(f'  warning: photos used more than once: {dups}')
    s = re.sub(r'[ \t]*<link rel="preconnect"[^>]*>\n', '', s)
    s = re.sub(r'<link href="(https://fonts\.googleapis\.com/[^"]+)" rel="stylesheet"\s*/?>', lambda m: fonts_style(m[1], s), s)
    # menu items reference photos by id; emit one lookup table instead of repeating data URIs
    ids = sorted(set(re.findall(r'img: "([\da-f-]+)"', s)))
    if ids and 'const IMG = {' not in s:
        table = '\n        const IMG = {\n' + ''.join(f'            "{i}": "{photo(i, 800)}",\n' for i in ids) + '        };'
        s = s.replace("        const grid = document.getElementById('menu-grid');", table + "\n        const grid = document.getElementById('menu-grid');", 1)
    s = re.sub(r'https://images\.unsplash\.com/photo-([\da-f-]+)\?[^\'")\s]*?w=(\d+)[^\'")\s]*', lambda m: photo(m[1], m[2]), s)
    left = re.findall(r'(?:src=|url\()["\']?https?://[^"\')]+|<link[^>]*https?://[^>]*>', s)
    print(p, len(s), 'remaining refs:', left)
    open(p, 'w').write(s)
