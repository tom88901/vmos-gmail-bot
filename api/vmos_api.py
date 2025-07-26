# api/vmos_api.py

import datetime
import hmac
import hashlib
import json
import requests
import binascii

def get_signature(data, x_date, host, content_type, signed_headers, sk):
    json_string = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    x_content_sha256 = hashlib.sha256(json_string.encode()).hexdigest()
    canonical_string = (
        f"host:{host}\n"
        f"x-date:{x_date}\n"
        f"content-type:{content_type}\n"
        f"signedHeaders:{signed_headers}\n"
        f"x-content-sha256:{x_content_sha256}"
    )
    short_x_date = x_date[:8]
    credential_scope = f"{short_x_date}/armcloud-paas/request"
    string_to_sign = f"HMAC-SHA256\n{x_date}\n{credential_scope}\n{hashlib.sha256(canonical_string.encode()).hexdigest()}"
    k_date = hmac.new(sk.encode(), short_x_date.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_date, b"armcloud-paas", hashlib.sha256).digest()
    signing_key = hmac.new(k_service, b"request", hashlib.sha256).digest()
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).digest()
    return binascii.hexlify(signature).decode()

def vmos_post(url_path, data, access_key, secret_key):
    host = "api.vmoscloud.com"
    full_url = f"https://{host}{url_path}"
    content_type = "application/json;charset=UTF-8"
    signed_headers = "content-type;host;x-content-sha256;x-date"
    x_date = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    short_date = x_date[:8]

    signature = get_signature(data, x_date, host, content_type, signed_headers, secret_key)

    headers = {
        "content-type": content_type,
        "x-date": x_date,
        "x-host": host,
        "authorization": f"HMAC-SHA256 Credential={access_key}, SignedHeaders={signed_headers}, Signature={signature}"
    }

    response = requests.post(full_url, headers=headers, json=data)
    return response
