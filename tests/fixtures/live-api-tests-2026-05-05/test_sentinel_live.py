"""Live API test for fetching-sentinel-imagery skill.

Exercises:
- OAuth2 token fetch against Copernicus Data Space Ecosystem
- STAC Catalogue search for Sentinel-2 L2A tiles over a small AOI
- Process API request to render an RGB PNG of the same AOI

The skill's `handling-credentials-safely` discipline applies — we print key
PRESENCE only (length), never the value, and we sanitise URLs in errors.
"""
import json
import os
import pathlib
import re
import sys
import time
import traceback

import httpx


# ---------------------------------------------------------------------------
# Env loader (local; avoids dotenv dep for ad-hoc testing)
# ---------------------------------------------------------------------------
ENV_PATH = (pathlib.Path(__file__).resolve().parents[3] / ".env")
for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    v = v.strip().strip('"').strip("'")
    os.environ.setdefault(k, v)

CID = os.environ.get("SH_CLIENT_ID", "")
CSEC = os.environ.get("SH_CLIENT_SECRET", "")
assert CID and CSEC, "SH_CLIENT_ID and SH_CLIENT_SECRET required"
print(f"[env] SH_CLIENT_ID  loaded, length={len(CID)}, prefix-shape={CID.startswith('sh-')}")
print(f"[env] SH_CLIENT_SECRET loaded, length={len(CSEC)}")


# ---------------------------------------------------------------------------
# Credential-safe HTTP wrappers
# ---------------------------------------------------------------------------
def redact(s: str) -> str:
    s = re.sub(r'((?:client_id|client_secret|api_key|key|token|access_token)=)[^&\s"]+',
               r'\1<redacted>', s, flags=re.IGNORECASE)
    s = re.sub(r'Bearer\s+\S+', 'Bearer <redacted>', s, flags=re.IGNORECASE)
    return s


def safe_post(url: str, **kwargs) -> httpx.Response:
    try:
        r = httpx.post(url, timeout=30, **kwargs)
        r.raise_for_status()
        return r
    except httpx.HTTPStatusError as e:
        body = e.response.text[:300]
        raise RuntimeError(f"POST {redact(str(e.request.url))} -> {e.response.status_code}; body[:300]={redact(body)}") from None
    except Exception as e:
        raise RuntimeError(f"POST {redact(url)} -> {type(e).__name__}: {redact(str(e))}") from None


# ---------------------------------------------------------------------------
# 1. OAuth2 token
# ---------------------------------------------------------------------------
print("\n=== 1. OAuth2 token (CDSE) ===")
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
t0 = time.time()
try:
    r = safe_post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CID,
        "client_secret": CSEC,
    })
    tok = r.json()["access_token"]
    print(f"  HTTP 200 in {time.time()-t0:.2f}s, token length={len(tok)}, expires_in={r.json().get('expires_in')}s")
    HEAD = {"Authorization": f"Bearer {tok}", "User-Agent": "strategic-analyst/0.1"}
    token_ok = True
except Exception as e:
    print(f"  FAIL: {e}")
    token_ok = False
    sys.exit(1)


# ---------------------------------------------------------------------------
# 2. STAC catalogue search
#    AOI: a 0.05° x 0.05° bbox around the Strait of Hormuz waterway
#    (representative of vessel-tracking workflows; lots of Sentinel-2 coverage).
# ---------------------------------------------------------------------------
print("\n=== 2. STAC catalogue search (Sentinel-2 L2A over Strait of Hormuz) ===")
BBOX = [56.20, 26.50, 56.30, 26.55]  # west, south, east, north
START = "2026-04-01T00:00:00Z"
END = "2026-04-30T23:59:59Z"
# IMPORTANT: catalogue.dataspace.copernicus.eu/stac does NOT have Sentinel-1/2.
# Use the SH-compatible catalogue at sh.dataspace.copernicus.eu.
STAC_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"

t0 = time.time()
try:
    r = safe_post(STAC_URL, headers=HEAD, json={
        "collections": ["sentinel-2-l2a"],
        "bbox": BBOX,
        "datetime": f"{START}/{END}",
        "limit": 20,
    })
    feats = r.json().get("features", [])
    print(f"  HTTP 200 in {time.time()-t0:.2f}s, {len(feats)} features in window")
    if feats:
        # filter for L2A and lowest cloud
        l2a = [f for f in feats if "L2A" in f.get("id", "")]
        candidates = l2a if l2a else feats
        candidates.sort(key=lambda f: f.get("properties", {}).get("eo:cloud_cover", 100))
        top = candidates[0]
        cloud = top["properties"].get("eo:cloud_cover")
        acquired = top["properties"].get("datetime")
        print(f"  best tile: id={top['id'][:60]}...")
        print(f"            cloud_cover={cloud}, datetime={acquired}, type={top['properties'].get('productType')}")
        catalogue_ok = True
    else:
        print("  no features returned — widening criteria might be needed")
        catalogue_ok = False
except Exception as e:
    print(f"  FAIL: {e}")
    catalogue_ok = False


# ---------------------------------------------------------------------------
# 3. Process API — render a small RGB PNG (cheap PU)
# ---------------------------------------------------------------------------
print("\n=== 3. Process API (RGB render, 256x256) ===")
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
RGB_EVAL = """//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04"],
    output: { bands: 3, sampleType: "AUTO" }
  };
}
function evaluatePixel(s) {
  return [2.5 * s.B04, 2.5 * s.B03, 2.5 * s.B02];
}
"""
t0 = time.time()
try:
    r = safe_post(PROCESS_URL, headers=HEAD, json={
        "input": {
            "bounds": {
                "bbox": BBOX,
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from": START, "to": END},
                    "maxCloudCoverage": 30,
                },
            }],
        },
        "output": {
            "width": 256,
            "height": 256,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}],
        },
        "evalscript": RGB_EVAL,
    })
    OUT = (pathlib.Path(__file__).resolve().parents[3] / "cache/sentinel/rgb-test.png")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(r.content)
    print(f"  HTTP 200 in {time.time()-t0:.2f}s, image bytes={len(r.content)}")
    print(f"  saved to {OUT}")
    print(f"  content-type={r.headers.get('content-type')}")
    process_ok = True
except Exception as e:
    print(f"  FAIL: {e}")
    process_ok = False


print("\n=== summary ===")
print(json.dumps({
    "oauth_token": token_ok,
    "catalogue_search": catalogue_ok,
    "process_render": process_ok,
}, indent=2))
