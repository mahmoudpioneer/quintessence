#!/usr/bin/env node
// Full-page screenshots for impeccable's review step, via headless Chrome over CDP (no npm deps; Node 22+).
//
//   node capture.mjs <url> [--out .impeccable/review] [--widths 1440,390] [--motion]
//
// Writes desktop.png (first width) and mobile.png (second width), plus <width>.png for any extra widths.
// Captures use prefers-reduced-motion by default so every entrance has settled; pass --motion to capture
// the animated state instead. Set CHROME_PATH to use a specific browser.
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--') && !/^\d/.test(a));
if (!url) { console.error('usage: node capture.mjs <url> [--out dir] [--widths 1440,390] [--motion]'); process.exit(2); }
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const out = resolve(opt('--out', '.impeccable/review'));
const widths = opt('--widths', '1440,390').split(',').map(Number);
const motion = args.includes('--motion');

// Any Chromium-based browser works: Chrome, Chromium, Edge, Brave.
const env = process.env;
const winRoots = [env.PROGRAMFILES, env['PROGRAMFILES(X86)'], env.LOCALAPPDATA].filter(Boolean);
const candidates = [env.CHROME_PATH,
  // macOS
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  // Windows
  ...winRoots.flatMap(r => [join(r, 'Google', 'Chrome', 'Application', 'chrome.exe'),
    join(r, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
    join(r, 'Chromium', 'Application', 'chrome.exe'),
    join(r, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')]),
  // Linux
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/snap/bin/chromium', '/usr/bin/microsoft-edge', '/usr/bin/brave-browser'].filter(Boolean);
const onPath = name => {
  const r = spawnSync(process.platform === 'win32' ? 'where' : 'which', [name], { encoding: 'utf8' });
  return r.status === 0 ? r.stdout.split(/\r?\n/)[0].trim() : null;
};
const chrome = candidates.find(p => existsSync(p)) ||
  ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'msedge', 'chrome'].map(onPath).find(Boolean);
if (!chrome) { console.error('No Chrome, Chromium, Edge or Brave found. Install one or set CHROME_PATH.'); process.exit(1); }

const sleep = ms => new Promise(r => setTimeout(r, ms));
const port = 9400 + Math.floor(Math.random() * 400);
const profile = mkdtempSync(join(tmpdir(), 'qcap-'));
const flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`];
// Chrome refuses to run as root without this (Docker, some CI images); /dev/shm is tiny in containers.
if (process.getuid?.() === 0 || env.CI) flags.push('--no-sandbox', '--disable-dev-shm-usage');
const proc = spawn(chrome, [...flags, 'about:blank'], { stdio: 'ignore' });

try {
  let targets;
  for (let i = 0; i < 75 && !targets; i++) {
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); } catch { await sleep(200); }
  }
  if (!targets) throw new Error('Chrome did not start');
  const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0; const pending = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; } };
  const send = (method, params = {}) => new Promise((r, j) => {
    const i = ++id; pending[i] = m => (m.error ? j(new Error(`${method}: ${m.error.message}`)) : r(m.result));
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluate = async expr => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result.value;

  await send('Page.enable');
  if (!motion) await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  mkdirSync(out, { recursive: true });

  for (const [n, width] of widths.entries()) {
    const mobile = width < 768;
    const viewH = mobile ? 844 : 900;
    await send('Emulation.setDeviceMetricsOverride', { width, height: viewH, deviceScaleFactor: 1, mobile });
    await send('Page.navigate', { url });
    await sleep(400);
    await evaluate(`new Promise(r => { const go = () => document.fonts.ready.then(() => setTimeout(r, ${motion ? 2500 : 900})); document.readyState === 'complete' ? go() : addEventListener('load', go); })`);
    const height = await evaluate('Math.ceil(document.documentElement.scrollHeight)');
    const overflow = await evaluate('document.documentElement.scrollWidth > innerWidth');
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
      clip: { x: 0, y: 0, width, height, scale: 1 } });
    const name = n === 0 ? 'desktop.png' : n === 1 ? 'mobile.png' : `${width}.png`;
    writeFileSync(join(out, name), Buffer.from(shot.data, 'base64'));
    console.log(`${name}: ${width}x${height}${overflow ? '  WARNING: horizontal overflow' : ''}`);
  }
  ws.close();
} catch (e) {
  console.error(e.message); process.exitCode = 1;
} finally {
  proc.kill();
  await sleep(500);
  // Windows keeps the profile locked for a moment after Chrome exits.
  try { rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
}
