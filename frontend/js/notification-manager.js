/**
 * Notification Manager
 * プッシュ通知の許可リクエスト・購読・表示を管理
 */

class NotificationManager {
  constructor(apiBaseUrl = '/api/v1/notifications') {
    this.apiBaseUrl = apiBaseUrl;
    this.userId = this.getUserId();
    this.publicKey = null;
    this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
  }

  /**
   * ユーザーIDを取得（またはセッションストレージから生成）
   * @returns {string} ユーザーID
   */
  getUserId() {
    let userId = sessionStorage.getItem('pri_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('pri_user_id', userId);
    }
    return userId;
  }

  /**
   * プッシュ通知がサポートされているか確認
   * @returns {boolean} サポート状況
   */
  isNotificationSupported() {
    return this.isSupported;
  }

  /**
   * 通知許可をリクエスト
   * @returns {Promise<string>} 許可状態 (granted/denied/default)
   */
  async requestPermission() {
    if (!this.isSupported) {
      throw new Error('Push notifications are not supported in this browser');
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    const permission = await Notification.requestPermission();
    console.log(`Notification permission: ${permission}`);
    return permission;
  }

  /**
   * VAPID公開鍵を取得
   * @returns {Promise<string>} VAPID公開鍵
   */
  async getPublicKey() {
    if (this.publicKey) {
      return this.publicKey;
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/public-key`);
      const result = await response.json();

      if (result.status === 'ok' && result.data?.public_key) {
        this.publicKey = result.data.public_key;
        return this.publicKey;
      } else {
        throw new Error(result.error || 'Failed to get public key');
      }
    } catch (error) {
      console.error('Get public key error:', error);
      throw error;
    }
  }

  /**
   * URLBase64文字列をUint8Arrayに変換
   * @param {string} base64String - URLBase64文字列
   * @returns {Uint8Array} 変換された配列
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  /**
   * Service Workerを登録
   * @returns {Promise<ServiceWorkerRegistration>} Service Worker登録オブジェクト
   */
  async registerServiceWorker() {
    if (!this.isSupported) {
      throw new Error('Service Worker is not supported in this browser');
    }

    try {
      const registration = await navigator.serviceWorker.register(
        '/service-worker.js',
        { scope: '/' }
      );
      console.log('Service Worker registered:', registration);
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      throw error;
    }
  }

  /**
   * プッシュ通知を購読
   * @returns {Promise<Object>} 購読結果
   */
  async subscribe() {
    try {
      // 通知許可をリクエスト
      const permission = await this.requestPermission();
      if (permission !== 'granted') {
        throw new Error('Notification permission denied');
      }

      // Service Workerを登録
      const registration = await this.registerServiceWorker();

      // VAPID公開鍵を取得
      const publicKey = await this.getPublicKey();
      const applicationServerKey = this.urlBase64ToUint8Array(publicKey);

      // プッシュマネージャーから購読を取得
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey,
      });

      console.log('Push subscription:', subscription);

      // サーバーに購読情報を送信
      const response = await fetch(`${this.apiBaseUrl}/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          subscription: subscription.toJSON(),
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        console.log('Successfully subscribed to push notifications');
        localStorage.setItem('pri_notification_subscribed', 'true');
        return result;
      } else {
        throw new Error(result.error || 'Subscription failed');
      }
    } catch (error) {
      console.error('Subscribe error:', error);
      throw error;
    }
  }

  /**
   * プッシュ通知の購読を解除
   * @returns {Promise<Object>} 購読解除結果
   */
  async unsubscribe() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        await subscription.unsubscribe();
        console.log('Push subscription unsubscribed');
      }

      // サーバーに購読解除を通知
      const response = await fetch(`${this.apiBaseUrl}/unsubscribe`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        console.log('Successfully unsubscribed from push notifications');
        localStorage.removeItem('pri_notification_subscribed');
        return result;
      } else {
        throw new Error(result.error || 'Unsubscription failed');
      }
    } catch (error) {
      console.error('Unsubscribe error:', error);
      throw error;
    }
  }

  /**
   * 購読状態を確認
   * @returns {Promise<boolean>} 購読しているか
   */
  async isSubscribed() {
    try {
      if (!this.isSupported) {
        return false;
      }

      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      return subscription !== null;
    } catch (error) {
      console.error('Check subscription error:', error);
      return false;
    }
  }

  /**
   * テスト通知を送信
   * @param {string} title - 通知タイトル
   * @param {string} body - 通知本文
   * @returns {Promise<Object>} 送信結果
   */
  async sendTestNotification(
    title = 'テスト通知',
    body = 'これはテスト通知です'
  ) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          title: title,
          body: body,
          data: { type: 'test' },
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        console.log('Test notification sent successfully');
        return result;
      } else {
        throw new Error(result.error || 'Failed to send test notification');
      }
    } catch (error) {
      console.error('Send test notification error:', error);
      throw error;
    }
  }

  /**
   * 食事リマインダーを設定
   * @param {string} mealType - 食事タイプ (breakfast/lunch/dinner)
   * @param {string} reminderTime - リマインダー時刻 (HH:MM)
   * @param {boolean} enabled - 有効/無効
   * @param {string} customMessage - カスタムメッセージ
   * @returns {Promise<Object>} 設定結果
   */
  async setMealReminder(
    mealType,
    reminderTime,
    enabled = true,
    customMessage = null
  ) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/meal-reminder`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          meal_type: mealType,
          reminder_time: reminderTime,
          enabled: enabled,
          custom_message: customMessage,
        }),
      });

      const result = await response.json();

      if (result.status === 'ok') {
        console.log(`Meal reminder set: ${mealType} at ${reminderTime}`);
        return result;
      } else {
        throw new Error(result.error || 'Failed to set meal reminder');
      }
    } catch (error) {
      console.error('Set meal reminder error:', error);
      throw error;
    }
  }

  /**
   * 食事リマインダースケジュールを取得
   * @returns {Promise<Object>} スケジュール情報
   */
  async getMealSchedules() {
    try {
      const response = await fetch(
        `${this.apiBaseUrl}/schedule?user_id=${this.userId}`
      );
      const result = await response.json();

      if (result.status === 'ok') {
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to get meal schedules');
      }
    } catch (error) {
      console.error('Get meal schedules error:', error);
      throw error;
    }
  }

  /**
   * ブラウザ通知を表示（フォールバック）
   * @param {string} title - 通知タイトル
   * @param {Object} options - 通知オプション
   */
  showNotification(title, options = {}) {
    if (!this.isSupported) {
      console.warn('Notifications not supported');
      return;
    }

    if (Notification.permission === 'granted') {
      new Notification(title, {
        icon: options.icon || '/icon-192x192.png',
        badge: options.badge || '/badge-72x72.png',
        body: options.body || '',
        data: options.data || {},
        ...options,
      });
    }
  }
}

// グローバルインスタンスをエクスポート
const notificationManager = new NotificationManager();

// モジュールとしてエクスポート（ES6対応）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NotificationManager;
}
