#!/usr/bin/env python3
"""Builds one landing page per airport, plus sitemap.xml and robots.txt.

    python3 tools/build_airports.py

Writes aircraft-detailing/<slug>/index.html for every airport below. Each page has its
own title, description, copy and structured data, so it can rank for searches like
"aircraft detailing SAC" or "jet detailing Mather" (the Chicago site does the same thing
with /aircraft-detailing-midway). Book buttons go back to the main page with the airport
already picked (?apt=SAC#book).

Edit AIRPORTS, then re-run. Before launch: set SITE to the real domain and NOINDEX = False.
"""
import html, json, pathlib, urllib.parse

SITE = 'https://www.anointedsuds.com'      # PLACEHOLDER: the real domain once he has one
NOINDEX = True                              # True until launch, same as index.html
PHONE_E164, PHONE_TEXT = '+19166136405', '(916) 613-6405'   # PLACEHOLDER: same as index.html
BUSINESS = 'AnointedSuds Aviation Detailing'

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Descriptions stick to well-known public facts about each field. PLACEHOLDER: swap in his
# own airport list and anything he knows about working there (FBOs, ramps, hangars).
AIRPORTS = [
  dict(code='SAC', name='Sacramento Executive Airport', short='Sacramento Executive', city='Sacramento', slug='sacramento-executive-airport-sac',
       about='Sacramento Executive sits just south of downtown Sacramento, which makes it a natural base for business flyers, flight departments and local owners.',
       angle='Most of our SAC work is turnarounds between trips, so we plan around your departure and work on the ramp or in your hangar.'),
  dict(code='SMF', name='Sacramento International Airport', short='Sacramento International', city='Sacramento', slug='sacramento-international-airport-smf',
       about="Sacramento International is the region's airline airport, northwest of downtown near Natomas, and it sees a steady flow of business jets and charter traffic.",
       angle='Charter and corporate aircraft at SMF often turn quickly, so we coordinate ramp access ahead of time and work to your schedule.'),
  dict(code='MHR', name='Sacramento Mather Airport', short='Sacramento Mather', city='Rancho Cordova', slug='mather-airport-mhr',
       about='Sacramento Mather, the former Mather Air Force Base in Rancho Cordova, has long runways and handles cargo, corporate and general aviation traffic.',
       angle='We detail aircraft based at Mather and transient aircraft passing through, inside and out.'),
  dict(code='MCC', name='McClellan Airfield', short='McClellan Airfield', city='McClellan Park', slug='mcclellan-airfield-mcc',
       about='McClellan Airfield, at the former McClellan Air Force Base in McClellan Park, is home to aviation businesses, maintenance shops and corporate operators.',
       angle='Coming out of maintenance at McClellan? We can clean up the cabin and exterior before it goes back into service.'),
  dict(code='LHM', name='Lincoln Regional Airport', short='Lincoln Regional', city='Lincoln', slug='lincoln-regional-airport-lhm',
       about='Lincoln Regional in Placer County serves a busy general aviation community north of Sacramento, from owner-pilots to business aircraft.',
       angle='We come to your hangar at Lincoln, so your airplane never has to move to get detailed.'),
  dict(code='AUN', name='Auburn Municipal Airport', short='Auburn Municipal', city='Auburn', slug='auburn-municipal-airport-aun',
       about='Auburn Municipal sits in the Sierra foothills off Interstate 80, a home field for many owner-pilots in Placer County.',
       angle='Foothill flying means bugs and dust on the leading edges. We take them off and protect the paint so the next wash is easier.'),
  dict(code='DWA', name='Yolo County Airport', short='Yolo County', city='Davis / Woodland / Winters', slug='yolo-county-airport-dwa',
       about='Yolo County Airport serves Davis, Woodland and Winters, with a general aviation community of owner-pilots and flight training.',
       angle='Ag-country flying is hard on paint and windscreens. We clean both with products made for aircraft.'),
  dict(code='EDU', name='University Airport', short='University Airport', city='Davis', slug='university-airport-davis-edu',
       about='University Airport is owned by UC Davis and sits just west of campus, home to light aircraft and owner-pilots.',
       angle="Light aircraft get the same care as jets: cabin, exterior, windows and carpet, quoted for what you fly."),
]

SERVICES = [
  ('Interior Cabin Detail', 'Seats, tables, side panels, galley, lav and every high-touch spot, cleaned with aviation-safe products.'),
  ('Exterior Dry Wash', 'A waterless wash that takes off bugs, exhaust film, oil and ramp grime, safe on the paint.'),
  ('Carpet Shampoo & Extraction', 'Pre-treat, shampoo and hot-water extraction to lift stains and embedded dirt.'),
]
STEPS = [
  ('Access, handled', 'We coordinate ramp access, badging and timing with your FBO or hangar.'),
  ('Photos on arrival', "We photograph the aircraft's condition before we touch it."),
  ('The detail', "We work around fueling, catering and crew so your departure doesn't move."),
  ('Photo report', 'You get after photos the moment we finish.'),
]

def mark_svg():
    i = (ROOT / 'assets' / 'mark.svg').read_text()
    return i.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">', '<svg class="mk" viewBox="0 0 64 64" aria-hidden="true">')

ICON = {
  'phone': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
  'cal': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  'msg': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
  'check': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>',
}

