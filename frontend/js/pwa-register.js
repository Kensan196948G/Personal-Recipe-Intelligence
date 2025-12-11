/**
 * PWA Registration Script
 * Service Worker の登録、インストールプロンプト、アップデート検出
 */

class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.isUpdateAvailable = false;
    this.registration = null;

    this.init();
  }

  /**
   * 初期化
   */
  async init() {
    if (!('serviceWorker' in navigator)) {
      console.warn('[PWA] Service Worker not supported');
      return;
    }

    try {
      await this.registerServiceWorker();
      this.setupInstallPrompt();
      this.setupUpdateDetection();
      this.setupOnlineOfflineHandlers();
    } catch (error) {
      console.error('[PWA] Initialization failed:', error);
    }
  }

  /**
   * Service Worker 登録
   */
  async registerServiceWorker() {
    try {
      this.registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('[PWA] Service Worker registered:', this.registration.scope);

      // 登録完了イベントを発火
      this.dispatchEvent('sw-registered', { registration: this.registration });

      return this.registration;
    } catch (error) {
      console.error('[PWA] Service Worker registration failed:', error);
      throw error;
    }
  }

  /**
   * インストールプロンプトのセットアップ
   */
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (event) => {
      console.log('[PWA] Install prompt available');

      // デフォルトのプロンプトを抑制
      event.preventDefault();

      // 後で使用するためにイベントを保存
      this.deferredPrompt = event;

      // インストール可能イベントを発火
      this.dispatchEvent('install-available', { prompt: event });

      // UI にインストールボタンを表示
      this.showInstallButton();
    });

    window.addEventListener('appinstalled', (event) => {
      console.log('[PWA] App installed');
      this.deferredPrompt = null;

      // インストール完了イベントを発火
      this.dispatchEvent('app-installed', { event });

      // インストールボタンを非表示
      this.hideInstallButton();
    });
  }

  /**
   * アプリをインストール
   */
  async installApp() {
    if (!this.deferredPrompt) {
      console.warn('[PWA] Install prompt not available');
      return false;
    }

    try {
      // プロンプトを表示
      this.deferredPrompt.prompt();

      // ユーザーの選択を待機
      const { outcome } = await this.deferredPrompt.userChoice;

      console.log('[PWA] Install outcome:', outcome);

      this.deferredPrompt = null;

      return outcome === 'accepted';
    } catch (error) {
      console.error('[PWA] Install failed:', error);
      return false;
    }
  }

  /**
   * アップデート検出のセットアップ
   */
  setupUpdateDetection() {
    if (!this.registration) {
      return;
    }

    // 新しい Service Worker が待機中
    this.registration.addEventListener('updatefound', () => {
      console.log('[PWA] Update found');

      const newWorker = this.registration.installing;

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          console.log('[PWA] New version available');

          this.isUpdateAvailable = true;

          // アップデート可能イベントを発火
          this.dispatchEvent('update-available', { worker: newWorker });

          // UI にアップデート通知を表示
          this.showUpdateNotification();
        }
      });
    });

    // 定期的にアップデートをチェック（1時間ごと）
    setInterval(() => {
      this.registration.update();
    }, 60 * 60 * 1000);
  }

  /**
   * アップデートを適用
   */
  async applyUpdate() {
    if (!this.isUpdateAvailable) {
      console.warn('[PWA] No update available');
      return false;
    }

    try {
      const registration = await navigator.serviceWorker.getRegistration();

      if (registration && registration.waiting) {
        // 新しい Service Worker にメッセージを送信
        registration.waiting.postMessage({ type: 'SKIP_WAITING' });

        // ページをリロード
        window.location.reload();

        return true;
      }

      return false;
    } catch (error) {
      console.error('[PWA] Update failed:', error);
      return false;
    }
  }

  /**
   * オンライン/オフラインハンドラーのセットアップ
   */
  setupOnlineOfflineHandlers() {
    window.addEventListener('online', () => {
      console.log('[PWA] Online');
      this.dispatchEvent('online', { online: true });
      this.showConnectionStatus('オンライン', 'success');
    });

    window.addEventListener('offline', () => {
      console.log('[PWA] Offline');
      this.dispatchEvent('offline', { online: false });
      this.showConnectionStatus('オフライン', 'warning');
    });

    // 初期状態を確認
    if (!navigator.onLine) {
      this.showConnectionStatus('オフライン', 'warning');
    }
  }

  /**
   * インストールボタンを表示
   */
  showInstallButton() {
    const button = document.getElementById('pwa-install-button');
    if (button) {
      button.style.display = 'block';
      button.addEventListener('click', () => this.installApp());
    }
  }

  /**
   * インストールボタンを非表示
   */
  hideInstallButton() {
    const button = document.getElementById('pwa-install-button');
    if (button) {
      button.style.display = 'none';
    }
  }

  /**
   * アップデート通知を表示
   */
  showUpdateNotification() {
    const notification = document.getElementById('pwa-update-notification');
    if (notification) {
      notification.style.display = 'block';

      const updateButton = notification.querySelector('.update-button');
      if (updateButton) {
        updateButton.addEventListener('click', () => this.applyUpdate());
      }
    }
  }

  /**
   * 接続状態を表示
   */
  showConnectionStatus(message, type) {
    const status = document.getElementById('pwa-connection-status');
    if (status) {
      status.textContent = message;
      status.className = `connection-status ${type}`;
      status.style.display = 'block';

      // 3秒後に非表示
      setTimeout(() => {
        status.style.display = 'none';
      }, 3000);
    }
  }

  /**
   * カスタムイベントを発火
   */
  dispatchEvent(name, detail) {
    const event = new CustomEvent(`pwa:${name}`, {
      detail,
      bubbles: true,
      cancelable: true
    });

    window.dispatchEvent(event);
  }

  /**
   * Service Worker にメッセージを送信
   */
  async sendMessage(message) {
    if (!navigator.serviceWorker.controller) {
      console.warn('[PWA] No active Service Worker');
      return;
    }

    navigator.serviceWorker.controller.postMessage(message);
  }

  /**
   * 特定のURLをキャッシュ
   */
  async cacheUrls(urls) {
    await this.sendMessage({
      type: 'CACHE_URLS',
      urls
    });
  }

  /**
   * バックグラウンド同期を登録
   */
  async registerBackgroundSync(tag) {
    if (!('sync' in this.registration)) {
      console.warn('[PWA] Background Sync not supported');
      return false;
    }

    try {
      await this.registration.sync.register(tag);
      console.log('[PWA] Background sync registered:', tag);
      return true;
    } catch (error) {
      console.error('[PWA] Background sync registration failed:', error);
      return false;
    }
  }

  /**
   * プッシュ通知の許可を要求
   */
  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      console.warn('[PWA] Notifications not supported');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      console.log('[PWA] Notification permission:', permission);
      return permission === 'granted';
    } catch (error) {
      console.error('[PWA] Notification permission failed:', error);
      return false;
    }
  }

  /**
   * 通知を表示
   */
  async showNotification(title, options = {}) {
    if (!this.registration) {
      console.warn('[PWA] No Service Worker registration');
      return;
    }

    if (Notification.permission !== 'granted') {
      console.warn('[PWA] Notification permission not granted');
      return;
    }

    try {
      await this.registration.showNotification(title, {
        icon: '/icons/icon-192.png',
        badge: '/icons/icon-96.png',
        ...options
      });
    } catch (error) {
      console.error('[PWA] Show notification failed:', error);
    }
  }

  /**
   * アプリの情報を取得
   */
  getAppInfo() {
    return {
      isInstalled: window.matchMedia('(display-mode: standalone)').matches,
      isOnline: navigator.onLine,
      hasServiceWorker: 'serviceWorker' in navigator,
      hasBackgroundSync: this.registration && 'sync' in this.registration,
      hasNotifications: 'Notification' in window,
      notificationPermission: 'Notification' in window ? Notification.permission : 'not-supported'
    };
  }
}

// グローバルインスタンスを作成
const pwaManager = new PWAManager();

// エクスポート（モジュール環境の場合）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PWAManager;
}
