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
    print("🔎 Đang gửi yêu cầu lấy danh sách máy ảo...")
    resp = vmos_post(
        "/vcpcloud/api/padApi/infos",
        {"pageNo": 1, "pageSize": 10},
        ACCESS_KEY,
        SECRET_KEY
    )
    
    # --- BẮT ĐẦU MÃ GỠ LỖI ---
    print(f"🚦 Trạng thái phản hồi (Status Code): {resp.status_code}")
    
    try:
        res_json = resp.json()
        print("📋 Nội dung phản hồi đầy đủ (JSON):")
        # Dùng json.dumps để in đẹp hơn, dễ đọc hơn
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"⚠️ Không thể phân tích JSON. Nội dung thô: {resp.text}")
        raise e
    # --- KẾT THÚC MÃ GỠ LỖI ---

    pads = res_json.get("data", {}).get("list", [])
    if not pads:
        # Lỗi vẫn sẽ được đưa ra, nhưng bây giờ chúng ta có log chi tiết ở trên
        raise Exception("❌ Không tìm thấy máy ảo nào trong danh sách 'list'.")
    
    pad = pads[0]
    print(f"✅ Dùng máy ảo duy nhất: {pad['padName']} | ID: {pad['padCode']} | Trạng thái: {pad.get('status')}")
    return pad["padCode"], pad.get("status")

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