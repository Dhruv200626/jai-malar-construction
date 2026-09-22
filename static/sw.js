/**
 * Jai Malhar — Service Worker
 * Strategy: Cache First for static assets, Network First for pages
 */

const CACHE_NAME = 'jai-malhar-v1';
const OFFLINE_URL = '/offline/';

// Static assets to pre-cache on install
const PRECACHE_URLS = [
  '/',
  '/dashboard/',
  '/offline/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/images/icons/icon-192x192.png',
  '/static/images/icons/icon-512x512.png',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
];

// ── Install: pre-cache core assets ──
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(
        PRECACHE_URLS.map(url =>
          cache.add(url).catch(() => {
            // Don't fail install if one asset 404s (e.g. CDN offline during SW install)
          })
        )
      );
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: remove old caches ──
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: routing strategy ──
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET, chrome-extension, and admin requests
  if (
    request.method !== 'GET' ||
    url.pathname.startsWith('/admin/') ||
    url.pathname.startsWith('/api/') ||
    request.url.startsWith('chrome-extension')
  ) {
    return;
  }

  // Static assets (css, js, images, fonts) → Cache First
  if (
    url.pathname.startsWith('/static/') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('cdn.jsdelivr.net') ||
    url.hostname.includes('cdnjs.cloudflare.com')
  ) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return response;
        }).catch(() => new Response('', { status: 408 }));
      })
    );
    return;
  }

  // HTML pages → Network First, fall back to offline page
  if (request.headers.get('accept') && request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Cache successful page responses
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return response;
        })
        .catch(() =>
          caches.match(request).then(cached => cached || caches.match(OFFLINE_URL))
        )
    );
    return;
  }
});

// ── Background sync for offline form submissions (optional) ──
self.addEventListener('sync', event => {
  if (event.tag === 'sync-attendance') {
    event.waitUntil(syncPendingData());
  }
});

async function syncPendingData() {
  // Placeholder for future offline form sync
}
