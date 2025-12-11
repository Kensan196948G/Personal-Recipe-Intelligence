"""
IoTサービステスト

IoT連携機能のテストケース。
デバイス登録、在庫同期、アラート生成などをテストする。
"""

import pytest
import tempfile
import shutil
from datetime import datetime, timedelta

from backend.services.iot_service import (
  IoTService,
  DeviceType,
  ProtocolType,
  AlertType
)


@pytest.fixture
def temp_data_dir():
  """一時データディレクトリ"""
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)


@pytest.fixture
def iot_service(temp_data_dir):
  """IoTサービスインスタンス"""
  return IoTService(data_dir=temp_data_dir)


class TestDeviceManagement:
  """デバイス管理テスト"""

  def test_register_device(self, iot_service):
    """デバイス登録テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP,
      endpoint="http://example.com/api",
      metadata={"model": "FridgeX100"}
    )

    assert device.device_id.startswith("dev_")
    assert device.name == "Test Fridge"
    assert device.device_type == DeviceType.SMART_FRIDGE
    assert device.protocol == ProtocolType.HTTP
    assert device.endpoint == "http://example.com/api"
    assert device.api_key.startswith("iot_")
    assert device.is_active is True
    assert device.metadata["model"] == "FridgeX100"

  def test_get_device(self, iot_service):
    """デバイス取得テスト"""
    device = iot_service.register_device(
      name="Test Scale",
      device_type=DeviceType.SMART_SCALE,
      protocol=ProtocolType.MQTT,
      mqtt_topic="home/scale/data"
    )

    retrieved = iot_service.get_device(device.device_id)
    assert retrieved is not None
    assert retrieved.device_id == device.device_id
    assert retrieved.name == "Test Scale"

  def test_get_device_not_found(self, iot_service):
    """存在しないデバイス取得テスト"""
    device = iot_service.get_device("nonexistent_id")
    assert device is None

  def test_get_devices(self, iot_service):
    """デバイス一覧取得テスト"""
    iot_service.register_device(
      name="Fridge 1",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )
    iot_service.register_device(
      name="Scale 1",
      device_type=DeviceType.SMART_SCALE,
      protocol=ProtocolType.MQTT
    )

    devices = iot_service.get_devices()
    assert len(devices) == 2

  def test_get_devices_filtered(self, iot_service):
    """フィルター付きデバイス一覧取得テスト"""
    iot_service.register_device(
      name="Active Device",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    devices = iot_service.get_devices(is_active=True)
    assert len(devices) == 1
    assert devices[0].is_active is True

  def test_delete_device(self, iot_service):
    """デバイス削除テスト"""
    device = iot_service.register_device(
      name="To Delete",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    success = iot_service.delete_device(device.device_id)
    assert success is True

    retrieved = iot_service.get_device(device.device_id)
    assert retrieved is None

  def test_delete_device_not_found(self, iot_service):
    """存在しないデバイス削除テスト"""
    success = iot_service.delete_device("nonexistent_id")
    assert success is False

  def test_verify_api_key(self, iot_service):
    """APIキー検証テスト"""
    device = iot_service.register_device(
      name="Test Device",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    # 正しいAPIキー
    assert iot_service.verify_api_key(device.device_id, device.api_key) is True

    # 間違ったAPIキー
    assert iot_service.verify_api_key(device.device_id, "wrong_key") is False

    # 存在しないデバイス
    assert iot_service.verify_api_key("nonexistent_id", device.api_key) is False


class TestInventoryManagement:
  """在庫管理テスト"""

  def test_sync_inventory(self, iot_service):
    """在庫同期テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {
        "name": "牛乳",
        "quantity": 2.0,
        "unit": "本",
        "category": "乳製品",
        "expiry_date": (datetime.now() + timedelta(days=5)).isoformat()
      },
      {
        "name": "卵",
        "quantity": 6.0,
        "unit": "個",
        "category": "卵",
        "expiry_date": (datetime.now() + timedelta(days=10)).isoformat()
      }
    ]

    synced_items = iot_service.sync_inventory(device.device_id, items_data)

    assert len(synced_items) == 2
    assert synced_items[0].name == "牛乳"
    assert synced_items[0].quantity == 2.0
    assert synced_items[0].device_id == device.device_id
    assert synced_items[1].name == "卵"

  def test_sync_inventory_replaces_existing(self, iot_service):
    """在庫同期が既存データを置き換えることをテスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    # 初回同期
    items_data_1 = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data_1)

    # 2回目同期（上書き）
    items_data_2 = [
      {"name": "卵", "quantity": 6.0, "unit": "個"}
    ]
    iot_service.sync_inventory(device.device_id, items_data_2)

    inventory = iot_service.get_inventory(device_id=device.device_id)
    assert len(inventory) == 1
    assert inventory[0].name == "卵"

  def test_sync_inventory_invalid_device(self, iot_service):
    """存在しないデバイスでの在庫同期テスト"""
    with pytest.raises(ValueError):
      iot_service.sync_inventory("nonexistent_id", [])

  def test_get_inventory(self, iot_service):
    """在庫一覧取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本", "category": "乳製品"},
      {"name": "卵", "quantity": 6.0, "unit": "個", "category": "卵"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    inventory = iot_service.get_inventory()
    assert len(inventory) == 2

  def test_get_inventory_filtered_by_device(self, iot_service):
    """デバイスIDでフィルターした在庫取得テスト"""
    device1 = iot_service.register_device(
      name="Fridge 1",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )
    device2 = iot_service.register_device(
      name="Fridge 2",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    iot_service.sync_inventory(device1.device_id, [
      {"name": "牛乳", "quantity": 2.0, "unit": "本"}
    ])
    iot_service.sync_inventory(device2.device_id, [
      {"name": "卵", "quantity": 6.0, "unit": "個"}
    ])

    inventory = iot_service.get_inventory(device_id=device1.device_id)
    assert len(inventory) == 1
    assert inventory[0].name == "牛乳"

  def test_get_inventory_filtered_by_category(self, iot_service):
    """カテゴリでフィルターした在庫取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本", "category": "乳製品"},
      {"name": "ヨーグルト", "quantity": 3.0, "unit": "個", "category": "乳製品"},
      {"name": "卵", "quantity": 6.0, "unit": "個", "category": "卵"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    inventory = iot_service.get_inventory(category="乳製品")
    assert len(inventory) == 2
    assert all(item.category == "乳製品" for item in inventory)

  def test_get_inventory_item(self, iot_service):
    """在庫アイテム詳細取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本"}
    ]
    synced_items = iot_service.sync_inventory(device.device_id, items_data)

    item = iot_service.get_inventory_item(synced_items[0].item_id)
    assert item is not None
    assert item.name == "牛乳"


class TestAlertManagement:
  """アラート管理テスト"""

  def test_expiry_warning_alert(self, iot_service):
    """賞味期限警告アラート生成テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    # 3日後に期限切れ
    items_data = [
      {
        "name": "牛乳",
        "quantity": 2.0,
        "unit": "本",
        "expiry_date": (datetime.now() + timedelta(days=3)).isoformat()
      }
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts(alert_type=AlertType.EXPIRY_WARNING)
    assert len(alerts) > 0
    assert alerts[0].alert_type == AlertType.EXPIRY_WARNING
    assert "牛乳" in alerts[0].message

  def test_expired_alert(self, iot_service):
    """期限切れアラート生成テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    # 既に期限切れ
    items_data = [
      {
        "name": "牛乳",
        "quantity": 2.0,
        "unit": "本",
        "expiry_date": (datetime.now() - timedelta(days=1)).isoformat()
      }
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts(alert_type=AlertType.EXPIRED)
    assert len(alerts) > 0
    assert alerts[0].alert_type == AlertType.EXPIRED

  def test_out_of_stock_alert(self, iot_service):
    """在庫切れアラート生成テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 0.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts(alert_type=AlertType.OUT_OF_STOCK)
    assert len(alerts) > 0
    assert alerts[0].alert_type == AlertType.OUT_OF_STOCK

  def test_low_stock_alert(self, iot_service):
    """在庫少アラート生成テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 1.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts(alert_type=AlertType.LOW_STOCK)
    assert len(alerts) > 0
    assert alerts[0].alert_type == AlertType.LOW_STOCK

  def test_get_alerts(self, iot_service):
    """アラート一覧取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 0.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts()
    assert len(alerts) > 0

  def test_get_alerts_filtered(self, iot_service):
    """フィルター付きアラート取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 0.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    # 未読のみ
    alerts = iot_service.get_alerts(is_read=False)
    assert len(alerts) > 0
    assert all(not alert.is_read for alert in alerts)

  def test_mark_alert_as_read(self, iot_service):
    """アラート既読化テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 0.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts()
    alert_id = alerts[0].alert_id

    success = iot_service.mark_alert_as_read(alert_id)
    assert success is True

    # 既読になっているか確認
    updated_alerts = iot_service.get_alerts(is_read=True)
    assert any(a.alert_id == alert_id for a in updated_alerts)

  def test_delete_alert(self, iot_service):
    """アラート削除テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 0.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    alerts = iot_service.get_alerts()
    alert_id = alerts[0].alert_id

    success = iot_service.delete_alert(alert_id)
    assert success is True

    # 削除されているか確認
    all_alerts = iot_service.get_alerts()
    assert not any(a.alert_id == alert_id for a in all_alerts)


class TestStatistics:
  """統計情報テスト"""

  def test_get_statistics(self, iot_service):
    """統計情報取得テスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本", "category": "乳製品"},
      {"name": "卵", "quantity": 0.0, "unit": "個", "category": "卵"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    stats = iot_service.get_statistics()

    assert stats["total_devices"] == 1
    assert stats["active_devices"] == 1
    assert stats["total_items"] == 2
    assert stats["total_quantity"] == 2.0
    assert "乳製品" in stats["categories"]
    assert "卵" in stats["categories"]
    assert stats["unread_alerts"] > 0
    assert AlertType.OUT_OF_STOCK in stats["alert_breakdown"]


class TestDataPersistence:
  """データ永続化テスト"""

  def test_data_persists_across_instances(self, temp_data_dir):
    """インスタンス間でデータが永続化されることをテスト"""
    # 1つ目のインスタンス
    service1 = IoTService(data_dir=temp_data_dir)
    device = service1.register_device(
      name="Test Device",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )
    device_id = device.device_id

    # 2つ目のインスタンス（同じディレクトリ）
    service2 = IoTService(data_dir=temp_data_dir)
    retrieved = service2.get_device(device_id)

    assert retrieved is not None
    assert retrieved.device_id == device_id
    assert retrieved.name == "Test Device"

  def test_device_deletion_cascades_to_inventory(self, iot_service):
    """デバイス削除時に関連在庫も削除されることをテスト"""
    device = iot_service.register_device(
      name="Test Fridge",
      device_type=DeviceType.SMART_FRIDGE,
      protocol=ProtocolType.HTTP
    )

    items_data = [
      {"name": "牛乳", "quantity": 2.0, "unit": "本"}
    ]
    iot_service.sync_inventory(device.device_id, items_data)

    # デバイス削除
    iot_service.delete_device(device.device_id)

    # 在庫も削除されているか確認
    inventory = iot_service.get_inventory(device_id=device.device_id)
    assert len(inventory) == 0
