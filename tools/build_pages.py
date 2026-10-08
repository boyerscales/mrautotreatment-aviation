#!/usr/bin/env python3
"""Builds every page except the home page, plus sitemap.xml and robots.txt.

    python3 tools/build_pages.py

- aircraft-detailing/<slug>/  one landing page per airport in AIRPORTS. Each has its own
  title, description, copy and structured data, so it can rank for searches like
  "aircraft detailing SAC" (the Chicago site does the same with /aircraft-detailing-midway).
  Book buttons go back to the home page with the airport picked (?apt=SAC#book).
- services/ and services/<slug>/  the three core services, one page each. The service
  buttons on the home page point here. Book buttons pick the service (?svc=interior#book).
- about/  his bio and photo.

Edit the lists below, then re-run. Keep SERVICES in step with CFG.SERVICES in index.html. Before launch: set SITE to the real domain and NOINDEX = False.
"""
import html, json, pathlib, urllib.parse

SITE = 'https://www.anointedsuds.com'      # PLACEHOLDER: the real domain once he has one
NOINDEX = True                              # True until launch, same as index.html
PHONE_E164, PHONE_TEXT = '+19166780105', '(916) 678-0105'   # same as index.html
BUSINESS = 'AnointedSuds Aviation Detailing'

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Descriptions stick to well-known public facts about each field. PLACEHOLDER: swap in his
# own airport list and anything he knows about working there (FBOs, ramps, hangars).
AIRPORTS = [
  dict(code='SAC', name='Sacramento Executive Airport', short='Sacramento Executive', city='Sacramento', slug='sacramento-executive-airport-sac',
       about='Sacramento Executive sits just south of downtown Sacramento, which makes it a natural base for business flyers, flight departments and local owners.',
       angle='Most of our SAC work is turnarounds between trips, so we plan around your departure and work on the ramp or in your hangar.'),
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


# The three core services. Same names, photos and lists as CFG.SERVICES in index.html.
SERVICES = [
  dict(id='interior', slug='interior-cabin-detailing', label='Interior Cabin Detail', short='Interior cabin detailing',
       h1='Interior cabin detailing', photo='1768346564210-f382cdf18375', alt='Cream leather seats in a private jet cabin',
       card='Seats, tables, side panels, galley, lav and every high-touch spot, cleaned with aviation-safe products.',
       blurb='Cabins are full of delicate materials, so every surface gets the right product and the right touch. Seats, tables, side panels, galley, lav and every high-touch spot, cleaned with aviation-safe products.',
       why='Your passengers notice the cabin first. Leather, wood veneer, plastics and soft goods each need their own product, and nothing harsh goes near the cockpit, so we clean the non-sensitive areas only and leave avionics alone.',
       incl=['Full cabin vacuum','Seats and armrests cleaned','Tray tables and work surfaces','Side panels and cabin walls','Cockpit wipe-down, non-sensitive areas','Galley surfaces','Lavatory cleaned and sanitized','Interior windows','Trash removed','Spot treatment for stains']),
  dict(id='exterior', slug='exterior-dry-wash', label='Exterior Dry Wash', short='Exterior dry wash',
       h1='Exterior aircraft dry wash', photo='1783098269685-49990ec0f9c9', alt='A white private jet on a runway',
       card='A waterless wash that takes off bugs, exhaust film, oil and ramp grime, safe on the paint.',
       blurb='A waterless wash that takes the grime off without hoses on the ramp. Bugs, exhaust film, oil and ramp dirt come off with aviation-approved products that protect your paint. Ideal between trips.',
       why="Most ramps don't allow a wet wash, and you shouldn't have to tow to a wash rack. A dry wash is done right where you're parked, lifts the grime instead of grinding it in, and leaves a protective layer behind.",
       incl=['Complete exterior dry wash','Bugs and ramp grime removed','Leading edges cleaned','Fuselage and tail wiped down','Engine nacelles and pylons','Landing gear wipe-down','Windows and windscreen, acrylic-safe','Finishing detail spray for shine']),
  dict(id='carpet', slug='carpet-shampoo-extraction', label='Carpet Shampoo & Extraction', short='Carpet shampoo and extraction',
       h1='Aircraft carpet shampoo and extraction', photo='1768346564233-d71f37bd19b6', alt='A private jet cabin aisle with carpet and leather seats',
       card='Pre-treat, shampoo and hot-water extraction to lift stains and embedded dirt.',
       blurb='Cabin carpet takes every boarding. We pre-treat, shampoo and hot-water extract to pull out embedded dirt, lift stains and leave the cabin smelling clean.',
       why='Vacuuming only gets the top of the pile. Extraction rinses the dirt and residue out of the fibers, so stains are less likely to wick back and the carpet dries clean instead of sticky.',
       incl=['Carpet condition check','Full vacuum','Stain pre-treatment','Deep shampoo','Hot-water extraction','Embedded dirt pulled out','Odor treatment','Fibers groomed to an even finish']),
]
MORE = 'ceramic coating, brightwork and metal polish, paint correction, belly and gear degreasing, exhaust soot removal, leather care and de-ice residue removal'
STEPS = [
  ('Access, handled', 'We coordinate ramp access, badging and timing with your FBO or hangar.'),
  ('Photos on arrival', "We photograph the aircraft's condition before we touch it."),
  ('The detail', "We work around fueling, catering and crew so your departure doesn't move."),
  ('Photo report', 'You get after photos the moment we finish.'),
]

# About page. He's OK being named (Elijah, 2026-10-08). Two slots are still PLACEHOLDER:
# - ABOUT_PHOTO: a photo of him. Put it in assets/ (about 1000px tall, portrait) and set
#   the file name. Until then the page shows a "photo coming soon" frame.
# - ABOUT_BACKGROUND: his background in his own words (how he got into detailing, how long,
#   what he's worked on). Until then it's one honest holding line.
ABOUT_PHOTO = None          # e.g. 'emmanuel.jpg'
ABOUT_INTRO = "AnointedSuds Aviation Detailing is run by Emmanuel, who also owns Mr. Auto Treatment, a mobile detailing company in Sacramento."
ABOUT_BACKGROUND = [
  "More about Emmanuel's background is coming soon.",
]
ABOUT_HOW = [
  "AnointedSuds brings the same standard to aircraft: careful hands, the right product for every surface, and a finish you can see.",
  "We work on the ramp or in your hangar at airports around Sacramento, and we plan around your departure, not ours. Call and you'll talk to Emmanuel, the person doing the work.",
]

def mark_svg():
    i = (ROOT / 'assets' / 'mark.svg').read_text()
    return i.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">', '<svg class="mk" viewBox="0 0 64 64" aria-hidden="true">')

ICON = {
  'phone': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
  'cal': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  'msg': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
  'check': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>',
  'arrow': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}
e = html.escape
unsplash = lambda pid, w, q=70: f'https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w={w}&q={q}'
HERO_BG = 'https://images.unsplash.com/photo-1566212774847-025968e5bf56?auto=format&fit=crop&w=1600&q=70'

def provider():
    return {"@type":"ProfessionalService","name":BUSINESS,"telephone":"+1-" + PHONE_TEXT[1:4] + "-" + PHONE_TEXT[6:],"url":SITE + "/"}

def crumbs_ld(*items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":i + 1,"name":n,"item":u} for i, (n, u) in enumerate(items)]}

def steps_html():
    return ''.join(f'<li><span>0{i+1}</span><div><h3>{e(n)}</h3><p>{e(d)}</p></div></li>' for i, (n, d) in enumerate(STEPS))

def how_it_works(up):
    return f"""  <section class="sec">
    <div class="wrap two">
      <div>
        <span class="eye">How it works</span>
        <h2>Ready when you're <em>wheels-up</em></h2>
        <p class="lead">Every aircraft is quoted on its own. Book a time online and we call you with a quote, or call now. A deposit holds your time and goes toward your total.</p>
        <ul class="ticks"><li>{ICON['check']}No prices to guess: we quote your aircraft.</li><li>{ICON['check']}Online booking needs 24 hours' notice. Sooner? Call.</li><li>{ICON['check']}Before and after photos on every job.</li></ul>
      </div>
      <ol class="steps">{steps_html()}</ol>
    </div>
  </section>
"""

def quote_form(up, svc=None, apt=None):
    """The form at the bottom of every page. It sends service, airport, tail number and takeoff
    time to the home page's booking (?svc=&apt=&tail=&takeoff=#book), which fills them in, so the
    visitor picks a time and adds their name and number there. Nothing personal goes in the URL."""
    svc_opts = ''.join(f'<option value="{s["id"]}"{" selected" if s["id"] == svc else ""}>{e(s["label"])}</option>' for s in SERVICES)
    svc_opts += f'<option value="full"{" selected" if svc == "full" else ""}>Full Detail, Inside &amp; Out</option>'
    apt_opts = ''.join(f'<option value="{a["code"]}"{" selected" if a["code"] == apt else ""}>{a["code"]} · {e(a["short"])}</option>' for a in AIRPORTS)
    return f"""  <section class="sec quote" id="quote">
    <div class="wrap">
      <span class="eye">Book online</span>
      <h2>Need aircraft detailing in <em>Sacramento?</em></h2>
      <p class="lead">Tell us the service, the aircraft and when it flies, then pick a time. We call you with your quote.</p>
      <form class="qform" action="{up}#book" method="get">
        <div class="f"><label for="qSvc">Service requested</label><select id="qSvc" name="svc">{svc_opts}</select></div>
        <div class="f"><label for="qApt">Airport</label><select id="qApt" name="apt">{apt_opts}</select></div>
        <div class="f"><label for="qTail">Tail number</label><input id="qTail" name="tail" required maxlength="10" pattern="[A-Za-z0-9][A-Za-z0-9\\-]{{1,9}}" autocapitalize="characters" autocomplete="off" spellcheck="false" placeholder="N123AB"></div>
        <div class="f"><label for="qTakeoff">Takeoff date and time</label><input id="qTakeoff" name="takeoff" type="datetime-local"></div>
        <button class="btn btn-gold" type="submit">{ICON['cal']}Pick a time</button>
      </form>
      <p class="qnote">Parked somewhere else, or need it sooner than 24 hours? Call <a href="tel:{PHONE_E164}">{PHONE_TEXT}</a>.</p>
    </div>
  </section>
"""

def shell(up, title, desc, url, ld, main, book, sms_body, svc=None, apt=None):
    """Head, header, footer and phone bar shared by every generated page. `up` is the path back to the site root."""
    sms = f"sms:{PHONE_E164}?&body=" + urllib.parse.quote(sms_body)
    robots = '<meta name="robots" content="noindex">\n' if NOINDEX else ''
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)
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
<meta property="og:image" content="{up}assets/og.jpg">
<link rel="icon" type="image/svg+xml" href="{up}assets/mark.svg">
<link rel="apple-touch-icon" href="{up}assets/logo-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Instrument+Serif:ital@1&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/page.css">
{lds}</head>
<body>
<header class="hdr"><div class="wrap">
  <a class="brand" href="{up}" aria-label="{BUSINESS}, home">{mark_svg()}<span class="brand-txt"><b>Anointed<span>Suds</span></b><small>AVIATION DETAILING</small></span></a>
  <nav class="pnav" aria-label="Main"><a href="{up}">Home</a><a href="{up}services/">Services</a><a href="{up}#airports">Airports</a><a href="{up}about/">About</a><a href="{up}#book">Book</a></nav>
  <a class="btn btn-gold btn-sm" href="tel:{PHONE_E164}">{ICON['phone']}Call</a>
</div></header>
<main>
{main}{quote_form(up, svc, apt)}</main>
<footer class="foot"><div class="wrap">
  <p><b>{BUSINESS}</b> · Aircraft cleaning and detailing in and around Sacramento · <a href="tel:{PHONE_E164}">{PHONE_TEXT}</a></p>
  <p class="links"><a href="{up}services/">Services</a> · <a href="{up}about/">About</a> · <a href="{up}#airports">Airports</a> · <a href="{up}#book">Book online</a></p>
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

def hero(bg, crumbs, eye, h1, lead, cta):
    return f"""  <section class="hero">
    <div class="bg" aria-hidden="true"><img src="{bg}" alt="" fetchpriority="high"></div>
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
      <span class="eye">{eye}</span>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <div class="cta">
        {cta}
      </div>
    </div>
  </section>
"""

def call_btn(label='Call for a quote', cls='btn-gold'):
    return f'<a class="btn {cls}" href="tel:{PHONE_E164}">{ICON["phone"]}{label}</a>'

def airport_page(a):
    up = '../../'
    url = f"{SITE}/aircraft-detailing/{a['slug']}/"
    title = f"Aircraft Detailing at {a['name']} ({a['code']}) | AnointedSuds"
    desc = f"Aircraft cleaning and detailing at {a['name']} ({a['code']}) in {a['city']}, CA: interior cabin detailing, exterior dry wash and carpet extraction. Call {PHONE_TEXT} for a quote or book online."
    book = f"{up}?apt={a['code']}#book"
    others = ' · '.join(f'<a href="../{o["slug"]}/">{o["code"]} {e(o["short"])}</a>' for o in AIRPORTS if o is not a)
    ld = [
      {"@context":"https://schema.org","@type":"Service","name":f"Aircraft detailing at {a['name']}","serviceType":"Aircraft detailing",
       "provider":provider(),
       "areaServed":{"@type":"Airport","name":a['name'],"iataCode":a['code'],"icaoCode":"K" + a['code']},
       "url":url,"description":desc},
      crumbs_ld((BUSINESS, SITE + "/"), (f"Aircraft detailing at {a['code']}", url)),
    ]
    svc = ''.join(f'<article class="card"><h3><a href="{up}services/{s["slug"]}/">{e(s["label"])}</a></h3><p>{e(s["card"])}</p></article>' for s in SERVICES)
    main = hero(HERO_BG, f'<a href="{up}">AnointedSuds</a> / <span>{a["code"]}</span>',
                f"{a['code']} · K{a['code']} · {e(a['city'])}", f"Aircraft detailing at <em>{e(a['name'])}</em>",
                f"{e(a['about'])} {e(a['angle'])}",
                f'{call_btn()}\n        <a class="btn btn-ghost" href="{book}">{ICON["cal"]}Book at {a["code"]}</a>') + f"""  <section class="sec">
    <div class="wrap">
      <span class="eye">What we do at {a['code']}</span>
      <h2>Interior, exterior and carpet, <em>nose to tail</em></h2>
      <div class="cards">{svc}</div>
      <p class="more">Also: {MORE}. <a href="{up}services/">See every service</a></p>
    </div>
  </section>
""" + how_it_works(up) + f"""  <section class="sec end">
    <div class="wrap">
      <h2>Book a detail at <em>{a['code']}</em></h2>
      <p class="lead">Pick a service and a time, and the airport is already filled in.</p>
      <div class="cta center">
        <a class="btn btn-gold" href="{book}">{ICON['cal']}Book at {a['code']}</a>
        {call_btn(PHONE_TEXT, 'btn-ghost')}
      </div>
      <p class="others">Other airports we serve: {others}</p>
    </div>
  </section>
"""
    return shell(up, title, desc, url, ld, main, book, f"Hi AnointedSuds, I'd like a quote on a detail at {a['code']}. Tail number: ", apt=a['code'])

def service_page(s):
    up = '../../'
    url = f"{SITE}/services/{s['slug']}/"
    title = f"{s['h1']} in Sacramento | AnointedSuds Aviation Detailing"
    desc = f"{s['h1'].capitalize()} at Sacramento-area airports: {s['card']} Call {PHONE_TEXT} for a quote or book online."
    book = f"{up}?svc={s['id']}#book"
    ld = [
      {"@context":"https://schema.org","@type":"Service","name":s['label'],"serviceType":s['h1'],"provider":provider(),
       "areaServed":[{"@type":"Airport","name":a['name'],"iataCode":a['code']} for a in AIRPORTS],"url":url,"description":desc},
      crumbs_ld((BUSINESS, SITE + "/"), ("Services", SITE + "/services/"), (s['label'], url)),
    ]
    incl = ''.join(f'<li>{ICON["check"]}{e(x)}</li>' for x in s['incl'])
    apts = ''.join(f'<a class="apt-link" href="{up}aircraft-detailing/{a["slug"]}/"><b>{a["code"]}</b>{e(a["name"])}</a>' for a in AIRPORTS)
    others = ' · '.join(f'<a href="../{o["slug"]}/">{e(o["label"])}</a>' for o in SERVICES if o is not s)
    main = hero(unsplash(s['photo'], 1600), f'<a href="{up}">AnointedSuds</a> / <a href="../">Services</a> / <span>{e(s["label"])}</span>',
                f"Service 0{SERVICES.index(s) + 1} of 03 · Sacramento area", f"{e(s['h1'])} in <em>Sacramento</em>", e(s['blurb']),
                f'{call_btn()}\n        <a class="btn btn-ghost" href="{book}">{ICON["cal"]}Book this service</a>') + f"""  <section class="sec">
    <div class="wrap two">
      <div>
        <span class="eye">What's included</span>
        <h2>{e(s['label'])}, <em>done right</em></h2>
        <p class="lead">{e(s['why'])}</p>
        <ul class="ticks">{incl}</ul>
      </div>
      <figure class="ph"><img src="{unsplash(s['photo'], 1100)}" srcset="{unsplash(s['photo'], 700)} 700w, {unsplash(s['photo'], 1100)} 1100w" sizes="(max-width:859px) 100vw, 50vw" alt="{e(s['alt'])}" loading="lazy" decoding="async"></figure>
    </div>
  </section>
  <section class="sec">
    <div class="wrap">
      <span class="eye">Where we do it</span>
      <h2>{e(s['short'])} at <em>these airports</em></h2>
      <div class="apt-links">{apts}</div>
      <p class="more">Parked somewhere else? <a href="tel:{PHONE_E164}">Call us</a> and ask.</p>
    </div>
  </section>
""" + how_it_works(up) + f"""  <section class="sec end">
    <div class="wrap">
      <h2>Book your <em>{e(s['short'].lower())}</em></h2>
      <p class="lead">Pick a time and the service is already filled in. We call you with your quote.</p>
      <div class="cta center">
        <a class="btn btn-gold" href="{book}">{ICON['cal']}Book this service</a>
        {call_btn(PHONE_TEXT, 'btn-ghost')}
      </div>
      <p class="others">Our other services: {others} · <a href="../">All services</a></p>
    </div>
  </section>
"""
    return shell(up, title, desc, url, ld, main, book, f"Hi AnointedSuds, I'd like a quote on {s['short'].lower()}. Tail number: ", svc=s['id'])

def services_index():
    up = '../'
    url = f"{SITE}/services/"
    title = 'Aircraft Detailing Services in Sacramento | AnointedSuds'
    desc = f"Interior cabin detailing, exterior dry wash and carpet shampoo and extraction at Sacramento-area airports. Call {PHONE_TEXT} for a quote or book online."
    ld = [crumbs_ld((BUSINESS, SITE + "/"), ("Services", url))]
    cards = ''.join(f"""<article class="card svc-card">
        <img src="{unsplash(s['photo'], 800)}" alt="{e(s['alt'])}" decoding="async">
        <span class="eye">Service 0{i + 1}</span>
        <h3>{e(s['label'])}</h3><p>{e(s['card'])}</p>
        <a class="btn btn-ghost btn-sm" href="{s['slug']}/">See {e(s['short'].lower())}{ICON['arrow']}</a>
      </article>""" for i, s in enumerate(SERVICES))
    main = hero(HERO_BG, f'<a href="{up}">AnointedSuds</a> / <span>Services</span>', 'What we do',
                'Aircraft detailing services in <em>Sacramento</em>',
                'Three core services, nose to tail. Every one is quoted for your aircraft, so call for pricing or book a time and we\'ll call you.',
                f'{call_btn()}\n        <a class="btn btn-ghost" href="{up}#book">{ICON["cal"]}Book a service</a>') + f"""  <section class="sec">
    <div class="wrap">
      <span class="eye">Our three core services</span>
      <h2>Interior, exterior and carpet, <em>nose to tail</em></h2>
      <div class="cards">{cards}</div>
      <p class="more">Also on the list: {MORE}. <a href="tel:{PHONE_E164}">Call to ask about any of them.</a></p>
    </div>
  </section>
""" + how_it_works(up)
    return shell(up, title, desc, url, ld, main, f'{up}#book', "Hi AnointedSuds, I'd like a quote on a detail. Tail number: ")

def about_page():
    up = '../'
    url = f"{SITE}/about/"
    title = 'About AnointedSuds Aviation Detailing | Sacramento'
    desc = f"Who we are: AnointedSuds Aviation Detailing, aircraft cleaning and detailing at airports around Sacramento. Call {PHONE_TEXT}."
    ld = [{"@context":"https://schema.org","@type":"AboutPage","name":title,"url":url,"about":provider()},
          crumbs_ld((BUSINESS, SITE + "/"), ("About", url))]
    photo = (f'<img src="{up}assets/{ABOUT_PHOTO}" alt="Emmanuel, owner of AnointedSuds Aviation Detailing" loading="lazy" decoding="async">' if ABOUT_PHOTO
             else '<div class="person-ph" role="img" aria-label="Photo of Emmanuel, owner of AnointedSuds, coming soon">'
                  '<svg viewBox="0 0 120 150" aria-hidden="true"><circle cx="60" cy="52" r="26"/><path d="M14 150c0-30 20.6-50 46-50s46 20 46 50z"/></svg>'
                  '<span>Emmanuel · Owner</span><small>Photo coming soon</small></div>')
    bio = (f'<p class="lead-in">{e(ABOUT_INTRO)}</p>'
           + ''.join(f'<p>{e(p)}</p>' for p in ABOUT_BACKGROUND)
           + ''.join(f'<p>{e(p)}</p>' for p in ABOUT_HOW))
    main = hero(HERO_BG, f'<a href="{up}">AnointedSuds</a> / <span>About</span>', 'About us',
                'About <em>AnointedSuds</em>', 'Aircraft cleaning and detailing in and around Sacramento, from a local owner who answers his own phone.',
                f'{call_btn("Call Emmanuel")}\n        <a class="btn btn-ghost" href="{up}#book">{ICON["cal"]}Book a service</a>') + f"""  <section class="sec">
    <div class="wrap two about">
      <figure class="ph portrait">{photo}</figure>
      <div>
        <span class="eye">Our story</span>
        <h2>Meet <em>Emmanuel</em></h2>
        <div class="bio">{bio}</div>
        <blockquote class="verse-q">"But seek first the kingdom of God and His righteousness, and all these things shall be added to you."<cite>Matthew 6:33</cite></blockquote>
      </div>
    </div>
  </section>
""" + how_it_works(up) + f"""  <section class="sec end">
    <div class="wrap">
      <h2>Let's get your aircraft <em>ready</em></h2>
      <p class="lead">Call for a quote, or book your time online in under a minute.</p>
      <div class="cta center">
        {call_btn(PHONE_TEXT)}
        <a class="btn btn-ghost" href="{up}#book">{ICON['cal']}Book a service</a>
      </div>
      <p class="others"><a href="{up}services/">Our services</a> · <a href="{up}#airports">Airports we serve</a></p>
    </div>
  </section>
"""
    return shell(up, title, desc, url, ld, main, f'{up}#book', "Hi AnointedSuds, I'd like a quote on a detail. Tail number: ")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def main():
    for a in AIRPORTS:
        write(ROOT / 'aircraft-detailing' / a['slug'] / 'index.html', airport_page(a))
    for s in SERVICES:
        write(ROOT / 'services' / s['slug'] / 'index.html', service_page(s))
    write(ROOT / 'services' / 'index.html', services_index())
    write(ROOT / 'about' / 'index.html', about_page())
    urls = ([SITE + '/', SITE + '/services/'] + [f"{SITE}/services/{s['slug']}/" for s in SERVICES] + [SITE + '/about/']
            + [f"{SITE}/aircraft-detailing/{a['slug']}/" for a in AIRPORTS])
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'{len(AIRPORTS)} airport pages, {len(SERVICES)} service pages + services index, about page, sitemap.xml, robots.txt')

if __name__ == '__main__':
    main()
