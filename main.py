import os
import time
import json
from dotenv import load_dotenv
# Import cả vmos_get và vmos_post
from api.vmos_api import vmos_get, vmos_post

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
    print("🔎 Đang gửi yêu cầu GET để lấy danh sách máy ảo...")
    
    # Gọi hàm vmos_get với tham số là chuỗi
    resp = vmos_get(
        "/vcpcloud/api/padApi/infos",
        {"pageNo": "1", "pageSize": "10"},
        ACCESS_KEY,
        SECRET_KEY
    )
    
    print(f"🚦 Trạng thái phản hồi (Status Code): {resp.status_code}")
    res_json = resp.json()
    print("📋 Nội dung phản hồi đầy đủ (JSON):")
    print(json.dumps(res_json, indent=2, ensure_ascii=False))

    # Xử lý lỗi một cách toàn diện
    if resp.status_code != 200 or res_json.get("code") != 200:
        error_message = res_json.get("message") or res_json.get("msg", "Lỗi không xác định từ API.")
        raise Exception(f"API trả về lỗi: {error_message}")

    pads = res_json.get("data", {}).get("list", [])
    if not pads:
        raise Exception("Không tìm thấy máy ảo nào trong phản hồi từ API.")
    
    pad = pads[0]
    # Lấy thông tin máy ảo từ các key chính xác
    pad_name = pad.get("padName", "N/A")
    pad_id = pad.get("padCode", "N/A")
    pad_status = pad.get("status", "N/A")

    print(f"✅ Dùng máy ảo duy nhất: {pad_name} | ID: {pad_id} | Trạng thái: {pad_status}")
    return pad_id, pad_status

def start_device(instance_id):
    print("🚀 Đang gửi yêu cầu khởi động máy ảo...")
    # Khởi động vẫn dùng POST
    resp = vmos_post(
        "/vcpcloud/api/padApi/start",
        {"instanceId": instance_id},
        ACCESS_KEY,
        SECRET_KEY
    )
    print("📨 Phản hồi khởi động:", resp.json())

def install_apk(instance_id, apk_url):
    print("📦 Gửi yêu cầu cài đặt APK...")
    # Cài đặt vẫn dùng POST
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