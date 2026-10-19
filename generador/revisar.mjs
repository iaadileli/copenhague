#!/usr/bin/env node
// Revisión de la web CON LA PÁGINA EN MARCHA, no leyendo el HTML.
// Lo que se lee en el fichero no dice nada de lo que pasa cuando el JS pinta.
// Uso:  node generador/revisar.mjs            (levanta un servidor local y revisa)
//       node generador/revisar.mjs <url>      (revisa una url ya servida)
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import path from 'node:path';

const RAIZ = path.join(import.meta.dirname, '..');
const CANDIDATOS = [
  path.join(RAIZ, 'node_modules/playwright/index.mjs'),
  '/home/adil/proyectos-adil/maquetador-libros/node_modules/playwright/index.mjs',   // Ubuntu
];
const donde = CANDIDATOS.find(existsSync);
if (!donde) {
  console.error('Falta Playwright:  npm i -D playwright && npx playwright install chromium');
  process.exit(2);
}
const { chromium, webkit } = await import(donde);
// MOTOR=webkit node generador/revisar.mjs  → lo más parecido al Safari del iPad
const MOTOR = process.env.MOTOR === 'webkit' ? webkit : null;
if (MOTOR) console.log('Revisando con WebKit (Safari)');

// --- servidor local, para que el service worker y los fetch se comporten como en producción
let servidor = null, URL_BASE = process.argv[2];
if (!URL_BASE) {
  // Un puerto fijo es una trampa: si queda un servidor huérfano de otra guía,
  // spawn falla en silencio y se acaba revisando la web equivocada. Se busca
  // un puerto libre y además se comprueba que lo servido es ESTA carpeta.
  const { createServer } = await import('node:net');
  const libre = () => new Promise((res, rej) => {
    const s = createServer();
    s.on('error', rej);
    s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); });
  });
  const puerto = await libre();
  servidor = spawn('python3', ['-m', 'http.server', String(puerto), '-d', RAIZ, '-b', '127.0.0.1'],
                   { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 700));
  URL_BASE = `http://127.0.0.1:${puerto}/index.html`;
  const { readFileSync } = await import('node:fs');
  const mio = readFileSync(path.join(RAIZ, 'index.html'), 'utf8');
  const servido = await fetch(URL_BASE).then(r => r.text()).catch(() => '');
  if (servido.length !== mio.length) {
    console.error(`El servidor local no está sirviendo ${RAIZ}. Revisión abortada.`);
    if (servidor) servidor.kill();
    process.exit(2);
  }
}
const fin = (c) => { if (servidor) servidor.kill(); process.exit(c); };

const fallos = [], avisos = [];
const mal   = (m) => { fallos.push(m); console.log('  ⚠ ' + m); };
const ojo   = (m) => { avisos.push(m); console.log('  · ' + m); };
const bien  = (m) => console.log('  ✓ ' + m);
const grupo = (t) => console.log('\n' + t);

// en el Mac a veces no baja el «headless shell» (la CDN corta a los 30 s): se usa el
// Chromium completo en modo sin ventana, que es el mismo motor
const nav = MOTOR ? await MOTOR.launch()
  : await chromium.launch().catch(() => chromium.launch({ channel: 'chromium' }));
const ctx = await nav.newContext({ serviceWorkers: 'allow' });
const p = await ctx.newPage();
const errores = [], fallidos = [];
p.on('pageerror', e => errores.push(e.message.slice(0, 120)));
p.on('console', m => { if (m.type() === 'error') errores.push('consola: ' + m.text().slice(0, 120)); });
p.on('requestfailed', r => fallidos.push(r.url().split('/').pop()));
p.on('response', r => { if (r.status() >= 400) fallidos.push(r.status() + ' ' + r.url().split('/').pop()); });

await p.goto(URL_BASE, { waitUntil: 'networkidle' });

