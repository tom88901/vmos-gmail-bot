import requests

def install_apk(instance_id, token, apk_url):
    print(f"📦 Gửi yêu cầu cài APK từ: {apk_url}")

    url = f"https://api.vmoscloud.com/v1/devices/{instance_id}/install"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "app_url": apk_url,
        "auto_launch": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("✅ Đã gửi yêu cầu cài đặt APK.")
        print("🧾 Phản hồi:", response.json())
    else:
        print("❌ Cài đặt APK thất bại.")
        print("🔻 Status:", response.status_code)
        print("🔻 Nội dung:", response.text)
