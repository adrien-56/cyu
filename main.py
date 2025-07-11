import tls_client
import os
import logging
import sys
import subprocess
import pkg_resources
import colorama
from colorama import init, Fore, Style
import requests
import string
import json
import pyautogui
import time
import datetime
import random
import hashlib
import wmi
import keyboard
from typing import Optional, Dict
import itertools

PROXY_FILE = "proxiex.txt"
proxies = []
proxy_cycle = None

def install_requirements():
    required_packages = [
        'colorama',
        'requests',
        'pyautogui',
        'keyboard',
        'wmi',
        'tls_client'
    ]
    
    print(f"{Fore.BLUE}[INFO]{Fore.YELLOW} Checking required packages...{Style.RESET_ALL}")
    
    for package in required_packages:
        try:
            pkg_resources.require(package)
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"{Fore.BLUE}[INFO]{Fore.YELLOW} Installing {package}...{Style.RESET_ALL}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"{Fore.BLUE}[INFO]{Fore.GREEN} Successfully installed {package}{Style.RESET_ALL}")

try:
    import colorama
    from colorama import init, Fore, Style
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "--quiet"])
    import colorama
    from colorama import init, Fore, Style

init()

def timestamp():
    return f"{Fore.MAGENTA}[{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}]{Fore.RESET}"

def load_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        default_config = {
            "humanizer": True,
            "non_cap_maker": True,
            "server_invite_code": ""
        }
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

Config = load_config()

def load_proxies() -> None:
    global proxies, proxy_cycle
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if proxies:
            proxy_cycle = itertools.cycle(proxies)
            print(f"{timestamp()}{Fore.GREEN}[PROXY] Loaded {len(proxies)} proxies{Style.RESET_ALL}")
        else:
            print(f"{timestamp()}{Fore.RED}[PROXY] No valid proxies found in {PROXY_FILE}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{timestamp()}{Fore.RED}[PROXY] File {PROXY_FILE} not found{Style.RESET_ALL}")
        proxies = []

def get_next_proxy() -> Optional[Dict[str, str]]:
    global proxy_cycle
    
    if not proxy_cycle:
        return None
        
    try:
        proxy = next(proxy_cycle)
        username, password, host, port = proxy.split(':')
        formatted_proxy = f"http://{username}:{password}@{host}:{port}"
        print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.GREEN} Switching to next proxy{Style.RESET_ALL}")
        return {
            "http": formatted_proxy,
            "https": formatted_proxy
        }
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[PROXY] Error getting next proxy: {str(e)}{Style.RESET_ALL}")
        return None

def test_proxy_connection(proxy):
    try:
        client = tls_client.Session(
            client_identifier='chrome_110',
            random_tls_extension_order=True
        )
        client.proxies = proxy
        response = client.get("https://discord.com/api/v9/experiments")
        return response.status_code == 200
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[ERROR] Proxy test failed: {str(e)}{Style.RESET_ALL}")
        return False

def configure_chrome_proxy(proxy_dict):
    # Note: Chrome proxy for incognito will be set via command line args
    if not proxy_dict:
        return None
    proxy_url = proxy_dict['http']
    return proxy_url

def get_chrome_path():
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    print(f"{timestamp()}{Fore.RED}[ERROR] Chrome not found! Please install Chrome browser.{Style.RESET_ALL}")
    print(f"{timestamp()}{Fore.YELLOW}[INFO] You can download Chrome from: https://www.google.com/chrome{Style.RESET_ALL}")
    input("Press Enter to exit...")
    sys.exit(1)

def get_emails(email, api_key=None):
    headers = {"X-API-KEY": api_key} if api_key else {}
    response = requests.get(
        "https://cybertemp.xyz/api/getMail",
        params={"email": email},
        headers=headers
    )
    response.raise_for_status()
    return response.json()

