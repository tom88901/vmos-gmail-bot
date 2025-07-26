import json
import hashlib
import hmac
import datetime
import requests

def get_signature(data, x_date, host, content_type, signed_headers, sk):
    json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    x_content_sha256 = hashlib.sha256(json_str.encode()).hexdigest()

    canonical_request = (
        f"host:{host}\n"
        f"x-date:{x_date}\n"
        f"content-type:{content_type}\n"
        f"signedHeaders:{signed_headers}\n"
        f"x-content-sha256:{x_content_sha256}"
    )

    short_date = x_date[:8]
    service = "armcloud-paas"
    scope = f"{short_date}/{service}/request"

    string_to_sign = (
        f"HMAC-SHA256\n"
        f"{x_date}\n"
        f"{scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )

    k_date = hmac.new(sk.encode(), short_date.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_date, service.encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    return signature, x_content_sha256

def vmos_post(path, data, access_key, secret_key):
    # ✅ ĐỊA CHỈ MÁY CHỦ CHÍNH XÁC TỪ TÀI LIỆU
    host = "openapi-hk.armcloud.net"
    
    url = f"https://{host}{path}"
    
    content_type = "application/json;charset=UTF-8"
    signed_headers = "content-type;host;x-content-sha256;x-date"
    x_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    signature, x_content_sha256 = get_signature(
        data, x_date, host, content_type, signed_headers, secret_key
    )

    headers = {
        "Content-Type": content_type,
        "Host": host,
        "X-Date": x_date,
        "X-Content-Sha256": x_content_sha256,
        "Authorization": f"HMAC-SHA256 Credential={access_key}, SignedHeaders={signed_headers}, Signature={signature}",
    }

    return requests.post(url, headers=headers, json=data)