"""Zmenší obrázky z handoff/assets na max. 1920 px a uloží WebP (+ 960px varianta) a JPG/PNG fallback do docs/assets."""
import glob, json, os
from PIL import Image

SRC, DST, MAXW = 'handoff/assets', 'docs/assets', 1920
meta = {}
for f in sorted(glob.glob(f'{SRC}/**/*.*', recursive=True)):
    rel = os.path.relpath(f, SRC)
    base = os.path.splitext(rel)[0]
    im = Image.open(f)
    alpha = im.mode in ('RGBA', 'LA') and im.getchannel('A').getextrema()[0] < 255
    im = im.convert('RGBA' if alpha else 'RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(f'{DST}/{base}'), exist_ok=True)
    im.save(f'{DST}/{base}.webp', 'WEBP', quality=80, method=6)
    fb = f'{base}.png' if alpha else f'{base}.jpg'
    if alpha:
        im.save(f'{DST}/{fb}', 'PNG', optimize=True)
    else:
        im.save(f'{DST}/{fb}', 'JPEG', quality=80, optimize=True, progressive=True)
    meta[rel] = {'webp': f'assets/{base}.webp', 'fallback': f'assets/{fb}', 'w': im.width, 'h': im.height}
    if im.width > 1000:  # menší varianta pro mobily (srcset)
        im.resize((960, round(im.height * 960 / im.width)), Image.LANCZOS).save(f'{DST}/{base}-960.webp', 'WEBP', quality=80, method=6)
        meta[rel]['webp960'] = f'assets/{base}-960.webp'
    print(rel, im.size, 'alpha' if alpha else '')
json.dump(meta, open('images.json', 'w'), indent=1)
