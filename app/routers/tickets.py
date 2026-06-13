"""票务只读/核验 — 票种展示、票码/订单状态查询、入园核验"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Tickets"])

# ── 种子数据 ──
_TICKET_PRODUCTS: list[dict] = [
    {"id": "TP-001", "name": "成人票", "price": 50.0, "applicableCrowd": "成人", "refundable": True, "officialUrl": "https://tickets.example.com/buy?type=adult", "scenicId": "SA-001", "status": "active"},
    {"id": "TP-002", "name": "儿童票", "price": 25.0, "applicableCrowd": "1.2m-1.5m儿童", "refundable": True, "officialUrl": "https://tickets.example.com/buy?type=child", "scenicId": "SA-001", "status": "active"},
    {"id": "TP-003", "name": "老人票", "price": 25.0, "applicableCrowd": "60岁以上", "refundable": True, "officialUrl": "https://tickets.example.com/buy?type=senior", "scenicId": "SA-001", "status": "active"},
]

_ORDERS: dict[str, dict] = {
    "ORD-001": {"id": "ORD-001", "productId": "TP-001", "productName": "成人票", "customerName": "张三", "phone": "138****0001", "quantity": 1, "price": 50.0, "visitDate": "2026-06-13", "ticketCode": "TCK-A001", "status": "paid", "verifiedAt": None, "createdAt": "2026-06-10T08:00:00Z"},
    "ORD-002": {"id": "ORD-002", "productId": "TP-002", "productName": "儿童票", "customerName": "李四", "phone": "138****0002", "quantity": 2, "price": 50.0, "visitDate": "2026-06-13", "ticketCode": "TCK-A002", "status": "paid", "verifiedAt": None, "createdAt": "2026-06-11T10:00:00Z"},
    "ORD-003": {"id": "ORD-003", "productId": "TP-001", "productName": "成人票", "customerName": "王五", "phone": "138****0003", "quantity": 1, "price": 50.0, "visitDate": "2026-06-13", "ticketCode": "TCK-A003", "status": "refunded", "verifiedAt": None, "createdAt": "2026-06-11T12:00:00Z"},
}


class VerifyTicketRequest(BaseModel):
    ticketCode: str
    scenicId: str = "SA-001"


@router.get("/tickets/products")
def get_ticket_products(request: Request, scenic_id: str = "SA-001"):
    trace_id = request.state.trace_id
    products = [p for p in _TICKET_PRODUCTS if p["scenicId"] == scenic_id and p["status"] == "active"]
    return ok({"items": products, "officialPurchaseUrl": "https://tickets.example.com/buy"}, trace_id)


@router.get("/tickets/orders")
def get_ticket_orders(request: Request, phone: str | None = None, ticket_code: str | None = None):
    trace_id = request.state.trace_id
    orders = list(_ORDERS.values())
    if phone:
        orders = [o for o in orders if o["phone"] == phone]
    if ticket_code:
        orders = [o for o in orders if o["ticketCode"] == ticket_code]
    return ok({"items": orders, "total": len(orders)}, trace_id)


@router.post("/tickets/verify")
def verify_ticket(body: VerifyTicketRequest, request: Request):
    trace_id = request.state.trace_id
    # 查找订单
    order = None
    for o in _ORDERS.values():
        if o["ticketCode"] == body.ticketCode:
            order = o
            break

    if not order:
        return err(40404, f"票码 {body.ticketCode} 不存在", trace_id)
    if order["status"] == "refunded":
        return err(40001, "该票已退票", trace_id)
    if order["status"] == "used":
        return err(40002, "该票已使用", trace_id)
    if order["verifiedAt"] is not None:
        return err(40002, "该票已核验入园", trace_id)

    # 执行核验
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    order["verifiedAt"] = now
    order["status"] = "used"

    return ok({
        "ticketCode": body.ticketCode,
        "orderId": order["id"],
        "productName": order["productName"],
        "verifiedAt": now,
        "status": "verified",
    }, trace_id)
