---
name: fetching-sentinel-imagery
description: Use when the analyst needs free satellite imagery — Sentinel-2 optical (10m, every 5 days globally) or Sentinel-1 SAR (cloud-piercing, every 6 days) — to verify a claim, detect change, or characterise a location. Triggers include "is this base real", "what does the satellite show", "did this site expand", "before-and-after", NDVI / burn-scar / vegetation-loss queries, and any verification step that turns on what is physically present at a coordinate.
---

# Fetching Sentinel-1/2 Imagery

## Overview

The European Space Agency's Sentinel constellation provides **free, openly-licensed, globally-revisited satellite imagery** at resolutions sufficient for most analyst questions: 10m for optical (Sentinel-2) and 10m for SAR (Sentinel-1). Cloud-cover filtering, change detection, and cloud-piercing radar are all available without a paid commercial provider — the free tier covers most "what is at this location, did it change" questions outside the very fast tempo of live combat reporting (where Planet/Maxar's tasked imagery is the only option).

**Core principle:** *The image is evidence; the metadata is provenance.* Always record the satellite, the acquisition timestamp, the cloud-cover percentage, the processing level, and the tile ID alongside the image. A figure without that trail is illustration, not evidence.

## When to Use

- Verifying a claim about ground truth at a named coordinate (a port, an airfield, a refugee camp, a damaged building).
- Detecting change between two dates (construction, destruction, burning, deforestation, flooding).
- Spotting **vegetation health** (NDVI) — agricultural collapse, drought stress, post-conflict recovery.
- Cloud-piercing verification (SAR) when a region has persistent cloud cover or when the relevant date is overcast.
- Cross-checking a media-reported satellite image against the public archive.

**Skip for:**
- Real-time / sub-daily revisit — Planet's daily imagery or commercial tasked acquisitions are the only options here.
- Sub-3m resolution detail — Maxar/Planet's sub-metre is required for vehicle-counting, individual building damage assessment, etc. Sentinel-2 at 10m groups vehicles and obscures small damage.
- Indoor / urban-canyon questions — satellite imagery sees roofs.

## Two Free Providers

Both expose the same Sentinel data; pick by latency and ergonomics.

### A. Copernicus Data Space Ecosystem (CDSE) — preferred default

The current EU-run successor to the older SciHub. Generous free tier; STAC-compliant catalogue; OData and Sentinel Hub-compatible Process API.

Register at `https://dataspace.copernicus.eu/`. Get OAuth2 client credentials at `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/account/`.

```
SH_CLIENT_ID=...           # Sentinel Hub-compatible
SH_CLIENT_SECRET=...
```

### B. Sentinel Hub (Sinergise / Planet)

Commercial-friendly free tier (smaller PU budget than CDSE). Identical API to the Process and Catalogue APIs that CDSE now also serves. Use this if your workflow already integrates with Planet's stack.

Register at `https://apps.sentinel-hub.com/dashboard/`. Same OAuth2 pattern.

The skills below assume CDSE. To switch to Sentinel Hub, change the base URL only:

| Endpoint | CDSE | Sentinel Hub |
|---|---|---|
| OAuth2 token | `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token` | `https://services.sentinel-hub.com/oauth/token` |
| Catalogue (SH-compatible STAC) | `https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/` | `https://services.sentinel-hub.com/api/v1/catalog/1.0.0/` |
| Process API | `https://sh.dataspace.copernicus.eu/api/v1/process` | `https://services.sentinel-hub.com/api/v1/process` |

**Catalogue endpoint subtlety (verified 2026-05-05):** CDSE has *two* catalogue surfaces:

- `catalogue.dataspace.copernicus.eu/stac/` — **does NOT include Sentinel-1/2** directly. It only exposes Copernicus Contributing Missions (`ccm-optical`, `ccm-sar`) and CLMS burnt-area products. Use this only for those.
- `sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/` — the Sentinel Hub-compatible catalogue. **This is the one for Sentinel-1/2 work.** Collection IDs match the Process API's `type` field exactly: `sentinel-2-l2a`, `sentinel-2-l1c`, `sentinel-1-grd`, `sentinel-3-olci-l2`, `sentinel-5p-l2`, plus `landsat-ot-l1`.

The OData API at `catalogue.dataspace.copernicus.eu/odata/v1/Products` is the third surface — bulk listing and download — but for analyst-grade tile selection the SH-compatible catalogue above is the right tool.

## Authentication

OAuth2 client-credentials flow returns a Bearer token valid for 10 minutes.

```python
import os, httpx

def cdse_token() -> str:
    r = httpx.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["SH_CLIENT_ID"],
            "client_secret": os.environ["SH_CLIENT_SECRET"],
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["access_token"]
```

Cache the token; refresh before each batch fetch. `Authorization: Bearer <token>` on all subsequent calls.

## The Three Operations

