// Caché de la app para abrirla sin conexión. Los datos del clima se guardan aparte (localStorage).
// La página se pide primero a la red (así cada apertura trae la última versión) y solo sin conexión usa la copia.
const C = 'cielo-v8';
const SHELL = ['./', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png', 'icon-512.png',
  'https://cdn.jsdelivr.net/npm/suncalc@1.9.0/suncalc.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(SHELL)).catch(() => {})); self.skipWaiting() });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== C).map(x => caches.delete(x)))).then(() => self.clients.claim())) });
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET') return;
  if (r.mode === 'navigate' || (u.origin === location.origin && /\/(index\.html)?$/.test(u.pathname))) {
    e.respondWith(fetch(r, { cache: 'no-store' }).then(res => { if (res.ok) caches.open(C).then(c => c.put('./', res.clone())); return res })
      .catch(() => caches.match('./')));
    return;
  }
  const shell = u.origin === location.origin || u.host === 'cdn.jsdelivr.net' || u.host === 'cdnjs.cloudflare.com';
  if (!shell) return;
  e.respondWith(caches.open(C).then(async c => {
    const hit = await c.match(r);
    const net = fetch(r).then(res => { if (res.ok) c.put(r, res.clone()); return res }).catch(() => hit);
    return hit || net;
  }));
});
