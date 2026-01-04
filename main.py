import asyncio
import aiohttp
import re
import time
import os
import random

# ==========================================
# 📋 منابع (Sources)
# ==========================================
SOURCES = [
    # --- Premium GitHub Raw Sources ---
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies.txt",
    "https://raw.githubusercontent.com/MahsaNetConfigTopic/proxy/main/proxies.txt",
    
    # --- Telegram Channels (Web Preview Mode /s/) ---
    "https://t.me/s/ProxyMTProto",
    "https://t.me/s/TelMTProto",
    "https://t.me/s/Myporoxy",
    "https://t.me/s/ProxyMTProto_tel",
    "https://t.me/s/proxy_mci",
    "https://t.me/s/mtproto_proxy_iran",
    "https://t.me/s/PewezaVPN",
    "https://t.me/s/asrnovin_ir",
    "https://t.me/s/ProxyHagh",
    "https://t.me/s/iMTProto",
    "https://t.me/s/Proxy_Qavi",
    "https://t.me/s/NoteProxy",
    "https://t.me/s/proxymtprotoj",
    "https://t.me/s/Pen_Musix",
    "https://t.me/s/ShadowProxy66",
    "https://t.me/s/TelMTProto",
    "https://t.me/s/iRoProxy",

  
    # --- 👇 ADD YOUR OWN SOURCES HERE 👇 ---
    # "YOUR_CHANNEL_LINK_OR_RAW_URL",
]

# ==========================================
# 🛡️ تنظیمات امنیتی و هوشمند
# ==========================================
TIMEOUT = 3.0           # تایم‌اوت منطقی
CONCURRENT_LIMIT = 20   # همزمانی کم (برای جلوگیری از بن شدن)
LATEST_LIMIT = 30       # از هر منبع، فقط 30 تای آخر (جدیدترین‌ها) رو بردار

# لیست مرورگرهای واقعی برای گول زدن سرورها
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# ==========================================
# 🛠 توابع
# ==========================================

async def fetch_source(session, url):
    """دانلود سورس با هدرهای رندوم (مثل انسان)"""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        async with session.get(url, headers=headers, timeout=10) as response:
            text = await response.text()
            
            # استخراج لینک‌ها
            regex = r'(tg://proxy\?server=[^&]+&port=\d+&secret=[^"\s&\n]+|https://t\.me/proxy\?server=[^&]+&port=\d+&secret=[^"\s&\n]+)'
            found = re.findall(regex, text)
            
            # 🔥 نکته کلیدی: برداشتن فقط آخری‌ها (جدیدترین‌ها)
            if len(found) > LATEST_LIMIT:
                # برش لیست و برداشتن LATEST_LIMIT عدد آخر
                return found[-LATEST_LIMIT:] 
            return found
    except:
        return []

async def check_proxy(proxy, semaphore):
    """تست اتصال با رعایت صف"""
    async with semaphore: 
        try:
            # تمیزکاری لینک
            proxy = proxy.replace("https://t.me/proxy", "tg://proxy")
            
            # استخراج آدرس و پورت
            server = re.search(r'server=([^&]+)', proxy).group(1)
            port = int(re.search(r'port=(\d+)', proxy).group(1))
            
            start = time.time()
            # تست اتصال TCP
            future = asyncio.open_connection(server, port)
            reader, writer = await asyncio.wait_for(future, timeout=TIMEOUT)
            
            # محاسبه پینگ
            ping = int((time.time() - start) * 1000)
            
            writer.close()
            await writer.wait_closed()
            
            return {'link': proxy, 'ping': ping}
        except:
            return None

async def main():
    print("🕵️‍♂️ شروع عملیات مخفی (Fresh & Safe Mode)...")
    
    all_candidates = []
    
    # 1. جمع‌آوری هوشمند
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in SOURCES]
        results = await asyncio.gather(*tasks)
        
        # ترکیب نتایج
        for res in results:
            all_candidates.extend(res)

    # حذف تکراری‌ها
    unique_candidates = list(set(all_candidates))
    print(f"📦 کاندیداهای بررسی (جدیدترین‌ها): {len(unique_candidates)} مورد")
    
    # 2. تست با سرعت کنترل شده
    print(f"⚡️ شروع تست (با سرعت {CONCURRENT_LIMIT} ترد)...")
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    tasks = [check_proxy(p, semaphore) for p in unique_candidates]
    
    check_results = await asyncio.gather(*tasks)
    
    # 3. فیلتر و ذخیره
    working_proxies = [r for r in check_results if r is not None]
    
    # مرتب‌سازی بر اساس پینگ
    working_proxies.sort(key=lambda x: x['ping'])
    
    final_links = [x['link'] for x in working_proxies]
    
    if final_links:
        with open("mtproto.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_links))
        print(f"💎 پایان کار! {len(final_links)} پروکسی تازه و سالم ذخیره شد.")
    else:
        print("❌ هیچ پروکسی سالمی پیدا نشد.")

if __name__ == "__main__":
    asyncio.run(main())
