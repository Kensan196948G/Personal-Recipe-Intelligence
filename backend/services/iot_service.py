"""
IoT連携サービス

スマート冷蔵庫など外部デバイスとの連携を管理する。
MQTT/HTTP両対応、在庫同期、賞味期限アラート機能を提供。
"""

import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DeviceType(str, Enum):
    """デバイスタイプ"""

    SMART_FRIDGE = "smart_fridge"
    SMART_SCALE = "smart_scale"
    BARCODE_SCANNER = "barcode_scanner"


class ProtocolType(str, Enum):
    """通信プロトコル"""

    HTTP = "http"
    MQTT = "mqtt"
    WEBHOOK = "webhook"


class AlertType(str, Enum):
    """アラートタイプ"""

    EXPIRY_WARNING = "expiry_warning"
    EXPIRED = "expired"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


@dataclass
class Device:
    """IoTデバイス"""

    device_id: str
    name: str
    device_type: DeviceType
    protocol: ProtocolType
    api_key: str
    endpoint: Optional[str] = None
    mqtt_topic: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True
    last_sync: Optional[str] = None
    created_at: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class InventoryItem:
    """在庫アイテム"""

    item_id: str
    device_id: str
    name: str
    quantity: float
    unit: str
    expiry_date: Optional[str] = None
    category: Optional[str] = None
    barcode: Optional[str] = None
    location: Optional[str] = None
    synced_at: str = None

    def __post_init__(self):
        if self.synced_at is None:
            self.synced_at = datetime.now().isoformat()


