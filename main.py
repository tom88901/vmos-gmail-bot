import os
import time
import json
from dotenv import load_dotenv
from api.vmos_api import vmos_post

# Nạp các biến môi trường từ file .env
load_dotenv() 

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Shelter APK từ GitHub raw
APK_URL = "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk"

# Kiểm tra xem các biến môi trường đã được nạp chưa
if not ACCESS_KEY or not SECRET_KEY:
    raise ValueError("❌ Lỗi: Không tìm thấy ACCESS_KEY hoặc SECRET_KEY. Hãy kiểm tra lại file .env và GitHub Secrets.")

def get_device():
    # SỬ DỤNG ĐƯỜNG DẪN API V1 MỚI
    api_path = "/v1/devices"
    payload = {"page": 1, "per_page": 10} # API v1 thường dùng tham số này

    print(f"🔎 Đang gửi yêu cầu đến API mới: {api_path}")
    resp = vmos_post(
        api_path,
        payload,
        ACCESS_KEY,
        SECRET_KEY
    )
    
    print(f"🚦 Trạng thái phản hồi (Status Code): {resp.status_code}")
    res_json = resp.json()
    print("📋 Nội dung phản hồi đầy đủ (JSON):")
    print(json.dumps(res_json, indent=2, ensure_ascii=False))

    # Xử lý các lỗi có thể xảy ra từ API
    if resp.status_code != 200:
        error_message = res_json.get("message", "Lỗi không xác định.")
        raise Exception(f"API trả về lỗi HTTP {resp.status_code}: {error_message}")

    # API v1 có thể trả về danh sách thiết bị trong key 'devices' hoặc 'data'
    pads = res_json.get("devices", []) or res_json.get("data", [])
    if not pads:
        raise Exception("Không tìm thấy máy ảo nào trong phản hồi từ API v1.")
    
    pad = pads[0]
    # API v1 có thể dùng 'name' và 'id' thay vì 'padName' và 'padCode'
    pad_name = pad.get("name", "N/A")
    pad_id = pad.get("id", "N/A")
    pad_status = pad.get("status", "N/A")

    print(f"✅ Dùng máy ảo duy nhất: {pad_name} | ID: {pad_id} | Trạng thái: {pad_status}")
    return pad_id, pad_status

def start_device(instance_id):
    print("🚀 Đang gửi yêu cầu khởi động máy ảo...")
    resp = vmos_post(
        "/vcpcloud/api/padApi/start",
        {"instanceId": instance_id},
        ACCESS_KEY,
        SECRET_KEY
    )
    print("📨 Phản hồi khởi động:", resp.json())

def install_apk(instance_id, apk_url):
    print("📦 Gửi yêu cầu cài đặt APK...")
    resp = vmos_post(
        "/vcpcloud/api/appApi/installApp",
        {
            "instanceId": instance_id,
            "url": apk_url,
            "isAutoStart": False
        },
        ACCESS_KEY,
        SECRET_KEY
    )
    res_json = resp.json()
    print("📥 Phản hồi cài đặt:", res_json)
    if res_json.get("code") != 200:
        error_message = res_json.get("message", "Không có thông báo lỗi cụ thể.")
        raise Exception(f"❌ Cài APK thất bại. Phản hồi từ server: {error_message}")
    print("✅ Đã gửi yêu cầu cài APK thành công.")

if __name__ == "__main__":
    instance_id, status = get_device()

    if status not in ("ONLINE", "RUNNING"):
        print(f"⚠️ Máy chưa chạy (trạng thái = {status}) → đang khởi động...")
        start_device(instance_id)
        print("⏳ Đợi 25 giây để máy ảo khởi động...")
        time.sleep(25)

    install_apk(instance_id, APK_URL)