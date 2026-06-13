"""二维码解析 — 统一扫码入口，返回跳转目标"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["QR Code"])

# ── 码数据 ──
_QR_CODES: dict[str, dict] = {
    "SPOT-001": {"code": "SPOT-001", "type": "spot", "targetId": "POI-002", "targetName": "朝天门广场", "action": "guide", "url": "/spots/POI-002/guide", "validFrom": "2026-01-01", "validTo": "2026-12-31", "status": "active"},
    "SPOT-002": {"code": "SPOT-002", "type": "spot", "targetId": "POI-003", "targetName": "洪崖洞观景台", "action": "guide", "url": "/spots/POI-003/guide", "validFrom": "2026-01-01", "validTo": "2026-12-31", "status": "active"},
    "TICKET-001": {"code": "TICKET-001", "type": "ticket", "targetId": "ORD-001", "targetName": "成人票 #A001", "action": "verify", "url": "/tickets/verify", "validFrom": "2026-06-01", "validTo": "2026-06-30", "status": "active"},
    "EVENT-001": {"code": "EVENT-001", "type": "event", "targetId": "EVT-001", "targetName": "夜景灯光秀", "action": "info", "url": "/events/EVT-001", "validFrom": "2026-06-01", "validTo": "2026-06-30", "status": "active"},
    "DEVICE-001": {"code": "DEVICE-001", "type": "device", "targetId": "DEV-001", "targetName": "自助取票机A", "action": "service", "url": "/services/DEV-001", "validFrom": "2026-01-01", "validTo": "2026-12-31", "status": "active"},
    "DISABLED-QR": {"code": "DISABLED-QR", "type": "spot", "targetId": "POI-999", "targetName": "已停用景点", "action": "guide", "url": "", "validFrom": "2026-01-01", "validTo": "2026-01-02", "status": "disabled"},
}


class ResolveQrCodeRequest(BaseModel):
    code: str
    scenicId: str = "SA-001"
    sessionId: str | None = None


@router.post("/qrcode/resolve")
def resolve_qrcode(body: ResolveQrCodeRequest, request: Request):
    trace_id = request.state.trace_id
    qr = _QR_CODES.get(body.code)
    if not qr:
        return err(40404, f"未识别的二维码: {body.code}", trace_id)
    if qr["status"] == "disabled":
        return err(41004, f"该二维码已停用: {qr['targetName']}", trace_id)

    from datetime import datetime
    now = datetime.utcnow().strftime("%Y-%m-%d")
    if now < qr["validFrom"] or now > qr["validTo"]:
        return err(41005, f"该二维码不在有效期内 ({qr['validFrom']}~{qr['validTo']})", trace_id)

    return ok({
        "code": qr["code"],
        "type": qr["type"],
        "action": qr["action"],
        "targetId": qr["targetId"],
        "targetName": qr["targetName"],
        "url": qr["url"],
    }, trace_id)
