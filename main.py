import requests
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor

# ==========================================================
# 🏆 TOP TIER SOURCES (منابع مادر و تایید شده گیت‌هاب)
# ==========================================================
# این‌ها لیست‌هایی هستند که خودشان تست شده و تمیز هستند.
SOURCES = [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies.txt",
    "https://raw.githubusercontent.com/porridgewithraisins/telegram-proxy-collector/main/proxy-list.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/mtproto.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/mtproto.txt"
]

# تنظیمات
TIMEOUT = 2.0  # تایم‌اوت تست (فقط سرورهای تیز رو میخوایم)

def fetch_proxies():
    print("💎 در حال استخراج از مخازن معتبر گیت‌هاب...")
    unique_proxies = set()
    
    for url in SOURCES:
        try:
            print(f"   📥 دریافت: {url.split('com/')[1][:30]}...")
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # ریجکس برای استخراج دقیق لینک‌های تلگرام
                links = re.findall(r'tg://proxy\?server=[^&]+&port=\d+&secret=[a-zA-Z0-9]+', resp.text)
                for link in links:
                    unique_proxies.add(link)
        except:
            print(f"   ❌ خطا در دریافت منبع")

    print(f"\n📦 مجموع پروکسی‌های جمع‌آوری شده: {len(unique_proxies)}")
    return list(unique_proxies)

def test_proxy(link):
    """تست واقعی اتصال (TCP)"""
    try:
        # پارس کردن لینک
        match = re.search(r'server=([^&]+)&port=(\d+)', link)
        if not match: return None
        
        server = match.group(1)
        port = int(match.group(2))
        
        start = time.time()
        # تست سوکت
        sock = socket.create_connection((server, port), timeout=TIMEOUT)
        sock.close()
        
        # محاسبه پینگ
        ping = int((time.time() - start) * 1000)
        return {'link': link, 'ping': ping}
    except:
        return None

def main():
    # 1. جمع‌آوری
    all_links = fetch_proxies()
    
    if not all_links:
        print("🔴 هیچ پروکسی‌ای پیدا نشد! اینترنت سرور چک شود.")
        return

    # 2. تست سرعت (مولتی ترد)
    print(f"⚡️ شروع تست سلامت روی {len(all_links)} پروکسی...")
    working_proxies = []
    
    # استفاده از 50 کارگر همزمان برای سرعت بالا
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(test_proxy, all_links)
        
        for res in results:
            if res:
                working_proxies.append(res)

    # 3. مرتب‌سازی و ذخیره
    # اونایی که پینگ کمتر دارن میان اول
    working_proxies.sort(key=lambda x: x['ping'])
    
    # جدا کردن لینک نهایی
    final_list = [item['link'] for item in working_proxies]
    
    # نوشتن در فایل
    with open("mtproto.txt", "w", encoding="utf-8") as f:
        # هدر برای اینکه گیت‌هاب بفهمه فایل عوض شده
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"# Telegram MTProto Proxy List\n")
        f.write(f"# Updated: {now} UTC\n")
        f.write(f"# Total Active: {len(final_list)}\n")
        f.write("\n".join(final_list))
        
    print(f"\n✅ پایان عملیات.")
    print(f"💎 تعداد پروکسی سالم و تست شده: {len(final_list)}")
    if len(final_list) > 0:
        print(f"🚀 بهترین پینگ: {working_proxies[0]['ping']}ms")

if __name__ == "__main__":
    main()