def page(a):
    e = html.escape
    url = f"{SITE}/aircraft-detailing/{a['slug']}/"
    title = f"Aircraft Detailing at {a['name']} ({a['code']}) | AnointedSuds"
    desc = f"Aircraft cleaning and detailing at {a['name']} ({a['code']}) in {a['city']}, CA: interior cabin detailing, exterior dry wash and carpet extraction. Call {PHONE_TEXT} for a quote or book online."
    book = f"../../?apt={a['code']}#book"
    sms = f"sms:{PHONE_E164}?&body=" + urllib.parse.quote(f"Hi AnointedSuds, I'd like a quote on a detail at {a['code']}. Tail number: ")
    others = ' · '.join(f'<a href="../{o["slug"]}/">{o["code"]} {e(o["short"])}</a>' for o in AIRPORTS if o is not a)
    ld = [
      {"@context":"https://schema.org","@type":"Service","name":f"Aircraft detailing at {a['name']}","serviceType":"Aircraft detailing",
       "provider":{"@type":"ProfessionalService","name":BUSINESS,"telephone":"+1-916-613-6405","url":SITE + "/"},
       "areaServed":{"@type":"Airport","name":a['name'],"iataCode":a['code'],"icaoCode":"K" + a['code']},
       "url":url,"description":desc},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":BUSINESS,"item":SITE + "/"},
        {"@type":"ListItem","position":2,"name":f"Aircraft detailing at {a['code']}","item":url}]},
    ]
    svc = ''.join(f'<article class="card"><h3>{e(n)}</h3><p>{e(d)}</p></article>' for n, d in SERVICES)
    steps = ''.join(f'<li><span>0{i+1}</span><div><h3>{e(n)}</h3><p>{e(d)}</p></div></li>' for i, (n, d) in enumerate(STEPS))
    robots = '<meta name="robots" content="noindex">\n' if NOINDEX else ''
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="../../assets/og.jpg">
<link rel="icon" type="image/svg+xml" href="../../assets/mark.svg">
<link rel="apple-touch-icon" href="../../assets/logo-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Instrument+Serif:ital@1&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/page.css">
<script type="application/ld+json">{json.dumps(ld[0], ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld[1], ensure_ascii=False)}</script>
</head>
<body>
<header class="hdr"><div class="wrap">
  <a class="brand" href="../../" aria-label="{BUSINESS}, home">{mark_svg()}<span class="brand-txt"><b>Anointed<span>Suds</span></b><small>AVIATION DETAILING</small></span></a>
  <a class="btn btn-gold btn-sm" href="tel:{PHONE_E164}">{ICON['phone']}Call</a>
</div></header>
<main>
  <section class="hero">
    <div class="bg" aria-hidden="true"><img src="https://images.unsplash.com/photo-1566212774847-025968e5bf56?auto=format&fit=crop&w=1600&q=70" alt="" fetchpriority="high"></div>
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../../">AnointedSuds</a> / <span>{a['code']}</span></nav>
      <span class="eye">{a['code']} · K{a['code']} · {e(a['city'])}</span>
      <h1>Aircraft detailing at <em>{e(a['name'])}</em></h1>
      <p class="lead">{e(a['about'])} {e(a['angle'])}</p>
      <div class="cta">
        <a class="btn btn-gold" href="tel:{PHONE_E164}">{ICON['phone']}Call for a quote</a>
        <a class="btn btn-ghost" href="{book}">{ICON['cal']}Book at {a['code']}</a>
      </div>
    </div>
  </section>
  <section class="sec">
    <div class="wrap">
      <span class="eye">What we do at {a['code']}</span>
      <h2>Interior, exterior and carpet, <em>nose to tail</em></h2>
      <div class="cards">{svc}</div>
      <p class="more">Also: ceramic coating, brightwork and metal polish, paint correction, belly and gear degreasing, exhaust soot removal, leather care and de-ice residue removal. <a href="../../#services">See every service</a></p>
    </div>
  </section>
  <section class="sec">
    <div class="wrap two">
      <div>
        <span class="eye">How it works</span>
        <h2>Ready when you're <em>wheels-up</em></h2>
        <p class="lead">Every aircraft is quoted on its own. Book a time online and we call you with a quote, or call now. A deposit holds your time and goes toward your total.</p>
        <ul class="ticks"><li>{ICON['check']}No prices to guess: we quote your aircraft.</li><li>{ICON['check']}Online booking needs 24 hours' notice. Sooner? Call.</li><li>{ICON['check']}Before and after photos on every job.</li></ul>
      </div>
      <ol class="steps">{steps}</ol>
    </div>
  </section>
  <section class="sec end">
    <div class="wrap">
      <h2>Book a detail at <em>{a['code']}</em></h2>
      <p class="lead">Pick a service and a time, and the airport is already filled in.</p>
      <div class="cta center">
        <a class="btn btn-gold" href="{book}">{ICON['cal']}Book at {a['code']}</a>
        <a class="btn btn-ghost" href="tel:{PHONE_E164}">{ICON['phone']}{PHONE_TEXT}</a>
      </div>
      <p class="others">Other airports we serve: {others}</p>
    </div>
  </section>
</main>
<footer class="foot"><div class="wrap">
  <p><b>{BUSINESS}</b> · Aircraft cleaning and detailing in and around Sacramento · <a href="tel:{PHONE_E164}">{PHONE_TEXT}</a></p>
  <p class="verse">"Seek first the kingdom of God." Matthew 6:33</p>
</div></footer>
<nav class="bar" aria-label="Call, text or book">
  <a class="b-call" href="tel:{PHONE_E164}">{ICON['phone']}Call</a>
  <a class="b-alt" href="{sms}">{ICON['msg']}Text</a>
  <a class="b-alt" href="{book}">{ICON['cal']}Book</a>
</nav>
</body>
</html>
"""

def main():
    out = ROOT / 'aircraft-detailing'
    for a in AIRPORTS:
        d = out / a['slug']; d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(page(a))
    urls = [SITE + '/'] + [f"{SITE}/aircraft-detailing/{a['slug']}/" for a in AIRPORTS]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'{len(AIRPORTS)} airport pages, sitemap.xml, robots.txt')

if __name__ == '__main__':
    main()
