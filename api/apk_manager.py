import requests
import time

def install_apk(instance_id, token, apk_url):
    install_url = "https://api.vmos.cn/v1/device/app/install"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "instance_id": instance_id,
        "apk_url": apk_url
    }

    print("[📦] Đang gửi yêu cầu cài đặt APK...")
    response = requests.post(install_url, headers=headers, json=data)
    if response.status_code == 200 and response.json().get("code") == 0:
        print("✅ APK đang được cài đặt...")
    else:
        print("❌ Lỗi khi cài APK:", response.text)
        return

    # Chờ đợi quá trình cài đặt hoàn tất (tùy mạng)
    for i in range(20):
        time.sleep(5)
        status = check_apk_status(instance_id, token)
        if status == "installed":
            print("✅ APK Shelter đã cài xong.")
            return
        else:
            print(f"⏳ Đang đợi cài đặt... ({i+1}/20)")
    print("❌ Cài APK timeout.")

def check_apk_status(instance_id, token):
    url = "https://api.vmos.cn/v1/device/app/list"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "instance_id": instance_id
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        apps = response.json().get("data", [])
        for app in apps:
            if app.get("package_name") == "net.typeblog.shelter":
                return "installed"
    return "not_installed"
