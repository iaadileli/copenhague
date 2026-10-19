#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Candidatas a foto para cada plato de «Qué hay que probar» de Copenhague (oct-2026).
Las categorías de Commons salen de la investigación (platos.json, campo busqueda_commons,
comprobadas con list=search); donde no hay categoría, búsqueda por texto. Reanudable.
Luego: hoja-contacto.py y elegir-platos.py"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buscafotos import de_categoria, buscar
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDA = 'generador/datos-fuente/fotos-platos.json'
PLATOS = json.load(open('generador/datos-fuente/investigacion/platos.json'))
TEXTO = {'dyrlaegens-natmad': 'dyrlægens natmad', 'aeg-og-rejer': 'smørrebrød rejer æg',
         'rullepolse': 'rullepølse'}

res = json.load(open(SALIDA)) if os.path.exists(SALIDA) else {}
for p in PLATOS:
    k = p['clave']
    if res.get(k):
        print('  %-18s ya estaba (%d)' % (k, len(res[k]))); continue
    cat = (p.get('busqueda_commons') or '').replace('Category:', '').strip()
    try:
        r = de_categoria(cat, 24) if cat else buscar(TEXTO.get(k, p['nombre_danes']), 12)
    except RuntimeError as e:
        print('  %-18s ✗ %s' % (k, e)); continue
    res[k] = r
    print('  %-18s %2d candidatas (%s)' % (k, len(r), cat or 'texto'))
    json.dump(res, open(SALIDA, 'w'), ensure_ascii=False)
    time.sleep(5)
