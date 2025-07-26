import json
import hashlib
import hmac
import datetime
import requests

def get_signature_for_get(host, path, query_params, x_date, access_key, secret_key):
    """Tạo chữ ký cho yêu cầu GET."""
    
    # 1. Tạo Canonical Request
    # Đối với GET, body là rỗng
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    # Sắp xếp và mã hóa query parameters
    sorted_params = sorted(query_params.items())
    canonical_query_string = "&".join(f"{k}={v}" for k, v in sorted_params)
    
    canonical_headers = f"host:{host}\nx-date:{x_date}\n"
    signed_headers = "host;x-date"

    canonical_request = (
        f"GET\n"
        f"{path}\n"
        f"{canonical_query_string}\n"
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{hashed_payload}"
    )

    # 2. Tạo String to Sign
    short_date = x_date[:8]
    scope = f"{short_date}/armcloud-paas/request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    string_to_sign = (
        f"HMAC-SHA256\n"
        f"{x_date}\n"
        f"{scope}\n"
        f"{hashed_canonical_request}"
    )

    # 3. Tính chữ ký
    k_date = hmac.new(secret_key.encode('utf-8'), short_date.encode('utf-8'), hashlib.sha256).digest()
    k_service = hmac.new(k_date, b"armcloud-paas", hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # 4. Tạo header Authorization
    authorization_header = (
        f"HMAC-SHA256 Credential={access_key}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    
    return authorization_header

def vmos_get(path, params, access_key, secret_key):
    """Gửi yêu cầu GET đến VMOS API."""
    host = "openapi-hk.armcloud.net"
    url = f"https://{host}{path}"
    x_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    authorization = get_signature_for_get(host, path, params, x_date, access_key, secret_key)
    
    headers = {
        "Host": host,
        "X-Date": x_date,
        "Authorization": authorization,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    return requests.get(url, headers=headers, params=params)

# Hàm vmos_post vẫn giữ nguyên để dùng cho các tác vụ khác như cài APK
def vmos_post(path, data, access_key, secret_key):
    """Gửi yêu cầu POST đến VMOS API."""
    host = "openapi-hk.armcloud.net"
    url = f"https://{host}{path}"
    content_type = "application/json;charset=UTF-8"
    signed_headers = "content-type;host;x-content-sha256;x-date"
    x_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    # Nội dung hàm này giữ nguyên như cũ...
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
    k_date = hmac.new(secret_key.encode(), short_date.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_date, service.encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": content_type,
        "Host": host,
        "X-Date": x_date,
        "X-Content-Sha256": x_content_sha256,
        "Authorization": f"HMAC-SHA256 Credential={access_key}, SignedHeaders={signed_headers}, Signature={signature}",
    }

    return requests.post(url, headers=headers, json=data)