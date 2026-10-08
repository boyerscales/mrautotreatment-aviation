#!/usr/bin/env python3
"""Writes the home page's script-built content into index.html itself.

    python3 tools/prerender_home.py

The page builds its service list, airport list, map pins, footer lists, booking choices
and every call/text/email link from CFG with JavaScript. Visitors never notice, but
anything that reads the raw HTML (search engines, link previews, his mentor's site check)
saw empty boxes and no phone link. This loads the page in headless Chrome, copies what
the script built back into the matching empty elements, and fills in the links straight
from CFG. The script still runs and rebuilds the same thing, so nothing changes on screen.

Re-run it after any change to CFG or to the templates in fill() / booking().
"""
import functools, html, http.server, pathlib, re, subprocess, threading, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# elements fill() and booking() write with innerHTML
TARGETS = ['svcList', 'moreList', 'footSvcs', 'footApts', 'aptGuides', 'aptList', 'pins',
           'segService', 'segSize', 'bApt', 'bExtras']
# runtime-only state the static copy shouldn't carry
STATE = {'aptList': ['on'], 'pins': ['on']}


def inner_span(doc, el_id):
    """(start, end) of the inner HTML of the element with this id, by counting its own tag."""
    m = re.search(r'<(\w+)\b[^>]*\bid="%s"[^>]*>' % re.escape(el_id), doc)
    if not m:
        raise SystemExit(f'#{el_id} not found')
    tag, start, depth = m.group(1), m.end(), 1
    for t in re.finditer(r'<(/?)%s\b[^>]*>' % tag, doc[start:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return start, start + t.start()
    raise SystemExit(f'#{el_id} never closes')


def rendered_dom():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        url = f'http://127.0.0.1:{srv.server_address[1]}/'
        out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--virtual-time-budget=6000',
                              '--dump-dom', url], capture_output=True, text=True, timeout=90)
        return out.stdout
    finally:
        srv.shutdown()


def cfg(doc, key):
    return re.search(r"\b%s\s*:\s*'([^']*)'" % key, doc).group(1)


def main():
    doc = PAGE.read_text()
    dom = rendered_dom()
    if 'id="svcList"' not in dom:
        raise SystemExit('Chrome returned no page. Is Google Chrome installed?')

    for el_id in TARGETS:
        a, b = inner_span(dom, el_id)
        inner = dom[a:b]
        for cls in STATE.get(el_id, []):
            inner = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % ' '.join(c for c in m.group(1).split() if c != cls), inner)
        inner = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % ' '.join(c for c in m.group(1).split() if c != 'in'), inner)
        if not inner.strip():
            raise SystemExit(f'#{el_id} came back empty, so the page script probably failed')
        a, b = inner_span(doc, el_id)
        doc = doc[:a] + inner + doc[b:]

    tel, text, mail, short = cfg(doc, 'PHONE_E164'), cfg(doc, 'PHONE_TEXT'), cfg(doc, 'EMAIL'), cfg(doc, 'SHORT')
    sms = f'sms:{tel}?&body=' + urllib.parse.quote(f"Hi {short}, I'd like a quote on a detail. Tail number: ", safe="~()*!.'")
    links = {'data-tel': 'tel:' + tel, 'data-sms': sms, 'data-mail': 'mailto:' + mail}

    def link(m):
        tag = re.sub(r'\shref="[^"]*"', '', m.group(0))
        for attr, href in links.items():
            if re.search(r'\s%s\b' % attr, tag):
                return tag[:-1] + f' href="{html.escape(href)}">'
        return m.group(0)
    doc = re.sub(r'<a\b[^>]*\sdata-(?:tel|sms|mail)\b[^>]*>', link, doc)
    doc = re.sub(r'(<(\w+)\b[^>]*\sdata-phone\b[^>]*>)[^<]*(</\2>)', lambda m: m.group(1) + html.escape(text) + m.group(3), doc)
    doc = re.sub(r'(<(\w+)\b[^>]*\sdata-email\b[^>]*>)[^<]*(</\2>)', lambda m: m.group(1) + html.escape(mail) + m.group(3), doc)

    PAGE.write_text(doc)
    print(f'index.html: {len(TARGETS)} lists written in, call/text/email links filled from CFG')


if __name__ == '__main__':
    main()
