#!/usr/bin/env python3
"""Monta index.html juntando las piezas de generador/plantilla/ (Copenhague, oct-2026):
 - cada zona (plantilla/zonas/<z>.html) con sus huecos {{VER}} {{COMER}} {{TIENDAS}}
   rellenos con lo que deja construir.py
 - #comer con la leyenda, las tablas de quién abre, «qué probar» y las panaderías
 - los créditos de las fotos en el pie, leídos de datos-fuente/creditos*.json"""
import json, re, os
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
P = 'generador/plantilla/'
ZONAS = ['indre', 'nyhavn', 'christianshavn', 'vesterbro', 'norrebro', 'excursiones']
lee = lambda f: open(P + f).read() if os.path.exists(P + f) else ''

def zona(z):
    s = lee('zonas/%s.html' % z)
    for hueco, f in (('{{VER}}', '-ver'), ('{{COMER}}', '-comer'), ('{{TIENDAS}}', '-tiendas')):
        assert hueco in s, 'falta %s en %s' % (hueco, z)
        s = s.replace(hueco, lee('zonas/%s%s.html' % (z, f)))
    return s

comer = lee('d3-comer.html')
for hueco, pieza in (('{{LEYENDA}}', 'comer/leyenda.html'), ('{{ABRE}}', 'e-abre.html'),
                     ('{{PROBAR}}', 'e-probar.html'), ('{{PAN}}', 'e-pan.html')):
    assert hueco in comer, 'falta ' + hueco
    comer = comer.replace(hueco, lee(pieza))
comer = comer.replace('{{ABREPAN}}', lee('e-abre-pan.html'))

hoteles = lee('d1-hoteles.html').replace('{{TABLA}}', lee('d1-tabla-hoteles.html'))

partes = [lee('head-nuevo.html'), lee('css-base.html'), lee('css-cph.html'),
          lee('c1-cabecera.html'), lee('c2-navidad.html'), lee('d0-tiempo.html'), lee('c3-mapa.html')]
partes += [zona(z) for z in ZONAS]
partes += [comer, lee('d4-tiendas.html'), hoteles, lee('d5-transporte.html'), lee('d6-practico.html').replace('{{PRACTICO_EXTRA}}', lee('d6-extra.html')),
           lee('d7-offline.html'), lee('d8-footer.html'), lee('js-tiempo.html'), lee('3-scripts.html')]
html = ''.join(partes)
assert '{{' not in html, 'queda un hueco sin rellenar: ' + html[html.index('{{'):html.index('{{') + 30]

# --- créditos de las fotos
c = {}
for f, pref in (('creditos.json', ''), ('creditos-platos.json', 'plato-')):
    ruta = 'generador/datos-fuente/' + f
    if os.path.exists(ruta):
        c.update({pref + k: v for k, v in json.load(open(ruta)).items()})
lis = '\n'.join(
    '    <li><a href="%s" target="_blank" rel="noopener">%s</a> · %s%s</li>'
    % (v['pagina'], v['titulo'], v['licencia'], (' · ' + v['autor']) if v.get('autor') else '')
    for v in c.values())
html, n = re.subn(r'(<ul id="creditos-fotos">)\s*(</ul>)', r'\1\n%s\n    \2' % lis.replace('\\', '\\\\'), html, count=1)
assert n == 1, 'no encontré dónde poner los créditos de las fotos'

html = html.replace('</style>\n<body>', '</style>\n</head>\n<body>', 1)
if not html.rstrip().endswith('</html>'):
    html = html.rstrip() + '\n</html>\n'
open('index.html', 'w').write(html)
print('index.html montado: %d KB · %d fichas · %d planes · %d hoteles · créditos de %d fotos'
      % (len(html) // 1024, html.count('<li><span class="nombre">'), html.count('class="dia plan-card"'),
         html.count('class="hotel"'), len(c)))
