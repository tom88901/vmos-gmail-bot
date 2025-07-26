import os
from dotenv import load_dotenv
from api.vmos_api import vmos_post
from api.apk_manager import install_apk

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


def get_running_instance_id():
    """Tự động lấy máy ảo đang hoạt động dựa trên status."""
    print("🔍 Đang lấy danh sách máy ảo...")

    resp = vmos_post(
        "/vcpcloud/api/padApi/infos",
        {"pageNo": 1, "pageSize": 10},
        ACCESS_KEY,
        SECRET_KEY
    )

    pads = resp.json().get("data", {}).get("list", [])

    if not pads:
        raise Exception("❌ Không tìm thấy máy ảo nào trong tài khoản.")

    print("📋 Danh sách máy ảo:")
    for pad in pads:
        name = pad.get("padName")
        status = pad.get("status")
        code = pad.get("padCode")
        print(f"  • {name} | ID: {code} | Trạng thái: {status}")

    for pad in pads:
        if pad.get("status") in ["ONLINE", "RUNNING", "ACTIVE"]:
            print(f"✅ Chọn máy ảo: {pad['padName']} ({pad['padCode']})")
            return pad["padCode"]

    raise Exception("❌ Không có máy ảo nào đang hoạt động (ONLINE/RUNNING/ACTIVE).")


def get_token(instance_id):
    """Lấy token từ instance ID."""
    print(f"🔐 Lấy token cho instance {instance_id}...")
    resp = vmos_post(
        "/vcpcloud/api/padApi/stsToken",
        {"instanceId": instance_id},
        ACCESS_KEY,
        SECRET_KEY
    )

    data = resp.json()
    if data.get("code") == 0:
        return data["data"]["token"]

    raise Exception(f"❌ Token API lỗi: {data}")


if __name__ == "__main__":
    instance_id = get_running_instance_id()
    token = get_token(instance_id)
    install_apk(
        instance_id,
        token,
        "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk"
    )
