"""Web copies for the Kybele page: python3 tools/build_img.py

Needs Pillow, numpy and python-pptx; LibreOffice (soffice) unpacks the monthly renders, which
the presentation keeps inside a WMF picture. The originals (the .pptx and the PNG exports in the
repository root) are never changed; everything is written to img/.

  name.webp     shown on the page        name-l.webp   opened when a picture is clicked
  name-n.webp   the Night copy (light ink instead of dark), for pictures made on white paper
"""
import base64, glob, hashlib, io, os, re, subprocess, tempfile
import numpy as np
from PIL import Image
from pptx import Presentation

Image.MAX_IMAGE_PIXELS = None
OUT = "img"
os.makedirs(OUT, exist_ok=True)
PPTX = "Simulation for Food_v3.pptx"
INK, INK_N = np.array([17, 17, 17.]), np.array([241, 239, 234.])


def save(im, name, s=720, l=1600, q=82):
    for tag, w in (("", s), ("-l", l)):
        if not w: continue
        c = im
        if c.width > w: c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
        c.save(f"{OUT}/{name}{tag}.webp", "WEBP", quality=q, method=6)


def paper(im, ink):
    """White paper to transparency; greys and lines become ink, colours stay as they are."""
    a = np.asarray(im.convert("RGBA")).astype(float)
    rgb, a0 = a[..., :3], a[..., 3:] / 255
    sat = rgb.max(2, keepdims=True) - rgb.min(2, keepdims=True)
    w = np.clip((sat - 5) / 8, 0, 1)
    an = np.clip((255 - rgb.mean(2, keepdims=True)) / (255 - 17), 0, 1)
    alpha = w + (1 - w) * an
    col = (w * rgb + (1 - w) * an * ink) / np.maximum(alpha, 1e-6)
    out = np.concatenate([np.clip(col, 0, 255), np.clip(alpha * a0 * 255, 0, 255)], 2)
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def save_paper(im, name, **kw):
    save(paper(im, INK), name, **kw); save(paper(im, INK_N), name + "-n", **kw)


def canvas_night(im, r=3, strip=1200):
    """Grasshopper canvas on transparency: titles, notes and wires drawn straight on the canvas
    (dark, grey, with transparency close by) turn light for Night; components keep their colours.
    Worked in strips so the large copy fits in memory."""
    from PIL import ImageFilter
    out = im.copy()
    for y0 in range(0, im.height, strip):
        y1 = min(im.height, y0 + strip); p0, p1 = max(0, y0 - r), min(im.height, y1 + r)
        a = np.asarray(im.crop((0, p0, im.width, p1))).astype(np.float32)
        rgb, al = a[..., :3], a[..., 3]
        clear = Image.fromarray(((al < 30) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))
        near = np.asarray(clear) > 0
        sat = rgb.max(2) - rgb.min(2); L = rgb.mean(2)
        m = near & (sat < 30) & (L < 200)
        rgb[m] = 255 - rgb[m] * 0.55
        a = a[y0 - p0: y0 - p0 + (y1 - y0)]
        out.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), (0, y0))
    return out


# pictures inside the presentation, by content hash
blobs, wmf = {}, None
def walk(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from walk(sh.shapes)
        else: yield sh
for slide in Presentation(PPTX).slides:
    for sh in walk(slide.shapes):
        if sh.shape_type == 13:
            blobs[hashlib.md5(sh.image.blob).hexdigest()[:6]] = sh.image
def pic(h): return Image.open(io.BytesIO(blobs[h].blob))
by_ext = {}
for h, b in blobs.items(): by_ext.setdefault(b.ext, []).append(h)

# the logo, grey and orange (the version in the presentation)
logo = pic("5a3d75").convert("RGBA")
save(logo.crop(logo.getbbox()), "kybele-logo", s=900, l=None, q=88)
logo.crop(logo.getbbox()).resize((180, round(180 * logo.getbbox()[3] / logo.getbbox()[2])) if False else (192, 192), Image.LANCZOS).save(f"{OUT}/icon.png")

# the three photobiological responses
for i, h in enumerate(("s2_5", "s2_6", "s2_7")):
    pass
icons = [h for h, b in blobs.items() if b.size == (384, 384)]
# keep slide order: photosynthesis, photomorphogenesis, photoperiod
order = []
for slide in list(Presentation(PPTX).slides)[1:2]:
    for sh in walk(slide.shapes):
        if sh.shape_type == 13: order.append(hashlib.md5(sh.image.blob).hexdigest()[:6])
for i, h in enumerate(order, 1):
    save(pic(h).convert("RGBA"), f"response-{i}", s=192, l=None, q=90)

# annual heat maps (slides 6 and 7)
pngs = {b.size: h for h, b in blobs.items() if b.ext == "png"}
save_paper(pic(pngs[(1620, 720)]), "heat-ppfd", s=1100, l=1620)
save_paper(pic(pngs[(1433, 444)]), "heat-dli", s=1100, l=1433)

# monthly renders at noon on the 21st (slide 5, a WMF picture holding 12 renders and a scale)
wmf_h = by_ext["wmf"][0]
with tempfile.TemporaryDirectory() as d:
    open(f"{d}/m.wmf", "wb").write(blobs[wmf_h].blob)
    subprocess.run(["soffice", "--headless", "--convert-to", "svg", "m.wmf"], cwd=d, check=True, capture_output=True)
    svg = open(f"{d}/m.svg").read()
ims = re.findall(r'<image x="(\d+)" y="(\d+)"[^>]*xlink:href="data:image/png;base64,([^"]+)"', svg)
ims = [(int(y), int(x), b) for x, y, b in ims]
renders = sorted([t for t in ims if t[0] < 23000])
for k, (y, x, b) in enumerate(renders, 1):
    save(Image.open(io.BytesIO(base64.b64decode(b))).convert("RGB"), f"month-{k:02d}", s=462, l=None, q=84)

# the case study model
cs = Image.open("case study UW.png").convert("RGBA")
save_paper(cs, "case-study", s=1100, l=2020)

# the two Grasshopper definitions, in black and white (grey components, ink and paper)
for src, name in (("Three_channelworkflow.png", "workflow-three-channel"), ("hyperspectral_workflow.png", "workflow-hyperspectral")):
    im = Image.open(src).convert("RGBA")
    im = im.crop(im.getbbox())
    gray = im.convert("LA").convert("RGBA")
    gray.putalpha(im.getchannel("A")); im = gray; del gray
    sizes = {w: im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) for w in (1400, 9000)}
    del im
    for tag, w in (("", 1400), ("-l", 9000)):
        c = sizes[w]
        c.save(f"{OUT}/{name}{tag}.webp", "WEBP", quality=80, method=4)
        canvas_night(c, 2 if tag == "" else 4).save(f"{OUT}/{name}-n{tag}.webp", "WEBP", quality=80, method=4)
print("done", len(os.listdir(OUT)), "files")
