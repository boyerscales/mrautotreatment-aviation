# AnointedSuds Aviation Detailing website

Emmanuel's (Mr. Auto Treatment) aircraft detailing business, its own brand. One
self-contained `index.html`, no build step, same setup as the car site.

Everything tweakable is in the `CFG` object near the bottom of the file. Anything
marked `PLACEHOLDER` is still a guess.

> **Rebuilt 2026-10-07 from his email (2026-10-06).** He asked for:
> - the name **AnointedSuds Aviation Detailing** ("everything is different for this one")
> - the layout and content of https://www.chicagoaircraftdetailers.com/ "pretty much word for word"
> - his logo on the first page, good quality stock images everywhere else
> - online booking with a **deposit required**, same as the car site
> - **no prices anywhere**: he wants people to call
> - a list of airports (he's sending it)

## What we copied from the Chicago site, and what we didn't
We followed its **structure and offer**: hero with a big Call Now, an airports-served
list with a "Book a service" on each, the same three core services (interior,
exterior dry wash, carpet shampoo and extraction) with what's included in each, the
extra services from its footer and About page, its four-step process (access and
badging, arrival photos, the detail, a photo report), a who-we-serve section, and
a booking form that asks for the tail number, airport and takeoff time.

We did **not** paste their text. All the copy is rewritten in our own words, because
lifting another company's site word for word is copyright infringement and Google
treats duplicate text as a reason to rank the copy below the original. We also left
out anything that would be a false claim for him:
- their **client list** (Flexjet, McDonald's, Caterpillar…). Ours lists the *kinds* of
  operators he serves (Part 91, Part 135, FBOs, MROs, GA), which makes no claim.
- their **certifications** (Aviation Detailing Association, System X, Dassault)
- their **testimonial**
- **24/7 on-call** and a **two-hour response window**. Ours says "call, and we'll tell
  you straight away when we can be on the ramp." Swap in his real promise when he gives one.
- **Disinsection**: it's applying insecticide inside an aircraft, which is regulated. Add only if he does it.

## Where things came from
- **Logo:** `aircraft.png` from his email of 2026-10-06 (1254px). Original: `assets/logo-source.png`
  (gitignored). It came on a black square, so it was cut out (2026-10-07): the medallion disc stays
  solid and everything outside it keeps only its own light, so the glow, wing tips and lettering
  float on real transparency. Web copies: `logo-1100.webp` (hero), `logo-560.webp` (finale),
  `logo-180.png` (home-screen icon), `og.jpg` (link previews).
- **Header mark:** `#mark` in the page's SVG sprite, also `assets/mark.svg` (favicon). It's a flat
  redraw of his logo (ring, cross, jet head-on, swoosh) because the full logo is unreadable at 40px.
  The wordmark next to it is live text in Cinzel, the Roman capitals his logo uses.
- **Photos:** Unsplash, free under the Unsplash License (commercial use OK, no credit required),
  loaded from images.unsplash.com in the size each screen needs. No faces.
  - Hero background (jet tail against the sun): https://unsplash.com/photos/silhouette-of-airplane-pz7vx75iMx0
  - Interior: https://unsplash.com/photos/luxurious-interior-of-a-private-jet-with-comfortable-seating-lU1pEjWZzXg
  - Exterior: https://unsplash.com/photos/a-white-private-jet-on-an-airport-runway-A8O5zhN5hF4
  - Carpet: https://unsplash.com/photos/luxurious-interior-of-a-private-jet-with-comfortable-seating-ogUyaf8JWA4
  - Pricing band: https://unsplash.com/photos/airplane-during-golden-hour-r1o0YEBIiEo
  When he sends photos of his own aircraft work, swap them in (`photo` in `CFG.SERVICES`).
- **Matthew 6:33** is on his logo, so it's in About, the footer, and the runway is painted "33".
- **Airports:** 8 public fields around Sacramento until his list arrives (`CFG.AIRPORTS`, with
  rough map positions).

## Design (revised 2026-10-07 after Elijah's review)
- **Modern, not 90s.** No metallic gradient type, no sunburst. Manrope for everything, Instrument
  Serif italic for the gold accent words, IBM Plex Mono for codes and labels, Cinzel only in the
  wordmark. Gold buttons have a soft two-tone fill (the one gradient on the page), a light glint
  that passes every few seconds, lean toward the mouse on desktop, and pop a little burst of
  suds and gold sparks wherever they're tapped.
- **Hero:** the golden-hour photo with his logo sitting on the sun, slow zoom-in on load, moves
  slightly with the mouse, bubbles rising behind the logo.
- **The walkaround (`tour.js`)** is the centerpiece. A business jet built in three.js from code
  (no model file, not any one real aircraft). It draws itself in gold lines nose to tail, like the
  line-drawing jet from the first draft he liked, then a ring of light sweeps down it and it turns
  solid. Scrolling flies the camera through 9 stops, each with a card: overview, nose, windscreen,
  leading edges, **one square foot** (zooms onto the wing: grime wiped off, polish sheen, water
  beads after the coating, with Lift / Polish / Protect filling in), engines, gear, the cabin
  (hull goes x-ray, seats and carpet inside), and a wrap-up with Book and Call. A "Skip the
  walkaround" button is always there, and the stop list on desktop jumps to any stop.
  three.js loads from jsDelivr. With no WebGL, or if it can't load, the stops show as plain cards.
- **Airport map** is flat now, every pin is a real button, and tapping one selects it in the form.

## Phones (checked at 360, 390 and 430 wide)
- Logo, headline and both buttons fit on the first screen.
- Taps are 44px or bigger (Apple's minimum; Google's is 48dp), with 8px or more between them.
- Call / Text / Book bar at thumb height, hidden at the top of the page and while the booking form
  is on screen so it never covers a field.
- Service checklists show 5 items with "Show all"; extra services are a 2-up grid; footer drops the
  link lists.
- Booking asks only name, mobile and tail number up front. Takeoff time, model, email, FBO, extras
  and notes sit behind one "Add … (optional)" toggle.
- In the walkaround the card sits above the phone bar and the aircraft is framed above the card.

## Calls first
He wants calls, so the phone number is in the header (always), the hero, every service
("Call for a quote"), the big pricing band, the booking sidebar ("Need it sooner?"),
the finale, the footer and the phone bar. "Ask about it" on the extra services opens a
pre-filled text.

## Booking
Same code as mrautotreatment.com, pointed at slug **`anointedsuds`**:
`https://dashboard.boyerscales.com/api/public/schedule/anointedsuds`.

**Right now that slug doesn't exist, so the form runs in preview mode:** it shows sample
busy times, nothing saves and nothing is texted. The confirmation says so in small print.

The customer picks a service, aircraft class (piston to large cabin, with silhouettes), an
airport, a day and a time, then gives name, mobile, **tail number** (required), make and
model, takeoff time, email for the photo report, FBO or hangar, extra services and notes.
No price is shown anywhere: the summary says "We call you with a quote".

The dashboard has one notes field (300 characters) and one address field (160), so:
- `address`: airport + FBO/hangar
- `vehicle`: tail number + make and model; `vehicle_size`: aircraft class
- `notes`: tail, model, class, takeoff time, email, extras, "Needs a quote", then the
  customer's own notes last, so they're what gets cut if it runs long

To make it live:
1. **He needs a second dashboard account.** One account holds one booking slug, and his
   `mrautotreatment@gmail.com` account already holds `mrautotreatment`. A new email for
   AnointedSuds (or any other address he owns) works.
2. Run `Dashboards/Client Dash/anointedsuds-booking-setup.sql` after putting that email in it.
3. Connect his Stripe on that account. The site follows the dashboard: deposit `0` →
   "Book my time", nothing due; deposit > 0 → "Hold my time with $X" and straight to
   Stripe checkout. Stripe sends them back with `?deposit=paid` or `?deposit=canceled`,
   which shows a toast.

Test with the network stubbed, never by submitting the live form.

## Before it goes live
1. His airport list → `CFG.AIRPORTS` (with map positions).
2. Phone and email for this business. Both are his car-business ones for now.
3. Deposit amount (`CFG.DEPOSIT.AMOUNT` is what preview shows, $50 placeholder) and the
   amount on the dashboard.
4. Hours: his car hours for now (Mon to Sat, 6am to 6pm). Online booking needs 24 hours'
   notice; anything sooner is a phone call, which is what he wants.
5. **Insurance.** Don't add "insured" until he confirms aviation coverage. Most airports and
   FBOs want proof of it before a vendor works on the field.
6. His About paragraph (marked `PLACEHOLDER` in the HTML).
7. Confirm the four process steps are how he works, especially arrival photos and the
   photo report, since the site promises them.
8. Domain → GitHub Pages + `CNAME`, then remove `<meta name="robots" content="noindex">`.
9. Once he has a domain, the Chicago site's per-airport pages (`/aircraft-detailing-midway`
   etc.) are worth copying as a pattern: one short page per airport ranks for "aircraft
   detailing SAC" style searches.

## Local preview
```
python3 -m http.server 4898
```
