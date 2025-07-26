import os
import time
from dotenv import load_dotenv # <--- THÊM DÒNG NÀY
from api.vmos_api import vmos_post

load_dotenv() # <--- VÀ THÊM DÒNG NÀY

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# (Tùy chọn) Thêm một bước kiểm tra để báo lỗi sớm hơn và rõ ràng hơn
if not ACCESS_KEY or not SECRET_KEY:
    raise ValueError("❌ Lỗi: Không tìm thấy ACCESS_KEY hoặc SECRET_KEY. Hãy kiểm tra lại file .env và GitHub Secrets.")


def get_device():
    # ... phần còn lại của file giữ nguyên ...
    resp = vmos_post(
        "/vcpcloud/api/padApi/infos",
        {"pageNo": 1, "pageSize": 10},
        ACCESS_KEY,
        SECRET_KEY
    )
    pads = resp.json().get("data", {}).get("list", [])
    if not pads:
        raise Exception("❌ Không tìm thấy máy ảo nào.")
    
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
    print("📨 Phản hồi:", resp.json())

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
        # In ra thông báo lỗi từ API để dễ gỡ lỗi hơn
        error_message = res_json.get("message", "Không có thông báo lỗi.")
        raise Exception(f"❌ Cài APK thất bại. Phản hồi từ server: {error_message}")
    print("✅ Đã gửi yêu cầu cài APK thành công.")

if __name__ == "__main__":
    # Shelter APK từ GitHub raw
    APK_URL = "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk"
    
    instance_id, status = get_device()

    if status not in ("ONLINE", "RUNNING"):
        print(f"⚠️ Máy chưa chạy (trạng thái = {status}) → đang khởi động...")
        start_device(instance_id)
        print("⏳ Đợi 25 giây để máy ảo khởi động...")
        time.sleep(25)

    install_apk(instance_id, APK_URL)