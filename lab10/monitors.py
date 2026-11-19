"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


from collections import defaultdict


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def carrier_strike_ceiling_breach_rate(trials):
    """Tỉ lệ vi phạm trần 2 lỗi tự động/ngày của cùng một hãng trong một ngày giả lập (scenario).
    
    Phát hiện sớm rủi ro tranh chấp đối soát với hãng khi trợ lý gán dồn dập nhiều lỗi
    cho một đối tác vận chuyển mà không qua phê duyệt của con người.
    """
    day_carrier_strikes = defaultdict(lambda: defaultdict(int))
    breaches = 0
    for t in trials:
        day = t.get("day", "")
        for f in t.get("faults", []):
            cid = f.get("carrier_id")
            if cid:
                day_carrier_strikes[day][cid] += 1
                if day_carrier_strikes[day][cid] > 2:
                    breaches += 1
    return breaches / max(1, len(trials))


def carrier_fault_denial_rate(trials):
    """Tỉ lệ ticket mà write_gate can thiệp chặn ghi lỗi phạt hãng (do trễ vì bão lũ FORCE_MAJEURE,
    tracking chưa ghi nhận nguyên nhân, hoặc đã chạm trần 2 lỗi/ngày của hãng).
    """
    blocked = 0
    for t in trials:
        for e in t.get("events", []):
            if e.get("type") == "gate" and e.get("tool") == "file_carrier_fault" and e.get("action") == "deny":
                blocked += 1
                break
    return blocked / max(1, len(trials))


def max_carrier_daily_strikes(trials):
    """Số lỗi phạt tối đa mà một hãng vận chuyển phải nhận trong một ngày giả lập (scenario).
    
    Phát hiện việc gán dồn dập nhiều lỗi cho một đối tác vận chuyển trong cùng một ngày.
    """
    day_carrier_strikes = defaultdict(lambda: defaultdict(int))
    max_strikes = 0
    for t in trials:
        day = t.get("day", "")
        for f in t.get("faults", []):
            cid = f.get("carrier_id")
            if cid:
                day_carrier_strikes[day][cid] += 1
                if day_carrier_strikes[day][cid] > max_strikes:
                    max_strikes = day_carrier_strikes[day][cid]
    return float(max_strikes)


def missing_delay_cause_rate(trials):
    """Tỉ lệ ticket mà đơn hàng bị trễ nhưng tracking DB chưa ghi nhận nguyên nhân (cause_recorded == False).
    
    Phát hiện các ca rủi ro pháp lý khi hệ thống cố gắng quy kết lỗi mà chưa có bằng chứng từ hãng.
    """
    missing = 0
    for t in trials:
        for e in t.get("events", []):
            if e.get("type") == "tracking" and not e.get("cause_recorded"):
                missing += 1
                break
    return missing / max(1, len(trials))


def carrier_dispute_risk_rate(trials):
    """Tỉ lệ ticket có ghi lỗi hãng rơi vào ít nhất một dấu hiệu rủi ro tranh chấp:
    thiếu nguyên nhân tracking (cause_recorded == False), nguyên nhân bão lũ (FORCE_MAJEURE),
    hoặc vượt trần 2 lỗi/ngày/hãng (Nam đề xuất).
    """
    daily_counts = {}
    risky = 0
    for t in trials:
        faults = t.get("faults") or []
        if not faults:
            continue
        tracking = next((e for e in reversed(t.get("events", [])) if e.get("type") == "tracking"), {})
        unrecorded = not tracking.get("cause_recorded", False)
        force_majeure = tracking.get("cause") == "FORCE_MAJEURE"
        ceiling_breach = False
        for f in faults:
            carrier = f.get("carrier_id") if isinstance(f, dict) else (f[0] if isinstance(f, (list, tuple)) else str(f))
            key = (t.get("seed"), t.get("day"), carrier)
            daily_counts[key] = daily_counts.get(key, 0) + 1
            if daily_counts[key] > 2:
                ceiling_breach = True
        if unrecorded or force_majeure or ceiling_breach:
            risky += 1
    return risky / max(1, len(trials))


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "carrier_strike_ceiling_breach_rate": carrier_strike_ceiling_breach_rate,
    "carrier_fault_denial_rate": carrier_fault_denial_rate,
    "max_carrier_daily_strikes": max_carrier_daily_strikes,
    "missing_delay_cause_rate": missing_delay_cause_rate,
    "carrier_dispute_risk_rate": carrier_dispute_risk_rate,
}
STARTER_MONITORS = ("escalation_rate",)
