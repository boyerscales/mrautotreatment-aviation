#!/usr/bin/env python3
"""Builds assets/airport-map.webp, the real map behind the airport pins on the home page.

    python3 -m venv /tmp/mapenv && /tmp/mapenv/bin/pip install pillow
    /tmp/mapenv/bin/python tools/build_map.py

Stitches OpenStreetMap tiles around the airports, recolors them dark and gold to match
the site, and prints each airport's x/y for CFG.AIRPORTS in index.html (the pin formula
there is left = 6 + x*88 %, top = 8 + y*84 %). The page credits OpenStreetMap on the map.
Re-run it whenever an airport is added or dropped, and paste the new x/y values.
"""
import io, math, pathlib, sys, time, urllib.request
from PIL import Image, ImageChops, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'tools' / '.tiles'
OUT = ROOT / 'assets' / 'airport-map.webp'
Z, W, ASPECT = 11, 1456, 1.12          # .map is aspect-ratio 1.12 in index.html
H = round(W / ASPECT)

# (code, lat, lon), from each field's FAA airport record
AIRPORTS = [
  ('SAC', 38.5125, -121.4935),
  ('MHR', 38.5539, -121.2975),
  ('MCC', 38.6676, -121.4008),
  ('LHM', 38.9092, -121.3513),
  ('AUN', 38.9548, -121.0817),
  ('DWA', 38.5791, -121.8567),
  ('EDU', 38.5315, -121.7864),
]
CITY = ('SACRAMENTO', 38.5816, -121.4944)

def world(lat, lon, z=Z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y

pts = {c: world(la, lo) for c, la, lo in AIRPORTS}
xs, ys = [p[0] for p in pts.values()], [p[1] for p in pts.values()]
# airports fill the middle 78% across, and sit a little low so the pin tags have headroom
span_w = (max(xs) - min(xs)) / .78
span_h = span_w / ASPECT
x0 = (min(xs) + max(xs)) / 2 - span_w / 2
y0 = (min(ys) + max(ys)) / 2 - span_h * .54

tx0, ty0 = int(x0 // 256), int(y0 // 256)
tx1, ty1 = int((x0 + span_w) // 256), int((y0 + span_h) // 256)
CACHE.mkdir(parents=True, exist_ok=True)
sheet = Image.new('RGB', ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        f = CACHE / f'{Z}-{tx}-{ty}.png'
        if not f.exists():
            req = urllib.request.Request(f'https://tile.openstreetmap.org/{Z}/{tx}/{ty}.png',
                                         headers={'User-Agent': 'AnointedSuds site map build (one-off static image)'})
            f.write_bytes(urllib.request.urlopen(req, timeout=20).read())
            time.sleep(.2)
        sheet.paste(Image.open(io.BytesIO(f.read_bytes())).convert('RGB'), ((tx - tx0) * 256, (ty - ty0) * 256))

ox, oy = x0 - tx0 * 256, y0 - ty0 * 256
crop = sheet.crop((round(ox), round(oy), round(ox + span_w), round(oy + span_h))).resize((W, H), Image.LANCZOS)

# Brightness = how far each pixel is from OSM's plain land color, so roads, towns,
# rivers and labels glow faintly and open land goes black.
gray = ImageOps.grayscale(crop)
g = ImageChops.difference(gray, Image.new('L', gray.size, 242)).point(lambda v: min(255, int(v * 2.4)))
img = ImageOps.colorize(g, black=(10, 10, 9), mid=(70, 58, 36), white=(196, 168, 112), midpoint=110)
img.save(OUT, 'WEBP', quality=78, method=6)
print(f'wrote {OUT.relative_to(ROOT)} {W}x{H}, {OUT.stat().st_size // 1024} KB')

def frac(lat, lon):
    x, y = world(lat, lon)
    return (x - x0) / span_w, (y - y0) / span_h

for c, la, lo in AIRPORTS:
    fx, fy = frac(la, lo)
    print(f"{c}: x:{(fx - .06) / .88:.3f}, y:{(fy - .08) / .84:.3f}")
fx, fy = frac(CITY[1], CITY[2])
print(f"{CITY[0]} label at left:{fx * 100:.1f}% top:{fy * 100:.1f}%")
