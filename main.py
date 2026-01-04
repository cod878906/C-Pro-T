import urllib.request
import re
import socket
import time
import html
from concurrent.futures import ThreadPoolExecutor

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
# ⚙️ تنظیمات
TIMEOUT = 2.0       # تایم‌اوت تست اتصال
MAX_THREADS = 50    # سرعت تست

# ==========================================
# 🛠 توابع
# ==========================================

def fetch_content(url):
    try:
        # شبیه‌سازی مرورگر واقعی
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8', errors='ignore')
            # 💡 نکته مهم: تبدیل کاراکترهای HTML مثل &amp; به &
            return html.unescape(raw_data)
    except Exception as e:
        print(f"      ❌ دانلود نشد: {e}")
        return ""

def extract_proxies(text):
    # ریجکس ساده و قدرتمند
    # دنبال الگوی server=...&port=...&secret=... میگرده
    pattern = r'(?:server|server_name)=([^&"\s]+)&(?:port|p)=(\d+)&(?:secret|s)=([^&"\s]+)'
    return re.findall(pattern, text)

def check_proxy(proxy_tuple):
    server, port, secret = proxy_tuple
    try:
        start = time.time()
        # تست اتصال TCP
        sock = socket.create_connection((server, int(port)), timeout=TIMEOUT)
        sock.close()
        ping = int((time.time() - start) * 1000)
        return f"tg://proxy?server={server}&port={port}&secret={secret}", ping
    except:
        return None, None

def main():
    print("🚀 شروع اسکنر جدید (HTML Unescape Mode)...")
    
    all_candidates = set()
    
    # 1. جمع‌آوری
    for url in SOURCES:
        print(f"📥 بررسی: {url}")
        content = fetch_content(url)
        
        found = extract_proxies(content)
        
        if len(found) > 0:
            print(f"   ✅ {len(found)} مورد پیدا شد.")
            for item in found:
                all_candidates.add(item)
        else:
            print(f"   ⚠️ خالی بود. (نمونه محتوا: {content[:100]}...)")

    candidates_list = list(all_candidates)
    print(f"\n📦 کل پروکسی‌های یکتا: {len(candidates_list)}")
    
    if len(candidates_list) == 0:
        print("🔴 هیچ پروکسی‌ای پیدا نشد. احتمالا گیت‌هاب دسترسی به تلگرام را محدود کرده است.")
        return

    # 2. تست
    print(f"⚡️ شروع تست اتصال روی {len(candidates_list)} مورد...")
    valid_proxies = []
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(check_proxy, candidates_list)
        
        for link, ping in results:
            if link:
                valid_proxies.append({'link': link, 'ping': ping})

    # 3. ذخیره
    valid_proxies.sort(key=lambda x: x['ping'])
    final_links = [x['link'] for x in valid_proxies]
    
    if final_links:
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("mtproto.txt", "w", encoding="utf-8") as f:
            f.write(f"# Updated: {now} UTC\n")
            f.write("\n".join(final_links))
            
        print(f"\n💎 موفقیت‌آمیز! {len(final_links)} پروکسی سالم ذخیره شد.")
    else:
        print("\n❌ پروکسی پیدا شد ولی هیچکدام وصل نشدند (مشکل پورت/فیلترینگ).")

if __name__ == "__main__":
    main()
