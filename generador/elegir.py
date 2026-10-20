#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copia a img/ las fotos elegidas a mano tras mirar las hojas de contacto.
El tamaño se le PIDE A LA API (iiurlwidth); manipular la url del thumb a mano
no funciona y dejaba fotos de 1280 px donde el original tenía 13.000.
Deja el título, autor y licencia en datos-fuente/creditos.json: son CC BY / BY-SA
y hay que citarlas."""
import json, os, subprocess, time, urllib.parse
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UA = 'guia-viaje-copenhague/1.0 (uso personal)'

# destino -> (fichero de candidatos, clave, índice elegido, ancho que se pide)
ELEGIDAS = {
 # oct-2026, tras mirar las hojas de contacto de fotos1.json (fotos-candidatas.py)
 # 20-oct-2026: Adil eligió él mismo Nyhavn al atardecer (no estaba entre las candidatas:
 # va por título directo; antes, Nyhavn a pleno sol = fotos1 nyhavn 6)
 'portada-hero': ('File:2018 - Nyhavn on sunset.jpg', None, None, 2400),
 'tivoli':       ('fotos1.json', 'tivoli',         8, 1600),  # el árbol grande y el arco, de noche
 'indre':        ('fotos1.json', 'navidad',        0, 1600),  # d'Angleterre con su decoración, Kongens Nytorv
 'nyhavn':       ('fotos1.json', 'nyhavn',        13, 1600),
 'christianshavn':('fotos1.json', 'christiania',   3, 1600),
 'vesterbro':    ('fotos1.json', 'kodbyen',        5, 1600),
 'norrebro':     ('fotos1.json', 'superkilen',     6, 1600),
 'torvehallerne':('fotos1.json', 'torvehallerne', 11, 1600),  # con nieve, febrero de 2026
 'rosenborg':    ('fotos1.json', 'rosenborg',      9, 1600),
}

def thumb(titulo, ancho):
    """URL del thumb del ancho pedido (o del original si es más pequeño)."""
    cmd = ['curl','-s','--max-time','30','-G','https://commons.wikimedia.org/w/api.php','-A',UA,
           '--data-urlencode','action=query','--data-urlencode','titles='+titulo,
           '--data-urlencode','prop=imageinfo','--data-urlencode','iiprop=url|size|extmetadata',
           '--data-urlencode','iiurlwidth=%d' % ancho,'--data-urlencode','format=json']
    # la API corta cuando se le piden varias seguidas y devuelve texto plano:
    # sin esto, el script moría con un JSONDecodeError sin explicar nada
    for intento in range(4):
        salida = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            d = json.loads(salida or '{}')
            break
        except Exception:
            print('    ↻ la API ha cortado, espero (%d/4)' % (intento + 1))
            time.sleep(20 * (intento + 1))
    else:
        raise RuntimeError('Wikimedia no responde para ' + titulo)
    p = list(d.get('query', {}).get('pages', {}).values())[0]
    i = p['imageinfo'][0]
    m = i.get('extmetadata', {})
    return (i.get('thumburl') or i['url'], i['width'],
            m.get('LicenseShortName', {}).get('value', '?'),
            m.get('Artist', {}).get('value', ''))

import re, time as _t
from PIL import Image

def baja(url, ruta, intentos=3):
    """Descarga comprobando que lo que llega ES una imagen: Wikimedia devuelve
    una página de error HTML de 2 KB cuando corta, y eso pasaba desapercibido."""
    for i in range(intentos):
        subprocess.run(['curl','-sL','--max-time','90','-A',UA,'-o',ruta,url], check=False)
        with open(ruta,'rb') as f:
            cabecera = f.read(3)
        if cabecera == b'\xff\xd8\xff':
            return
        print('    ↻ %s: no ha llegado una imagen, reintento %d/%d' % (ruta, i+1, intentos))
        _t.sleep(15 * (i + 1))
    raise RuntimeError('no he podido bajar ' + url)

def encoge(ruta, ancho_max):
    """Las fotos van a mirarse en un móvil: 1,9 MB por foto no tienen sentido."""
    im = Image.open(ruta)
    if im.width > ancho_max:
        im = im.resize((ancho_max, round(im.height * ancho_max / im.width)), Image.LANCZOS)
    im.convert('RGB').save(ruta, 'JPEG', quality=82, optimize=True, progressive=True)
    return im.size

# con argumentos solo se bajan esas (p. ej. `elegir.py portada-hero`) y se
# conservan los créditos de las demás
import sys
SOLO = sys.argv[1:]
RUTA_CRED = 'generador/datos-fuente/creditos.json'
creditos = json.load(open(RUTA_CRED)) if SOLO and os.path.exists(RUTA_CRED) else {}
for destino, (fich, clave, idx, ancho) in ELEGIDAS.items():
    if SOLO and destino not in SOLO: continue
    c = ({'t': fich} if fich.startswith('File:')
         else json.load(open('generador/datos-fuente/' + fich))[clave][idx])
    url, ancho_original, lic, autor = thumb(c['t'], ancho)
    ruta = 'img/%s.jpg' % destino
    baja(url, ruta)
    autor = re.sub(r'<[^>]+>', '', autor).strip()[:60]
    creditos[destino] = {'titulo': c['t'][5:], 'licencia': lic, 'autor': autor,
                         'pagina': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(c['t'].replace(' ', '_'))}
    w, h = encoge(ruta, ancho)
    forma = 'apaisada' if w > h * 1.15 else ('VERTICAL: se recorta fatal en el banner' if h > w else 'cuadrada')
    print('  %-16s %6d KB  %dx%d  %s  [%s]' %
          (destino, os.path.getsize(ruta)//1024, w, h, forma, lic))
    time.sleep(4)
json.dump(creditos, open(RUTA_CRED,'w'), ensure_ascii=False, indent=1)
print('\nCréditos en generador/datos-fuente/creditos.json')