@dataclass
class Alert:
    """アラート"""

    alert_id: str
    alert_type: AlertType
    item_id: str
    item_name: str
    device_id: str
    message: str
    created_at: str
    is_read: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class IoTService:
    """IoT連携サービス"""

    def __init__(self, data_dir: str = "data/iot"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.devices_file = self.data_dir / "devices.json"
        self.inventory_file = self.data_dir / "inventory.json"
        self.alerts_file = self.data_dir / "alerts.json"

        self._initialize_storage()

    def _initialize_storage(self) -> None:
        """ストレージ初期化"""
        for file_path in [self.devices_file, self.inventory_file, self.alerts_file]:
            if not file_path.exists():
                file_path.write_text(json.dumps([]), encoding="utf-8")

    def _read_json(self, file_path: Path) -> List[Dict]:
        """JSONファイル読み込み"""
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_json(self, file_path: Path, data: List[Dict]) -> None:
        """JSONファイル書き込み"""
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def generate_api_key(self) -> str:
        """APIキー生成"""
        return f"iot_{secrets.token_urlsafe(32)}"

    def register_device(
        self,
        name: str,
        device_type: DeviceType,
        protocol: ProtocolType,
        endpoint: Optional[str] = None,
        mqtt_topic: Optional[str] = None,
        webhook_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Device:
        """デバイス登録"""
        devices = self._read_json(self.devices_file)

        # デバイスID生成
        device_id = f"dev_{secrets.token_hex(8)}"
        api_key = self.generate_api_key()

        device = Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            protocol=protocol,
            api_key=api_key,
            endpoint=endpoint,
            mqtt_topic=mqtt_topic,
            webhook_url=webhook_url,
            metadata=metadata or {},
        )

        devices.append(asdict(device))
        self._write_json(self.devices_file, devices)

        return device

    def get_device(self, device_id: str) -> Optional[Device]:
        """デバイス取得"""
        devices = self._read_json(self.devices_file)
        device_data = next((d for d in devices if d["device_id"] == device_id), None)

        if device_data:
            return Device(**device_data)
        return None

    def get_devices(self, is_active: Optional[bool] = None) -> List[Device]:
        """デバイス一覧取得"""
        devices = self._read_json(self.devices_file)

        if is_active is not None:
            devices = [d for d in devices if d.get("is_active") == is_active]

        return [Device(**d) for d in devices]

    def delete_device(self, device_id: str) -> bool:
        """デバイス削除"""
        devices = self._read_json(self.devices_file)
        initial_count = len(devices)
        devices = [d for d in devices if d["device_id"] != device_id]

        if len(devices) < initial_count:
            self._write_json(self.devices_file, devices)

            # 関連する在庫データも削除
            inventory = self._read_json(self.inventory_file)
            inventory = [i for i in inventory if i["device_id"] != device_id]
            self._write_json(self.inventory_file, inventory)

            return True
        return False

    def verify_api_key(self, device_id: str, api_key: str) -> bool:
        """APIキー検証"""
        device = self.get_device(device_id)
        if not device:
            return False
        return device.api_key == api_key and device.is_active

    def sync_inventory(
        self, device_id: str, items: List[Dict[str, Any]]
    ) -> List[InventoryItem]:
        """在庫同期"""
        device = self.get_device(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        inventory = self._read_json(self.inventory_file)

        # 既存のデバイス在庫を削除
        inventory = [i for i in inventory if i["device_id"] != device_id]

        # 新しい在庫を追加
        synced_items = []
        for item_data in items:
            item_id = f"item_{secrets.token_hex(8)}"
            item = InventoryItem(
                item_id=item_id,
                device_id=device_id,
                name=item_data["name"],
                quantity=item_data["quantity"],
                unit=item_data["unit"],
                expiry_date=item_data.get("expiry_date"),
                category=item_data.get("category"),
                barcode=item_data.get("barcode"),
                location=item_data.get("location"),
            )
            inventory.append(asdict(item))
            synced_items.append(item)

        self._write_json(self.inventory_file, inventory)

        # デバイスの最終同期時刻を更新
        devices = self._read_json(self.devices_file)
        for d in devices:
            if d["device_id"] == device_id:
                d["last_sync"] = datetime.now().isoformat()
                break
        self._write_json(self.devices_file, devices)

        # アラートをチェック
        self._check_and_create_alerts(synced_items)

        return synced_items

    def get_inventory(
        self, device_id: Optional[str] = None, category: Optional[str] = None
    ) -> List[InventoryItem]:
        """在庫一覧取得"""
        inventory = self._read_json(self.inventory_file)

        if device_id:
            inventory = [i for i in inventory if i["device_id"] == device_id]

        if category:
            inventory = [i for i in inventory if i.get("category") == category]

        return [InventoryItem(**i) for i in inventory]

    def get_inventory_item(self, item_id: str) -> Optional[InventoryItem]:
        """在庫アイテム取得"""
        inventory = self._read_json(self.inventory_file)
        item_data = next((i for i in inventory if i["item_id"] == item_id), None)

        if item_data:
            return InventoryItem(**item_data)
        return None

    def _check_and_create_alerts(self, items: List[InventoryItem]) -> None:
        """アラートチェックと生成"""
        alerts = self._read_json(self.alerts_file)
        now = datetime.now()

        for item in items:
            # 賞味期限チェック
            if item.expiry_date:
                try:
                    expiry = datetime.fromisoformat(item.expiry_date)
                    days_until_expiry = (expiry - now).days

                    if days_until_expiry < 0:
                        # 期限切れ
                        alert = Alert(
                            alert_id=f"alert_{secrets.token_hex(8)}",
                            alert_type=AlertType.EXPIRED,
                            item_id=item.item_id,
                            item_name=item.name,
                            device_id=item.device_id,
                            message=f"{item.name} は賞味期限が切れています（{item.expiry_date}）",
                            created_at=now.isoformat(),
                            metadata={
                                "expiry_date": item.expiry_date,
                                "days_overdue": abs(days_until_expiry),
                            },
                        )
                        alerts.append(asdict(alert))
                    elif days_until_expiry <= 3:
                        # 期限間近
                        alert = Alert(
                            alert_id=f"alert_{secrets.token_hex(8)}",
                            alert_type=AlertType.EXPIRY_WARNING,
                            item_id=item.item_id,
                            item_name=item.name,
                            device_id=item.device_id,
                            message=f"{item.name} の賞味期限が近づいています（残り{days_until_expiry}日）",
                            created_at=now.isoformat(),
                            metadata={
                                "expiry_date": item.expiry_date,
                                "days_remaining": days_until_expiry,
                            },
                        )
                        alerts.append(asdict(alert))
                except ValueError:
                    pass  # 日付形式が不正な場合はスキップ

            # 在庫数チェック
            if item.quantity <= 0:
                alert = Alert(
                    alert_id=f"alert_{secrets.token_hex(8)}",
                    alert_type=AlertType.OUT_OF_STOCK,
                    item_id=item.item_id,
                    item_name=item.name,
                    device_id=item.device_id,
                    message=f"{item.name} の在庫がありません",
                    created_at=now.isoformat(),
                    metadata={"quantity": item.quantity, "unit": item.unit},
                )
                alerts.append(asdict(alert))
            elif item.quantity < 2:  # しきい値は調整可能
                alert = Alert(
                    alert_id=f"alert_{secrets.token_hex(8)}",
                    alert_type=AlertType.LOW_STOCK,
                    item_id=item.item_id,
                    item_name=item.name,
                    device_id=item.device_id,
                    message=f"{item.name} の在庫が少なくなっています（残り{item.quantity}{item.unit}）",
                    created_at=now.isoformat(),
                    metadata={"quantity": item.quantity, "unit": item.unit},
                )
                alerts.append(asdict(alert))

        self._write_json(self.alerts_file, alerts)

    def get_alerts(
        self,
        is_read: Optional[bool] = None,
        alert_type: Optional[AlertType] = None,
        device_id: Optional[str] = None,
    ) -> List[Alert]:
        """アラート一覧取得"""
        alerts = self._read_json(self.alerts_file)

        if is_read is not None:
            alerts = [a for a in alerts if a["is_read"] == is_read]

        if alert_type:
            alerts = [a for a in alerts if a["alert_type"] == alert_type]

        if device_id:
            alerts = [a for a in alerts if a["device_id"] == device_id]

        # 新しい順にソート
        alerts.sort(key=lambda x: x["created_at"], reverse=True)

        return [Alert(**a) for a in alerts]

    def mark_alert_as_read(self, alert_id: str) -> bool:
        """アラートを既読にする"""
        alerts = self._read_json(self.alerts_file)

        for alert in alerts:
            if alert["alert_id"] == alert_id:
                alert["is_read"] = True
                self._write_json(self.alerts_file, alerts)
                return True

        return False

    def delete_alert(self, alert_id: str) -> bool:
        """アラート削除"""
        alerts = self._read_json(self.alerts_file)
        initial_count = len(alerts)
        alerts = [a for a in alerts if a["alert_id"] != alert_id]

        if len(alerts) < initial_count:
            self._write_json(self.alerts_file, alerts)
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        devices = self.get_devices()
        inventory = self.get_inventory()
        alerts = self.get_alerts(is_read=False)

        active_devices = len([d for d in devices if d.is_active])
        total_items = len(inventory)
        total_quantity = sum(item.quantity for item in inventory)

        # カテゴリ別集計
        categories = {}
        for item in inventory:
            cat = item.category or "未分類"
            if cat not in categories:
                categories[cat] = {"count": 0, "quantity": 0}
            categories[cat]["count"] += 1
            categories[cat]["quantity"] += item.quantity

        # アラート種別集計
        alert_counts = {}
        for alert in alerts:
            alert_type = alert.alert_type
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1

        return {
            "total_devices": len(devices),
            "active_devices": active_devices,
            "total_items": total_items,
            "total_quantity": total_quantity,
            "categories": categories,
            "unread_alerts": len(alerts),
            "alert_breakdown": alert_counts,
        }
