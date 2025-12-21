/**
 * Service Worker for Push Notifications
 * プッシュ通知を処理するService Worker
 */

// Service Worker バージョン
const CACHE_VERSION = 'v1';
const CACHE_NAME = `pri-cache-${CACHE_VERSION}`;

// キャッシュするリソース
const CACHED_RESOURCES = [
  '/',
  '/index.html',
  '/js/notification-manager.js',
  '/icon-192x192.png',
  '/badge-72x72.png',
];

// インストールイベント
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Caching resources...');
      return cache.addAll(CACHED_RESOURCES).catch((error) => {
        console.error('Cache addAll error:', error);
      });
    })
  );

  // 新しいService Workerを即座にアクティベート
  self.skipWaiting();
});

// アクティベートイベント
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );

  // すべてのクライアントを即座に制御
  return self.clients.claim();
});

// フェッチイベント（オプション - キャッシュ戦略）
self.addEventListener('fetch', (event) => {
  // 通知API以外のGETリクエストをキャッシュから返す
  if (event.request.method === 'GET' && !event.request.url.includes('/api/')) {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});

// プッシュ通知受信イベント
self.addEventListener('push', (event) => {
  console.log('Push notification received:', event);

  let data = {
    title: 'Personal Recipe Intelligence',
    body: '新しい通知があります',
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    timestamp: Date.now(),
  };

  // プッシュデータを解析
  if (event.data) {
    try {
      data = event.data.json();
    } catch (error) {
      console.error('Failed to parse push data:', error);
      data.body = event.data.text();
    }
  }

  // 通知オプションを設定
  const options = {
    body: data.body,
    icon: data.icon || '/icon-192x192.png',
    badge: data.badge || '/badge-72x72.png',
    tag: data.tag || 'pri-notification',
    requireInteraction: data.requireInteraction || false,
    data: data.data || {},
    timestamp: data.timestamp || Date.now(),
    actions: data.actions || [],
    vibrate: [200, 100, 200],
  };

  // 通知を表示
  event.waitUntil(self.registration.showNotification(data.title, options));
});

// 通知クリックイベント
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);

  event.notification.close();

  // アクションボタンがクリックされた場合
  if (event.action) {
    console.log('Notification action clicked:', event.action);
    // 特定のアクションに応じた処理を追加可能
  }

  // 通知に関連付けられたデータを取得
  const notificationData = event.notification.data || {};

  // アプリを開く
  event.waitUntil(
    clients
      .matchAll({
        type: 'window',
        includeUncontrolled: true,
      })
      .then((clientList) => {
        // 既に開いているウィンドウがあればフォーカス
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }

        // なければ新しいウィンドウを開く
        if (clients.openWindow) {
          const url = notificationData.url || '/';
          return clients.openWindow(url);
        }
      })
  );
});

// 通知クローズイベント（オプション）
self.addEventListener('notificationclose', (event) => {
  console.log('Notification closed:', event);

  // 通知が閉じられた時の処理（分析など）
  const notificationData = event.notification.data || {};

  if (notificationData.trackClose) {
    // トラッキング処理を追加可能
    console.log('Tracking notification close:', notificationData);
  }
});

// メッセージイベント（オプション - Service WorkerとUIの通信）
self.addEventListener('message', (event) => {
  console.log('Service Worker received message:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  // カスタムメッセージハンドラを追加可能
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_VERSION });
  }
});

// バックグラウンド同期イベント（オプション）
self.addEventListener('sync', (event) => {
  console.log('Background sync:', event.tag);

  if (event.tag === 'sync-notifications') {
    event.waitUntil(syncNotifications());
  }
});

/**
 * 通知を同期（バックグラウンド同期用）
 */
async function syncNotifications() {
  try {
    console.log('Syncing notifications...');
    // サーバーから未読通知を取得するなどの処理
    // 必要に応じて実装
  } catch (error) {
    console.error('Sync notifications error:', error);
  }
}

// プッシュ購読変更イベント
self.addEventListener('pushsubscriptionchange', (event) => {
  console.log('Push subscription changed');

  event.waitUntil(
    self.registration.pushManager
      .subscribe(event.oldSubscription.options)
      .then((subscription) => {
        console.log('Re-subscribed:', subscription);
        // サーバーに新しい購読情報を送信
        return fetch('/api/v1/notifications/subscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            subscription: subscription.toJSON(),
          }),
        });
      })
  );
});

console.log('Service Worker loaded');