### 1. Catalogue search — what's available for an AOI and time window

Sentinel-2 L2A (atmospherically-corrected reflectance, ready for analysis):

```python
import httpx, datetime as dt

def catalogue_search(token: str, bbox: list, start: dt.date, end: dt.date,
                     collection: str = "sentinel-2-l2a", max_cloud: int = 30) -> dict:
    """Note the URL: SH-compatible catalogue at sh.dataspace.copernicus.eu, NOT
    catalogue.dataspace.copernicus.eu (which lacks Sentinel-1/2)."""
    r = httpx.post(
        "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search",
        json={
            "collections": [collection],
            "bbox": bbox,                 # [west, south, east, north] in WGS84
            "datetime": f"{start.isoformat()}T00:00:00Z/{end.isoformat()}T23:59:59Z",
            "limit": 50,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    feats = r.json().get("features", [])
    # Filter cloud cover client-side (the catalogue accepts a query but the
    # SH-compatible variant ignores eo:cloud_cover in the body)
    return [f for f in feats
            if f["properties"].get("eo:cloud_cover", 100) < max_cloud]
```

Each returned feature has `id` (the tile ID, e.g. `S2A_MSIL2A_20260415T103021_N0510_R108_T31UCT_20260415T134445`), `properties.eo:cloud_cover`, and `geometry`. Pick the lowest-cloud-cover tile in the window.

For Sentinel-1 SAR (cloud-piercing), set `collection="sentinel-1-grd"`. SAR doesn't have cloud cover; it has acquisition mode (`IW` for interferometric wide swath, the default) and polarisation.

### 2. Process API — get a processed image (RGB, NDVI, etc.)

The Process API takes an *evalscript* — a small JS function that turns raw band values into the output you want. The most useful evalscripts for analysts:

