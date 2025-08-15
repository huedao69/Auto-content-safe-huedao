import os, requests, logging

def send_pending_digest(posts):
    """Gửi email danh sách bài Pending (nếu cấu hình Mailgun)."""
    domain = os.environ.get("MAILGUN_DOMAIN")
    api_key = os.environ.get("MAILGUN_API_KEY")
    to_email = os.environ.get("DIGEST_TO")
    if not (domain and api_key and to_email):
        logging.info("Mailgun not configured; skip digest.")
        return

    pending = [p for p in posts if p.get("status") == "pending"]
    if not pending:
        logging.info("No pending posts; skip digest.")
        return

    subject = f"[ACS] {len(pending)} bài mới ở trạng thái Pending"
    lines = []
    for i, p in enumerate(pending, 1):
        title = p.get("title", "Bài không có tiêu đề")
        src = p.get("source_url", "")
        reasons = ", ".join(p.get("moderation", {}).get("reasons", []))
        lines.append(f"{i}. {title}\nNguồn: {src}\nModeration: {reasons}\n")

    text = "\n\n".join(lines) + "\n\nVào WordPress → Posts → Pending để duyệt."
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    data = {
        "from": f"ACS Safe Mode <digest@{domain}>",
        "to": [to_email],
        "subject": subject,
        "text": text
    }
    try:
        r = requests.post(url, auth=("api", api_key), data=data, timeout=30)
        r.raise_for_status()
        logging.info("Pending digest sent.")
    except Exception as ex:
        logging.warning(f"Send digest failed: {ex}")
