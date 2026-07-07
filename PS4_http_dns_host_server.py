# PS4_http_dns_ server.py by hejran7

import sys
import socket
import os
import json
import threading
import time
import msvcrt
import ctypes
import re
from datetime import datetime
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import fakedns as FAKEDNS

# Enable ANSI colors on Windows
ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)

R    = "\033[91m"
G    = "\033[92m"
Y    = "\033[93m"
B    = "\033[94m"
M    = "\033[95m"
C    = "\033[96m"
W    = "\033[97m"
DIM  = "\033[2m"
BO   = "\033[1m"
GOLD = "\033[33m"
RS   = "\033[0m"

PORT     = 80
DNS_PORT = 53
_BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(_BASE_DIR, 'host')

EXCLUDED_DIRS  = {'.git', '__pycache__', '.venv', 'build', 'dist'}
EXCLUDED_EXTS  = {'.py', '.bat', '.bak', '.zip', '.exe', '.mp4', '.mp3', '.sh', '.md', '.spec'}
EXCLUDED_FILES = {'.gitignore', 'LICENSE', 'offline.cache'}
OUTPUT_FILE     = 'offline.cache'
MANIFEST_HEADER = "# PS-Phive! For PS4 7.00-9.60 By Leeful/Sinajet"

# Domains redirected to this PC — PS4 uses these to find the server
DNS_REDIRECT = [
    'lapse.tow',
    'www.playstation.com',
    'manuals.playstation.net',
    r'(get|post).net.playstation.net',
    r'(d|f|h)[a-z]{2}01.(ps4|psp2).update.playstation.net',
    'update.playstation.net',
]

# Domains blocked (resolved to 0.0.0.0)
DNS_BLOCK = [
    r'(.*[.])?207.net',
    r'(.*[.])?akadns.net',
    r'(.*[.])?akamai.net',
    r'(.*[.])?akamaiedge.net',
    r'(.*[.])?playstation.(com|net|org)',
]


def get_machine_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def make_timestamp():
    now = datetime.now()
    cs = f"{int(now.microsecond / 10000):02d}"
    return now.strftime(f"%d/%m/%Y-%H:%M:%S.{cs}")


def create_manifest():
    lines = [
        "CACHE MANIFEST",
        MANIFEST_HEADER,
        f"# {make_timestamp()}",
        "",
        "/",
    ]
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in EXCLUDED_EXTS or filename in EXCLUDED_FILES:
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, ROOT_DIR).replace(os.sep, '/')
            lines.append(rel_path)
    lines += ["", "NETWORK:", "*", "", "SETTINGS:", "prefer-online:"]
    with open(os.path.join(ROOT_DIR, OUTPUT_FILE), 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


def generate_dns_rules(ip):
    rules = []
    for domain in DNS_REDIRECT:
        rules.append(f"A {domain} {ip}")
    for domain in DNS_BLOCK:
        rules.append(f"A {domain} 0.0.0.0")
    return rules


class CustomHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        '.bin':      'application/octet-stream',
        '.mjs':      'application/javascript',
        '.cache':    'text/cache-manifest',
        '.manifest': 'text/cache-manifest',
    }

    def do_GET(self):
        m = re.match(r'^/document/[a-zA-Z\-]{2,5}/(ps4|psvita)(/.*)$', self.path)
        if m:
            self.path = m.group(2) or '/index.html'
        if self.path == '/':
            self.path = '/index.html'
        super().do_GET()

    def do_POST(self):
        if self.path == '/generate_manifest':
            try:
                create_manifest()
                response = {'status': 'success', 'message': f'{OUTPUT_FILE} created. Please refresh.'}
                code = 200
                print(f"{G}[manifest]{RS} {OUTPUT_FILE} regenerated")
            except Exception as e:
                response = {'status': 'error', 'message': str(e)}
                code = 500
                print(f"{R}[manifest error]{RS} {e}")
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, fmt, *args):
        global fetch_count
        msg = fmt % args
        try:
            parts = msg.split('"')
            request = parts[1].strip()
            rest = parts[2].strip()
            method, path, protocol = request.split(' ', 2)
            code = rest.split()[0]
            color = G if code == '200' else B if code == '304' else Y
            fetch_count += 1
            print(f"{DIM}{self.address_string()}{RS} {C}→{RS} {protocol} {color}{rest}{RS} {method} {path}")
        except Exception:
            print(f"{DIM}{self.address_string()}{RS} {C}→{RS} {msg}")


