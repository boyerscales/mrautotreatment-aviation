# Mr. Auto Treatment Aviation website

A separate site for aircraft detailing, sister to mrautotreatment.com. One self-contained
`index.html`, no build step, same setup as the car site.

Everything tweakable is in the `CFG` object near the bottom of the file. Anything
marked `PLACEHOLDER` is a guess.

> **Started 2026-10-05 with no aviation info from him.** Every service, aircraft class,
> airport and line of copy is our draft of a typical aircraft detailing business.
> Nothing claims experience, years, reviews, certifications or insurance. Keep it
> that way until he confirms. Questions to send him are in `OWNER-QUESTIONS.md`.

## Where things came from
- **Logo, phone, email, Instagram, payment types:** copied from his car site
  (`../mrautotreatment`). Real, but confirm he wants the same number and email for aircraft.
- **Design:** the car site's system (Archivo, 2px buttons, thin rules, numbered lists,
  black and gold), plus IBM Plex Mono for airport codes, tail numbers and dimensions.
- **No photos.** We have none of his aircraft work, and stock photos of other people's
  planes would look like his work. The hero is a gold line drawing of a jet seen from
  above instead. It's hand-drawn SVG and not modeled on any one real aircraft. When he
  sends real photos, they can go beside or instead of it.
- **Airports:** public fields around Sacramento. Identifiers are the standard ICAO/FAA
  codes, but which ones he can actually work at is up to him.
- **Aircraft lengths** on the size bars are rough real-world figures for the example
  models, there only to make the bars meaningful.

## The quote form
No backend. It builds a message from the form and opens the customer's texts (on a
phone) or email (on a computer) addressed to him, filled in. Nothing is saved and
nothing sends until the customer presses send in their own app. It does **not** post
to the BoyerScales dashboard. Wire it up later if he wants aviation leads in the
dashboard.

"Add to quote" on each service ticks the matching box in the form.

## Before it goes live
1. He answers `OWNER-QUESTIONS.md`, at least: name, airports, services, aircraft
   sizes, and insurance.
2. **Insurance.** Don't add "licensed and insured" for aircraft until he confirms
   aviation coverage. A car detailing policy usually doesn't cover aircraft, and
   most airports and FBOs want proof of coverage before a vendor works on the field.
3. Domain, then a GitHub repo + Pages like the car site, then a `CNAME`.
4. Remove `<meta name="robots" content="noindex">`.

## Local preview
```
python3 -m http.server 4898
```
