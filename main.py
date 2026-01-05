import requests
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 🎯 منابع (همون قبلی‌ها + چندتا جدید)
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/mix",
    "https://raw.githubusercontent.com/MrMohebi/xray-proxy-grabber-telegram/master/collected-proxies/row-url/all.txt",
    "https://raw.githubusercontent.com/miladrf/telegram-proxy/main/proxy.txt"
]

TIMEOUT = 2.0 

def fetch_proxies():
    print("💎 در حال استخراج (با الگوی جدید)...")
    unique_proxies = set()
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            print(f"   📥 دریافت: {url.split('com/')[1][:20]}...")
            resp = requests.get(url, headers=headers, timeout=10)
            
            # --- تغییر مهم اینجاست ---
            # الگوی قبلی خیلی سخت‌گیر بود. این الگو میگه:
            # هر چیزی که با tg:// یا https://t.me/proxy شروع میشه
            # و توش server=... port=... secret=... داره رو بردار (مهم نیست وسطش چیه)
            
            text = resp.text
            
            # الگوی آزاد برای پیدا کردن لینک‌ها
            # این الگو میگه: سکرت هر چیزی میتونه باشه تا زمانی که به فاصله یا " یا & برسه
            pattern = r'(?:tg://|https://t\.me/)proxy\?server=([^&]+)&port=(\d+)&secret=([^"\s&\n]+)'
            
            matches = re.findall(pattern, text)
            
            if len(matches) == 0:
                print(f"      ⚠️ فرمت این فایل عجیب بود. (تعداد: 0)")
            else:
                print(f"      ✅ {len(matches)} مورد پیدا شد.")

            for server, port, secret in matches:
                # ساخت لینک استاندارد
                link = f"tg://proxy?server={server}&port={port}&secret={secret}"
                unique_proxies.add(link)
                
        except Exception as e:
            print(f"   ❌ خطا: {e}")

    print(f"\n📦 مجموع کل پروکسی‌های پیدا شده: {len(unique_proxies)}")
    return list(unique_proxies)

def test_proxy(link):
    try:
        # استخراج آدرس و پورت برای تست
        match = re.search(r'server=([^&]+)&port=(\d+)', link)
        if not match: return None
        
        server = match.group(1)
        port = int(match.group(2))
        
        start = time.time()
        # تست اتصال
        sock = socket.create_connection((server, port), timeout=TIMEOUT)
        sock.close()
        
        ping = int((time.time() - start) * 1000)
        return {'link': link, 'ping': ping}
    except:
        return None

def main():
    # 1. جمع‌آوری
    all_links = fetch_proxies()
    
    if not all_links:
        print("🔴 هیچی پیدا نشد! احتمالاً آی‌پی گیت‌هاب مسدود شده.")
        return

    # 2. تست محدود (برای بن نشدن)
    # اینجا اگر تعداد خیلی زیاد بود، فقط 500 تا رو تست میکنیم
    # چون هوک‌زوف به تنهایی 4000 تا پروکسی میده، اگه همشو تست کنی بن میشی
    limit = 500
    if len(all_links) > limit:
        print(f"⚠️ تعداد خیلی زیاد است ({len(all_links)}). فقط {limit} تای آخر تست می‌شوند.")
        target_list = all_links[-limit:] # جدیدترین‌ها (معمولا ته لیست هستن)
    else:
        target_list = all_links

    print(f"\n⚡️ شروع تست سلامت روی {len(target_list)} پروکسی...")
    working_proxies = []
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        results = executor.map(test_proxy, target_list)
        
        for res in results:
            if res:
                working_proxies.append(res)

    # 3. ذخیره
    working_proxies.sort(key=lambda x: x['ping'])
    final_list = [item['link'] for item in working_proxies]
    
    if final_list:
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("mtproto.txt", "w", encoding="utf-8") as f:
            f.write(f"# Updated: {now} UTC\n")
            f.write("\n".join(final_list))
            
        print(f"\n💎 تمام! {len(final_list)} پروکسی سالم ذخیره شد.")
    else:
        print("\n❌ همه پروکسی‌ها تست شدند ولی هیچکدام وصل نشدند.")

if __name__ == "__main__":
    main()
