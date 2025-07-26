from api.vmos_api import vmos_post
from api.apk_manager import install_apk
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

def get_running_instance_id():
    resp = vmos_post("/vcpcloud/api/padApi/infos", {
        "pageNo": 1,
        "pageSize": 10
    }, ACCESS_KEY, SECRET_KEY)

    pads = resp.json().get("data", {}).get("list", [])
    for pad in pads:
        if pad["status"] == "ONLINE":
            return pad["padCode"]
    raise Exception("❌ Không có máy ảo nào ONLINE.")

def get_token(instance_id):
    resp = vmos_post("/vcpcloud/api/padApi/stsToken", {
        "instanceId": instance_id
    }, ACCESS_KEY, SECRET_KEY)

    data = resp.json()
    if data["code"] != 0:
        raise Exception(f"❌ Token API lỗi: {data}")
    return data["data"]["token"]

if __name__ == "__main__":
    instance_id = get_running_instance_id()
    token = get_token(instance_id)
    install_apk(instance_id, token, "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk")