grupo('RECURSOS');
fallidos.length ? mal(`${fallidos.length} recursos no cargan: ` + [...new Set(fallidos)].slice(0,6).join(', '))
                : bien('todos los recursos cargan');
const imgs = await p.evaluate(() => ({
  total: document.images.length,
  rotas: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.split('/').pop()),
  sinAlt: [...document.images].filter(i => !i.alt).length,
  sinLazy: [...document.images].filter(i => i.loading !== 'lazy').length,
}));
imgs.rotas.length ? mal('imágenes rotas: ' + imgs.rotas.join(', ')) : bien(`${imgs.total} imágenes, todas cargan`);
imgs.sinAlt ? mal(`${imgs.sinAlt} imágenes sin alt`) : bien('todas con alt');
if (imgs.sinLazy > 2) ojo(`${imgs.sinLazy} imágenes sin carga diferida`);

grupo('ESTRUCTURA Y ENLACES');
const est = await p.evaluate(() => {
  const enlaces = [...document.querySelectorAll('a[href]')];
  const internos = enlaces.map(a => a.getAttribute('href')).filter(h => h.startsWith('#') && h.length > 1);
  return {
    anidados: document.querySelectorAll('.tip .madrugador, .madrugador .tip').length,
    rotos: [...new Set(internos)].filter(h => { try { return !document.querySelector(h); } catch { return true; } }),
    vacios: enlaces.filter(a => { const h = a.getAttribute('href'); return !h || h === '#' || h === 'javascript:void(0)'; }).length,
    sinNoopener: enlaces.filter(a => a.target === '_blank' && !/noopener/.test(a.rel)).length,
    externos: enlaces.filter(a => /^https?:/.test(a.getAttribute('href') || '')).length,
    sitios: document.querySelectorAll('.sitios li').length,
    repes: (() => { const n = [...document.querySelectorAll('.sitios li .nombre')].map(e => e.textContent.trim());
                    return [...new Set(n.filter((x, i) => n.indexOf(x) !== i))]; })(),
    secciones: document.querySelectorAll('section[id]').length,
    navRoto: [...document.querySelectorAll('nav a[href^="#"]')]
               .map(a => a.getAttribute('href')).filter(h => { try { return !document.querySelector(h); } catch { return true; } }),
  };
});
est.anidados ? mal(`${est.anidados} bloques anidados donde no deben`) : bien('ningún bloque mal anidado');
est.rotos.length ? mal('enlaces internos rotos: ' + est.rotos.join(', ')) : bien('enlaces internos, todos existen');
est.navRoto.length ? mal('el menú apunta a secciones que no existen: ' + est.navRoto.join(', ')) : bien('el menú lleva a todas sus secciones');
est.vacios ? mal(`${est.vacios} enlaces sin destino`) : bien(`${est.externos} enlaces externos con destino`);
est.sinNoopener ? ojo(`${est.sinNoopener} enlaces a otra pestaña sin rel="noopener"`) : bien('los enlaces externos, con noopener');
est.repes.length ? mal('sitios repetidos: ' + est.repes.join(', ')) : bien(`${est.sitios} sitios de comer, ninguno repetido`);

