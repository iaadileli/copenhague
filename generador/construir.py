#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye las piezas de Copenhague a partir de la investigación (oct-2026).

Fuente única: generador/datos-fuente/investigacion/*.json (lo que salió de buscar en la
web, con sus fuentes) + generador/curado.py (mis decisiones: qué entra, en qué zona, con
qué sello y nota). Genera:
  plantilla/zonas/<zona>-ver.html   (planes de la zona)
  plantilla/zonas/<zona>-comer.html (restaurantes, panaderías y cafés de la zona)
  plantilla/zonas/<zona>-tiendas.html
  plantilla/comer/leyenda.html, plantilla/d1-hoteles.html, plantilla/e-tablas.html
  sitios.js (el «¿qué tengo cerca?», con comida, café, tiendas y planes)
Coordenadas: las de la investigación (Nominatim); si faltan, se piden a Nominatim aquí."""
import html, json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curado as C

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
INV = 'generador/datos-fuente/investigacion/'
P = 'generador/plantilla/'
os.makedirs(P + 'zonas', exist_ok=True)
os.makedirs(P + 'comer', exist_ok=True)

def carga(f):
    return json.load(open(INV + f)) if os.path.exists(INV + f) else []

esc = lambda t: html.escape(str(t or ''), quote=False)

# ------------------------------------------------------------------ sellos
SVG = {
 'smorre': '<path d="M3 13.5h18l-1.2 3.2a2 2 0 0 1-1.9 1.3H6.1a2 2 0 0 1-1.9-1.3z"/>'
           '<circle cx="8" cy="10.5" r="2.4"/><circle cx="13" cy="9.6" r="2.4"/><path d="M15.5 11.6l3.5-4 1.3 1.2-2.6 2.8z"/>',
 'pan':    '<path d="M12 3.5a8.5 8.5 0 1 0 8.5 8.5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'
           '<path d="M12 7.5a4.5 4.5 0 1 0 4.5 4.5A2.2 2.2 0 0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>',
 'cafe':   '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2.5 2.5 0 0 1 0 5H16" fill="none" stroke="currentColor" stroke-width="2"/>'
           '<path d="M8 3.5c-.8 1 .8 2 0 3M12 3.5c-.8 1 .8 2 0 3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
 'tienda': '<path d="M5 8h14l-1 13H6z"/><path d="M9 10V6.5a3 3 0 0 1 6 0V10" fill="none" stroke="currentColor" stroke-width="2"/>',
 'pinzas': '<path d="M6 4h12a2 2 0 0 1 2 2v2.5a2 2 0 0 1-2 2h-1.5L12 20l-4.5-9.5H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>',
 'navidad':'<path d="M12 2l4.5 7H14l4 6h-3l3.5 5h-13L9 15H6l4-6H7.5z"/>',
 'plan':   '<path d="M12 22s-7-7.2-7-12.2A7 7 0 0 1 19 9.8C19 14.8 12 22 12 22z"/><circle cx="12" cy="9.8" r="2.6" fill="#fff"/>',
 'leyenda':'<path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3-5.8 3 1.1-6.5L2.6 9.4l6.5-.9z"/>',
 'capricho':'<path d="M6 3h12l4 6-10 12L2 9z"/>',
}
BARATO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round">'
          '<path d="M11.5 2.5H20a1.5 1.5 0 0 1 1.5 1.5v8.5L12 21.5 2.5 12z"/>'
          '<circle cx="17" cy="7" r="1.6" fill="currentColor" stroke="none"/></svg>')
TITULO = {'smorre': 'smørrebrød de los buenos', 'pan': 'panadería o pastelería', 'cafe': 'café de especialidad',
          'tienda': 'tienda curiosa', 'pinzas': 'la tienda de las pinzas', 'navidad': 'cosa de Navidad',
          'plan': 'plan', 'leyenda': 'lleva más de un siglo abierto', 'capricho': 'el capricho del viaje',
          'barato': 'se come por menos de 20 €'}
COLOR = {'smorre': '#1f4b6e', 'pan': '#a8661c', 'cafe': '#6b4a33', 'tienda': '#7a4a86', 'pinzas': '#c2185b',
         'navidad': '#b3122e', 'leyenda': '#8a6a1f', 'capricho': '#4a3f8f', 'barato': '#2f6f8f'}

def cuerpo_sello(k):
    if k == 'barato':
        return BARATO
    return '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">%s</svg>' % SVG[k]

def sello(k):
    return '<span class="sello %s" title="%s">%s</span>' % (k, TITULO[k], cuerpo_sello(k))

NOTA = {3: 'imprescindible', 2: 'muy bueno', 1: 'correcto, o plan B'}
def estrellas(r):
    if not r: return ''
    return ('<span class="nota n%d" title="%d de 3: %s" aria-label="%d de 3 estrellas: %s">%s'
            '<i>%s</i></span>' % (r, r, NOTA[r], r, NOTA[r], '★' * r, '☆' * (3 - r)))

def maps(nombre, direccion):
    q = '%s, %s' % (nombre.split(' (')[0], direccion)
    return 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(q)

# --------------------------------------------------------------- coordenadas
CACHE = 'generador/datos-fuente/coordenadas.json'
coords = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def geo(x):
    if x.get('lat') and x.get('lon'):
        return float(x['lat']), float(x['lon'])
    q = x.get('direccion') or ''
    if q in coords:
        return coords[q]
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'q': q.split(' · ')[0], 'format': 'json', 'limit': 1})
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            url, headers={'User-Agent': 'guia-copenhague/1.0 (uso personal)'}), timeout=20))
        coords[q] = [float(r[0]['lat']), float(r[0]['lon'])] if r else None
    except Exception:
        coords[q] = None
    time.sleep(1.1)
    print('  geo %s → %s' % (q, coords[q]))
    return coords[q]

# ------------------------------------------------------------------- datos
def con_curado(lista, tipo):
    """Aplica curado.py: fuera lo descartado, zona/sellos/nota/textos retocados."""
    out = []
    for x in lista:
        n = x['nombre']
        if n in C.FUERA or (tipo, n) in C.FUERA_TIPO:
            continue
        x = dict(x)
        if isinstance(x.get('horario'), dict):
            x['horario'] = ' · '.join('%s %s' % kv for kv in x['horario'].items())
        x.update(C.RETOQUE.get(n, {}))
        x['_tipo'] = tipo
        x['_zona'] = x.get('_zona') or C.zona(x.get('zona', ''), n)
        if not x['_zona']:
            print('  ¡SIN ZONA!', n, x.get('zona')); continue
        out.append(x)
    return out

REST = con_curado(carga('restaurantes.json'), 'comer')
PAN = con_curado(carga('pan-cafe.json'), 'pan')
TIENDAS = con_curado(carga('tiendas.json'), 'tienda')
PLANES = con_curado(carga('planes.json'), 'plan')
HOTELES = [h for h in carga('hoteles.json') if h['nombre'] not in C.FUERA]

def sellos_de(x):
    if '_sellos' in x:
        return x['_sellos']
    t = x['_tipo']
    if t == 'pan':
        return ['cafe'] if x.get('tipo') == 'cafe' else ['pan']
    if t == 'tienda':
        return ['pinzas'] if x.get('pinzas') else ['tienda']
    if t == 'plan':
        return ['navidad'] if x.get('tipo') == 'navidad' else []
    s = []
    k = x.get('sello')
    if k == 'smorrebrod': s.append('smorre')
    if k == 'julefrokost': s.append('navidad')
    if k == 'capricho': s.append('capricho')
    if x.get('precio', '').strip() == '€': s.append('barato')
    return s

def li_sitio(x):
    """Ficha de comer / panadería / tienda, con el formato que leen el buscador,
    el contador de sitios y el «qué tengo cerca»."""
    nombre = x.get('_nombre') or x['nombre']
    dirx = x.get('_dir') or x.get('direccion', '')
    texto = x.get('_texto') or ' '.join(t for t in [x.get('que_es'), x.get('por_que')] if t)
    pedir = x.get('_pedir') or x.get('que_pedir') or ''
    datos = []
    if x.get('_horario') or x.get('horario'):
        datos.append('🕐 ' + esc(x.get('_horario') or x.get('horario')))
    precio = x.get('_precio') or x.get('precio_txt') or x.get('precio')
    if precio and precio != 'sin confirmar':
        datos.append('💶 ' + esc(precio))
    if x.get('_tipo') == 'comer' and x.get('reservar'):
        datos.append('📞 ' + esc(x['reservar']))
    if x.get('_aviso'):
        datos.append('<b>⚠ %s</b>' % esc(x['_aviso']))
    web = (x.get('web') or '').split(' ')[0]
    h = ['      <li><span class="nombre">%s</span>%s%s — <span class="dir">%s</span> · %s'
         % (esc(nombre), estrellas(x.get('_r', x.get('nota')) if x['_tipo'] in ('comer', 'pan') else 0),
            ''.join(sello(k) for k in sellos_de(x)), esc(dirx), esc(texto))]
    if pedir:
        h.append('        <span class="pedir"><b>%s</b> %s</span>'
                 % ('Pedid' if x['_tipo'] in ('comer', 'pan') else 'Buscad', esc(pedir)))
    h.append('        <span class="datos">%s</span>' % ' · '.join(datos))
    enl = ['<a href="%s" target="_blank" rel="noopener">📍 Maps</a>' % maps(nombre, dirx)]
    if web.startswith('http'):
        enl.append('<a href="%s" target="_blank" rel="noopener">🌐 Web</a>' % esc(web))
    h.append('        ' + ' · '.join(enl) + '</li>')
    return '\n'.join(h)

ORDEN_COMER = lambda x: (-(x.get('_r') or x.get('nota') or 0), x['nombre'])

def bloque(titulo, items, clase='comer', platos=None, intro=None):
    if not items:
        return ''
    h = ['  <div class="%s">' % clase, '    <h3>%s</h3>' % titulo]
    if intro:
        h.append('    <p class="comer-intro">%s</p>' % intro)
    if platos:
        h += ['    <div class="platos">', '      ' + ''.join('<span class="plato">%s</span>' % p for p in platos), '    </div>']
    h.append('    <ul class="sitios">')
    h += [li_sitio(x) for x in items]
    h += ['    </ul>', '  </div>']
    return '\n'.join(h) + '\n'

def plan_html(x):
    tit = esc(x.get('_nombre') or x['nombre'])
    if x.get('nombre_local') and x['nombre_local'] not in x['nombre']:
        tit += ' <i class="local">%s</i>' % esc(x['nombre_local'])
    chip = []
    if x.get('precio_dkk') not in (None, '', 'sin confirmar'):
        p = str(x['precio_dkk'])
        if p == '0': p = 'gratis'
        chip.append(p + ' DKK' if p[:1].isdigit() and 'DKK' not in p else ('gratis' if p == '0' else p))
    if x.get('duracion'):
        chip.append(esc(x['duracion']))
    sell = ''.join(sello(k) for k in sellos_de(x))
    cuerpo = esc(x.get('_texto') or x.get('que_es', ''))
    if x.get('por_que') and not x.get('_texto'):
        cuerpo += ' ' + esc(x['por_que'])
    hor = x.get('_horario') or x.get('horario_dic') or ''
    enl = ['<a href="%s" target="_blank" rel="noopener">📍 Maps</a>' % maps(x['nombre'], x.get('direccion', ''))]
    web = (x.get('web') or '').split(' ')[0]
    if web.startswith('http'):
        enl.append('<a href="%s" target="_blank" rel="noopener">🌐 Web</a>' % esc(web))
    h = ['    <div class="dia plan-card" data-plan="%s"><h4>%s%s <span class="fecha">%s</span></h4>'
         % (esc(x['nombre']), tit, sell, esc(' · '.join(chip)))]
    h.append('      <p>%s</p>' % cuerpo)
    if hor:
        h.append('      <p class="plan-hor sans">🕐 %s</p>' % esc(hor))
    if x.get('_tip'):
        h.append('      <div class="tip">%s</div>' % x['_tip'])
    h.append('      <p class="plan-enl sans">%s</p></div>' % ' · '.join(enl))
    return '\n'.join(h)

# ---------------------------------------------------------- piezas por zona
cuentas = {}
for z in C.ZONAS:
    planes = [x for x in PLANES if x['_zona'] == z]
    planes.sort(key=lambda x: (C.ORDEN_PLAN.get(x['nombre'], 50), x['nombre']))
    ver = '  <h3 class="sub-h">Qué ver y qué hacer</h3>\n  <div class="dias planes">\n%s\n  </div>\n' % \
          '\n'.join(plan_html(x) for x in planes) if planes else ''
    open(P + 'zonas/%s-ver.html' % z, 'w').write(ver)

    rest = sorted([x for x in REST if x['_zona'] == z], key=ORDEN_COMER)
    pan = sorted([x for x in PAN if x['_zona'] == z], key=ORDEN_COMER)
    com = bloque('Dónde comer en %s' % C.ZONAS[z]['corto'], rest, platos=C.ZONAS[z].get('platos'))
    com += bloque('Panaderías, pastelerías y cafés en %s' % C.ZONAS[z]['corto'], pan, clase='comer pan-bloque')
    open(P + 'zonas/%s-comer.html' % z, 'w').write(com)

    tie = [x for x in TIENDAS if x['_zona'] == z]
    tie.sort(key=lambda x: (not x.get('pinzas'), not x.get('destacada'), x['nombre']))
    open(P + 'zonas/%s-tiendas.html' % z, 'w').write(
        bloque('Tiendas curiosas en %s' % C.ZONAS[z]['corto'], tie, clase='comer tiendas-bloque'))
    cuentas[z] = (len(planes), len(rest), len(pan), len(tie))
    print('%-15s planes %2d · comer %2d · pan/café %2d · tiendas %2d' % ((z,) + cuentas[z]))

LEYENDA = ('  <div class="leyenda-sellos">' +
  ''.join('<span><i style="background:%s">%s</i>%s</span>' % (COLOR[k], cuerpo_sello(k), TITULO[k])
          for k in ['smorre', 'pan', 'cafe', 'navidad', 'leyenda', 'barato', 'capricho', 'tienda', 'pinzas']) +
  '<span><b class="nota n3">★★★</b> imprescindible · <b class="nota n2">★★<i>☆</i></b> muy bueno · '
  '<b class="nota n1">★<i>☆☆</i></b> correcto o plan B</span></div>\n')
open(P + 'comer/leyenda.html', 'w').write(LEYENDA)

# --------------------------------------------------------------- sitios.js
ETQ = {z: C.ZONAS[z]['etiqueta'] for z in C.ZONAS}
js, faltan = [], []
for x in REST + PAN + TIENDAS + PLANES:
    if x['_zona'] == 'excursiones':
        continue
    c = geo(x)
    if not c:
        faltan.append(x['nombre']); continue
    s = sellos_de(x)
    cat = {'comer': 'comer', 'pan': 'pan', 'tienda': 'tienda', 'plan': 'plan'}[x['_tipo']]
    js.append({'n': x.get('_nombre') or x['nombre'], 'z': (x.get('_dir') or x.get('direccion', '')).split(',')[0],
               'e': ETQ[x['_zona']], 'c': cat, 's': s[0] if s else '',
               'r': (x.get('_r') or x.get('nota') or 0) if cat in ('comer', 'pan') else 0,
               'la': round(c[0], 6), 'lo': round(c[1], 6), 'ap': 0,
               'q': urllib.parse.quote('%s, %s' % ((x.get('_nombre') or x['nombre']).split(' (')[0],
                                                   x.get('_dir') or x.get('direccion', '')))})
json.dump(coords, open(CACHE, 'w'), ensure_ascii=False, indent=1)
open('sitios.js', 'w').write('const SITIOS=' + json.dumps(js, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('sitios.js · %d sitios con coordenadas%s' % (len(js), (' · SIN COORDENADAS: ' + ', '.join(faltan)) if faltan else ''))

# ---------------------------------------------------------------- hoteles
def hoteles():
    if not HOTELES:
        return
    TRAMO = [('barato', '①  Baratos · hasta 120 € la noche'), ('medio', '②  Precio medio · de 120 a 200 € la noche'),
             ('mejor', '③  Algo mejor · de 200 a 280 € la noche')]
    filas = []
    for clave, tit in TRAMO:
        hs = [h for h in HOTELES if C.tramo(h) == clave]
        hs.sort(key=lambda h: C.precio_num(h))
        if not hs: continue
        filas.append('      <tr class="grupo"><td colspan="5">%s   ·   4 dic → 8 dic</td></tr>' % tit)
        for h in hs:
            r = C.RECO_HOTEL.get(h['nombre'], '')
            bk = ('https://www.booking.com/searchresults.es.html?ss=%s&checkin=2026-12-04&checkout=2026-12-08'
                  '&group_adults=2&no_rooms=1&group_children=0' % urllib.parse.quote(h['nombre'] + ' Copenhague'))
            eur = lambda v: ('%s €' % v) if str(v).replace('.', '').isdigit() else (v or '—')
            noche, total = eur(h.get('precio_noche_eur')), eur(h.get('total_4_noches_eur'))
            fuente = h.get('precio_fuente') or 'orientativo'
            if fuente.startswith('Booking') and '4-8 dic' in fuente:
                fuente = 'Booking con vuestras fechas, consultado el 19 de octubre (cambia a diario)'
            flojo = (' <span class="flojo">Lo flojo: %s</span>' % esc(h['flojo'])) if h.get('flojo') else ''
            filas.append(
                '      <tr><td><a class="hotel" href="%s" target="_blank" rel="noopener">%s</a>%s<br>'
                '<a class="booking" href="%s" target="_blank" rel="noopener">🏨 Booking · 4–8 dic</a></td>'
                '<td class="zona-cell">%s<br><small>%s</small></td>'
                '<td class="precio-cell"><b>%s</b><span class="tot">por noche</span><b>%s</b><span class="tot">las 4 noches</span></td>'
                '<td class="nota-cell">%s</td>'
                '<td>%s%s<br><small class="fuente-precio">Precio: %s</small></td></tr>'
                % (maps(h['nombre'], h.get('direccion', '')), esc(h['nombre']),
                   (' <span class="reco">%s</span>' % r) if r else '', bk,
                   esc(h.get('zona')), esc(h.get('transporte')), esc(noche), esc(total),
                   esc(h.get('nota_media') or ''), esc(h.get('que_tiene')), flojo, esc(fuente)))
    open(P + 'd1-tabla-hoteles.html', 'w').write(
        '  <div class="tabla-wrap">\n    <table class="hoteles h-tarjetas">\n      <thead><tr><th>Hotel</th><th>Zona y transporte</th>'
        '<th>Precio</th><th>Nota</th><th>Qué tiene</th></tr></thead>\n      <tbody>\n%s\n      </tbody>\n    </table>\n  </div>\n'
        % '\n'.join(filas))
    print('d1-tabla-hoteles.html · %d hoteles' % len(HOTELES))
hoteles()

# --------------------------------------------- tabla de quién abre dom / lun
def tabla_abre(items, archivo, titulo_cols, franja=False):
    filas = []
    for x in items:
        if (x.get('_r') or x.get('nota') or 0) < 2 or x['_zona'] == 'excursiones':
            continue
        hs = C.horas(x) if franja else C.abre(x)
        if not hs: continue
        celdas = ''.join('<td class="%s">%s</td>' % ({'sí': 'ab-si', '—': 'ab-no', '?': 'ab-medio'}.get(v, 'ab-medio' if not franja else 'ab-si'), v) for v in hs)
        filas.append('      <tr><td class="ab-n"><a href="#%s">%s</a></td>%s</tr>'
                     % (x['_zona'], esc(x.get('_nombre') or x['nombre']), celdas))
    open(P + archivo, 'w').write(
        '  <div class="tabla-wrap">\n    <table class="hoteles tabla-abre">\n      <thead><tr><th></th>%s</tr></thead>\n'
        '      <tbody>\n%s\n      </tbody>\n    </table>\n  </div>\n' % (''.join('<th>%s</th>' % c for c in titulo_cols), '\n'.join(filas)))
    print('%s · %d filas' % (archivo, len(filas)))
tabla_abre(sorted(REST, key=ORDEN_COMER), 'e-abre.html', ['vie 4', 'sáb 5', 'dom 6', 'lun 7', 'mar 8'])
tabla_abre(sorted(PAN, key=ORDEN_COMER), 'e-abre-pan.html', ['vie 4', 'sáb 5', 'dom 6', 'lun 7', 'mar 8'], franja=True)

# ------------------------------------------------- «qué hay que probar» (#probar)
GRUPOS = [('smorrebrod', 'El smørrebrød y lo que lleva encima', 'Pan de centeno con mantequilla y algo encima, a mediodía, con cuchillo y tenedor.'),
          ('platos', 'Platos daneses de toda la vida', 'Cocina de casa: cerdo, salsas y patatas. La de las abuelas, y la de los kro.'),
          ('navidad', 'Lo de Navidad, que os coincide', 'Solo estas semanas: en mercadillos, en Tivoli y en las mesas de julefrokost.'),
          ('calle', 'En la calle: el pølsevogn', 'El carrito de salchichas es una institución, y lo más barato que vais a comer.'),
          ('dulces', 'Dulces y pan', 'La bollería, con más detalle, en «Panaderías» aquí debajo.'),
          ('bebida', 'Para beber', 'Para acompañar o para brindar.')]
FOTOS_PLATOS = 'generador/datos-fuente/creditos-platos.json'
def probar():
    platos = carga('platos.json')
    fotos = json.load(open(FOTOS_PLATOS)) if os.path.exists(FOTOS_PLATOS) else {}
    h = ['  <h3 class="ir-titulo" id="probar" style="margin-top:30px">Qué hay que probar, y qué es cada cosa</h3>',
         '  <p class="intro">Aquí van <b>%d platos y bebidas</b>, con foto, para que en la carta no haya que '
         'adivinar nada. No hace falta probarlos todos, pero sí saber qué son. Entre paréntesis, dónde '
         'probarlo de entre los sitios de la guía.</p>' % len(platos)]
    for g, tit, sub in GRUPOS:
        de = [p for p in platos if p['grupo'] == g]
        if not de: continue
        h.append('  <h4 class="probar-grupo">%s <span>%s</span></h4>' % (tit, sub))
        h.append('  <div class="probar">')
        for p in de:
            k = p['clave']
            nombre = esc(p['nombre_danes'])
            if p.get('nombre_es') and p['nombre_es'].lower() != p['nombre_danes'].lower():
                nombre += ' <i>(%s)</i>' % esc(p['nombre_es'])
            d = p.get('donde') or []
            d = [x for x in (d if isinstance(d, list) else [d]) if 'sin confirmar' not in x.lower()]
            donde = (' <span class="donde">(%s)</span>' % esc(' · '.join(d))) if d else ''
            txt = '<p><b>%s</b> — %s%s</p>' % (nombre, esc(p['que_es']), donde)
            if k in fotos:
                h.append('    <div class="probar-item"><img src="img/platos/%s.jpg" alt="%s" loading="lazy" '
                         'width="800" height="600">%s</div>' % (k, esc(fotos[k].get('alt') or p['nombre_danes']), txt))
            else:
                h.append('    <div class="probar-item sin-foto">%s</div>' % txt)
        h.append('  </div>')
    open(P + 'e-probar.html', 'w').write('\n'.join(h) + '\n')
    print('e-probar.html · %d platos, %d con foto' % (len(platos), sum(1 for p in platos if p['clave'] in fotos)))
probar()
