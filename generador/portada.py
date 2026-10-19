"""Genera img/portada.jpg (1200x630, Open Graph) y los iconos de la PWA."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = 'img/portada-hero.jpg'
import os
def fuente(*rutas):
    return next(r for r in rutas if os.path.exists(r))
# en el Mac, Georgia y Arial; en Ubuntu (donde nació la guía), DejaVu
SERIF  = fuente('/System/Library/Fonts/Supplemental/Georgia.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
SANS_B = fuente('/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')

# ---------- portada 1200x630 ----------
W, H = 1200, 630
im = Image.open(BASE).convert('RGB')
r = max(W/im.width, H/im.height)
im = im.resize((round(im.width*r), round(im.height*r)), Image.LANCZOS)
im = im.crop(((im.width-W)//2, (im.height-H)//3, (im.width-W)//2+W, (im.height-H)//3+H))

# degradado oscuro de abajo arriba, para que se lea el texto
grad = Image.new('L', (1, H))
for y in range(H):
    t = y / H
    # la foto de la fuente es clara (sep-2026): el degradado empieza antes y aprieta más
    grad.putpixel((0, y), int(15 + 225 * max(0, (t-0.2)/0.8) ** 1.1))
capa = Image.new('RGB', (W, H), (12, 20, 34))
im = Image.composite(capa, im, grad.resize((W, H)))

d = ImageDraw.Draw(im)
def texto(xy, t, font, fill):
    # sombra debajo, para que se lea también donde la foto es clara
    for dx, dy in ((2, 2), (1, 1), (0, 2)):
        d.text((xy[0]+dx, xy[1]+dy), t, font=font, fill=(10, 8, 12))
    d.text(xy, t, font=font, fill=fill)
texto((64, 372), 'PARA ALICIA Y LUIS · DEL 4 AL 8 DE DICIEMBRE',
       font=ImageFont.truetype(SANS_B, 22), fill=(230, 236, 244))
texto((60, 414), 'Copenhague en Navidad',
       font=ImageFont.truetype(SERIF, 76), fill='white')
texto((64, 522), 'Tivoli, smørrebrød, kanelsnegle y tiendas raras',
       font=ImageFont.truetype(SERIF, 33), fill=(232, 236, 242))
im.save('img/portada.jpg', quality=90, optimize=True)
print('img/portada.jpg', im.size)

# ---------- iconos 192 / 512 ----------
for lado in (192, 512):
    base = Image.open(BASE).convert('RGB')
    r = max(lado/base.width, lado/base.height)
    b = base.resize((round(base.width*r), round(base.height*r)), Image.LANCZOS)
    b = b.crop(((b.width-lado)//2, 0, (b.width-lado)//2+lado, lado))
    # banda inferior con el nombre
    d = ImageDraw.Draw(b, 'RGBA')
    alto = int(lado*0.30)
    d.rectangle([0, lado-alto, lado, lado], fill=(179, 18, 46, 236))
    f = ImageFont.truetype(SANS_B, int(lado*0.125))
    txt = 'KBH'
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=f)
    d.text(((lado-(x1-x0))//2 - x0, lado-alto + (alto-(y1-y0))//2 - y0), txt, font=f, fill='white')
    b.save(f'img/icono-{lado}.png')
    print(f'img/icono-{lado}.png', b.size)
