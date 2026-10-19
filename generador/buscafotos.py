"""Busca fotos en Wikimedia Commons.

Ojo: la API corta si se la aprieta (varias búsquedas seguidas) y devolvía una
respuesta vacía que el script contaba como «0 resultados». Eso dejaba hojas de
contacto a medias sin decir por qué. Ahora distingue las dos cosas y reintenta.
Wikimedia además pide un User-Agent identificable."""
import json, subprocess, time, sys

UA = 'guia-viaje-copenhague/1.0 (uso personal; contacto via github.com/iaadileli)'

def _pide(q, n):
    cmd = ['curl','-s','--max-time','25','-G','https://commons.wikimedia.org/w/api.php','-A',UA,
      '--data-urlencode','action=query','--data-urlencode','generator=search',
      '--data-urlencode',f'gsrsearch={q}','--data-urlencode','gsrnamespace=6',
      '--data-urlencode',f'gsrlimit={n}','--data-urlencode','prop=imageinfo',
      '--data-urlencode','iiprop=url|size|extmetadata','--data-urlencode','iiurlwidth=1100',
      '--data-urlencode','format=json']
    salida = subprocess.run(cmd, capture_output=True, text=True).stdout
    if not salida.strip():
        return None, 'respuesta vacía (la API ha cortado)'
    try:
        d = json.loads(salida)
    except Exception as e:
        return None, 'no es JSON (%s): %s' % (e, salida[:120])
    if 'error' in d:
        return None, 'error de la API: %s' % d['error'].get('info', '')
    return d.get('query', {}).get('pages', {}), None

def buscar(q, n=6, intentos=3):
    paginas, fallo = None, None
    for i in range(intentos):
        paginas, fallo = _pide(q, n)
        if paginas is not None:
            break
        print('    ↻ reintento %d/%d (%s)' % (i + 1, intentos, fallo))
        time.sleep(20 * (i + 1))
    if paginas is None:
        raise RuntimeError('Wikimedia no responde para «%s»: %s' % (q, fallo))
    out = []
    for p in paginas.values():
        i = p['imageinfo'][0]; m = i.get('extmetadata', {})
        if i['width'] < 640: continue
        if not p['title'].lower().endswith(('.jpg','.jpeg')): continue
        out.append({'t': p['title'], 'url': i.get('thumburl') or i['url'],
                    'lic': m.get('LicenseShortName', {}).get('value','?'),
                    'w': i['width'], 'h': i['height'],
                    'apaisada': i['width'] > i['height'] * 1.15})
    return out

if __name__ == '__main__':
    import os
    PLATOS = json.load(open(sys.argv[1]))
    # se reanuda: lo ya buscado no se vuelve a pedir (la API corta enseguida)
    res = json.load(open(sys.argv[2])) if os.path.exists(sys.argv[2]) else {}
    for k, q in PLATOS.items():
        if res.get(k):
            print(f'  {k:12s} ya estaba'); continue
        r = buscar(q, 8); res[k] = r
        apaisadas = sum(1 for x in r if x['apaisada'])
        print(f'  {k:12s} {len(r)} candidatas, {apaisadas} apaisadas · ' +
              (f'{r[0]["t"][5:52]}  [{r[0]["lic"]}]' if r else '— sin resultado'))
        json.dump(res, open(sys.argv[2],'w'), ensure_ascii=False)   # guarda sobre la marcha
        time.sleep(6)
    json.dump(res, open(sys.argv[2],'w'), ensure_ascii=False)

# --- por categoría: mucho más fiable que la búsqueda por texto, que devuelve
# --- logos, mapas y fotos de otras ciudades. Se usa desde categorias.py
def de_categoria(cat, n=12, intentos=3):
    for i in range(intentos):
        cmd = ['curl','-s','--max-time','30','-G','https://commons.wikimedia.org/w/api.php','-A',UA,
          '--data-urlencode','action=query','--data-urlencode','generator=categorymembers',
          '--data-urlencode','gcmtitle=Category:%s' % cat,'--data-urlencode','gcmtype=file',
          '--data-urlencode','gcmlimit=%d' % n,'--data-urlencode','prop=imageinfo',
          '--data-urlencode','iiprop=url|size|extmetadata','--data-urlencode','iiurlwidth=1100',
          '--data-urlencode','format=json']
        salida = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            d = json.loads(salida)
        except Exception:
            print('    ↻ %s: la API ha cortado, espero' % cat); time.sleep(20 * (i + 1)); continue
        if 'error' in d:
            raise RuntimeError('%s: %s' % (cat, d['error'].get('info','')))
        out = []
        for p in d.get('query', {}).get('pages', {}).values():
            if 'imageinfo' not in p: continue
            im = p['imageinfo'][0]; m = im.get('extmetadata', {})
            if im['width'] < 900: continue
            if not p['title'].lower().endswith(('.jpg','.jpeg')): continue
            out.append({'t': p['title'], 'url': im.get('thumburl') or im['url'],
                        'lic': m.get('LicenseShortName', {}).get('value','?'),
                        'w': im['width'], 'h': im['height'],
                        'apaisada': im['width'] > im['height'] * 1.15})
        return out
    raise RuntimeError('Wikimedia no responde para la categoría ' + cat)
