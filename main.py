import os
from dotenv import load_dotenv
from api.vmos_api import vmos_post
from api.apk_manager import install_apk

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

def get_token_and_instance():
    url_path = "/vcpcloud/api/padApi/stsToken"  # hoặc đường dẫn chính xác từ VMOS
    data = {}
    response = vmos_post(url_path, data, ACCESS_KEY, SECRET_KEY)
    if response.status_code != 200:
        print("❌ VMOS API lỗi:", response.status_code, response.text)
        raise Exception("❌ Không lấy được token")
    
    resp_json = response.json()
    print("📦 Res:", resp_json)

    if resp_json.get("code") != 0:
        raise Exception("❌ Token API trả lỗi: " + str(resp_json))
    
    token = resp_json["data"]["token"]
    instance_id = resp_json["data"]["instance_id"]
    return token, instance_id

if __name__ == "__main__":
    token, instance_id = get_token_and_instance()
    install_apk(instance_id, token, "https://raw.githubusercontent.com/tom88901/apk_debug/main/Shelter.apk")