def generate_unique_username():
    try:
        with open("usernames.txt", "r", encoding='cp1252') as f:
            usernames = f.readlines()
            usernames = [username.strip() for username in usernames]
            random_name = random.choice(usernames)
            random_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
            random_numbers = ''.join(random.choice('0123456789') for _ in range(2))
            new_username = f"{random_name}{random_suffix}{random_numbers}"
            return new_username
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[ERROR] Failed to generate username: {str(e)}{Style.RESET_ALL}")
        return f"user{''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))}"

def find_verification_link(email_data):
    # Example: search for Discord verification mail
    for mail in email_data.get("mails", []):
        if "discord" in mail.get("subject", "").lower() and "verify" in mail.get("subject", "").lower():
            # Try extracting the link - this depends on the API response structure
            body = mail.get("body", "")
            # Simple search for a discord verification URL
            import re
            match = re.search(r"https://discord\.com/verify\S+", body)
            if match:
                return match.group(0)
    return None

class Booster:
    # ... unchanged as before ...
    def __init__(self):
        self.client = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )
        self.tokens = []
        self.proxies = []
        self.failed = []
        self.success = []
        self.captcha_solved = []
        self.captcha_unsolved = []
        self.failed_tokens = []
    
    # ... rest unchanged ...

class Changer:
    # ... unchanged as before ...
    def __init__(self):
        self.cookies = self.get_discord_cookies()
    # ... rest unchanged ...

