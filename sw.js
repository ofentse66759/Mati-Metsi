const VERSION = 'v1.0.2';
const APP_CACHE = `mm-app-${VERSION}`;
const RUNTIME_CACHE = `mm-runtime-${VERSION}`;

// Extract the app path (e.g., /Mati-Metsi/)
const APP_PATH = decodeURIComponent(new URL(self.location).searchParams.get('p') || '/');

// APIs that MUST never be served from cache
const NETWORK_ONLY = [
  'api.open-meteo.com',
  'air-quality-api.open-meteo.com',
  'geocoding-api.open-meteo.com',
  'api.weatherapi.com',
  'supabase.co',
  'maps.googleapis.com',
  'maps.gstatic.com'
];

// CDN assets we can cache
const CDN_CACHEABLE = [
  'cdnjs.cloudflare.com',
  'cdn.jsdelivr.net',
  'unpkg.com'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(APP_CACHE).then((cache) => {
      return cache.add(new Request(APP_PATH, { cache: 'reload' })).catch(() => {});
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((k) => !k.endsWith(VERSION)).map((k) => caches.delete(k))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // 1. Network Only for APIs
  if (NETWORK_ONLY.some((h) => url.hostname.endsWith(h))) return;

  // 2. Network-First for App Shell
  const isShell = url.pathname === APP_PATH || url.pathname === '/' || url.pathname.endsWith('.html');
  if (isShell) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const cache = caches.open(APP_CACHE);
          cache.then((c) => c.put(req, res.clone()));
          return res;
        })
        .catch(async () => {
          // FALLBACK: If network fails, try cache
          const cached = await caches.match(req) || await caches.match(APP_PATH);
          return cached || new Response('<h1>Mati-Metsi is offline</h1><p>Please reconnect to the internet.</p>', {
            headers: { 'Content-Type': 'text/html' }
          });
        })
    );
    return;
  }

  // 3. Cache-First for CDN assets
  if (CDN_CACHEABLE.some((h) => url.hostname.endsWith(h))) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req)
          .then((res) => {
            if (res.ok) {
              const cache = caches.open(RUNTIME_CACHE);
              cache.then((c) => c.put(req, res.clone()));
            }
            return res;
          })
          .catch(() => new Response('Network error', { status: 408 })); // Catch the fetch failure!
      })
    );
    return;
  }
});

// Push notification handling
self.addEventListener('push', (event) => {
  let data = { title: 'Mati-Metsi', body: 'New alert in your area' };
  try { data = Object.assign(data, event.data.json()); } catch {}
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    icon: '/favicon.ico'
  }));
});
