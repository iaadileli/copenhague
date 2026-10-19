// captura de un selector concreto: node una.mjs '<selector>' nombre [ancho]
import { chromium } from '../node_modules/playwright/index.mjs';
import { spawn } from 'node:child_process';
import path from 'node:path';
const RAIZ = path.join(import.meta.dirname, '..');
const srv = spawn('python3', ['-m', 'http.server', '8771', '-d', RAIZ, '-b', '127.0.0.1'], { stdio: 'ignore' });
await new Promise(r => setTimeout(r, 700));
const nav = await chromium.launch().catch(() => chromium.launch({ channel: 'chromium' }));
const ancho = +(process.argv[4] || 1280);
const p = await nav.newPage({ viewport: { width: ancho, height: ancho < 600 ? 844 : 900 }, deviceScaleFactor: ancho < 600 ? 2 : 1 });
await p.goto('http://127.0.0.1:8771/index.html', { waitUntil: 'networkidle' });
const el = await p.$(process.argv[2]);
await el.scrollIntoViewIfNeeded(); await p.evaluate(s => document.querySelector(s).scrollIntoView(), process.argv[2]);
await p.evaluate(() => window.scrollBy(0, -60));
await p.waitForTimeout(400);
await p.screenshot({ path: path.join(RAIZ, 'generador/datos-fuente/capturas', process.argv[3] + '.png') });
await nav.close(); srv.kill();
