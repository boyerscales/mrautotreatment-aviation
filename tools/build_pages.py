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
- membership/  monthly membership sign-up. Plans and prices come from his dashboard
  (Settings > Membership plans), never from here; with none set it says "coming soon".

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
  'lock': '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
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

def shell(up, title, desc, url, ld, main, book, sms_body, svc=None, apt=None, quote=True):
    """Head, header, footer and phone bar shared by every generated page. `up` is the path back to the site root.
    quote=False leaves off the quote form at the bottom, for a page that has its own form."""
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
  <nav class="pnav" aria-label="Main"><a href="{up}">Home</a><a href="{up}services/">Services</a><a href="{up}#airports">Airports</a><a href="{up}membership/">Membership</a><a href="{up}about/">About</a><a href="{up}#book">Book</a></nav>
  <a class="btn btn-gold btn-sm" href="tel:{PHONE_E164}">{ICON['phone']}Call</a>
</div></header>
<main>
{main}{quote_form(up, svc, apt) if quote else ''}</main>
<footer class="foot"><div class="wrap">
  <p><b>{BUSINESS}</b> · Aircraft cleaning and detailing in and around Sacramento · <a href="tel:{PHONE_E164}">{PHONE_TEXT}</a></p>
  <p class="links"><a href="{up}services/">Services</a> · <a href="{up}about/">About</a> · <a href="{up}#airports">Airports</a> · <a href="{up}membership/">Membership</a> · <a href="{up}#book">Book online</a></p>
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

# The membership page's own look, on top of page.css: plan cards, the sign-up form,
# and the cancel panel a member's confirmation text links to.
MEMBERSHIP_CSS = """
.m-plans{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:12px;margin-top:30px}
.m-plan{display:flex;flex-direction:column;padding:24px;border-radius:20px;border:1px solid var(--line);background:var(--card);transition:border-color .25s,box-shadow .25s}
.m-plan.sel{border-color:var(--gold);box-shadow:inset 0 0 0 1px var(--gold)}
.m-plan h3{margin:0;font-size:19px;letter-spacing:-.01em}
.m-price{display:flex;align-items:baseline;gap:8px;margin:14px 0 2px}
.m-price b{font-size:42px;font-weight:700;letter-spacing:-.035em;line-height:1;color:var(--gold)}
.m-price span{color:var(--mute);font-size:14px}
.m-note{margin:6px 0 0;color:var(--mute);font-size:14px}
.m-covers{margin:14px 0 0;font-size:14.5px;color:#d4d0c7}
.m-covers b{display:block;font:700 12px/1.2 Manrope,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--gold);margin-bottom:4px}
.m-plan .ticks{margin:18px 0 22px;flex:1;font-size:15px}
.m-plan .btn{width:100%}
.m-wait{color:var(--mute);margin:30px 0 0}
.m-soon{margin-top:30px;padding:26px;border-radius:20px;border:1px solid var(--gline);background:rgba(224,180,92,.06)}
.m-soon b{display:block;font-size:24px;letter-spacing:-.02em;line-height:1.2;margin-bottom:8px}
.m-soon p{margin:0 0 18px;color:#d4d0c7}
.m-soon a.inl{color:var(--gold);font-weight:700}
.m-form{padding:24px;border-radius:20px;border:1px solid var(--line);background:var(--card)}
.m-form h2{margin:0 0 6px;font-size:clamp(1.6rem,3vw,2.1rem)}
.m-sub{color:var(--mute);font-size:14.5px;margin:0 0 20px}
.m-k{display:block;font-size:13px;font-weight:700;color:#d4d0c7;margin:0 0 7px}
.m-seg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-bottom:18px}
.m-seg button{text-align:left;padding:12px 14px;border-radius:12px;border:1px solid var(--line2);background:#050505;color:var(--ink);font:700 15px Manrope,sans-serif;cursor:pointer;display:grid;gap:2px}
.m-seg button small{font-weight:500;color:var(--mute);font-size:13px}
.m-seg button.sel{border-color:var(--gold);box-shadow:inset 0 0 0 1px var(--gold)}
.m-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0 12px}
.m-f{display:grid;gap:7px;margin-bottom:14px}
.m-f label{font-size:13px;font-weight:700;color:#d4d0c7}
.m-f input,.m-f select{height:50px;width:100%;padding:0 14px;border-radius:12px;border:1px solid var(--line2);background:#050505;color:var(--ink);font:500 16px Manrope,sans-serif;color-scheme:dark}
.m-f input:focus,.m-f select:focus{outline:none;border-color:var(--gold)}
.m-f input.tail{text-transform:uppercase;font-family:'IBM Plex Mono',monospace;letter-spacing:.06em}
.m-sum{margin:6px 0 18px;border-top:1px solid var(--line2)}
.m-sum div{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:14.5px;color:var(--mute)}
.m-sum b{color:var(--ink);text-align:right}
.m-form .btn{width:100%}
.m-form .btn[disabled]{opacity:.6}
.m-err{color:#ff8a7a;font-size:14px;margin:10px 0 0;min-height:1px}
.m-fine{color:var(--mute);font-size:13.5px;margin:12px 0 0;text-align:center}
.m-ok strong{display:block;font-size:26px;letter-spacing:-.02em;margin-bottom:10px}
.m-ok p{color:#d4d0c7;margin:0 0 12px}
.m-ok .cta{margin:18px 0}
.m-link{background:none;border:0;color:var(--mute);text-decoration:underline;text-underline-offset:3px;cursor:pointer;font:500 14px Manrope,sans-serif;padding:0}
.m-terms{margin:18px 0 0;color:#d4d0c7;font-size:14.5px}
.m-terms b{color:var(--gold)}
.m-cancel{max-width:560px}
.btn-bad{color:#ff9a8c;background:transparent;border:1px solid rgba(255,122,112,.5)}
.m-toast{position:fixed;left:50%;top:84px;z-index:40;transform:translateX(-50%);padding:14px 18px;border-radius:14px;background:#121211;border:1px solid var(--line2);font-size:15px;box-shadow:0 20px 50px rgba(0,0,0,.6);width:max-content;max-width:calc(100% - 32px)}
[hidden]{display:none!important}
@media (max-width:520px){.m-row{grid-template-columns:minmax(0,1fr)}.m-form{padding:18px}}
"""

