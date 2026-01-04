import asyncio
import aiohttp
import re
import time
import os

# ==========================================
# 💎 Proxy Sources List (Telegram & GitHub)
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
# ⚙️ Security Settings (Anti-Ban)
# ==========================================
TIMEOUT = 3           # Connection Timeout (seconds)
CONCURRENT_LIMIT = 40 # Max concurrent checks to prevent high CPU usage

# ==========================================
# 🚀 Core Functions
# ==========================================

async def fetch_source(session, url):
    """Fetch content from sources asynchronously."""
    try:
        async with session.get(url, timeout=10) as response:
            return await response.text()
    except:
        return ""

async def check_proxy(proxy, semaphore):
    """
    Test TCP connection to the proxy.
    Uses a semaphore to limit concurrent connections.
    """
    async with semaphore: 
        try:
            # Extract IP and Port using Regex
            # Pattern: server=...&port=...
            server = re.search(r'server=([^&]+)', proxy).group(1)
            port = int(re.search(r'port=(\d+)', proxy).group(1))
            
            start = time.time()
            # Open a TCP connection (Lightweight check)
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(server, port), timeout=TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            
            ping = int((time.time() - start) * 1000)
            return proxy, ping
        except:
            return None, None

async def main():
    print("🔥 Starting Proxy Collector (Safe & Turbo Mode)...")
    
    all_text = ""
    
    # 1. Download all sources concurrently
    print("📥 1. Fetching sources...")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source(session, url) for url in SOURCES]
        results = await asyncio.gather(*tasks)
        all_text = "\n".join(results)

    # 2. Extract links using Regex
    # Supports both tg:// and https://t.me/proxy formats
    print("🔍 2. Extracting and normalizing links...")
    regex = r'(tg://proxy\?server=[^&]+&port=\d+&secret=[^"\s&\n]+|https://t\.me/proxy\?server=[^&]+&port=\d+&secret=[^"\s&\n]+)'
    raw_proxies = re.findall(regex, all_text)
    
    # Normalize links (Convert all to tg://)
    normalized_proxies = set()
    for p in raw_proxies:
        p = p.replace("https://t.me/proxy", "tg://proxy")
        normalized_proxies.add(p)

    print(f"📦 Total Raw Proxies Found: {len(normalized_proxies)}")
    
    # 3. Test proxies with concurrency limit
    print("⚡️ 3. Starting Health Check (Ping Test)...")
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    tasks = [check_proxy(p, semaphore) for p in list(normalized_proxies)]
    
    # Execute tests
    results = await asyncio.gather(*tasks)
    
    # Filter valid proxies
    working_proxies = []
    for proxy, ping in results:
        if proxy:
            working_proxies.append({'link': proxy, 'ping': ping})

    # Sort by speed (Lowest ping first)
    working_proxies.sort(key=lambda x: x['ping'])
    
    # Extract final links
    final_links = [x['link'] for x in working_proxies]

    print(f"✅ Total Valid Proxies: {len(final_links)}")

    # 4. Save to file
    print("💾 4. Saving to file...")
    with open("mtproto.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_links))
    
    print("🎉 Done! File 'mtproto.txt' saved successfully.")

if __name__ == "__main__":
    asyncio.run(main())
