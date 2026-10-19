# -*- coding: utf-8 -*-
"""Mis decisiones sobre la investigación (19-oct-2026). Lo que sale de la web está en
datos-fuente/investigacion/*.json con sus fuentes; aquí solo se decide qué entra,
dónde va y cómo se marca. Si un dato cambia, se cambia en el JSON, no aquí."""
import re

# id de sección -> textos de la zona
ZONAS = {
 'indre':         {'corto': 'el centro', 'etiqueta': 'el centro (Indre By)',
                   'platos': ['Smørrebrød de mediodía', 'Torvehallerne', 'Hot dog de carrito', 'Kanelsnegl']},
 'nyhavn':        {'corto': 'Nyhavn y Frederiksstaden', 'etiqueta': 'Nyhavn y Frederiksstaden',
                   'platos': ['Smørrebrød junto al canal', 'Gløgg con æbleskiver']},
 'christianshavn':{'corto': 'Christianshavn', 'etiqueta': 'Christianshavn',
                   'platos': ['Julefrokost en un café de canal', 'Cocina nórdica']},
 'vesterbro':     {'corto': 'Vesterbro y Frederiksberg', 'etiqueta': 'Vesterbro y Frederiksberg',
                   'platos': ['Kødbyen de noche', 'Tivoli Food Hall', 'Vino natural']},
 'norrebro':      {'corto': 'Nørrebro y Østerbro', 'etiqueta': 'Nørrebro y Østerbro',
                   'platos': ['Pizza de masa madre', 'Panaderías de barrio', 'Café de especialidad']},
 'excursiones':   {'corto': 'las excursiones', 'etiqueta': 'fuera de la ciudad'},
}

def zona(z, nombre=''):
    z = (z or '').lower()
    if 'excurs' in z or 'helsing' in z or 'humleb' in z or 'roskilde' in z or 'malm' in z or 'klampenborg' in z:
        return 'excursiones'
    if 'slotsholm' in z:                     # antes que «holmen» (Refshaleøen/Holmen)
        return 'indre'
    if 'nyhavn' in z or 'frederiksstad' in z or 'kastellet' in z:
        return 'nyhavn'
    if 'christianshavn' in z or 'refshale' in z or 'holmen' in z or 'amager' in z or 'christiania' in z:
        return 'christianshavn'
    if 'vesterbro' in z or 'frederiksberg' in z or 'kødbyen' in z or 'valby' in z or 'carlsberg' in z:
        return 'vesterbro'
    if 'islands brygge' in z:
        return 'christianshavn'
    if 'nørrebro' in z or 'nordvest' in z or 'østerbro' in z or 'norrebro' in z or 'osterbro' in z:
        return 'norrebro'
    if 'indre' in z or 'slotsholm' in z or 'centro' in z or 'latin' in z or 'strøget' in z:
        return 'indre'
    return None

# Fuera de las fichas: cerrados, dudosos o de solo mención (se nombran en el texto)
FUERA = {
 'Café Halvvejen',      # sin fuente fiable de que siga abierto
 'Gasoline Grill',      # su web marca todos los locales «temporarily closed» (oct-2026)
 'Bageriet BRØD', 'Social Brew', 'Flindt & Ørsted (Ørstedsparken)',   # sin horario confirmado
 # planes que ya van a mano en #navidad, sin confirmar o cerrados en diciembre
 'Navidad en Højbro Plads', 'El Cascanueces del Ballet Real', 'Pista de hielo de Kongens Nytorv',
 'Reffen (comida callejera) — CERRADO en diciembre', 'Mercado de Navidad de Flid (artesanía y diseño)',
 'Noma', 'Alchemist', 'Kadeau Copenhagen', 'Koan',   # alta cocina: solo mención en #comer
}

# fuera solo en una de las listas (el mismo sitio sale en dos y el nombre se repetiría)
FUERA_TIPO = {
 ('tienda', 'Paludan Bog & Café'),   # va como café
 ('tienda', 'Torvehallerne'),        # va en comer
 ('pan', 'Hotel Sanders (lobby y patio)'),   # horario sin confirmar y es un hotel de lujo
}

# retoques puntuales (claves con _ ganan a las de la investigación)
RETOQUE = {
 'Restaurant Schønnemann': {'_sellos': ['smorre', 'leyenda']},
 'Det Lille Apotek':       {'_sellos': ['leyenda']},
 'Café Petersborg':        {'_sellos': ['leyenda']},
 'Restaurant Kronborg':    {'_sellos': ['smorre', 'navidad']},
 'Christianshavns Færgecafé': {'_sellos': ['navidad']},
 'Torvehallerne':          {'_sellos': ['barato']},
 'Hallernes Smørrebrød (Torvehallerne)': {'_sellos': ['smorre', 'barato']},
 'formel B':               {'_sellos': ['capricho']},
 'Jatak':                  {'_sellos': ['capricho']},
 'Pico Copenhagen (tienda original)': {'_nombre': 'Pico Copenhagen', '_sellos': ['pinzas']},
 'Sui Ava Store':          {'_nombre': 'Sui Ava', '_sellos': ['pinzas']},
}

