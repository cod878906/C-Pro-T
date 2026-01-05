import requests
import re
import socket
import time
import html
from urllib.parse import urlparse

# ==========================================
# 🎯 منابع (Sources)
# ==========================================
SOURCES = [
    # --- Premium GitHub Raw Sources ---
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.txt",
    
    # --- Telegram Channels (Web Preview Mode /s/) ---
    "https://t.me/s/ProxyMTProto",
    "https://t.me/s/TelMTProto",
    "https://t.me/s/Myporoxy",
    "https://t.me/s/PewezaVPN",
    "https://t.me/s/ProxyHagh",
    "https://t.me/s/iMTProto",
    "https://t.me/s/Proxy_Qavi",
    "https://t.me/s/NoteProxy",
    "https://t.me/s/proxymtprotoj",
    "https://t.me/s/TelMTProto",
    "https://t.me/s/iRoProxy",

  
    # --- 👇 ADD YOUR OWN SOURCES HERE 👇 ---
    # "YOUR_CHANNEL_LINK_OR_RAW_URL",
]

TIMEOUT = 2.0  # تایم‌اوت تست

def fetch_proxies():
    found_proxies = set()
    print("🔍 در حال جمع‌آوری پروکسی‌ها (مدل کلاسیک)...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in SOURCES:
        try:
            print(f"   📥 دریافت از: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            # 🔥 فیکس مهم: تبدیل کدهای HTML تلگرام به متن عادی
            text = html.unescape(response.text)

            # الگوی ساده و قوی برای همه مدل لینک‌ها
            regex = r'(?:tg://|https://t\.me/)proxy\?server=([^&]+)&port=(\d+)&secret=([^"\s&\n]+)'
            matches = re.findall(regex, text)
            
            for server, port, secret in matches:
                found_proxies.add((server, int(port), secret))

        except Exception as e:
            print(f"❌ خطا در لینک {url}: {e}")

    return list(found_proxies)

def is_proxy_alive(server, port):
    try:
        sock = socket.create_connection((server, port), timeout=TIMEOUT)
        sock.close()
        return True
    except:
        return False

def main():
    raw_proxies = fetch_proxies()
    print(f"\n📦 تعداد کل کاندیداها: {len(raw_proxies)}")
    
    working_proxies = []
    print("\n⚡️ در حال تست اتصال (صبر کنید)...")

    # تست همه موارد (محدودیت برداشته شد)
    for i, (server, port, secret) in enumerate(raw_proxies):
        if is_proxy_alive(server, port):
            print(f"✅ فعال: {server}:{port}")
            # فرمت استاندارد tg://
            link = f"tg://proxy?server={server}&port={port}&secret={secret}"
            working_proxies.append(link)
        
        # نمایش وضعیت هر 50 تا
        if i % 50 == 0 and i > 0:
            print(f"   ... {i} مورد چک شد")

    print(f"\n💎 تعداد نهایی پروکسی‌های سالم: {len(working_proxies)}")

    # ذخیره در فایل TXT
    if working_proxies:
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("mtproto.txt", "w", encoding="utf-8") as f:
            f.write(f"# Updated: {now} UTC\n")
            f.write("\n".join(working_proxies))
        print("💾 فایل mtproto.txt ذخیره شد.")
    else:
        print("❌ هیچ پروکسی سالمی پیدا نشد.")

if __name__ == "__main__":
    main()
