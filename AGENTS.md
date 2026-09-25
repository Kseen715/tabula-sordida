# AGENTS.md

## Layout

- `DE/`, `EN/`, `RU/` hold one standalone HTML page each.
- `inline.py` embeds external fonts and images into the pages.

## Rule: pages must work offline

Every HTML file has to open with no network access. Don't leave external resources in the committed pages. That covers stylesheets, fonts, images, scripts and `url(...)` references. Plain `<a href>` hyperlinks are fine.

To add a Google Font or an Unsplash photo:

1. Write the normal network reference in the page:
   - a `<link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">` tag, or
   - an `https://images.unsplash.com/photo-<id>?...&w=<width>...` URL.
2. Run `python3 inline.py */*.html`. It rewrites the files in place and is safe to rerun.
3. Check the script's output. Each file must print `remaining refs: []`.

What `inline.py` does:

- **Fonts** become base64 woff2 `@font-face` rules. It keeps only the latin, latin-ext, cyrillic and cyrillic-ext subsets.
- **Photos** become base64 webp data URIs at the `w=` width from the URL.
- **Dead photos** (non-200 response) stop the script and leave that file unchanged. Replace the id in the page source with a working photo that matches the `alt` text, then rerun.
- **Repeated photos** on one page print a warning. Each image slot should use its own photo unless reuse is deliberate.
- To swap an image that is already embedded, replace its `data:image/webp;base64,...` URI with an Unsplash URL again, then rerun.
- **RU menu cards** reference photos by id (`img: "<id>"`). The script adds a single `const IMG = {id: dataURI}` table so repeated photos are stored once, and the cards render `IMG[item.img]`. Put new menu items in as ids, not URLs. If you add new ids after the table already exists, delete the `const IMG = { ... };` block and rerun the script.

Other sources, such as other CDNs or other image hosts, are not handled yet. Extend `inline.py` for them rather than embedding them by hand.

## Checks

```sh
# should print only plain hyperlinks and the SVG xmlns
grep -o 'https\?://[^"'"'"' )<>]*' */*.html | grep -v 'w3.org/2000/svg' | sort -u
```

Test pages in a browser with the network disabled.