RETOQUE.update({
 'Tivoli en Navidad':               {'_zona': 'vesterbro'},
 'Gliptoteca Ny Carlsberg':         {'_zona': 'vesterbro'},
 'Colección Hirschsprung':          {'_zona': 'indre'},
 'La Ciudadela':                    {'_zona': 'nyhavn'},
 'La Sirenita':                     {'_zona': 'nyhavn'},
 'Paseo clásico por los canales con Strömma': {'_zona': 'nyhavn'},
})

# orden de los planes dentro de cada zona (lo que no está, va detrás por orden alfabético)
ORDEN_PLAN = {n: i for i, n in enumerate([
 'Mercadillo de Navidad de Nytorv y Gammeltorv', 'Strøget y el Barrio Latino', 'Torre Redonda',
 'Castillo de Rosenborg', 'Mercado de Torvehallerne', 'Palacio de Christiansborg', 'Torre de Christiansborg',
 'Museo Nacional', 'Galería Nacional de Dinamarca (SMK)',
 'Nyhavn', 'Paseo en barco por los canales con Netto-Bådene', 'Paseo clásico por los canales con Strömma',
 'Amalienborg (palacio y museo)', 'Iglesia de Mármol (Frederiks Kirke)', 'Museo del Diseño de Dinamarca',
 'La Ciudadela', 'La Sirenita',
 'Torre de la Iglesia de Nuestro Salvador', 'Christiania',
 'Tivoli en Navidad', 'Gliptoteca Ny Carlsberg', 'Kødbyen, el antiguo barrio del matadero',
 'Cementerio de Assistens', 'Superkilen',
 'Museo Louisiana de Arte Moderno', 'Castillo de Kronborg (el castillo de Hamlet)',
])}

# ------------------------------------------------------------------ hoteles
def precio_num(h):
    m = re.findall(r'\d+', str(h.get('precio_noche_eur') or ''))
    return int(m[0]) if m else 999

def tramo(h):
    t = (h.get('tramo') or '').lower()
    if 'barat' in t: return 'barato'
    if 'medio' in t: return 'medio'
    if 'mejor' in t or 'alto' in t: return 'mejor'
    n = precio_num(h)
    return 'barato' if n <= 120 else ('medio' if n <= 200 else 'mejor')

# mis tres recomendadas (★): buena nota, bien comunicadas y sin pasarse de precio
RECO_HOTEL = {
 'Next House Copenhagen': '★ el que yo cogería',
 'Wakeup Copenhagen – Borgergade': '★ el más céntrico por su precio',
 'Ibsens Hotel': '★ con encanto',
}

# ------------------------------------------- quién abre (vie, sáb, dom, lun, mar)
DIAS = ['vie', 'sáb', 'dom', 'lun', 'mar']
def _dia(h, d):
    m = re.search(r'\b%s\b\s*([^·]*)' % d, h)
    return m.group(1).strip() if m else None

def horas(x):
    """Para panaderías: la franja de cada día, compacta («7–18»), o «—» si cierra."""
    h = x.get('horario') or ''
    out = []
    for d in DIAS:
        t = _dia(h, d)
        if t is None:
            return None
        t = re.sub(r'^\d+\s+', '', t)          # «4 08:00–18:00» → «08:00–18:00»
        if t.lower().startswith('cerrad'):
            out.append('—'); continue
        m = re.match(r'0?(\d{1,2})(?::(\d\d))?\s*[-–]\s*0?(\d{1,2})(?::(\d\d))?', t)
        if not m:
            out.append('?'); continue
        a = m.group(1) + ((':' + m.group(2)) if m.group(2) and m.group(2) != '00' else '')
        b = m.group(3) + ((':' + m.group(4)) if m.group(4) and m.group(4) != '00' else '')
        out.append('%s–%s' % (a, '24' if b == '0' else b))
    return out

def abre(x):
    """De «vie 11:30-17 · sáb … · dom cerrado …» saca sí / mediodía / noche / —."""
    h = x.get('horario') or ''
    out = []
    for d in DIAS:
        t = _dia(h, d)
        if t is None:
            return None
        t = re.sub(r'^\d+\s+', '', t)
        if t.lower().startswith('cerrad'):
            out.append('—'); continue
        t = re.sub(r'\([^)]*\)?', '', t)       # fuera los paréntesis (cocina, notas)
        tramos = [(int(a), int(b)) for a, b in re.findall(r'(\d{1,2})(?::\d\d)?\s*[-–]\s*~?(\d{1,2})', t)]
        tramos += [(int(a), 24) for a in re.findall(r'desde\s+las?\s*(\d{1,2})|desde\s+(\d{1,2})', t) for a in a if a]
        if not tramos:
            out.append('?'); continue
        tarde = any(a >= 17 for a, b in tramos)
        dia = [(a, b) for a, b in tramos if a < 17]
        larga = any(b >= 19 or b < 6 for a, b in dia)
        out.append('sí' if (tarde and dia) or larga else ('noche' if tarde else 'mediodía'))
    return out