# --- Parse args ---
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        print("Usage: py serve.py [port]")
        sys.exit(1)

IP = get_machine_ip()

# --- Display ---
title = "PS4 Host Server v1.0 by hejran7 inspired by Leeful"
BOX = len(title) + 2
INNER = BOX - 2

def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*m', '', s)

def row(text=""):
    inner = f"  {text}"
    visible_len = len(strip_ansi(inner))
    padding = " " * max(0, INNER - visible_len)
    print(f"{B}║{RS}{inner}{padding}{B}║{RS}")

def lrow(label, value):
    visible_label = strip_ansi(label)
    padding = " " * max(0, 15 - len(visible_label))
    row(f"{label}{padding}{value}")

print(f"\n{B}{'═' * BOX}{RS}")
print(f"{B}║{RS}{BO}{C}{title}{RS}{B}║{RS}")
print(f"{B}{'═' * BOX}{RS}")
lrow(f"{Y}Local IP{RS}",    f"{G}{IP}{RS}")
lrow(f"{Y}Local Host{RS}",  f"{G}http://localhost:{PORT}/{RS}")
row()
row(f"{Y}HTTP Server running on {IP}:{PORT}{RS}")
row()
row(f"{G}Type {B}{IP}{RS}{G} directly in PS4 browser{RS}")
row(f"{G}Primary DNS settings is not needed with HTTP{RS}")
print(f"{B}{'=' * BOX}{RS}")
row(f"{Y}DNS Server running on {IP}:{DNS_PORT}{RS}")
row()
row(f"{G}Set PS4 Primary DNS to {IP}{RS}")
row(f"{G}Then go to {B}lapse.tow{RS}{G} in PS4 browser{RS}")
row(f"{Y}--- OR ---{RS}")
row(f"{G}Type {B}{IP}{RS}{G} directly in PS4 browser{RS}")
row()
stop_text = "Press Esc to stop server"
stop_pad = (INNER - len(stop_text)) // 2
print(f"{B}║{RS}{' ' * stop_pad}{R}{stop_text}{RS}{' ' * (INNER - len(stop_text) - stop_pad)}{B}║{RS}")
print(f"{B}{'═' * BOX}{RS}\n")

# --- Generate manifest ---
print(f"{G}[manifest]{RS} {Y}Generating offline.cache ...{RS}")
create_manifest()
print(f"{G}[manifest]{RS} {Y}Done.{RS}\n")

# --- Start DNS server ---
dns_rules = generate_dns_rules(IP)
try:
    FAKEDNS.main(IP, DNS_PORT, dns_rules, [], False)
except Exception as e:
    print(f"{R}[dns error]{RS} {e} (try running as Administrator)\n")

# --- Start HTTP server ---
os.chdir(ROOT_DIR)
fetch_count = 0
try:
    httpd = TCPServer(("0.0.0.0", PORT), CustomHandler)
except OSError as e:
    print(f"{R}[http error]{RS} {e}")
    sys.exit(1)

server_thread = threading.Thread(target=httpd.serve_forever)
server_thread.daemon = True
server_thread.start()

print(f"{G}[servers]{RS} {Y}Running...{RS}\n")

while True:
    time.sleep(0.05)
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\x1b':  # Esc
            print(f"\n{R}[server]{RS} Stopped. {DIM}Total files fetched: {fetch_count}{RS}")
            httpd.shutdown()
            break
