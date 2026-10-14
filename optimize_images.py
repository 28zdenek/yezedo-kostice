"""Zmenší obrázky z handoff/assets na max. 1920 px a uloží WebP (+ menší varianty 960 a 1280 px pro srcset) a JPG/PNG fallback do docs/assets."""
import glob, json, os
from PIL import Image

SRC, DST, MAXW = 'handoff/assets', 'docs/assets', 1920
Q = 75  # WebP; u vizualizací rozdíl proti 80 okem nepoznat, data o pětinu menší
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
    im.save(f'{DST}/{base}.webp', 'WEBP', quality=Q, method=6)
    fb = f'{base}.png' if alpha else f'{base}.jpg'
    if alpha:
        im.save(f'{DST}/{fb}', 'PNG', optimize=True)
    else:
        im.save(f'{DST}/{fb}', 'JPEG', quality=80, optimize=True, progressive=True)
    meta[rel] = {'webp': f'assets/{base}.webp', 'fallback': f'assets/{fb}', 'w': im.width, 'h': im.height}
    # menší varianty pro srcset: 960 pro malé displeje, 1280 pro telefony s hustým displejem (390 px × 3)
    for w in (960, 1280):
        if im.width > w + 100:
            im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f'{DST}/{base}-{w}.webp', 'WEBP', quality=Q, method=6)
            meta[rel]['webp%d' % w] = f'assets/{base}-{w}.webp'
    print(rel, im.size, 'alpha' if alpha else '')
json.dump(meta, open('images.json', 'w'), indent=1)