# __TOKENS__ are filled in by membership_page(). Plain string, so the JS keeps its own braces.
MEMBERSHIP_JS = r"""
const M = { API: 'https://dashboard.boyerscales.com', SLUG: 'anointedsuds', PHONE: '__PHONE_TEXT__', TEL: '__PHONE_E164__' };
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const usd = n => '$' + (Number.isInteger(Number(n)) ? Number(n) : Number(n).toFixed(2));
const digits = s => String(s||'').replace(/\D/g,'');
const fmtPhone = v => { const d = digits(v).replace(/^1(?=\d{10})/,'').slice(0,10); if (d.length < 4) return d; if (d.length < 7) return `(${d.slice(0,3)}) ${d.slice(3)}`; return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`; };
const CHECK = '__ICON_CHECK__', PHONE_IC = '__ICON_PHONE__', CAL = '__ICON_CAL__';
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const qs = new URLSearchParams(location.search);
// Tokens and flags come off the address bar once read, so a shared link never carries them.
if ([...qs.keys()].some(k => ['done','m','canceled','cancel'].includes(k))) history.replaceState(null, '', location.pathname + location.hash);
function toast(text, ms){ const t = document.createElement('div'); t.className = 'm-toast'; t.setAttribute('role','status'); t.textContent = text; document.body.append(t); setTimeout(() => t.remove(), ms); }

let plans = [], plan = null;
function renderPlans(){
  if (!plans.length){ $('#mList').hidden = true; $('#mSoon').hidden = false; $('#mJoin').hidden = true; return; }
  $('#mList').innerHTML = plans.map(p => `
    <article class="m-plan${plan && plan.id === p.id ? ' sel' : ''}">
      <h3>${esc(p.name)}</h3>
      <p class="m-price"><b>${usd(p.price)}</b><span>a month</span></p>
      ${p.vehicle_note ? `<p class="m-note">${esc(p.vehicle_note)}</p>` : ''}
      ${p.covers && p.covers.length ? `<p class="m-covers"><b>Covers</b>${p.covers.map(esc).join(', ')}</p>` : ''}
      ${p.includes && p.includes.length ? `<ul class="ticks">${p.includes.map(x => `<li>${CHECK}${esc(x)}</li>`).join('')}</ul>` : '<div style="flex:1;min-height:22px"></div>'}
      <button type="button" class="btn ${plan && plan.id === p.id ? 'btn-gold' : 'btn-ghost'}" data-pick="${esc(p.id)}">${plan && plan.id === p.id ? 'Selected' : 'Choose this plan'}</button>
    </article>`).join('');
  $$('[data-pick]').forEach(b => b.addEventListener('click', () => { pick(b.dataset.pick); $('#mJoin').scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth' }); }));
  $('#mSeg').innerHTML = plans.map(p => `<button type="button" data-seg="${esc(p.id)}"${plan && plan.id === p.id ? ' class="sel"' : ''}>${esc(p.name)}<small>${usd(p.price)} a month</small></button>`).join('');
  $$('[data-seg]').forEach(b => b.addEventListener('click', () => pick(b.dataset.seg)));
  if (plan) $('#mSum').innerHTML = `<div><span>${esc(plan.name)}</span><b>${usd(plan.price)} a month</b></div><div><span>Charged</span><b>After your plan's detail each month</b></div><div><span>Due today</span><b>Nothing</b></div>`;
}
function pick(id){ plan = plans.find(p => p.id === id) || plan; renderPlans(); }
async function loadPlans(){
  try {
    const r = await fetch(`${M.API}/api/public/membership/${M.SLUG}`);
    const j = r.ok ? await r.json() : {};
    plans = Array.isArray(j.plans) ? j.plans : [];
    if (j.terms){ $('#mTerms').innerHTML = '<b>Good to know.</b> ' + esc(j.terms); $('#mTerms').hidden = false; }
  } catch (_) { plans = []; }
  plan = plans[0] || null;
  if (plans.length) $('#mJoin').hidden = false;
  renderPlans();
}
const ph = $('#mPhone');
ph.addEventListener('input', () => { const end = ph.selectionStart === ph.value.length; ph.value = fmtPhone(ph.value); if (end) ph.setSelectionRange(ph.value.length, ph.value.length); });
$('#mApt').addEventListener('change', e => { $('#mAptOtherF').hidden = e.target.value !== 'other'; });
$('#mForm').addEventListener('submit', async e => {
  e.preventDefault();
  const err = $('#mErr'); err.textContent = '';
  const v = id => $(id).value.trim();
  const name = v('#mName'), phone = v('#mPhone'), email = v('#mEmail'), tail = v('#mTail').toUpperCase(), model = v('#mModel'), fbo = v('#mFbo');
  const aptSel = $('#mApt'), apt = aptSel.value === 'other' ? v('#mAptOther') : aptSel.options[aptSel.selectedIndex].text;
  const fail = (msg, sel) => { err.textContent = msg; const el = sel && $(sel); if (el) el.focus(); };
  if (!plan) return fail('Pick a plan first.');
  if (name.length < 2) return fail('We need your name.', '#mName');
  if (digits(phone).length < 10) return fail('That number looks short. We text your confirmation there.', '#mPhone');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return fail('We need an email for your receipts.', '#mEmail');
  if (!/^[A-Z0-9][A-Z0-9-]{1,9}$/.test(tail)) return fail("What's the tail number? Like N123AB.", '#mTail');
  if (model.length < 2) return fail('What do you fly? Make and model is perfect.', '#mModel');
  if (!apt) return fail('Which airport is it based at?', '#mAptOther');
  const btn = $('#mBtn');
  btn.disabled = true; btn.textContent = 'Opening secure checkout…';
  try {
    const r = await fetch(`${M.API}/api/public/membership/${M.SLUG}`, { method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ plan_id: plan.id, name, phone, email, vehicle: [tail, model].filter(Boolean).join(' · '), address: [apt, fbo].filter(Boolean).join(' · ').slice(0, 160) }) });
    const j = await r.json().catch(() => ({}));
    if (r.ok && /^https:\/\/checkout\.stripe\.com\//.test(j.checkout_url || '')){ location.href = j.checkout_url; return; }
    fail(j.error || `Something went wrong. Please call ${M.PHONE}.`);
  } catch (_) { fail(`Couldn't reach us just now. Please call or text ${M.PHONE}.`); }
  btn.disabled = false; btn.innerHTML = '__ICON_LOCK__Save my card';
});
function showJoined(token){
  $('#mJoin').hidden = false; $('#mForm').hidden = true;
  const box = $('#mOk');
  box.innerHTML = `<strong>You're a member.</strong>
    <p>Your card is saved. Nothing was charged today. We'll text you a confirmation with a link to cancel anytime.</p>
    <p>Book your detail whenever you're ready. As a member you don't pay the booking deposit for your plan's detail.</p>
    <div class="cta"><a class="btn btn-gold" href="../#book">${CAL}Book my detail</a><a class="btn btn-ghost" href="tel:${M.TEL}">${PHONE_IC}Call</a></div>
    ${token ? '<button type="button" class="m-link" id="mCancelMine">Changed your mind? Cancel your membership</button>' : ''}`;
  box.hidden = false;
  const c = $('#mCancelMine'); if (c) c.addEventListener('click', () => openCancel(token));
  requestAnimationFrame(() => $('#mJoin').scrollIntoView({ behavior: REDUCED ? 'auto' : 'smooth' }));
}
async function openCancel(token){
  $('#mPage').hidden = true; $('#mCancelSec').hidden = false; scrollTo(0, 0);
  const box = $('#mCancelBox');
  box.innerHTML = '<p class="m-sub">Loading your membership…</p>';
  let m = null;
  try { const r = await fetch(`${M.API}/api/public/membership/${M.SLUG}/m/${encodeURIComponent(token)}`); if (r.ok) m = await r.json(); } catch (_) {}
  if (!m){ box.innerHTML = `<h2>This link doesn't work</h2><p class="m-sub">It may be old, or typed in wrong. Call or text <a class="inl" href="tel:${M.TEL}" style="color:var(--gold);font-weight:700">${M.PHONE}</a> and we'll take care of it.</p>`; return; }
  if (m.status === 'canceled'){ box.innerHTML = `<h2>Already canceled</h2><p class="m-sub">Your ${esc(m.plan)} membership is canceled. Your card won't be charged again.</p><a class="btn btn-ghost" href="./">See the plans</a>`; return; }
  box.innerHTML = `<h2>Cancel your membership?</h2>
    <p class="m-sub">${m.first ? esc(m.first) + ', this' : 'This'} cancels your ${esc(m.plan)} membership (${usd(m.price)} a month). Your card won't be charged again. Anything already charged stays charged.</p>
    <button type="button" class="btn btn-bad" id="mCancelGo">Cancel my membership</button>
    <p class="m-err" id="mCancelErr" role="alert"></p>
    <p class="m-fine"><a class="m-link" href="./">Keep my membership</a></p>`;
  $('#mCancelGo').addEventListener('click', async function(){
    this.disabled = true; this.textContent = 'Canceling…';
    try {
      const r = await fetch(`${M.API}/api/public/membership/${M.SLUG}/m/${encodeURIComponent(token)}/cancel`, { method:'POST', headers:{'Content-Type':'application/json'}, body:'{}' });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(j.error || '');
      box.innerHTML = `<h2>Membership canceled</h2><p class="m-sub">Done. Your card won't be charged again. You're welcome back anytime.</p><a class="btn btn-gold" href="../#book">${CAL}Book a detail</a>`;
    } catch (e) {
      this.disabled = false; this.textContent = 'Cancel my membership';
      $('#mCancelErr').textContent = e.message || `Couldn't cancel just now. Please call or text ${M.PHONE}.`;
    }
  });
}
if (qs.get('cancel')) openCancel(qs.get('cancel'));
else {
  loadPlans().then(() => { if (qs.get('done') === '1') showJoined(qs.get('m') || ''); });
  if (qs.get('canceled') === '1') toast("No card was saved, so you're not signed up yet. Try again anytime.", 8000);
}
"""

