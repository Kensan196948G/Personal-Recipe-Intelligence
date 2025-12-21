/**
 * IoTダッシュボードコンポーネント
 *
 * スマートデバイス連携、在庫管理、アラート表示を統合したダッシュボード。
 */

import React, { useState, useEffect } from 'react';
import './IoTDashboard.css';

const API_BASE = '/api/v1/iot';

const IoTDashboard = () => {
  const [devices, setDevices] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showAddDevice, setShowAddDevice] = useState(false);

  // 新規デバイスフォーム
  const [newDevice, setNewDevice] = useState({
    name: '',
    device_type: 'smart_fridge',
    protocol: 'http',
    endpoint: '',
    mqtt_topic: '',
    webhook_url: ''
  });

  // データ取得
  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 30000); // 30秒ごとに更新
    return () => clearInterval(interval);
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchDevices(),
        fetchInventory(),
        fetchAlerts(),
        fetchStatistics()
      ]);
      setError(null);
    } catch (err) {
      setError('データ取得に失敗しました');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDevices = async () => {
    const response = await fetch(`${API_BASE}/devices`);
    const data = await response.json();
    if (data.status === 'ok') {
      setDevices(data.data);
    }
  };

  const fetchInventory = async () => {
    const response = await fetch(`${API_BASE}/inventory`);
    const data = await response.json();
    if (data.status === 'ok') {
      setInventory(data.data);
    }
  };

  const fetchAlerts = async () => {
    const response = await fetch(`${API_BASE}/alerts?is_read=false`);
    const data = await response.json();
    if (data.status === 'ok') {
      setAlerts(data.data);
    }
  };

  const fetchStatistics = async () => {
    const response = await fetch(`${API_BASE}/statistics`);
    const data = await response.json();
    if (data.status === 'ok') {
      setStatistics(data.data);
    }
  };

  // デバイス登録
  const handleAddDevice = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/devices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newDevice)
      });
      const data = await response.json();

      if (data.status === 'ok') {
        alert(`デバイス登録成功!\nAPI Key: ${data.data.api_key}\n※このAPIキーは再表示されません。必ず保存してください。`);
        setShowAddDevice(false);
        setNewDevice({
          name: '',
          device_type: 'smart_fridge',
          protocol: 'http',
          endpoint: '',
          mqtt_topic: '',
          webhook_url: ''
        });
        fetchDevices();
      }
    } catch (err) {
      alert('デバイス登録に失敗しました');
      console.error(err);
    }
  };

  // デバイス削除
  const handleDeleteDevice = async (deviceId) => {
    if (!confirm('このデバイスを削除しますか？関連する在庫データも削除されます。')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/devices/${deviceId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.status === 'ok') {
        alert('デバイスを削除しました');
        fetchAllData();
      }
    } catch (err) {
      alert('削除に失敗しました');
      console.error(err);
    }
  };

  // アラートを既読にする
  const handleMarkAlertAsRead = async (alertId) => {
    try {
      const response = await fetch(`${API_BASE}/alerts/${alertId}/read`, {
        method: 'PATCH'
      });
      const data = await response.json();

      if (data.status === 'ok') {
        fetchAlerts();
        fetchStatistics();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // アラート削除
  const handleDeleteAlert = async (alertId) => {
    try {
      const response = await fetch(`${API_BASE}/alerts/${alertId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.status === 'ok') {
        fetchAlerts();
        fetchStatistics();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // アラートタイプごとの色
  const getAlertColor = (type) => {
    switch (type) {
      case 'expired':
        return 'alert-danger';
      case 'expiry_warning':
        return 'alert-warning';
      case 'out_of_stock':
        return 'alert-danger';
      case 'low_stock':
        return 'alert-info';
      default:
        return 'alert-secondary';
    }
  };

  // デバイスタイプのアイコン
  const getDeviceIcon = (type) => {
    switch (type) {
      case 'smart_fridge':
        return '🧊';
      case 'smart_scale':
        return '⚖️';
      case 'barcode_scanner':
        return '📱';
      default:
        return '📡';
    }
  };

  // 賞味期限までの日数を計算
  const getDaysUntilExpiry = (expiryDate) => {
    if (!expiryDate) return null;
    const expiry = new Date(expiryDate);
    const now = new Date();
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  // ローディング表示
  if (loading && !statistics) {
    return (
      <div className="iot-dashboard">
        <div className="loading">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="iot-dashboard">
      <div className="dashboard-header">
        <h1>IoT連携ダッシュボード</h1>
        <button className="btn-refresh" onClick={fetchAllData}>
          🔄 更新
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* 統計サマリー */}
      {statistics && (
        <div className="statistics-summary">
          <div className="stat-card">
            <div className="stat-label">接続デバイス</div>
            <div className="stat-value">
              {statistics.active_devices} / {statistics.total_devices}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">在庫アイテム</div>
            <div className="stat-value">{statistics.total_items}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">未読アラート</div>
            <div className="stat-value alert-count">{statistics.unread_alerts}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">総在庫数</div>
            <div className="stat-value">{statistics.total_quantity.toFixed(1)}</div>
          </div>
        </div>
      )}

      {/* タブナビゲーション */}
      <div className="tab-navigation">
        <button
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          概要
        </button>
        <button
          className={activeTab === 'devices' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('devices')}
        >
          デバイス
        </button>
        <button
          className={activeTab === 'inventory' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('inventory')}
        >
          在庫
        </button>
        <button
          className={activeTab === 'alerts' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('alerts')}
        >
          アラート
          {alerts.length > 0 && <span className="badge">{alerts.length}</span>}
        </button>
      </div>

      {/* 概要タブ */}
      {activeTab === 'overview' && (
        <div className="tab-content">
          <div className="overview-grid">
            {/* アラート一覧（最新5件） */}
            <div className="overview-section">
              <h2>最新アラート</h2>
              {alerts.length === 0 ? (
                <p className="empty-message">アラートはありません</p>
              ) : (
                <div className="alert-list-compact">
                  {alerts.slice(0, 5).map((alert) => (
                    <div key={alert.alert_id} className={`alert-item-compact ${getAlertColor(alert.alert_type)}`}>
                      <div className="alert-message">{alert.message}</div>
                      <div className="alert-time">{new Date(alert.created_at).toLocaleString('ja-JP')}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* カテゴリ別在庫 */}
            <div className="overview-section">
              <h2>カテゴリ別在庫</h2>
              {statistics && statistics.categories && Object.keys(statistics.categories).length > 0 ? (
                <div className="category-list">
                  {Object.entries(statistics.categories).map(([category, data]) => (
                    <div key={category} className="category-item">
                      <div className="category-name">{category}</div>
                      <div className="category-stats">
                        <span>{data.count}品目</span>
                        <span>{data.quantity.toFixed(1)}個</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="empty-message">在庫データがありません</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* デバイスタブ */}
      {activeTab === 'devices' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>登録デバイス</h2>
            <button className="btn-primary" onClick={() => setShowAddDevice(true)}>
              ➕ デバイス追加
            </button>
          </div>

          {devices.length === 0 ? (
            <p className="empty-message">デバイスが登録されていません</p>
          ) : (
            <div className="device-grid">
              {devices.map((device) => (
                <div key={device.device_id} className={`device-card ${device.is_active ? 'active' : 'inactive'}`}>
                  <div className="device-header">
                    <div className="device-icon">{getDeviceIcon(device.device_type)}</div>
                    <div className="device-info">
                      <h3>{device.name}</h3>
                      <div className="device-type">{device.device_type}</div>
                    </div>
                    <div className={`status-badge ${device.is_active ? 'active' : 'inactive'}`}>
                      {device.is_active ? 'アクティブ' : '非アクティブ'}
                    </div>
                  </div>
                  <div className="device-details">
                    <div className="detail-row">
                      <span className="label">プロトコル:</span>
                      <span className="value">{device.protocol.toUpperCase()}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">最終同期:</span>
                      <span className="value">
                        {device.last_sync ? new Date(device.last_sync).toLocaleString('ja-JP') : '未同期'}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">登録日:</span>
                      <span className="value">{new Date(device.created_at).toLocaleDateString('ja-JP')}</span>
                    </div>
                  </div>
                  <div className="device-actions">
                    <button className="btn-danger-sm" onClick={() => handleDeleteDevice(device.device_id)}>
                      削除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* デバイス追加モーダル */}
          {showAddDevice && (
            <div className="modal-overlay" onClick={() => setShowAddDevice(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h2>デバイス追加</h2>
                <form onSubmit={handleAddDevice}>
                  <div className="form-group">
                    <label>デバイス名 *</label>
                    <input
                      type="text"
                      value={newDevice.name}
                      onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>デバイスタイプ *</label>
                    <select
                      value={newDevice.device_type}
                      onChange={(e) => setNewDevice({ ...newDevice, device_type: e.target.value })}
                    >
                      <option value="smart_fridge">スマート冷蔵庫</option>
                      <option value="smart_scale">スマート計量器</option>
                      <option value="barcode_scanner">バーコードスキャナー</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>プロトコル *</label>
                    <select
                      value={newDevice.protocol}
                      onChange={(e) => setNewDevice({ ...newDevice, protocol: e.target.value })}
                    >
                      <option value="http">HTTP</option>
                      <option value="mqtt">MQTT</option>
                      <option value="webhook">Webhook</option>
                    </select>
                  </div>
                  {newDevice.protocol === 'http' && (
                    <div className="form-group">
                      <label>エンドポイント</label>
                      <input
                        type="text"
                        value={newDevice.endpoint}
                        onChange={(e) => setNewDevice({ ...newDevice, endpoint: e.target.value })}
                        placeholder="http://example.com/api"
                      />
                    </div>
                  )}
                  {newDevice.protocol === 'mqtt' && (
                    <div className="form-group">
                      <label>MQTTトピック</label>
                      <input
                        type="text"
                        value={newDevice.mqtt_topic}
                        onChange={(e) => setNewDevice({ ...newDevice, mqtt_topic: e.target.value })}
                        placeholder="home/fridge/inventory"
                      />
                    </div>
                  )}
                  {newDevice.protocol === 'webhook' && (
                    <div className="form-group">
                      <label>Webhook URL</label>
                      <input
                        type="text"
                        value={newDevice.webhook_url}
                        onChange={(e) => setNewDevice({ ...newDevice, webhook_url: e.target.value })}
                        placeholder="https://example.com/webhook"
                      />
                    </div>
                  )}
                  <div className="form-actions">
                    <button type="button" className="btn-secondary" onClick={() => setShowAddDevice(false)}>
                      キャンセル
                    </button>
                    <button type="submit" className="btn-primary">
                      登録
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 在庫タブ */}
      {activeTab === 'inventory' && (
        <div className="tab-content">
          <h2>在庫一覧</h2>
          {inventory.length === 0 ? (
            <p className="empty-message">在庫データがありません</p>
          ) : (
            <div className="inventory-table">
              <table>
                <thead>
                  <tr>
                    <th>商品名</th>
                    <th>数量</th>
                    <th>カテゴリ</th>
                    <th>賞味期限</th>
                    <th>デバイス</th>
                    <th>同期日時</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.map((item) => {
                    const daysUntilExpiry = getDaysUntilExpiry(item.expiry_date);
                    const expiryClass =
                      daysUntilExpiry !== null
                        ? daysUntilExpiry < 0
                          ? 'expired'
                          : daysUntilExpiry <= 3
                          ? 'expiring-soon'
                          : ''
                        : '';

                    return (
                      <tr key={item.item_id}>
                        <td>{item.name}</td>
                        <td>
                          {item.quantity} {item.unit}
                        </td>
                        <td>{item.category || '未分類'}</td>
                        <td className={expiryClass}>
                          {item.expiry_date ? (
                            <>
                              {new Date(item.expiry_date).toLocaleDateString('ja-JP')}
                              {daysUntilExpiry !== null && (
                                <span className="days-until">
                                  {daysUntilExpiry < 0
                                    ? `(${Math.abs(daysUntilExpiry)}日超過)`
                                    : `(残り${daysUntilExpiry}日)`}
                                </span>
                              )}
                            </>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td>
                          {devices.find((d) => d.device_id === item.device_id)?.name || item.device_id}
                        </td>
                        <td>{new Date(item.synced_at).toLocaleString('ja-JP')}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* アラートタブ */}
      {activeTab === 'alerts' && (
        <div className="tab-content">
          <h2>アラート一覧</h2>
          {alerts.length === 0 ? (
            <p className="empty-message">アラートはありません</p>
          ) : (
            <div className="alerts-list">
              {alerts.map((alert) => (
                <div key={alert.alert_id} className={`alert-card ${getAlertColor(alert.alert_type)}`}>
                  <div className="alert-header">
                    <div className="alert-type-badge">{alert.alert_type}</div>
                    <div className="alert-actions">
                      <button
                        className="btn-icon"
                        onClick={() => handleMarkAlertAsRead(alert.alert_id)}
                        title="既読にする"
                      >
                        ✓
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() => handleDeleteAlert(alert.alert_id)}
                        title="削除"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                  <div className="alert-body">
                    <div className="alert-message-full">{alert.message}</div>
                    <div className="alert-details">
                      <div className="detail-item">
                        <span className="label">商品:</span>
                        <span className="value">{alert.item_name}</span>
                      </div>
                      <div className="detail-item">
                        <span className="label">デバイス:</span>
                        <span className="value">
                          {devices.find((d) => d.device_id === alert.device_id)?.name || alert.device_id}
                        </span>
                      </div>
                      <div className="detail-item">
                        <span className="label">発生日時:</span>
                        <span className="value">{new Date(alert.created_at).toLocaleString('ja-JP')}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IoTDashboard;
