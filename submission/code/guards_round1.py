"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).
"""
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    # Ghim chính sách đang có hiệu lực để tránh model đọc nhầm phiên bản cũ
    pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if pol:
        return Verdict.allow(policy_id=pol["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    tool = action.get("tool")

    # Cổng 1: Kiểm tra issue_refund - Chống hoàn sai tiền / vượt trần ngày / không đủ ngày trễ
    if tool == "issue_refund":
        # Trần hoàn tiền tự động trong ngày
        cap = (ctx.gates or {}).get("business", {}).get("daily_refund_cap_vnd")
        spent = ctx.tools.auto_refund_today_vnd()
        amt = action.get("amount_vnd", 0)
        if cap is not None and spent + amt > cap:
            return Verdict.escalate("Vượt trần hoàn tiền tự động trong ngày, chuyển người duyệt")

        order_id = action.get("order_id")
        if order_id:
            order = ctx.tools.lookup_order(order_id)
            if order:
                parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
                pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
                if pol:
                    delay = H.db_delay_days(parcel, ctx.as_of)
                    entitlement = H.entitlement_vnd(pol, order, delay, parcel.get("delay_cause"))
                    if entitlement == 0 and amt > 0:
                        return Verdict.deny(f"Đơn không đủ điều kiện hoàn tiền theo tracking DB (trễ {delay} ngày)")
                    if amt > entitlement:
                        return Verdict.modify(f"Giảm mức hoàn về đúng quyền lợi tracking DB ({entitlement}đ)", amount_vnd=entitlement)

    # Cổng 2: Kiểm tra file_carrier_fault - Chống phạt oan hãng vận chuyển khi tracking không có lỗi
    if tool == "file_carrier_fault":
        order_id = action.get("order_id")
        if order_id:
            order = ctx.tools.lookup_order(order_id)
            if order:
                parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
                pol = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
                if pol:
                    delay = H.db_delay_days(parcel, ctx.as_of)
                    if not H.carrier_at_fault(pol, parcel, delay):
                        return Verdict.deny(f"Lỗi không thuộc về hãng hoặc chưa đủ ngày trễ theo DB ({delay} ngày)")

    # Cổng 3: Kiểm tra notify_carrier - Chống rò rỉ dữ liệu cá nhân PII cho hãng vận chuyển
    if tool == "notify_carrier":
        payload = action.get("payload") or {}
        blocked_fields = (ctx.gates or {}).get("legal", {}).get("pii_fields_blocked_to_third_party", []) or ["phone", "street", "recipient_contact"]
        clean_payload = dict(payload)
        modified = False
        for fld in blocked_fields:
            if fld in clean_payload:
                del clean_payload[fld]
                modified = True
        order_id = action.get("order_id")
        if order_id:
            order = ctx.tools.lookup_order(order_id)
            if order and order.get("recipient"):
                rec = order["recipient"]
                phone = H.digits(rec.get("phone", ""))
                note = clean_payload.get("customer_note", "")
                if phone and len(phone) >= 9 and phone[-9:] in H.digits(note):
                    clean_payload["customer_note"] = "[Đã ẩn thông tin liên hệ]"
                    modified = True
        if modified:
            return Verdict.modify("Ẩn thông tin cá nhân PII trước khi gửi cho bên thứ ba", payload=clean_payload)

    return Verdict.allow()
