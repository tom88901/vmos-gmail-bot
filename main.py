import os
import time
from vmos_api import vmos_post

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# ✅ Shelter APK từ GitHub raw
APK_URL = "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk"

def get_device():
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
        raise Exception("❌ Cài APK thất bại.")
    print("✅ Đã gửi yêu cầu cài APK thành công.")

if __name__ == "__main__":
    instance_id, status = get_device()

    if status not in ("ONLINE", "RUNNING"):
        print(f"⚠️ Máy chưa chạy (trạng thái = {status}) → đang khởi động...")
        start_device(instance_id)
        time.sleep(25)  # đợi máy ảo lên (có thể điều chỉnh thời gian này)

    install_apk(instance_id, APK_URL)