grupo('FECHAS DE BOOKING Y MAPS');
const reservas = await p.evaluate(() => {
  const filas = [...document.querySelectorAll('table.hoteles tbody tr')];
  let etapa = null; const problemas = [];
  const mes = { ene:0,feb:1,mar:2,abr:3,may:4,jun:5,jul:6,ago:7,sep:8,oct:9,nov:10,dic:11 };
  for (const tr of filas) {
    if (tr.classList.contains('grupo')) { etapa = tr.innerText; continue; }
    const a = tr.querySelector('a.booking'); if (!a) continue;
    const u = new URL(a.href);
    const inm = etapa.match(/(\d+)\s+(\w{3})\w*\s*→\s*(\d+)\s+(\w{3})/);
    if (!inm) continue;
    const iso = (d, m) => `2026-${String(mes[m.slice(0,3).toLowerCase()] + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
    const esperado = [iso(inm[1], inm[2]), iso(inm[3], inm[4])];
    const real = [u.searchParams.get('checkin'), u.searchParams.get('checkout')];
    if (real[0] !== esperado[0] || real[1] !== esperado[1])
      problemas.push(`${tr.querySelector('.hotel')?.textContent}: ${real.join('→')} debería ser ${esperado.join('→')}`);
  }
  return { total: filas.filter(f => f.querySelector('a.booking')).length, problemas };
});
reservas.problemas.length ? reservas.problemas.forEach(x => mal('fechas de Booking mal — ' + x))
                          : bien(`${reservas.total} enlaces de Booking con las fechas de su etapa`);

grupo('MODO «HOY», DÍA A DÍA');
const primero = await p.$('#hoyVerPrimero');
if (primero) await primero.click();
const dias = await p.evaluate(() => {
  const out = [], norm = t => t.replace(/\s+/g, ' ').trim();
  for (let n = 0; n < 40; n++) {
    const caja = document.querySelector('#hoy .hoy-caja');
    if (!caja) break;
    const fecha = norm(caja.querySelector('.hoy-fecha')?.innerText || '').split('·')[0];
    const plano = norm(caja.innerText);
    const cuenta = (sel) => {
      const el = caja.querySelector(sel); if (!el) return null;
      const frase = norm(el.querySelector('p')?.innerText || el.innerText).slice(0, 60);
      let c = 0, i = -1; while (frase && (i = plano.indexOf(frase, i + 1)) !== -1) c++;
      return c;
    };
    out.push({ fecha, titulo: norm(caja.querySelector('h2')?.innerText || ''),
               mad: cuenta('.hoy-mad'), tip: cuenta('.hoy-tip:not(.hoy-mad)'),
               // ojo: el CSS pone los títulos en mayúsculas y innerText los devuelve así
               comer: [...caja.querySelectorAll('.hoy-tarjeta h4')].some(h => /comer/i.test(h.innerText)),
               audios: caja.querySelectorAll('.hoy-audio').length });
    const sig = document.querySelector('#hoySig'); if (!sig) break;
    const antes = fecha; sig.click();               // pinta() es síncrona
    if (norm(document.querySelector('#hoy .hoy-fecha')?.innerText || '').split('·')[0] === antes) break;
  }
  return out;
});
const totalDias = await p.evaluate(() => new Set([...document.querySelectorAll('[data-fecha]')].map(d => d.dataset.fecha)).size);
dias.length === totalDias ? bien(`se recorren los ${totalDias} días con las flechas`)
  : mal(`las flechas solo llegan a ${dias.length} de ${totalDias} días (atascadas en ${dias.at(-1)?.fecha})`);
const dobles = dias.filter(d => (d.mad ?? 1) !== 1 || (d.tip ?? 1) !== 1);
dobles.length ? mal('texto repetido en: ' + dobles.map(d => d.titulo.split('·')[0]).join(', '))
              : bien(`ningún texto repetido (${dias.filter(d => d.mad).length} días con madrugador)`);
const sinComer = dias.filter(d => !d.comer);
sinComer.length ? mal('días sin dónde comer: ' + sinComer.map(d => d.fecha).join(', ')) : bien('todos los días tienen dónde comer');
const sinAudio = dias.filter(d => !d.audios).length;
sinAudio ? ojo(`${sinAudio} de ${dias.length} días sin audios que escuchar`) : bien('todos los días con audios');

grupo('AUDIOGUÍA');
const audio = await p.evaluate(async () => {
  if (typeof AUDIOS === 'undefined') return { sin: 'no hay catálogo' };
  const malos = [];
  for (const a of AUDIOS) {
    const r = await fetch(a.f || ('audio/' + a.id + '.mp3'), { method: 'HEAD' }).catch(() => null);
    if (!r || !r.ok) malos.push(a.id);
  }
  return { total: AUDIOS.length, malos, pistas: document.querySelectorAll('.pista').length };
});
if (audio.sin) ojo('sin catálogo de audios');
else {
  audio.malos.length ? mal(`${audio.malos.length} audios sin fichero: ` + audio.malos.slice(0,5).join(', '))
                     : bien(`${audio.total} audios, todos con su fichero`);
  audio.pistas !== audio.total ? ojo(`${audio.pistas} pistas en la página para ${audio.total} del catálogo`)
                               : bien('catálogo y pistas cuadran');
}

grupo('BUSCADOR, TEMA Y «QUÉ TENGO CERCA»');
const buscador = await p.$('input[type="search"], #buscar, .buscador input');
if (!buscador) ojo('no encuentro el buscador');
else {
  await buscador.fill('smørrebrød');
  await p.waitForTimeout(500);
  const r = await p.evaluate(() => {
    const caja = document.querySelector('.res-buscar, #resultados, .buscador-res');
    return { visible: !!caja && caja.offsetHeight > 0, n: caja ? caja.querySelectorAll('li, a').length : 0 };
  });
  r.visible && r.n ? bien(`el buscador responde (${r.n} resultados para «smørrebrød»)`) : mal('el buscador no devuelve resultados');
  await buscador.fill('');
}
const tema = await p.evaluate(() => {
  const b = document.querySelector('[id*="tema"], .tema, button[title*="scuro"], button[title*="tema"]');
  if (!b) return null;
  const antes = document.documentElement.dataset.tema || '';
  b.click();
  const despues = document.documentElement.dataset.tema || '';
  const fondo = getComputedStyle(document.body).backgroundColor;
  b.click();
  return { antes, despues, fondo };
});
tema ? (tema.antes !== tema.despues ? bien(`el tema cambia (${tema.antes || 'claro'} → ${tema.despues})`)
                                    : mal('el botón de tema no cambia nada'))
     : ojo('no encuentro el botón de tema');
const cerca = await p.evaluate(() => typeof SITIOS !== 'undefined'
  ? { n: SITIOS.length, aprox: SITIOS.filter(s => s.ap).length, sinCoord: SITIOS.filter(s => !s.la || !s.lo).length }
  : null);
cerca ? (cerca.sinCoord ? mal(`${cerca.sinCoord} sitios sin coordenadas`)
                        : bien(`${cerca.n} sitios geolocalizados (${cerca.aprox} con el centro de su zona)`))
      : ojo('no hay datos de «qué tengo cerca»');

grupo('SELLOS Y TABLA DE HORARIOS');
// el sello de «lleva décadas» heredaba la caja .leyenda del mapa y salía gigante:
// esto no se ve leyendo el CSS, hay que medirlo en la página
const sellos = await p.evaluate(() => {
  const s = [...document.querySelectorAll('.sitios .sello')];
  const grandes = s.filter(e => { const r = e.getBoundingClientRect(); return r.width > 26 || r.height > 26; })
                   .map(e => e.className);
  const tipos = {};
  s.forEach(e => { const k = e.className.replace('sello ', ''); tipos[k] = (tipos[k] || 0) + 1; });
  return { total: s.length, grandes: [...new Set(grandes)], tipos };
});
sellos.grandes.length ? mal('sellos con el tamaño descuadrado: ' + sellos.grandes.join(', '))
                      : bien(`${sellos.total} sellos, todos a su tamaño (${Object.keys(sellos.tipos).join(', ')})`);

// la tabla de «quién abre el finde» es el dato más accionable: ninguna celda vacía
const abre = await p.evaluate(() => {
  const filas = [...document.querySelectorAll('.tabla-abre tbody tr')];
  // Copenhague (oct-2026): varias tablas con distinto número de columnas; cada fila
  // tiene que tener tantas celdas como su cabecera y ninguna vacía
  const malas = filas.filter(tr => {
                       const cols = tr.closest('table').querySelectorAll('thead th').length;
                       const tds = [...tr.querySelectorAll('td')];
                       return tds.length !== cols || tds.some(td => !td.innerText.trim());
                     }).map(tr => tr.querySelector('.ab-n')?.innerText || tr.innerText.slice(0, 40));
  const anclas = [...document.querySelectorAll('.tabla-abre .ab-n a')]
                   .map(a => a.getAttribute('href')).filter(h => !document.querySelector(h));
  return { filas: filas.length, malas, anclas };
});
abre.malas.length ? mal('filas incompletas en la tabla de horarios: ' + abre.malas.join(', '))
                  : bien(`${abre.filas} filas en las tablas de horarios, todas completas`);
abre.anclas.length ? mal('la tabla de horarios enlaza a secciones que no existen: ' + abre.anclas.join(', ')) : null;

// los accesos rápidos flotantes: en Nerja uno apuntaba a una sección de otra guía
const rapidos = await p.evaluate(() => {
  const b = [...document.querySelectorAll('#rapido .rap-item')].map(x => x.dataset.a);
  return b.filter(a => a.startsWith('#') && !document.querySelector(a));
});
rapidos.length ? mal('accesos rápidos que no llevan a ningún sitio: ' + rapidos.join(', '))
               : bien('los accesos rápidos llevan todos a su sección');

grupo('MODO OSCURO');
// el texto claro sobre fondo claro de los bloques .comer: pasó en las tres guías
const oscuro = await p.evaluate(() => {
  const btn = document.querySelector('#tema'); if (btn) btn.click();
  function lum(c) {
    const m = c.match(/\d+/g).map(Number).map(v => { v /= 255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); });
    return .2126*m[0] + .7152*m[1] + .0722*m[2];
  }
  function contraste(el) {
    let f = el, fondo = 'rgba(0, 0, 0, 0)';
    while (f && /rgba\(0, 0, 0, 0\)|transparent/.test(fondo)) { fondo = getComputedStyle(f).backgroundColor; f = f.parentElement; }
    const a = lum(getComputedStyle(el).color), b = lum(fondo);
    return (Math.max(a,b) + .05) / (Math.min(a,b) + .05);
  }
  const malos = [];
  document.querySelectorAll('.comer p, .comer .dir, .sitios li, .lista-ver li, .bcard p, .tip, .t-dia, .hoteles td, .ab-nota, .intro')
    .forEach(el => { if (el.offsetHeight && contraste(el) < 4.5) malos.push(el.className || el.tagName); });
  if (btn) btn.click();
  return [...new Set(malos)].slice(0, 6);
});
oscuro.length ? mal('contraste bajo en modo oscuro: ' + oscuro.join(', ')) : bien('el modo oscuro se lee bien');

grupo('MÓVIL (390 px)');
await p.setViewportSize({ width: 390, height: 844 });
await p.waitForTimeout(400);
const movil = await p.evaluate(() => {
  const anchos = [...document.querySelectorAll('body *')]
    .filter(e => e.getBoundingClientRect().width > window.innerWidth + 2 && getComputedStyle(e).overflowX !== 'auto')
    .map(e => (e.className || e.tagName).toString().split(' ')[0]);
  return { desborda: document.documentElement.scrollWidth > window.innerWidth + 2, culpables: [...new Set(anchos)].slice(0, 5) };
});
movil.desborda ? mal('la página se desborda a lo ancho en móvil: ' + (movil.culpables.join(', ') || '?'))
               : bien('no se desborda a lo ancho');

grupo('CONSOLA');
errores.length ? mal('errores de JavaScript: ' + [...new Set(errores)].slice(0,4).join(' | '))
               : bien('sin errores de JavaScript');

await nav.close();
console.log(`\n${fallos.length ? '⚠ ' + fallos.length + ' FALLO(S)' : '✓ todo correcto'}` +
            (avisos.length ? ` · ${avisos.length} aviso(s)` : ''));
fin(fallos.length ? 1 : 0);