**True-colour RGB (Sentinel-2):**

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04"],
    output: { bands: 3, sampleType: "AUTO" },
  };
}
function evaluatePixel(s) {
  return [2.5 * s.B04, 2.5 * s.B03, 2.5 * s.B02];  // 2.5x stretch for visibility
}
```

**NDVI (vegetation health):**

```javascript
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: { bands: 1, sampleType: "FLOAT32" },
  };
}
function evaluatePixel(s) {
  return [(s.B08 - s.B04) / (s.B08 + s.B04 + 1e-6)];  // NDVI in [-1, 1]
}
```

**SAR backscatter (cloud-piercing change detection):**

```javascript
//VERSION=3
function setup() {
  return {
    input: ["VV", "VH"],
    output: { bands: 2, sampleType: "FLOAT32" },
  };
}
function evaluatePixel(s) {
  return [s.VV, s.VH];
}
```

**Submitting a Process request:**

```python
def process_request(token: str, bbox: list, date_from: str, date_to: str,
                    evalscript: str, collection: str = "sentinel-2-l2a",
                    width: int = 1024, height: int = 1024,
                    fmt: str = "image/png") -> bytes:
    r = httpx.post(
        "https://sh.dataspace.copernicus.eu/api/v1/process",
        json={
            "input": {
                "bounds": {"bbox": bbox, "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},
                "data": [{
                    "type": collection,
                    "dataFilter": {
                        "timeRange": {"from": date_from, "to": date_to},
                        "maxCloudCoverage": 20,
                    },
                }],
            },
            "output": {
                "width": width,
                "height": height,
                "responses": [{"identifier": "default", "format": {"type": fmt}}],
            },
            "evalscript": evalscript,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.content  # PNG/JPEG/TIFF bytes
```

For analytical use (NDVI computation, multi-band differencing), request `image/tiff` (returns 32-bit float GeoTIFF) and read with `rasterio` or `xarray`.

### 3. Differencing for change detection

```python
import numpy as np
from io import BytesIO
import rasterio  # uv add rasterio

def fetch_ndvi(token, bbox, date_from, date_to) -> np.ndarray:
    tiff = process_request(token, bbox, date_from, date_to, NDVI_EVALSCRIPT, fmt="image/tiff")
    with rasterio.open(BytesIO(tiff)) as ds:
        return ds.read(1)  # single-band float32

ndvi_before = fetch_ndvi(token, bbox, "2024-05-01T00:00:00Z", "2024-05-15T23:59:59Z")
ndvi_after  = fetch_ndvi(token, bbox, "2026-05-01T00:00:00Z", "2026-05-15T23:59:59Z")
delta = ndvi_after - ndvi_before
# delta < -0.3 mass-flagged as significant vegetation loss
```

## Worked Example — verify a "destroyed bridge" claim

Claim: "the bridge at 30.123°N, 31.456°E was destroyed between 2026-04-01 and 2026-04-30."

```python
token = cdse_token()
bbox = [31.451, 30.118, 31.461, 30.128]   # ~1km square around the bridge

# Pull RGB tiles for before and after
before = process_request(token, bbox, "2026-03-15T00:00:00Z", "2026-03-31T23:59:59Z",
                         RGB_EVALSCRIPT, fmt="image/png")
after  = process_request(token, bbox, "2026-05-01T00:00:00Z", "2026-05-15T23:59:59Z",
                         RGB_EVALSCRIPT, fmt="image/png")
pathlib.Path("evidence/bridge-before.png").write_bytes(before)
pathlib.Path("evidence/bridge-after.png").write_bytes(after)

# Catalogue lookup for the actual tile metadata that was used
search = catalogue_search(token, bbox, dt.date(2026,3,15), dt.date(2026,3,31))
tile_id_before = search["features"][0]["id"]
cloud_before = search["features"][0]["properties"]["eo:cloud_cover"]
```

The evidence-ledger row for the claim now has `primary_url` = the catalogue search response (or the tile ID), `accessed_at` = the fetch timestamp, `notes` = `"Sentinel-2 L2A; tile=<id>; cloud_cover=X%; before/after RGB rendered via custom evalscript at 1024x1024"`. This is verification-grade.

## Pitfalls

| Pitfall | Why | Fix |
|---|---|---|
| Cloud cover invisible until you fetch | Catalogue's `eo:cloud_cover` is per-tile, but a 30%-cloud tile may still be 100% clouded over your specific AOI | Always render a small RGB preview before committing PU budget on a full-resolution analytical fetch |
| Treating SAR brightness as visible-light intensity | SAR is radar backscatter; bright pixels are *radar-reflective*, which doesn't map to "lit up" | Read SAR with awareness of polarisation (VV vs VH); cite as "backscatter", not "image" |
| Old timestamps mislabelled as recent | The catalogue returns `properties.datetime` per the *acquisition*, not the *processing* | Always cite acquisition date, never processing date |
| 5-day "revisit" is global average | At your specific lat/lon the revisit may be 2–10 days. For high-tempo verification, expect gaps | Use SAR (which has different orbit) as a cloud-resistant supplement |
| Forgetting CRS specification in bbox | Process API defaults to CRS84 (lon, lat) but other CRSes require the `properties.crs` field | Always set the CRS explicitly in the request |
| PU (processing unit) burn from large requests | PU consumption scales with output area × bands × bit depth | Start with low-res preview; reserve high-res for the cited tile only |
| Naive RGB looks dark/grey | Atmospheric correction leaves L2A reflectance values in [0, ~0.4] not [0, 1] | Apply 2–3x stretch in the evalscript or contrast-normalise post-fetch |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Fetching a single-date image and treating it as evidence of *change* | Change requires *two* timestamps. Pull before *and* after; difference the bands. |
| Using L1C instead of L2A | L1C is top-of-atmosphere; L2A is surface reflectance. For analytical work always L2A. |
| Cloud-cover filter set too generously | `max_cloud=80` lets through tiles where the AOI is fully obscured. Filter at 20–30% and pre-render a preview. |
| Citing the rendered PNG, not the underlying tile | The PNG is a thumbnail; the *tile ID* is the citation. Record both. |
| Forgetting to log the evalscript | The evalscript determines the output. Two analysts with the same tile and different evalscripts produce different findings. Record the evalscript text in `notes`. |
| Confusing 10m resolution with 10m feature detection | Sentinel-2 distinguishes 10m features at high contrast; sub-10m features (vehicles, doors) are smeared into pixels. |
| Treating absence of clouds as proof | A clear sky on the day of acquisition is independent of conditions over the days between acquisitions. Multiple-date stacks are stronger. |
| Skipping the catalogue step | The catalogue tells you what tiles *exist* for your AOI/window. Fetching blind via Process API can return a fallback tile that doesn't match the claimed date. |

## Cross-References

- **REQUIRED: Apply `handling-credentials-safely`.** OAuth2 Bearer tokens are credential-shaped; never echo `SH_CLIENT_SECRET` or token bytes in summaries or logs. Use header-based auth (already standard) — but if a 401/403 traceback exposes the Authorization header value, redact before logging.
- **Pair with `geolocating-imagery`** for the analyst's verification chain — Sentinel imagery feeds into the reverse-search → cues → SunCalc → AI-artefact workflow as one of the corroborating sources.
- Output rows feed `building-evidence-ledger`. Cite Sentinel imagery at **A2** (primary observation, but with processing-step caveats). Record: satellite, processing level, tile ID, acquisition datetime, cloud-cover percentage, evalscript identity (or hash), AOI bbox.
- `analysing-military-lens` and `analysing-geographic-lens` reach for satellite imagery when claims turn on infrastructure or terrain. The lens-applier agent dispatched on those should know to invoke this skill.
- For sub-metre resolution that Sentinel can't deliver, see (when written): Planet, Maxar, Airbus skills. These require paid subscriptions.
