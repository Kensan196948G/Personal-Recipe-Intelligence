/**
 * Notification Manager Tests
 * NotificationManagerのユニットテスト
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'bun:test';

// NotificationManagerをモック環境でテスト
describe('NotificationManager', () => {
  let notificationManager;
  let mockFetch;
  let mockServiceWorker;
  let mockNotification;

  beforeEach(() => {
    // fetchをモック
    mockFetch = vi.fn();
    global.fetch = mockFetch;

    // Service Workerをモック
    mockServiceWorker = {
      register: vi.fn().mockResolvedValue({
        pushManager: {
          subscribe: vi.fn().mockResolvedValue({
            toJSON: () => ({
              endpoint: 'https://example.com/push',
              keys: {
                p256dh: 'test-p256dh',
                auth: 'test-auth',
              },
            }),
          }),
          getSubscription: vi.fn().mockResolvedValue(null),
        },
      }),
      ready: Promise.resolve({
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue(null),
        },
      }),
      getRegistrations: vi.fn().mockResolvedValue([]),
    };

    global.navigator = {
      serviceWorker: mockServiceWorker,
    };

    // Notificationをモック
    mockNotification = {
      permission: 'default',
      requestPermission: vi.fn().mockResolvedValue('granted'),
    };
    global.Notification = mockNotification;

    // sessionStorageをモック
    global.sessionStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    };

    // localStorageをモック
    global.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    };

    // window.atobをモック
    global.window = {
      atob: vi.fn((str) => str),
    };

    // NotificationManagerをインポート（動的）
    const NotificationManager = require('../js/notification-manager.js');
    notificationManager = new NotificationManager();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with default values', () => {
      expect(notificationManager.apiBaseUrl).toBe('/api/v1/notifications');
      expect(notificationManager.userId).toBeTruthy();
      expect(notificationManager.publicKey).toBeNull();
    });

    it('should check if notifications are supported', () => {
      const isSupported = notificationManager.isNotificationSupported();
      expect(isSupported).toBe(true);
    });
  });

  describe('User ID Management', () => {
    it('should generate user ID if not exists', () => {
      global.sessionStorage.getItem.mockReturnValue(null);

      const userId = notificationManager.getUserId();

      expect(userId).toBeTruthy();
      expect(userId).toContain('user_');
      expect(global.sessionStorage.setItem).toHaveBeenCalledWith(
        'pri_user_id',
        expect.any(String)
      );
    });

    it('should retrieve existing user ID', () => {
      const existingUserId = 'user_12345';
      global.sessionStorage.getItem.mockReturnValue(existingUserId);

      const userId = notificationManager.getUserId();

      expect(userId).toBe(existingUserId);
    });
  });

  describe('Permission Request', () => {
    it('should request notification permission', async () => {
      const permission = await notificationManager.requestPermission();

      expect(permission).toBe('granted');
      expect(mockNotification.requestPermission).toHaveBeenCalled();
    });

    it('should return granted if already granted', async () => {
      mockNotification.permission = 'granted';

      const permission = await notificationManager.requestPermission();

      expect(permission).toBe('granted');
      expect(mockNotification.requestPermission).not.toHaveBeenCalled();
    });

    it('should throw error if not supported', async () => {
      notificationManager.isSupported = false;

      await expect(notificationManager.requestPermission()).rejects.toThrow(
        'Push notifications are not supported'
      );
    });
  });

  describe('Public Key Retrieval', () => {
    it('should fetch public key from API', async () => {
      const mockPublicKey = 'test-public-key';
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: { public_key: mockPublicKey },
        }),
      });

      const publicKey = await notificationManager.getPublicKey();

      expect(publicKey).toBe(mockPublicKey);
      expect(notificationManager.publicKey).toBe(mockPublicKey);
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/notifications/public-key'
      );
    });

    it('should return cached public key', async () => {
      notificationManager.publicKey = 'cached-key';

      const publicKey = await notificationManager.getPublicKey();

      expect(publicKey).toBe('cached-key');
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should throw error on API failure', async () => {
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'error',
          error: 'API Error',
        }),
      });

      await expect(notificationManager.getPublicKey()).rejects.toThrow();
    });
  });

  describe('URL Base64 Conversion', () => {
    it('should convert URLBase64 to Uint8Array', () => {
      const base64String = 'test';
      const result = notificationManager.urlBase64ToUint8Array(base64String);

      expect(result).toBeInstanceOf(Uint8Array);
    });
  });

  describe('Service Worker Registration', () => {
    it('should register service worker', async () => {
      const registration = await notificationManager.registerServiceWorker();

      expect(registration).toBeDefined();
      expect(mockServiceWorker.register).toHaveBeenCalledWith(
        '/service-worker.js',
        { scope: '/' }
      );
    });

    it('should throw error if not supported', async () => {
      notificationManager.isSupported = false;

      await expect(
        notificationManager.registerServiceWorker()
      ).rejects.toThrow('Service Worker is not supported');
    });
  });

  describe('Subscription Management', () => {
    it('should subscribe to push notifications', async () => {
      mockNotification.permission = 'granted';
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: { subscribed: true },
        }),
      });

      const result = await notificationManager.subscribe();

      expect(result.status).toBe('ok');
      expect(global.localStorage.setItem).toHaveBeenCalledWith(
        'pri_notification_subscribed',
        'true'
      );
    });

    it('should throw error if permission denied', async () => {
      mockNotification.permission = 'denied';
      mockNotification.requestPermission.mockResolvedValue('denied');

      await expect(notificationManager.subscribe()).rejects.toThrow(
        'Notification permission denied'
      );
    });

    it('should unsubscribe from push notifications', async () => {
      mockServiceWorker.ready = Promise.resolve({
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue({
            unsubscribe: vi.fn().mockResolvedValue(true),
          }),
        },
      });

      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: { subscribed: false },
        }),
      });

      const result = await notificationManager.unsubscribe();

      expect(result.status).toBe('ok');
      expect(global.localStorage.removeItem).toHaveBeenCalledWith(
        'pri_notification_subscribed'
      );
    });

    it('should check subscription status', async () => {
      mockServiceWorker.ready = Promise.resolve({
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue({ endpoint: 'test' }),
        },
      });

      const isSubscribed = await notificationManager.isSubscribed();

      expect(isSubscribed).toBe(true);
    });
  });

  describe('Notification Sending', () => {
    it('should send test notification', async () => {
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: { sent: true },
        }),
      });

      const result = await notificationManager.sendTestNotification(
        'Test',
        'Test Body'
      );

      expect(result.status).toBe('ok');
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/notifications/send',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    it('should use default test message', async () => {
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: { sent: true },
        }),
      });

      await notificationManager.sendTestNotification();

      const callArgs = mockFetch.mock.calls[0][1];
      const body = JSON.parse(callArgs.body);

      expect(body.title).toBe('テスト通知');
      expect(body.body).toBe('これはテスト通知です');
    });
  });

  describe('Meal Reminder Management', () => {
    it('should set meal reminder', async () => {
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: {
            meal_type: 'breakfast',
            reminder_time: '07:00',
            enabled: true,
          },
        }),
      });

      const result = await notificationManager.setMealReminder(
        'breakfast',
        '07:00',
        true,
        'Good morning!'
      );

      expect(result.status).toBe('ok');
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/notifications/meal-reminder',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should get meal schedules', async () => {
      const mockSchedules = {
        breakfast: { time: '07:00', enabled: true },
        lunch: { time: '12:00', enabled: true },
      };

      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'ok',
          data: mockSchedules,
        }),
      });

      const schedules = await notificationManager.getMealSchedules();

      expect(schedules).toEqual(mockSchedules);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/notifications/schedule?user_id=')
      );
    });

    it('should handle meal reminder error', async () => {
      mockFetch.mockResolvedValue({
        json: async () => ({
          status: 'error',
          error: 'Invalid meal type',
        }),
      });

      await expect(
        notificationManager.setMealReminder('invalid', '07:00')
      ).rejects.toThrow('Invalid meal type');
    });
  });

  describe('Browser Notification', () => {
    it('should show browser notification', () => {
      mockNotification.permission = 'granted';
      const mockNotificationInstance = vi.fn();
      global.Notification = mockNotificationInstance;

      notificationManager.showNotification('Test Title', {
        body: 'Test Body',
      });

      expect(mockNotificationInstance).toHaveBeenCalledWith(
        'Test Title',
        expect.objectContaining({
          body: 'Test Body',
        })
      );
    });

    it('should not show notification if permission not granted', () => {
      mockNotification.permission = 'denied';
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      notificationManager.isSupported = false;
      notificationManager.showNotification('Test');

      expect(consoleSpy).toHaveBeenCalledWith('Notifications not supported');
      consoleSpy.mockRestore();
    });
  });
});
