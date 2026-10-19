#!/usr/bin/env python3
"""Pone en sw.js la lista de RECURSOS con todo lo que hay en img/ (para «guardar sin
conexión»). No toca el nombre de la caché: eso se sube a mano al publicar."""
import os, re, glob
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fich = ['./', 'index.html', 'manifest.webmanifest', 'sitios.js'] + sorted(
    f for f in glob.glob('img/**/*', recursive=True) if os.path.isfile(f) and not f.endswith('.DS_Store'))
s = open('sw.js').read()
s, n = re.subn(r'const RECURSOS = \[.*?\];', 'const RECURSOS = [\n%s\n];' % '\n'.join("  '%s'," % f for f in fich), s, count=1, flags=re.S)
assert n == 1
open('sw.js', 'w').write(s)
print('sw.js · %d recursos · %s' % (len(fich), re.search(r"CACHE = '([^']+)'", s).group(1)))
