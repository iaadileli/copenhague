#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Candidatas a foto de Copenhague, sacadas de CATEGORÍAS de Commons (oct-2026).
Los nombres de categoría salen de list=search (srnamespace=14); los que no se han
podido comprobar se marcan con «?» y, si salen vacíos, se ve en la salida.
Reanudable: solo pide lo que falta. Luego: hoja-contacto.py → mirar → elegir.py"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buscafotos import de_categoria
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDA = 'generador/datos-fuente/fotos1.json'

CATS = {
 'nyhavn':        'Nyhavn',
 'navidad':       'Christmas in Copenhagen',
 'tivoli':        'Christmas 2016 in Tivoli Gardens',
 'tivoli2':       'Christmas decorations in Tivoli Gardens',
 'christiansborg':'Christiansborg Palace',
 'christiania':   'Christiania (Copenhagen)',
 'kodbyen':       'Kødbyen',
 'rundetaarn':    'Rundetårn',
 'torvehallerne': 'Torvehallerne',
 'refshaleoen':   'Refshaleøen',
 'reffen':        'Reffen',
 'stroget':       'Strøget',
 'rosenborg':     'Rosenborg Castle',
 'superkilen':    'Superkilen',
 'assistens':     'Assistens Kirkegård (København)',
 'amalienborg':   'Amalienborg',           # ?
 'vesterbro':     'Vesterbro',             # ?
 'norrebro':      'Nørrebro',              # ?
 'frederiksberg': 'Frederiksberg Gardens', # ?
 'christianshavn':'Christianshavn',        # ?
 'vorfrelsers':   "Church of Our Saviour, Copenhagen",  # ?
 'osterbro':      'Østerbro',              # ?
}

res = json.load(open(SALIDA)) if os.path.exists(SALIDA) else {}
for k, cat in CATS.items():
    if res.get(k):
        print('  %-14s ya estaba (%d)' % (k, len(res[k]))); continue
    try:
        r = de_categoria(cat, 30)
    except RuntimeError as e:
        print('  %-14s ✗ %s' % (k, e)); continue
    res[k] = [x for x in r if x['apaisada']] or r
    print('  %-14s %2d candidatas · %s' % (k, len(res[k]), res[k][0]['t'][5:60] if res[k] else '— VACÍA'))
    json.dump(res, open(SALIDA, 'w'), ensure_ascii=False)
    time.sleep(6)