def membership_page():
    up = '../'
    url = f"{SITE}/membership/"
    title = 'Monthly Aircraft Detailing Membership | AnointedSuds'
    desc = f"A monthly maintenance membership for your aircraft at Sacramento-area airports. Save a card, get your detail, and you're billed after each month's service. Cancel anytime. {PHONE_TEXT}."
    ld = [crumbs_ld((BUSINESS, SITE + "/"), ("Membership", url))]
    apt_opts = ''.join(f'<option value="{a["code"]}">{a["code"]} · {e(a["short"])}</option>' for a in AIRPORTS) + '<option value="other">Somewhere else</option>'
    steps = [
      ('Pick a plan', 'Choose the plan that fits your aircraft and how often it flies.'),
      ('Save a card', "On Stripe's secure page. Nothing is charged today, and we never see the number."),
      ('Book your detail', "Online or by phone, any time each month. Members don't pay the booking deposit for their plan's detail."),
      ('Billed after the service', "When your plan's detail that month is done, your card is charged the plan price. No plan detail that month, no charge. Anything outside your plan is quoted and paid like normal."),
      ('Cancel anytime', f'Use the link in your confirmation text, or call or text {PHONE_TEXT}.'),
    ]
    steps_list = ''.join(f'<li><span>0{i+1}</span><div><h3>{e(n)}</h3><p>{e(d)}</p></div></li>' for i, (n, d) in enumerate(steps))
    js = (MEMBERSHIP_JS.replace('__PHONE_TEXT__', PHONE_TEXT).replace('__PHONE_E164__', PHONE_E164)
          .replace('__ICON_CHECK__', ICON['check']).replace('__ICON_PHONE__', ICON['phone'])
          .replace('__ICON_CAL__', ICON['cal']).replace('__ICON_LOCK__', ICON['lock']))
    main = f"""  <style>{MEMBERSHIP_CSS}</style>
  <section class="sec m-cancel-sec" id="mCancelSec" hidden>
    <div class="wrap"><div class="m-form m-cancel" id="mCancelBox" aria-live="polite"></div></div>
  </section>
  <div id="mPage">
""" + hero(HERO_BG, f'<a href="{up}">AnointedSuds</a> / <span>Membership</span>', 'Monthly membership',
                'Keep it ready to fly, <em>every month</em>',
                "Pick a plan and save a card. Book your detail each month like always, and your card is charged the plan price after the service is done. Cancel anytime.",
                f'<a class="btn btn-gold" href="#plans">{ICON["arrow"]}See the plans</a>\n        {call_btn("Call us", "btn-ghost")}') + f"""  <section class="sec" id="plans">
    <div class="wrap">
      <span class="eye">The plans</span>
      <h2>Monthly plans for <em>your aircraft</em></h2>
      <div class="m-plans" id="mList"><p class="m-wait">Loading the plans…</p></div>
      <div class="m-soon" id="mSoon" hidden>
        <b>Memberships are coming soon.</b>
        <p>Call or text <a class="inl" href="tel:{PHONE_E164}">{PHONE_TEXT}</a> and we'll set you up.</p>
        <div class="cta">{call_btn('Call')}<a class="btn btn-ghost" href="sms:{PHONE_E164}?&amp;body={urllib.parse.quote("Hi AnointedSuds, I'd like to sign up for a monthly membership. Tail number: ")}">{ICON['msg']}Text us</a></div>
      </div>
    </div>
  </section>
  <section class="sec" id="mJoin" hidden>
    <div class="wrap two">
      <div class="m-form">
        <form id="mForm" novalidate>
          <h2>Join</h2>
          <p class="m-sub">Takes about a minute. Your card goes on Stripe's secure page next.</p>
          <span class="m-k">Your plan</span>
          <div class="m-seg" id="mSeg"></div>
          <div class="m-row">
            <div class="m-f"><label for="mName">Name</label><input id="mName" autocomplete="name" placeholder="First and last name"></div>
            <div class="m-f"><label for="mPhone">Mobile</label><input id="mPhone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(916) 555-0123"></div>
          </div>
          <div class="m-f"><label for="mEmail">Email</label><input id="mEmail" type="email" inputmode="email" autocomplete="email" placeholder="Where your receipts go"></div>
          <div class="m-row">
            <div class="m-f"><label for="mTail">Tail number</label><input class="tail" id="mTail" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="10" placeholder="N123AB"></div>
            <div class="m-f"><label for="mModel">Make and model</label><input id="mModel" autocomplete="off" placeholder="Citation CJ3"></div>
          </div>
          <div class="m-f"><label for="mApt">Where it's based</label><select id="mApt">{apt_opts}</select></div>
          <div class="m-f" id="mAptOtherF" hidden><label for="mAptOther">Which airport?</label><input id="mAptOther" autocomplete="off" placeholder="Name or code"></div>
          <div class="m-f"><label for="mFbo">FBO, hangar or parking spot (optional)</label><input id="mFbo" autocomplete="off" placeholder="FBO name, hangar 12"></div>
          <div class="m-sum" id="mSum"></div>
          <button type="submit" class="btn btn-gold" id="mBtn">{ICON['lock']}Save my card</button>
          <p class="m-err" id="mErr" role="alert"></p>
          <p class="m-fine">Nothing is charged today. Stripe keeps your card, we never see the number.</p>
        </form>
        <div class="m-ok" id="mOk" hidden></div>
      </div>
      <div>
        <span class="eye">How it works</span>
        <h2>Billed after the work, <em>never before</em></h2>
        <ol class="steps">{steps_list}</ol>
        <p class="m-terms" id="mTerms" hidden></p>
      </div>
    </div>
  </section>
  </div>
  <script>{js}</script>
"""
    return shell(up, title, desc, url, ld, main, f'{up}#book', "Hi AnointedSuds, I'd like to sign up for a monthly membership. Tail number: ", quote=False)

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
    write(ROOT / 'membership' / 'index.html', membership_page())
    urls = ([SITE + '/', SITE + '/services/'] + [f"{SITE}/services/{s['slug']}/" for s in SERVICES] + [SITE + '/about/', SITE + '/membership/']
            + [f"{SITE}/aircraft-detailing/{a['slug']}/" for a in AIRPORTS])
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    print(f'{len(AIRPORTS)} airport pages, {len(SERVICES)} service pages + services index, about page, membership page, sitemap.xml, robots.txt')

if __name__ == '__main__':
    main()
