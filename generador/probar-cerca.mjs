// Prueba el «¿qué tengo cerca?» EJECUTÁNDOLO: GPS simulado en Nyhavn, se abre el panel
// y se pulsa cada filtro. Uso: node generador/probar-cerca.mjs
import { chromium } from '../node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import path from 'node:path';
const RAIZ = path.join(import.meta.dirname, '..');
const srv = spawn('python3', ['-m', 'http.server', '8772', '-d', RAIZ, '-b', '127.0.0.1'], { stdio: 'ignore' });
await new Promise(r => setTimeout(r, 700));
const nav = await chromium.launch().catch(() => chromium.launch({ channel: 'chromium' }));
const ctx = await nav.newContext({ geolocation: { latitude: 55.6798, longitude: 12.5910 }, permissions: ['geolocation'],
                                   viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
const p = await ctx.newPage();
const errores = [];
p.on('pageerror', e => errores.push(e.message));
await p.goto('http://127.0.0.1:8772/index.html', { waitUntil: 'networkidle' });
await p.evaluate(() => window.abrirCerca());
await p.waitForTimeout(800);
let fallos = 0;
for (const c of ['', 'comer', 'pan', 'tienda', 'plan']) {
  await p.click(`.cerca-filtros button[data-c="${c}"]`);
  await p.waitForTimeout(300);
  const r = await p.evaluate(() => ({
    estado: document.querySelector('.cerca-estado').innerText,
    items: [...document.querySelectorAll('.cerca-item')].map(a => a.querySelector('.cerca-n').childNodes[0].textContent + ' · ' + a.querySelector('.cerca-d').innerText),
  }));
  console.log(`[${c || 'todo'}] ${r.estado}\n   ` + r.items.slice(0, 4).join('\n   '));
  if (!r.items.length) { fallos++; console.log('   ⚠ sin resultados'); }
}
await p.screenshot({ path: path.join(RAIZ, 'generador/datos-fuente/capturas/cerca-movil.png') });
if (errores.length) { fallos++; console.log('⚠ errores JS:', errores); }
console.log(fallos ? `⚠ ${fallos} fallo(s)` : '✓ el «¿qué tengo cerca?» funciona con los cinco filtros');
await nav.close(); srv.kill(); process.exit(fallos ? 1 : 0);
