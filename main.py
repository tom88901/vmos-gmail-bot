import os
import requests
from dotenv import load_dotenv
from api.apk_manager import install_apk

load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# ✅ B1: Lấy token và instance_id
def get_token_and_instance():
    url = "https://api.vmos.cn/v1/auth"
    resp = requests.post(url, json={
        "access_key": ACCESS_KEY,
        "secret_key": SECRET_KEY
    })

    if resp.status_code != 200:
        raise Exception("❌ Lỗi lấy token")

    data = resp.json().get("data", {})
    token = data.get("token")
    instance_id = data.get("instance_id")
    print(f"✅ Token & Instance ID lấy thành công.")
    return token, instance_id

if __name__ == "__main__":
    token, instance_id = get_token_and_instance()
    apk_url = "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk"
    install_apk(instance_id, token, apk_url)
