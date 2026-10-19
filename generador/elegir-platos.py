#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baja a img/platos/ la foto elegida de cada plato de «Qué hay que probar» (sep-2026),
tras mirar las hojas de contacto de fotos-platos.json. Reutiliza thumb/baja/encoge de
elegir.py sin ejecutarlo. Créditos en datos-fuente/creditos-platos.json (montar.py los
pone en el pie, junto a los de las demás fotos)."""
import json, os, re, sys, time, urllib.parse
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
# funciones de elegir.py, sin disparar su bucle de descargas
fuente = open('generador/elegir.py').read().split('creditos = {}')[0].split('# con argumentos')[0]
exec(fuente)

# plato -> (clave en fotos-platos.json, índice elegido en su hoja de contacto, texto alternativo)
# Copenhague, oct-2026. Sin foto (ninguna candidata era el plato de verdad): stegt flæsk,
# tarteletter, julefrokost, fransk hotdog y Carlsberg (la rødkål sale del plato de flæskesteg de la hoja de brunede kartofler)
PLATOS = {
 'smorrebrod':        ('smorrebrod', 5, 'Varios smørrebrød en una bandeja: huevo y caviar, salmón, queso y tomate'),
 'stjerneskud':       ('stjerneskud', 0, 'Stjerneskud: filetes de platija rebozados con gambas, caviar y limón'),
 'dyrlaegens-natmad': ('dyrlaegens-natmad', 0, 'Dyrlægens natmad: ternera en salazón con aros de cebolla y eneldo sobre paté'),
 'aeg-og-rejer':      ('aeg-og-rejer', 0, 'Bandeja de smørrebrød con medios huevos y gambas, caballa y paté'),
 'rullepolse':        ('rullepolse', 4, 'Smørrebrød de rullepølse con aros de cebolla, pepino y gelatina'),
 'sild':              ('sild', 0, 'Arenques marinados cortados en una fuente, con aros de cebolla'),
 'leverpostej':       ('leverpostej', 5, 'Leverpostej untado sobre pan de centeno con una rodaja de remolacha'),
 'frikadeller':       ('frikadeller', 13, 'Frikadeller con patatas cocidas, salsa marrón y ensalada'),
 'flaeskesteg':       ('flaeskesteg', 0, 'Flæskesteg recién sacado del horno, con la corteza crujiente cortada en tiras'),
 'biksemad':          ('biksemad', 9, 'Biksemad: picadillo de carne y patata con huevo frito y remolacha'),
 'rod-polse':         ('ristet-hotdog', 6, 'Dos platos de røde pølser con pan y kétchup en un banco de la calle'),
 'ristet-hotdog':     ('ristet-hotdog', 4, 'Ristet hotdog con cebolla frita, pepinillos en rodajas, mostaza y remulada'),
 'aebleskiver':       ('aebleskiver', 3, 'Æbleskiver en un cuenco de papel con mermelada roja'),
 'risalamande':       ('risalamande', 3, 'Risalamande con salsa de cerezas en un cuenco de cristal'),
 'juleol':            ('juleol', 7, 'Una juleøl, cerveza de Navidad, servida en vaso junto a su botella'),
 'brunede-kartofler': ('brunede-kartofler', 0, 'Una fuente de brunede kartofler, patatitas caramelizadas, en una mesa de Navidad'),
 'rodkal':            ('brunede-kartofler', 6, 'Plato de flæskesteg con rødkål (lombarda), patatas cocidas y patatas caramelizadas'),
 'kanelsnegl':        ('kanelsnegl', 4, 'Un kanelsnegl, caracola de canela con su glaseado blanco, en un plato'),
 'wienerbrod':        ('wienerbrod', 1, 'Bandejas de wienerbrød surtido: caracolas de canela y pastas de crema y fruta'),
 'flodebolle':        ('flodebolle', 11, 'Una flødebolle bañada en chocolate con virutas de frambuesa'),
 'kardemommebolle':   ('kardemommebolle', 1, 'Bollos de cardamomo trenzados en una cesta con paño de cuadros rojos'),
 'hindbaersnitte':    ('hindbaersnitte', 5, 'Dos hindbærsnitter con glaseado blanco y virutas de colores en un plato'),
 'sportskage':        ('sportskage', 13, 'Dos sportskager enteras en el escaparate de La Glace'),
 'rugbrod':           ('rugbrod', 10, 'Una hogaza de rugbrød, pan de centeno oscuro con semillas, sobre una tabla'),
 'akvavit':           ('akvavit', 5, 'Botella de akvavit casero con ramas de eneldo dentro'),
 'gammel-dansk':      ('gammel-dansk', 0, 'Un vasito de Gammel Dansk servido junto a su botellita'),
 'mikkeller':         ('mikkeller', 6, 'La pizarra y los grifos de cerveza del Mikkeller Bar de Copenhague'),
 'glogg':             ('glogg', 6, 'Un vaso de gløgg caliente con su cucharilla'),
}
cand = json.load(open('generador/datos-fuente/fotos-platos.json'))
os.makedirs('img/platos', exist_ok=True)
RUTA = 'generador/datos-fuente/creditos-platos.json'
cred = json.load(open(RUTA)) if os.path.exists(RUTA) else {}
for plato, (clave, idx, alt) in PLATOS.items():
    ruta = 'img/platos/%s.jpg' % plato
    c = cand[clave][idx]
    if os.path.exists(ruta) and cred.get(plato, {}).get('titulo') == c['t'][5:]:
        cred[plato]['alt'] = alt
        continue
    url, _, lic, autor = thumb(c['t'], 800)
    baja(url, ruta)
    w, h = encoge(ruta, 800)
    cred[plato] = {'titulo': c['t'][5:], 'licencia': lic, 'alt': alt,
                   'autor': re.sub(r'<[^>]+>', '', autor).strip()[:60],
                   'pagina': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(c['t'].replace(' ', '_'))}
    print('  %-13s %4d KB  %dx%d  [%s]' % (plato, os.path.getsize(ruta)//1024, w, h, lic))
    json.dump(cred, open(RUTA, 'w'), ensure_ascii=False, indent=1)
    time.sleep(3)
json.dump(cred, open(RUTA, 'w'), ensure_ascii=False, indent=1)
