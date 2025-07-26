import json
import hashlib
import hmac
import datetime

def get_signature(data, x_date, host, content_type, signed_headers, sk):
    json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    x_content_sha256 = hashlib.sha256(json_str.encode()).hexdigest()

    # ✅ SỬA LỖI: Xây dựng chuỗi canonical request ĐÚNG theo tài liệu
    # Sắp xếp lại thứ tự và thêm dòng "signedHeaders" bị thiếu
    canonical_request = (
        f"host:{host}\n"
        f"x-date:{x_date}\n"
        f"content-type:{content_type}\n"
        f"signedHeaders:{signed_headers}\n"
        f"x-content-sha256:{x_content_sha256}"
    )

    short_date = x_date[:8]
    service = "armcloud-paas" # Dịch vụ cố định [cite: 5]
    scope = f"{short_date}/{service}/request"

    # ✅ SỬA LỖI: Sử dụng canonical_request đã được sửa
    string_to_sign = (
        f"HMAC-SHA256\n"
        f"{x_date}\n"
        f"{scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )

    # Phần tính toán key không đổi
    k_date = hmac.new(sk.encode(), short_date.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_date, service.encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    return signature, x_content_sha256