if __name__ == "__main__":
    try:
        print(f"{timestamp()}{Fore.YELLOW}[PROXY] Loading proxies...{Style.RESET_ALL}")
        load_proxies()
        
        # Get the Chrome path for incognito
        chrome_path = get_chrome_path()
        discord_register_url = "https://discord.com/register"

        # If 'usernames.txt' doesn't exist, create it
        if not os.path.exists("usernames.txt"):
            with open("usernames.txt", "w") as f:
                f.write("user\ntest\ndemo\nexample\n")

        # User input email and api_key for cybertemp
        user_email = input("Enter the base email for registration: ").strip()
        user_api_key = input("Enter cybertemp.xyz API key (leave blank for free tier): ").strip() or None

        email_index = 0

        while True:
            for attempt in range(5):
                proxy = get_next_proxy()
                if not proxy:
                    print(f"{timestamp()}{Fore.RED}[ERROR] No proxies available{Style.RESET_ALL}")
                    sys.exit(1)
            
                print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.YELLOW} Testing proxy: {proxy['http']}{Style.RESET_ALL}")
            
                if test_proxy_connection(proxy):
                    print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.GREEN} Found working proxy{Style.RESET_ALL}")
                    chrome_proxy_url = configure_chrome_proxy(proxy)
                    break
                print(f"{timestamp()}{Fore.RED}[PROXY] Failed, trying next...{Style.RESET_ALL}")
                time.sleep(2)
            else:
                print(f"{timestamp()}{Fore.RED}[ERROR] Could not find working proxy after {attempt+1} attempts{Style.RESET_ALL}")
                sys.exit(1)

            # Launch Chrome incognito with proxy, open Discord registration
            chrome_args = [
                chrome_path,
                "--incognito",
                f"--proxy-server={chrome_proxy_url}",
                discord_register_url
            ]
            chrome_proc = subprocess.Popen(chrome_args)
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Opened the Discord registration page in Incognito Chrome" + Style.RESET_ALL)
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW}" + " [!] Press Enter to start registration" + Style.RESET_ALL)
            keyboard.wait('enter')
            
            # Fetch emails using API
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW} Fetching emails from API...{Style.RESET_ALL}")
            email_data = get_emails(user_email, user_api_key)
            emails_list = email_data.get("emails", [])
            if email_index >= len(emails_list):
                print(f"{timestamp()}{Fore.RED}[ERROR] No more emails left from API!{Style.RESET_ALL}")
                sys.exit(1)
            email = emails_list[email_index]
            email_index += 1

            # Use a default password for the email, or generate one
            email_pass = "ultimate12$$"

            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Using mail from API: {email}" + Style.RESET_ALL)
            
            # Username for account
            name = generate_unique_username()

            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Starting registration" + Style.RESET_ALL)
            time.sleep(3)

            # Fill registration form via pyautogui
            pyautogui.write(email)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write(name) 
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write(name) # Display name (if required)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write(email_pass)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write("12") # Day
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write("5") # Month  
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write("1996") # Year
            time.sleep(0.5)
            pyautogui.moveTo(679, 805)
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(0.5)
            pyautogui.press('enter')

            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Registration submitted" + Style.RESET_ALL)
            time.sleep(2)

            # Wait for Discord verification mail (poll API)
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW} Waiting for Discord verification mail...{Style.RESET_ALL}")
            verification_link = None
            for poll_attempt in range(60):
                email_data = get_emails(user_email, user_api_key)
                verification_link = find_verification_link(email_data)
                if verification_link:
                    print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN} [+] Verification mail received! Opening link...{Style.RESET_ALL}")
                    # Open link in new Chrome tab (incognito)
                    subprocess.Popen([
                        chrome_path,
                        "--incognito",
                        f"--proxy-server={chrome_proxy_url}",
                        verification_link
                    ])
                    break
                time.sleep(5)
            else:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Did not receive verification mail in time{Style.RESET_ALL}")

            # Save email and password
            try:
                with open("email_pass.txt","a") as f:
                    f.write(f"{email}:{email_pass} \n")
                    print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}"+"[+] EMAIL AND PASSWORD SAVED TO email_pass.txt" + Style.RESET_ALL)
            except Exception as e:
                print(timestamp(),Fore.RED + f"Error saving email/password: {e}" + Style.RESET_ALL)
                
            # Get token
            try:
                session = requests.Session()
                with open('tokens.txt', 'a') as f:
                    payload = {
                        'login': email,
                        'password': email_pass,
                    }
                    headers = {
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Origin': 'https://discord.com',
                        'Referer': 'https://discord.com/login'
                    }
                    response = session.post('https://discord.com/api/v9/auth/login', json=payload, headers=headers)
                    try:
                        response_data = response.json()
                        if response.status_code == 200 and 'token' in response_data:
                            token = response_data['token']
                            f.write(f'{token}\n')
                            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Logged in to {email} with token {token[:25]}"+"***" + Style.RESET_ALL)
                            with open('evs.txt', 'a') as a:
                                a.write(f'{email}:{email_pass}:{token}\n')
                        else:
                            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Failed to login to {email}. Error: {response_data}" + Style.RESET_ALL)
                    except json.JSONDecodeError:
                        print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Failed to parse response for {email}. Response: {response.text}" + Style.RESET_ALL)
            except Exception as e:
                print(timestamp(),Fore.RED + f"Error getting token: {e}" + Style.RESET_ALL)
            
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.LIGHTMAGENTA_EX}" + f" [+] HUMANIZING TOKEN",token[:25]+"***")
            changer = Changer()
            ishumanizertrue = Config["humanizer"]
            if ishumanizertrue:
                try:
                    changer.Add_HypeSquad(token)
                    changer.Add_Pron(token)
                    changer.Add_Bio(token)
                    print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.LIGHTMAGENTA_EX}" + f"[+] HUMANIZED TOKEN",token[:25]+"***")
                except:
                    print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED}" + f" [-] FAILED TO HUMANIZE TOKEN",token[:25]+"***")
            isnoncapmaker = Config["non_cap_maker"]
            if isnoncapmaker:
                b = Booster()
                invite = Config["server_invite_code"]
                c = b.join(token=token,invite=invite)
                g = 1
                while c!=2:
                    c = b.join(token=token,invite=invite)
                    g+=1
                print("MADE TOKEN",token[:25]+"***",f"NON CAP IN {g} TRIES")

            # Close Chrome tab
            chrome_proc.terminate()
            time.sleep(1)
                
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}Critical error: {str(e)}{Style.RESET_ALL}")
        input("Press Enter to exit...")
        sys.exit(1)
                    
