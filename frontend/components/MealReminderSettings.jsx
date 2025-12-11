/**
 * Meal Reminder Settings Component
 * 食事リマインダー設定UI
 */

import React, { useState, useEffect } from 'react';

const MealReminderSettings = ({ notificationManager }) => {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [schedules, setSchedules] = useState({
    breakfast: { time: '07:00', enabled: false, custom_message: '' },
    lunch: { time: '12:00', enabled: false, custom_message: '' },
    dinner: { time: '18:00', enabled: false, custom_message: '' },
  });
  const [saveStatus, setSaveStatus] = useState('');

  // 食事タイプの日本語名
  const mealNames = {
    breakfast: '朝食',
    lunch: '昼食',
    dinner: '夕食',
  };

  // 初期化
  useEffect(() => {
    initializeSettings();
  }, []);

  /**
   * 設定を初期化
   */
  const initializeSettings = async () => {
    try {
      setIsLoading(true);

      // 購読状態を確認
      const subscribed = await notificationManager.isSubscribed();
      setIsSubscribed(subscribed);

      // 既存のスケジュールを取得
      if (subscribed) {
        const existingSchedules = await notificationManager.getMealSchedules();
        if (existingSchedules) {
          setSchedules((prev) => ({
            ...prev,
            ...existingSchedules,
          }));
        }
      }
    } catch (error) {
      console.error('Initialize settings error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 通知を有効化
   */
  const handleEnableNotifications = async () => {
    try {
      setIsLoading(true);
      setSaveStatus('通知を有効化しています...');

      await notificationManager.subscribe();
      setIsSubscribed(true);
      setSaveStatus('通知が有効になりました');

      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Enable notifications error:', error);
      setSaveStatus('通知の有効化に失敗しました: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 通知を無効化
   */
  const handleDisableNotifications = async () => {
    try {
      setIsLoading(true);
      setSaveStatus('通知を無効化しています...');

      await notificationManager.unsubscribe();
      setIsSubscribed(false);
      setSaveStatus('通知が無効になりました');

      // スケジュールもリセット
      setSchedules({
        breakfast: { time: '07:00', enabled: false, custom_message: '' },
        lunch: { time: '12:00', enabled: false, custom_message: '' },
        dinner: { time: '18:00', enabled: false, custom_message: '' },
      });

      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Disable notifications error:', error);
      setSaveStatus('通知の無効化に失敗しました: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 時刻変更ハンドラ
   */
  const handleTimeChange = (mealType, newTime) => {
    setSchedules((prev) => ({
      ...prev,
      [mealType]: {
        ...prev[mealType],
        time: newTime,
      },
    }));
  };

  /**
   * 有効/無効切り替えハンドラ
   */
  const handleToggleEnabled = (mealType) => {
    setSchedules((prev) => ({
      ...prev,
      [mealType]: {
        ...prev[mealType],
        enabled: !prev[mealType].enabled,
      },
    }));
  };

  /**
   * カスタムメッセージ変更ハンドラ
   */
  const handleMessageChange = (mealType, newMessage) => {
    setSchedules((prev) => ({
      ...prev,
      [mealType]: {
        ...prev[mealType],
        custom_message: newMessage,
      },
    }));
  };

  /**
   * 設定を保存
   */
  const handleSaveSettings = async () => {
    try {
      setIsLoading(true);
      setSaveStatus('設定を保存しています...');

      // 各食事リマインダーを設定
      for (const [mealType, config] of Object.entries(schedules)) {
        await notificationManager.setMealReminder(
          mealType,
          config.time,
          config.enabled,
          config.custom_message || null
        );
      }

      setSaveStatus('設定を保存しました');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Save settings error:', error);
      setSaveStatus('設定の保存に失敗しました: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * テスト通知を送信
   */
  const handleTestNotification = async () => {
    try {
      setSaveStatus('テスト通知を送信しています...');
      await notificationManager.sendTestNotification(
        '食事リマインダーテスト',
        'これはテスト通知です。設定が正しく機能しています。'
      );
      setSaveStatus('テスト通知を送信しました');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Test notification error:', error);
      setSaveStatus('テスト通知の送信に失敗しました: ' + error.message);
    }
  };

  if (isLoading && !isSubscribed) {
    return (
      <div className="meal-reminder-settings loading">
        <div className="loading-spinner">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="meal-reminder-settings">
      <h2 className="settings-title">食事リマインダー設定</h2>

      {/* 通知有効化セクション */}
      <div className="notification-status-section">
        <div className="status-info">
          <span className={`status-indicator ${isSubscribed ? 'active' : ''}`}>
            {isSubscribed ? '有効' : '無効'}
          </span>
          <span className="status-text">
            {isSubscribed
              ? 'プッシュ通知が有効になっています'
              : 'プッシュ通知を有効にしてください'}
          </span>
        </div>

        <div className="notification-actions">
          {!isSubscribed ? (
            <button
              className="btn btn-primary"
              onClick={handleEnableNotifications}
              disabled={isLoading}
            >
              通知を有効にする
            </button>
          ) : (
            <>
              <button
                className="btn btn-secondary"
                onClick={handleTestNotification}
                disabled={isLoading}
              >
                テスト通知
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDisableNotifications}
                disabled={isLoading}
              >
                通知を無効にする
              </button>
            </>
          )}
        </div>
      </div>

      {/* リマインダー設定セクション */}
      {isSubscribed && (
        <div className="reminder-settings-section">
          <h3 className="section-subtitle">リマインダー時刻設定</h3>

          {Object.entries(schedules).map(([mealType, config]) => (
            <div key={mealType} className="meal-reminder-item">
              <div className="meal-header">
                <label className="meal-toggle">
                  <input
                    type="checkbox"
                    checked={config.enabled}
                    onChange={() => handleToggleEnabled(mealType)}
                  />
                  <span className="meal-name">{mealNames[mealType]}</span>
                </label>

                <input
                  type="time"
                  className="time-input"
                  value={config.time}
                  onChange={(e) => handleTimeChange(mealType, e.target.value)}
                  disabled={!config.enabled}
                />
              </div>

              {config.enabled && (
                <div className="meal-options">
                  <label className="custom-message-label">
                    カスタムメッセージ（任意）
                  </label>
                  <input
                    type="text"
                    className="custom-message-input"
                    placeholder={`今日の${mealNames[mealType]}は何にしますか？`}
                    value={config.custom_message}
                    onChange={(e) =>
                      handleMessageChange(mealType, e.target.value)
                    }
                  />
                </div>
              )}
            </div>
          ))}

          <div className="settings-actions">
            <button
              className="btn btn-primary btn-large"
              onClick={handleSaveSettings}
              disabled={isLoading}
            >
              設定を保存
            </button>
          </div>
        </div>
      )}

      {/* ステータスメッセージ */}
      {saveStatus && (
        <div className="save-status-message">
          <span>{saveStatus}</span>
        </div>
      )}

      <style jsx>{`
        .meal-reminder-settings {
          max-width: 800px;
          margin: 0 auto;
          padding: 24px;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .settings-title {
          margin: 0 0 24px 0;
          font-size: 24px;
          font-weight: 600;
          color: #333;
        }

        .notification-status-section {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 6px;
          margin-bottom: 24px;
        }

        .status-info {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .status-indicator {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 500;
          background: #e0e0e0;
          color: #666;
        }

        .status-indicator.active {
          background: #4caf50;
          color: white;
        }

        .status-text {
          font-size: 14px;
          color: #666;
        }

        .notification-actions {
          display: flex;
          gap: 12px;
        }

        .reminder-settings-section {
          margin-top: 24px;
        }

        .section-subtitle {
          margin: 0 0 16px 0;
          font-size: 18px;
          font-weight: 600;
          color: #555;
        }

        .meal-reminder-item {
          padding: 16px;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          margin-bottom: 12px;
        }

        .meal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .meal-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .meal-toggle input[type='checkbox'] {
          width: 20px;
          height: 20px;
          cursor: pointer;
        }

        .meal-name {
          font-size: 16px;
          font-weight: 500;
          color: #333;
        }

        .time-input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 16px;
        }

        .time-input:disabled {
          background: #f5f5f5;
          cursor: not-allowed;
        }

        .meal-options {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #f0f0f0;
        }

        .custom-message-label {
          display: block;
          margin-bottom: 8px;
          font-size: 14px;
          color: #666;
        }

        .custom-message-input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .settings-actions {
          margin-top: 24px;
          display: flex;
          justify-content: center;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-primary {
          background: #2196f3;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #1976d2;
        }

        .btn-secondary {
          background: #757575;
          color: white;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #616161;
        }

        .btn-danger {
          background: #f44336;
          color: white;
        }

        .btn-danger:hover:not(:disabled) {
          background: #d32f2f;
        }

        .btn-large {
          padding: 12px 32px;
          font-size: 16px;
        }

        .save-status-message {
          margin-top: 16px;
          padding: 12px;
          background: #e3f2fd;
          border-left: 4px solid #2196f3;
          border-radius: 4px;
          text-align: center;
        }

        .save-status-message span {
          font-size: 14px;
          color: #1976d2;
        }

        .loading {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 200px;
        }

        .loading-spinner {
          font-size: 16px;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default MealReminderSettings;
