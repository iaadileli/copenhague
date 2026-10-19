import json, subprocess, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
CAND = {}
for f in sys.argv[1:-1]:
    CAND.update(json.load(open(f)))
SALIDA = sys.argv[-1]
os.makedirs('generador/datos-fuente/cand', exist_ok=True)
try: fuente = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.pil', 13)
except Exception:
    try: fuente = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 13)
    except Exception: fuente = ImageFont.load_default()

CELDA, ALTO_TXT = 300, 46
for clave, lista in CAND.items():
    if not lista: continue
    fichas = []
    for n, c in enumerate(lista[:14]):
        ruta = f'generador/datos-fuente/cand/{clave}-{n}.jpg'
        if not os.path.exists(ruta):
            subprocess.run(['curl','-sL','--max-time','40','-o',ruta,c['url']], check=False)
        try:
            im = Image.open(ruta).convert('RGB')
        except Exception:
            continue
        im.thumbnail((CELDA, CELDA))
        fichas.append((n, im, c['t'][5:]))
    if not fichas: continue
    cols = min(3, len(fichas)); filas = (len(fichas)+cols-1)//cols
    hoja = Image.new('RGB', (cols*CELDA, filas*(CELDA+ALTO_TXT)), '#ffffff')
    d = ImageDraw.Draw(hoja)
    for i,(n,im,tit) in enumerate(fichas):
        x, y = (i%cols)*CELDA, (i//cols)*(CELDA+ALTO_TXT)
        hoja.paste(im, (x+(CELDA-im.width)//2, y+(CELDA-im.height)//2))
        d.rectangle([x,y,x+CELDA-1,y+CELDA+ALTO_TXT-1], outline='#cccccc')
        d.text((x+6, y+CELDA+3), f'[{n}] ' + '\n'.join(textwrap.wrap(tit, 40)[:2]), fill='#111111', font=fuente)
    ruta = f'{SALIDA}/hoja-{clave}.jpg'
    hoja.save(ruta, quality=88)
    print(ruta, hoja.size, len(fichas), 'candidatas')
