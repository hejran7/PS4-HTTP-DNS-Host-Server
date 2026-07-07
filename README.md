### PS4 HTTP DNS Host Server

A simple, lightweight HTTP and DNS server to host PS4 exploits on a local network.

---


### HTTP Server
- Hosts your PS4 exploit files on your local network on port 80
- The PS4 browser connects to it and downloads the exploit


### DNS Server
- Runs on port 53 alongside the HTTP server
- Intercepts PS4 DNS queries and redirects these domains to your PC:


---

## Highlights

- Auto-generates `offline.cache` so the PS4 can cache the exploit for offline use
- Runs multi-threaded so multiple PS4 requests are handled simultaneously

---


## Where To Place Your Exploit Files

```
psphive-lapse-2-main/
├── PS4_http_dns_ host_server.exe  ← run this as Administrator
└── host/                          ← put ALL your exploit files here
    ├── index.html                 ← main exploit page
    ├── offline.cache              ← auto-generated, don't touch
    └── files/
        ├── bundle.js
        ├── style.css
        ├── img/
        ├── js/
        └── *.bin
```

**Rules:**
- Everything inside `host/` gets served and cached
- beside `.py`, `.bat`, `.exe`, `.zip` files inside `host/` — they get excluded automatically

---

## How To Run

1. Right-click `PS4_http_dns_ host_server.exe` → **Run as administrator**
2. The terminal shows your PC's IP (e.g. `192.168.x.xxx`)
3. Server is ready when you see `[servers] Running...`

---

## How To Connect Your PS4

### Method A — Direct IP (simplest, no DNS needed)
1. On PS4, go to **Browser**
2. Type your PC's IP directly: `192.168.x.xxx`
3. Exploit loads

### Method B — Domain (via DNS)
1. On PS4 go to **Settings → Network → Set Up Internet Connection**
2. Set **Primary DNS** to your PC's IP (e.g. `192.168.x.xxx`)
3. Open PS4 browser and type `lapse.tow`

### Method C — User's Guide
1. Set **Primary DNS** to your PC's IP same as Method B
2. From PS4 home screen open **User's Guide**
3. It automatically navigates to `manuals.playstation.net` which DNS redirects to your server

---

## Ports Required

| Port | Protocol | Purpose |
|------|----------|---------|
| 80   | TCP      | HTTP — serves exploit files |
| 53   | UDP      | DNS — redirects PS4 domains |

Both require **Administrator privileges** on Windows.

---

## Credits & Special Thanks

| Name | Contribution |
|------|-------------|
| [**Leeful**](https://github.com/Leeful) | Inspiration for combining HTTP + DNS into one server and DNS rules |
| [**Crypt0s**](https://github.com/Crypt0s) | fakedns.py — original DNS MITM server |

---

**This project is for educational and research purposes only. Use at your own risk.**
