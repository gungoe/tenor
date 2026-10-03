/* Tenor — service worker.
   Bewaart alleen de app zelf: index.html, manifest, iconen en lettertypes (stale-while-revalidate).
   Aanroepen naar api.github.com, en dus monitor.json, blijven ongemoeid: de app bewaart zijn eigen
   kopie in tenor.kopie. Een tweede kopie hier zou een netwerkfout laten lijken op een geslaagde 200,
   de offline-regel verbergen en de time-out van 15 s omzeilen. */

const VERSIE = '0.5.1';                 // bij elke uitrol verhogen, samen met VERSIE in index.html
const CACHE = `tenor-app-${VERSIE}`;

const APP = [
  './',
  './index.html',
  './manifest.webmanifest',
  './iconen/tenor-papier-180.png',
  './iconen/tenor-papier-192.png',
  './iconen/tenor-papier-512.png',
  /* ==== letters ==== */
  './letters/ibm-plex-mono-normal-400.woff2',
  './letters/ibm-plex-mono-normal-500.woff2',
  './letters/ibm-plex-sans-normal-400.woff2',
  './letters/newsreader-italic-400.woff2',
  './letters/newsreader-normal-400.woff2',
  /* ==== einde letters ==== */
];

// alleen deze paden worden uit de cache bediend; al de rest gaat gewoon naar het netwerk
function hoortBijApp(url, verzoek) {
  if (url.origin !== self.location.origin) return false;
  if (verzoek.mode === 'navigate') return true;
  const pad = url.pathname;
  return pad.endsWith('/index.html') || pad.endsWith('/manifest.webmanifest') ||
    pad.includes('/iconen/') || pad.includes('/letters/');
}

self.addEventListener('install', gebeurtenis => {
  gebeurtenis.waitUntil(
    // cache: 'reload' slaat de HTTP-cache over: GitHub Pages geeft max-age=600, en anders krijgt de nieuwe cache de oude index.html
    caches.open(CACHE).then(cache => cache.addAll(APP.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', gebeurtenis => {
  gebeurtenis.waitUntil(
    caches.keys()
      .then(namen => Promise.all(namen.filter(n => n.startsWith('tenor-') && n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', gebeurtenis => {
  const verzoek = gebeurtenis.request;
  if (verzoek.method !== 'GET') return;
  const url = new URL(verzoek.url);
  if (!hoortBijApp(url, verzoek)) return;           // api.github.com en al het andere: ongemoeid
  gebeurtenis.respondWith(uitCache(gebeurtenis, verzoek));
});

async function uitCache(gebeurtenis, verzoek) {
  const cache = await caches.open(CACHE);
  const sleutel = verzoek.mode === 'navigate' ? './index.html' : verzoek;
  const bewaard = await cache.match(sleutel, { ignoreSearch: true });
  // verversen met cache: 'no-cache': de HTTP-cache mag alleen antwoorden na controle bij de server
  const vers = fetch(verzoek.mode === 'navigate' ? './index.html' : verzoek, { cache: 'no-cache' }).then(antwoord => {
    if (antwoord.ok && antwoord.type === 'basic') cache.put(sleutel, antwoord.clone());
    return antwoord;
  });
  if (bewaard) {
    gebeurtenis.waitUntil(vers.catch(() => {}));     // op de achtergrond verversen
    return bewaard;
  }
  return vers;
}
