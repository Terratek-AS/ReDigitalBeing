import json
import urllib.request
import urllib.error

LOCAL_BASE = "http://127.0.0.1:8000"
PAGES_BASE = "https://terratek-as.github.io/ReDigitalBeing"

pages_urls = [
    f"{PAGES_BASE}/",
    f"{PAGES_BASE}/index.html",
    f"{PAGES_BASE}/config.js",
    f"{PAGES_BASE}/app.js",
    f"{PAGES_BASE}/manifest.json",
]

def fetch(url: str):
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return {"url": url, "ok": True, "status": resp.status, "len": len(body)}
    except urllib.error.HTTPError as e:
        return {"url": url, "ok": False, "status": e.code, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"url": url, "ok": False, "status": None, "error": str(e)}

def cors_request(method: str, origin: str, path: str, with_json: bool = False):
    url = f"{LOCAL_BASE}{path}"
    headers = {"Origin": origin}
    data = None
    if method == "OPTIONS":
        headers["Access-Control-Request-Method"] = "GET" if not with_json else "POST"
        headers["Access-Control-Request-Headers"] = "content-type"
    elif method == "POST":
        headers["Content-Type"] = "application/json"
        data = b"{}"

    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            hdr = dict(resp.headers.items())
            return {
                "method": method,
                "origin": origin,
                "path": path,
                "status": resp.status,
                "acao": hdr.get("Access-Control-Allow-Origin"),
                "acam": hdr.get("Access-Control-Allow-Methods"),
                "acah": hdr.get("Access-Control-Allow-Headers"),
                "ok": True,
            }
    except urllib.error.HTTPError as e:
        hdr = dict(e.headers.items()) if e.headers else {}
        return {
            "method": method,
            "origin": origin,
            "path": path,
            "status": e.code,
            "acao": hdr.get("Access-Control-Allow-Origin"),
            "acam": hdr.get("Access-Control-Allow-Methods"),
            "acah": hdr.get("Access-Control-Allow-Headers"),
            "ok": False,
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        return {
            "method": method,
            "origin": origin,
            "path": path,
            "status": None,
            "acao": None,
            "acam": None,
            "acah": None,
            "ok": False,
            "error": str(e),
        }

def main():
    print("== Local health/ui reachability ==")
    print(json.dumps(fetch(f"{LOCAL_BASE}/health"), ensure_ascii=False))
    print(json.dumps(fetch(f"{LOCAL_BASE}/ui"), ensure_ascii=False))

    print("\n== GitHub Pages runtime assets ==")
    for u in pages_urls:
        print(json.dumps(fetch(u), ensure_ascii=False))

    print("\n== CORS matrix ==")
    allowed = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://terratek-as.github.io",
    ]
    disallowed = [
        "https://evil.example.com",
        "https://randomdomain.com",
    ]

    for o in allowed + disallowed:
        print(json.dumps(cors_request("OPTIONS", o, "/health"), ensure_ascii=False))
        print(json.dumps(cors_request("GET", o, "/health"), ensure_ascii=False))

if __name__ == "__main__":
    main()
