import requests
import re
import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 🎯 منابع (تلفیقی از گیت‌هاب و تلگرام)
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

# تایم‌اوت رو زیاد کردم که مطمئن بشیم مشکل از کندی نیست
TIMEOUT = 10.0 

def fetch_proxies():
    print("🔍 شروع اسکن منابع...")
    all_proxies = set()
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            print(f"   📥 در حال دانلود: {url} ...")
            resp = requests.get(url, headers=headers, timeout=10)
            text = resp.text
            
            # ریجکس ساده‌تر و کلی‌تر
            # دنبال هر چیزی میگرده که server=...&port=... داشته باشه
            matches = re.findall(r'(?:server|server_name)=([^&]+)&(?:port|p)=([^&]+)&(?:secret|s)=([^"\s&\n]+)', text)
            
            if len(matches) == 0:
                print(f"      ⚠️ هیچ پروکسی در این لینک یافت نشد.")
            else:
                print(f"      ✅ {len(matches)} پروکسی پیدا شد.")

            for server, port, secret in matches:
                all_proxies.add((server, int(port), secret))
                
        except Exception as e:
            print(f"      ❌ خطا در دانلود سورس: {e}")
            
    print(f"\n📦 مجموع کل کاندیداها برای تست: {len(all_proxies)}")
    return list(all_proxies)

def check_proxy(proxy_data):
    server, port, secret = proxy_data
    try:
        # تست اتصال TCP ساده
        sock = socket.create_connection((server, port), timeout=TIMEOUT)
        sock.close()
        return f"tg://proxy?server={server}&port={port}&secret={secret}"
    except Exception as e:
        # اینجا ارور رو برمی‌گردونیم که ببینیم چرا وصل نمیشه
        return None

def main():
    raw_proxies = fetch_proxies()
    
    if not raw_proxies:
        print("🔴 ارور مهلک: هیچ پروکسی‌ای جمع‌آوری نشد! مشکل از دانلود سورس‌هاست.")
        sys.exit(1)

    print(f"\n⚡️ شروع تست اتصال (روی {len(raw_proxies)} مورد)...")
    
    valid_count = 0
    final_links = []

    # تست با ترد کمتر برای اطمینان بیشتر
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_proxy, raw_proxies)
        
        for res in results:
            if res:
                valid_count += 1
                final_links.append(res)
                # چاپ اولین موفقیت برای دلگرمی
                if valid_count == 1:
                    print(f"   🎉 اولین پروکسی سالم پیدا شد: {res[:40]}...")

    print(f"\n📊 گزارش نهایی:")
    print(f"   - کل موارد تست شده: {len(raw_proxies)}")
    print(f"   - تعداد سالم: {valid_count}")

    if final_links:
        # ذخیره با هدر زمان (برای اجبار به آپدیت گیت)
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("mtproto.txt", "w", encoding="utf-8") as f:
            f.write(f"# Updated: {now}\n")
            f.write("\n".join(final_links))
        print("💎 فایل mtproto.txt با موفقیت ذخیره شد.")
    else:
        print("❌ متاسفانه هیچ پروکسی‌ای وصل نشد.")
        print("💡 دلیل احتمالی: آی‌پی‌های گیت‌هاب (Azure) توسط فایروال ایران یا خود پروکسی‌ها مسدود شده‌اند.")

if __name__ == "__main__":
    main()
