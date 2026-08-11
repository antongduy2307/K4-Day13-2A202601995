from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Hộ chiếu VN: 1 chữ cái + 7 chữ số (B1234567); hộ chiếu mẫu mới có thể 2 chữ cái
    "passport": r"\b[A-Z]{1,2}\d{7}\b",
    # Địa chỉ VN: bắt theo từ khóa (có dấu và không dấu), cắt tới dấu phân cách gần nhất
    "address_vn": (
        r"(?i)\b(?:số nhà|so nha|đường|duong|phố|ngõ|ngo|ngách|hẻm|khu phố|khu pho|"
        r"thôn|thon|ấp|phường|phuong|thị trấn|thi tran|quận|quan|huyện|huyen|"
        r"tỉnh|thành phố|thanh pho)\s+[^\n,;.]{1,40}"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
