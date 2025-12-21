/**
 * Service Worker for Personal Recipe Intelligence PWA
 * キャッシュ戦略: Static assets = Cache First, API = Network First
 */

const CACHE_VERSION = 'pri-v1.0.0';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const API_CACHE = `${CACHE_VERSION}-api`;

// キャッシュ対象の静的ファイル
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/css/main.css',
  '/js/app.js',
  '/js/pwa-register.js',
  '/js/indexed-db.js',
  '/manifest.json'
];

// キャッシュサイズ制限
const CACHE_SIZE_LIMIT = 50;

/**
 * キャッシュサイズを制限
 */
const limitCacheSize = async (cacheName, maxItems) => {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > maxItems) {
    await cache.delete(keys[0]);
    await limitCacheSize(cacheName, maxItems);
  }
};

/**
 * Install Event - 静的アセットをキャッシュ
 */
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...', CACHE_VERSION);

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Precaching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((err) => console.error('[SW] Install failed:', err))
  );
});

/**
 * Activate Event - 古いキャッシュを削除
 */
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...', CACHE_VERSION);

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name.startsWith('pri-') && name !== STATIC_CACHE && name !== DYNAMIC_CACHE && name !== API_CACHE)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

/**
 * Fetch Event - リクエストに応じたキャッシュ戦略
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API リクエスト: Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
    return;
  }

  // 静的アセット: Cache First
  if (STATIC_ASSETS.some((asset) => url.pathname === asset || url.pathname.endsWith(asset))) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
    return;
  }

  // その他の動的コンテンツ: Cache First with Network Fallback
  event.respondWith(cacheFirstStrategy(request, DYNAMIC_CACHE));
});

/**
 * Cache First Strategy
 * キャッシュを優先、なければネットワークから取得
 */
const cacheFirstStrategy = async (request, cacheName) => {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);

    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      await limitCacheSize(cacheName, CACHE_SIZE_LIMIT);
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache First failed:', error);

    // オフライン時はオフラインページを返す
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }

    throw error;
  }
};

/**
 * Network First Strategy
 * ネットワークを優先、失敗したらキャッシュから取得
 */
const networkFirstStrategy = async (request, cacheName) => {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      await limitCacheSize(cacheName, CACHE_SIZE_LIMIT);
    }

    return networkResponse;
  } catch (error) {
    console.error('[SW] Network First failed, trying cache:', error);

    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    throw error;
  }
};

/**
 * Background Sync Event
 * オフライン時のデータ同期
 */
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);

  if (event.tag === 'sync-recipes') {
    event.waitUntil(syncRecipes());
  }
});

/**
 * レシピデータの同期処理
 */
const syncRecipes = async () => {
  try {
    // IndexedDB から同期待ちデータを取得
    const db = await openIndexedDB();
    const syncQueue = await getSyncQueue(db);

    for (const item of syncQueue) {
      try {
        const response = await fetch(item.url, {
          method: item.method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(item.data)
        });

        if (response.ok) {
          // 同期成功したらキューから削除
          await removeSyncQueueItem(db, item.id);
          console.log('[SW] Synced:', item.id);
        }
      } catch (error) {
        console.error('[SW] Sync failed for item:', item.id, error);
      }
    }
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
    throw error;
  }
};

/**
 * IndexedDB を開く（同期用）
 */
const openIndexedDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('PRIDatabase', 1);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

/**
 * 同期キューを取得
 */
const getSyncQueue = (db) => {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['syncQueue'], 'readonly');
    const store = transaction.objectStore('syncQueue');
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

/**
 * 同期キューアイテムを削除
 */
const removeSyncQueueItem = (db, id) => {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    const request = store.delete(id);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
};

/**
 * Push Notification Event（将来の拡張用）
 */
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');

  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Personal Recipe Intelligence';
  const options = {
    body: data.body || '新しい通知があります',
    icon: '/icon-192.png',
    badge: '/icon-96.png',
    data: data.url || '/'
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

/**
 * Notification Click Event
 */
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked');

  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data || '/')
  );
});

/**
 * Message Event - クライアントとの通信
 */
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(DYNAMIC_CACHE)
        .then((cache) => cache.addAll(event.data.urls))
    );
  }
});
