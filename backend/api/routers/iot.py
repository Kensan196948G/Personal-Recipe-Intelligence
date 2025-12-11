"""
IoT連携APIルーター

スマートデバイスとの連携、在庫管理、アラート管理のエンドポイントを提供。
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, Field

from backend.services.iot_service import (
  IoTService,
  DeviceType,
  ProtocolType,
  AlertType
)


router = APIRouter(prefix="/api/v1/iot", tags=["iot"])
iot_service = IoTService()


# ============================================================
# Request / Response Models
# ============================================================

class DeviceRegisterRequest(BaseModel):
  """デバイス登録リクエスト"""
  name: str = Field(..., description="デバイス名")
  device_type: DeviceType = Field(..., description="デバイスタイプ")
  protocol: ProtocolType = Field(..., description="通信プロトコル")
  endpoint: Optional[str] = Field(None, description="HTTPエンドポイント")
  mqtt_topic: Optional[str] = Field(None, description="MQTTトピック")
  webhook_url: Optional[str] = Field(None, description="Webhook URL")
  metadata: Optional[Dict[str, Any]] = Field(None, description="メタデータ")


class DeviceResponse(BaseModel):
  """デバイスレスポンス"""
  device_id: str
  name: str
  device_type: str
  protocol: str
  api_key: str
  endpoint: Optional[str] = None
  mqtt_topic: Optional[str] = None
  webhook_url: Optional[str] = None
  is_active: bool
  last_sync: Optional[str] = None
  created_at: str
  metadata: Dict[str, Any]


class InventoryItemData(BaseModel):
  """在庫アイテムデータ"""
  name: str = Field(..., description="商品名")
  quantity: float = Field(..., ge=0, description="数量")
  unit: str = Field(..., description="単位")
  expiry_date: Optional[str] = Field(None, description="賞味期限 (ISO8601)")
  category: Optional[str] = Field(None, description="カテゴリ")
  barcode: Optional[str] = Field(None, description="バーコード")
  location: Optional[str] = Field(None, description="保管場所")


class InventorySyncRequest(BaseModel):
  """在庫同期リクエスト"""
  device_id: str = Field(..., description="デバイスID")
  items: List[InventoryItemData] = Field(..., description="在庫アイテムリスト")


class InventoryItemResponse(BaseModel):
  """在庫アイテムレスポンス"""
  item_id: str
  device_id: str
  name: str
  quantity: float
  unit: str
  expiry_date: Optional[str] = None
  category: Optional[str] = None
  barcode: Optional[str] = None
  location: Optional[str] = None
  synced_at: str


class AlertResponse(BaseModel):
  """アラートレスポンス"""
  alert_id: str
  alert_type: str
  item_id: str
  item_name: str
  device_id: str
  message: str
  created_at: str
  is_read: bool
  metadata: Dict[str, Any]


class APIResponse(BaseModel):
  """標準APIレスポンス"""
  status: str
  data: Any = None
  error: Optional[str] = None


# ============================================================
# Helper Functions
# ============================================================

def verify_device_auth(device_id: str, api_key: Optional[str]) -> None:
  """デバイス認証チェック"""
  if not api_key:
    raise HTTPException(status_code=401, detail="API key required")

  if not iot_service.verify_api_key(device_id, api_key):
    raise HTTPException(status_code=403, detail="Invalid API key or inactive device")


# ============================================================
# Device Endpoints
# ============================================================

@router.post("/devices", response_model=APIResponse)
def register_device(request: DeviceRegisterRequest):
  """
  デバイス登録

  新しいIoTデバイスを登録し、APIキーを発行する。
  """
  try:
    device = iot_service.register_device(
      name=request.name,
      device_type=request.device_type,
      protocol=request.protocol,
      endpoint=request.endpoint,
      mqtt_topic=request.mqtt_topic,
      webhook_url=request.webhook_url,
      metadata=request.metadata
    )

    return APIResponse(
      status="ok",
      data=DeviceResponse(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        protocol=device.protocol,
        api_key=device.api_key,
        endpoint=device.endpoint,
        mqtt_topic=device.mqtt_topic,
        webhook_url=device.webhook_url,
        is_active=device.is_active,
        last_sync=device.last_sync,
        created_at=device.created_at,
        metadata=device.metadata
      ).dict()
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices", response_model=APIResponse)
def get_devices(is_active: Optional[bool] = Query(None, description="アクティブフィルター")):
  """
  デバイス一覧取得

  登録済みのデバイス一覧を取得する。
  """
  try:
    devices = iot_service.get_devices(is_active=is_active)

    device_list = [
      DeviceResponse(
        device_id=d.device_id,
        name=d.name,
        device_type=d.device_type,
        protocol=d.protocol,
        api_key=d.api_key,
        endpoint=d.endpoint,
        mqtt_topic=d.mqtt_topic,
        webhook_url=d.webhook_url,
        is_active=d.is_active,
        last_sync=d.last_sync,
        created_at=d.created_at,
        metadata=d.metadata
      ).dict()
      for d in devices
    ]

    return APIResponse(status="ok", data=device_list)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}", response_model=APIResponse)
def get_device(device_id: str):
  """
  デバイス詳細取得

  指定したデバイスの詳細情報を取得する。
  """
  try:
    device = iot_service.get_device(device_id)

    if not device:
      raise HTTPException(status_code=404, detail="Device not found")

    return APIResponse(
      status="ok",
      data=DeviceResponse(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        protocol=device.protocol,
        api_key=device.api_key,
        endpoint=device.endpoint,
        mqtt_topic=device.mqtt_topic,
        webhook_url=device.webhook_url,
        is_active=device.is_active,
        last_sync=device.last_sync,
        created_at=device.created_at,
        metadata=device.metadata
      ).dict()
    )
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.delete("/devices/{device_id}", response_model=APIResponse)
def delete_device(device_id: str):
  """
  デバイス削除

  指定したデバイスと関連する在庫データを削除する。
  """
  try:
    success = iot_service.delete_device(device_id)

    if not success:
      raise HTTPException(status_code=404, detail="Device not found")

    return APIResponse(status="ok", data={"deleted": True})
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Inventory Endpoints
# ============================================================

@router.post("/inventory/sync", response_model=APIResponse)
def sync_inventory(
  request: InventorySyncRequest,
  x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
  """
  在庫同期

  デバイスから在庫データを同期する。
  APIキー認証が必要。
  """
  try:
    # 認証チェック
    verify_device_auth(request.device_id, x_api_key)

    # 在庫同期
    items = iot_service.sync_inventory(
      device_id=request.device_id,
      items=[item.dict() for item in request.items]
    )

    item_list = [
      InventoryItemResponse(
        item_id=item.item_id,
        device_id=item.device_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        expiry_date=item.expiry_date,
        category=item.category,
        barcode=item.barcode,
        location=item.location,
        synced_at=item.synced_at
      ).dict()
      for item in items
    ]

    return APIResponse(status="ok", data={"synced_count": len(item_list), "items": item_list})
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory", response_model=APIResponse)
def get_inventory(
  device_id: Optional[str] = Query(None, description="デバイスIDフィルター"),
  category: Optional[str] = Query(None, description="カテゴリフィルター")
):
  """
  在庫一覧取得

  同期された在庫データを取得する。
  """
  try:
    items = iot_service.get_inventory(device_id=device_id, category=category)

    item_list = [
      InventoryItemResponse(
        item_id=item.item_id,
        device_id=item.device_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        expiry_date=item.expiry_date,
        category=item.category,
        barcode=item.barcode,
        location=item.location,
        synced_at=item.synced_at
      ).dict()
      for item in items
    ]

    return APIResponse(status="ok", data=item_list)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/{item_id}", response_model=APIResponse)
def get_inventory_item(item_id: str):
  """
  在庫アイテム詳細取得

  指定した在庫アイテムの詳細を取得する。
  """
  try:
    item = iot_service.get_inventory_item(item_id)

    if not item:
      raise HTTPException(status_code=404, detail="Inventory item not found")

    return APIResponse(
      status="ok",
      data=InventoryItemResponse(
        item_id=item.item_id,
        device_id=item.device_id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        expiry_date=item.expiry_date,
        category=item.category,
        barcode=item.barcode,
        location=item.location,
        synced_at=item.synced_at
      ).dict()
    )
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Alert Endpoints
# ============================================================

@router.get("/alerts", response_model=APIResponse)
def get_alerts(
  is_read: Optional[bool] = Query(None, description="既読フィルター"),
  alert_type: Optional[AlertType] = Query(None, description="アラート種別フィルター"),
  device_id: Optional[str] = Query(None, description="デバイスIDフィルター")
):
  """
  アラート一覧取得

  賞味期限、在庫不足などのアラート一覧を取得する。
  """
  try:
    alerts = iot_service.get_alerts(
      is_read=is_read,
      alert_type=alert_type,
      device_id=device_id
    )

    alert_list = [
      AlertResponse(
        alert_id=alert.alert_id,
        alert_type=alert.alert_type,
        item_id=alert.item_id,
        item_name=alert.item_name,
        device_id=alert.device_id,
        message=alert.message,
        created_at=alert.created_at,
        is_read=alert.is_read,
        metadata=alert.metadata
      ).dict()
      for alert in alerts
    ]

    return APIResponse(status="ok", data=alert_list)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.patch("/alerts/{alert_id}/read", response_model=APIResponse)
def mark_alert_as_read(alert_id: str):
  """
  アラートを既読にする

  指定したアラートを既読状態にする。
  """
  try:
    success = iot_service.mark_alert_as_read(alert_id)

    if not success:
      raise HTTPException(status_code=404, detail="Alert not found")

    return APIResponse(status="ok", data={"marked_as_read": True})
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}", response_model=APIResponse)
def delete_alert(alert_id: str):
  """
  アラート削除

  指定したアラートを削除する。
  """
  try:
    success = iot_service.delete_alert(alert_id)

    if not success:
      raise HTTPException(status_code=404, detail="Alert not found")

    return APIResponse(status="ok", data={"deleted": True})
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Statistics Endpoint
# ============================================================

@router.get("/statistics", response_model=APIResponse)
def get_statistics():
  """
  統計情報取得

  デバイス、在庫、アラートの統計情報を取得する。
  """
  try:
    stats = iot_service.get_statistics()
    return APIResponse(status="ok", data=stats)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
