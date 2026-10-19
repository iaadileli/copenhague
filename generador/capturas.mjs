// Capturas de la página en marcha, para revisar el diseño mirándolo.
import { existsSync, mkdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import path from 'node:path';
const RAIZ = path.join(import.meta.dirname, '..');
const donde = ['/home/adil/proyectos-adil/maquetador-libros/node_modules/playwright/index.mjs',
               path.join(RAIZ,'node_modules/playwright/index.mjs')].find(existsSync);
const { chromium } = await import(donde);
const { createServer } = await import('node:net');
const puerto = await new Promise((res, rej) => { const s = createServer();
  s.on('error', rej); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); }); });
const srv = spawn('python3', ['-m','http.server',String(puerto),'-d',RAIZ,'-b','127.0.0.1'], {stdio:'ignore'});
await new Promise(r => setTimeout(r, 700));
const URL = `http://127.0.0.1:${puerto}/index.html`;
const salida = path.join(RAIZ, 'generador/datos-fuente/capturas');
mkdirSync(salida, { recursive: true });

// en el Mac a veces no baja el «headless shell» (la CDN corta a los 30 s): se usa el
// Chromium completo en modo sin ventana, que es el mismo motor
const nav = await chromium.launch().catch(() => chromium.launch({ channel: 'chromium' }));
// --- escritorio
const p = await nav.newPage({ viewport: { width: 1280, height: 900 } });
await p.goto(URL, { waitUntil: 'networkidle' });
await p.screenshot({ path: `${salida}/1-portada.png` });
for (const [nombre, sel] of [['2-navidad','#navidad'], ['3-tiempo','#tiempo'], ['4-mapa','#mapa'],
                             ['5-indre','#indre'], ['6-comida','#indre .comer'], ['6b-tiendas','#indre .tiendas-bloque'], ['7-comer','#comer'],
                             ['7b-mejores','.podio'], ['7c-probar','#probar'], ['8-pan','#pan'], ['8b-tiendas','#tiendas'], ['9-hoteles','#hoteles'],
                             ['13-transporte','#transporte']]) {
  const el = await p.$(sel);
  if (el) { await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(350);
            await p.screenshot({ path: `${salida}/${nombre}.png` }); }
}
// --- modo oscuro
await p.evaluate(() => document.querySelector('#tema')?.click());
await p.evaluate(() => document.querySelector('#indre')?.scrollIntoView());
await p.waitForTimeout(350);
await p.screenshot({ path: `${salida}/10-oscuro.png` });
await p.evaluate(() => document.querySelector('.podio')?.scrollIntoView());
await p.waitForTimeout(350);
await p.screenshot({ path: `${salida}/10b-oscuro-mejores.png` });
// --- móvil
const m = await nav.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
await m.goto(URL, { waitUntil: 'networkidle' });
await m.screenshot({ path: `${salida}/11-movil-portada.png` });
await m.evaluate(() => document.querySelector('#indre')?.scrollIntoView());
await m.waitForTimeout(300);
await m.screenshot({ path: `${salida}/12-movil-este.png` });
await m.evaluate(() => document.querySelector('.probar')?.scrollIntoView());
await m.waitForTimeout(300);
await m.screenshot({ path: `${salida}/14-movil-probar.png` });
await nav.close(); srv.kill();
console.log('capturas en', salida);
