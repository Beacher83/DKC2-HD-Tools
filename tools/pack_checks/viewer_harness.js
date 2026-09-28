// Runs the viewer's inline script in Node with a do-nothing DOM, so its ROM/sprite
// functions can be called directly. Usage: node viewer_harness.js <script.js to run after>
const fs = require('fs'), vm = require('vm'), path = require('path');
const VIEWER = 'C:/DEV Claude/DKC2-HD-Tools/dkc2-viewer';
const html = fs.readFileSync(path.join(VIEWER, 'index.html'), 'utf8');
const inline = [...html.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
const srcs = [...html.matchAll(/<script[^>]*src="([^"]+)"[^>]*><\/script>/g)].map(m => m[1])
  .filter(s => !/^https?:/.test(s));

const dummy = () => new Proxy(function () {}, {
  get(t, k) {
    if (k === Symbol.toPrimitive) return () => '';
    if (k === 'style' || k === 'dataset' || k === 'classList') return dummy();
    if (k === 'length') return 0;
    if (k === 'value' || k === 'textContent' || k === 'innerHTML') return '';
    if (k === 'checked') return false;
    if (k === Symbol.iterator) return function* () {};
    if (k === 'then') return undefined;
    return dummy();
  },
  apply() { return dummy(); },
  construct() { return dummy(); },
  set() { return true; },
});
const ctx = {
  console, setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, clearInterval() {},
  requestAnimationFrame: () => 0, performance: { now: () => Date.now() },
  document: dummy(), navigator: dummy(), location: dummy(),
  localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  indexedDB: undefined, fetch: undefined, alert() {}, confirm: () => false, prompt: () => null,
  atob: s => Buffer.from(s, 'base64').toString('latin1'), btoa: s => Buffer.from(s, 'latin1').toString('base64'),
  Image: function () { return dummy(); }, OffscreenCanvas: function () { return dummy(); },
  ImageData: function (w, h) { return { width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }; },
  Blob: function () {}, URL: { createObjectURL: () => '' }, TextDecoder, TextEncoder,
  Uint8Array, Uint16Array, Uint32Array, Int32Array, Float32Array, Uint8ClampedArray, ArrayBuffer, DataView,
  Map, Set, WeakMap, Math, JSON, Date, BigInt, Array, Object, Number, String, Promise, Error, RegExp, Symbol,
  isNaN, parseInt, parseFloat,
};
ctx.window = ctx; ctx.self = ctx; ctx.globalThis = ctx;
ctx.addEventListener = () => {}; ctx.getComputedStyle = () => dummy();
vm.createContext(ctx);
for (const s of srcs) {
  try { vm.runInContext(fs.readFileSync(path.join(VIEWER, s), 'utf8'), ctx, { filename: s }); }
  catch (e) { console.error('[harness] ' + s + ': ' + e.message); }
}
// top-level const/let are not properties of the context — re-export the ones we need
const exportNames = ['rom', 'spriteCapPairs', 'spriteCapRows', 'spriteCapHashRow'];
try {
  vm.runInContext(inline + '\n;globalThis.__setRom = (d) => { rom = new RomBuffer(d); };' +
    'globalThis.__get = (n) => eval(n); globalThis.__set = (n, v) => eval(n + " = v");', ctx, { filename: 'index.html' });
} catch (e) { console.error('[harness] inline: ' + e.stack.split('\n').slice(0, 3).join(' | ')); }
module.exports = ctx;
if (require.main === module && process.argv[2]) {
  const run = fs.readFileSync(process.argv[2], 'utf8');
  ctx.require = require; ctx.Buffer = Buffer;
  vm.runInContext(run, ctx, { filename: process.argv[2] });
}
