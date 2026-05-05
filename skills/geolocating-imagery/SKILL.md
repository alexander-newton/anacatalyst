---
name: geolocating-imagery
description: Use when an image or video is cited as evidence — strike footage, protest scenes, satellite-derived claims, military movement, "this is happening at X". Triggers include "where was this taken", "is this real", "geolocate this", "verify this image", reverse-image-search requests, and any case where a photo or video is being treated as evidence rather than illustration.
---

# Geolocating and Verifying Imagery

## Overview

A photo or video presented as evidence has three things you need to confirm: **what** is depicted, **where** it was taken, and **when**. The first you can usually read off the image; the second and third are detective work. The skill is the standard Bellingcat-style chain — reverse search → first-known-appearance → geocoding cues → terrain match → time-of-day verification — applied with the discipline that **AI-generated imagery is now common**, so a verification chain that doesn't address generative artefacts is incomplete.

**Core principle:** *Treat any image without a verifiable source chain as unconfirmed regardless of how plausible it looks.* Plausibility is a property of the analyst's prior, not of the image.

## When to Use

- An image / video is being cited in an evidence ledger or claim.
- A social-media post includes media as supporting evidence.
- "Footage shows…" or "satellite imagery confirms…" is in the draft.
- A claim about *where* something happened depends on geocoded landmarks.
- Suspected AI-generated content: too-glossy, anatomical inconsistencies, mangled text, repeating textures.

**Skip for:**
- Stock or illustrative imagery clearly labelled as such.
- Imagery from a primary source you trust (an official defence ministry briefing, a published satellite operator's release).
- Internal team material.

## The Workflow

### 1. Reverse-image search — find earliest known appearance

Always start here. The image may be old, recycled, or already debunked.

| Tool | Strength |
|---|---|
| **TinEye** | Best for finding the earliest indexed appearance and tracing rehosting chains. |
| **Yandex Images** | Strongest face/object matching, especially for non-Western imagery. The default for any image that may originate in Russian, Turkish, Chinese, or Iranian media. |
| **Google Images** | Broad but ranks recent over earliest; useful as a third check, not first. |
| **Bing Visual Search** | Sometimes catches what Google misses. |

For each tool, record: did it return hits? What's the earliest date observed? Are any of the hits from contexts that contradict the current claim ("same image, different conflict, three years ago")?

If reverse search finds the image *earlier than* the current claim's date — the image is recycled. Stop and report.

### 2. Identify geocoding cues

Walk the image systematically. Record what you see:

| Cue | What it tells you |
|---|---|
| **Signage** (road signs, shop names, advertisements) | Country, often city. Read the script. |
| **Vehicle plates / formats** | Country (plate format is often country-distinctive). |
| **Architecture** | Period and region. Soviet-era panel housing vs Ottoman vs Bauhaus vs colonial — all distinguishable. |
| **Vegetation** | Climate band. Palm trees rule out high latitudes; conifers rule out tropics. |
| **Terrain / horizon** | Mountains, coast, plains. Shape of mountains is often diagnostic. |
| **Power lines, road markings** | Country-specific norms (lane width, line colour, tower design). |
| **Uniforms, equipment** | Military / police / emergency-service identifiers. Patches, helmet types, vehicle models. |
| **Language fragments** | Even partial text in a writing system narrows the country space. |
| **Sun position** | Time of day plus rough latitude (combined with shadows). |

A useful checklist mantra: **script → signage → architecture → vegetation → terrain**. Most images can be narrowed to a country in three of these.

### 3. Cross-reference against map sources

Once you have candidate locations:

- **Google Earth / Google Street View** — the default. Match landmarks, building shapes, road geometry.
- **Yandex Maps / Yandex Panoramas** — better than Google for Russia, Belarus, Central Asia, Turkey.
- **Mapillary** — crowdsourced street-level imagery, good for places Google hasn't driven.
- **Wikimapia** — annotated points of interest.
- **OpenStreetMap (Overpass API)** — query for *features* ("petrol stations within 500m of a railway crossing within X polygon").

Bellingcat's *OSM Search* tool wraps Overpass for feature-pattern searches and is the standard for this step.

### 4. Verify time and lighting

Time-of-day claims can be falsified with sun-angle math.

- **SunCalc** (`suncalc.org`) — given a date, time, and location, returns sun azimuth and altitude. Compare to the shadows in the image. A 30° mismatch on the sun azimuth means the time or location claim is wrong.
- **Mooncalc** — same for moon position; useful for night imagery.
- **Weather** — historical weather data (NOAA, Wunderground archive). If the claim is "this rainy footage from Tuesday", and Tuesday was clear and dry at the location, the claim is wrong.

### 5. Check for AI-generation artefacts

**This step is non-optional now.** Generative-image models are cheap, fast, and getting harder to spot. Look for:

| Artefact | What it looks like |
|---|---|
| **Mangled text** | Signage with garbled letters, plates that aren't valid in any country, watch faces with impossible numbers. |
| **Anatomical inconsistencies** | Extra fingers, asymmetric ears, eyes that don't focus on the same point, teeth that don't line up. |
| **Impossible reflections** | Mirror or window reflections that don't match the scene; light sources reflecting from wrong angles. |
| **Repeating-pattern backgrounds** | Crowds where faces repeat, foliage with copied-and-pasted leaves. |
| **Seams in shadows / edges** | Object edges that don't align with their cast shadows. |
| **Over-glossy textures** | Skin too smooth, foliage too uniform, all surfaces with the same contrast. |
| **Watermark presence / absence** | An AI-watermark (e.g., SynthID-like indicator); or *suspicious absence* of expected metadata. |

Tools: invert / increase contrast / push saturation in your viewer to make seams visible. EXIF inspection (`exiftool`) — most images stripped on social, but try anyway. **Hive AI**, **Optic AI-or-Not**, **Sensity** are commercial AI-detection services; treat their output as one signal, not as ground truth.

### 6. Document the verification chain

Every image cited as evidence gets a row in the evidence ledger plus a *verification trail* in the row's `notes`. A working format:

```
notes: "Image verified by: TinEye (earliest 2026-05-02, current claim 2026-05-05 — consistent);
geocoding cues: shop signage in Cyrillic + tram tracks + Soviet-era housing block →
matched to Kharkiv via Yandex Panoramas (street: Sumska, 49.999N 36.231E);
sun azimuth 134° at observed shadow direction consistent with 09:30 UTC at lat 50N on 2026-05-05;
no AI-generation artefacts visible at 2x zoom; EXIF stripped (social-media upload)."
```

If any step fails or returns ambiguous results, the row is downgraded and the failure is recorded.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Skipping reverse-image search | The first step. Old / recycled imagery is the cheapest way to be wrong. |
| Trusting the social-media post's caption | Captions are the *claim*, not the evidence. Verify the image, then compare to the caption. |
| Single-tool reverse search | Yandex catches what Google misses, especially non-Western imagery. Use at least two. |
| Treating an absence of reverse-search hits as "this is original" | It might be original, or it might be too small / too new / behind a CDN. Move to geocoding. |
| Identifying "a Eurasian city" and stopping there | The job is the specific location, not the broad region. Push to building-level. |
| Sun-angle check only at the photographer's claimed coordinates | Verify the *shadow direction* is consistent with the time-of-day claim independently. Many fake-time claims fail at this step. |
| Ignoring AI-generation possibility for "ordinary-looking" imagery | The default assumption now is *might be generated*. The check is non-optional. |
| Accepting a Hive / Optic verdict as ground truth | Detection tools have high false-negative rates on newer models. Treat as one signal. |
| Forgetting to record the *negative* verifications | "Reverse search found no hits before 2026-05-05" is a finding worth recording. Negative verification is verification. |

## Adversarial Imagery — Active Manipulation

Beyond AI generation, watch for:

- **Recycled imagery presented as current** — by far the most common.
- **Mirror-flipped imagery** — reverses signage, plate text, vehicles' driver-side; defeats some reverse-search tools. Try mirroring the image and re-searching.
- **Cropped imagery** — geocoding cues deliberately cut. Search the full versions; ask whoever posted it for the original aspect ratio.
- **Re-encoded / heavily-compressed imagery** — destroys EXIF and some artefacts. The verification chain must lean more on cues than on metadata.
- **Pre-positioned propaganda** — imagery prepared in advance of an event, released to the timeline at the planned moment. The earliest-appearance check usually catches this.

## Cross-References

- `archiving-with-wayback` — archive the page hosting the image *and* the image URL itself.
- `building-evidence-ledger` — the row format the verification chain populates.
- `translating-foreign-source` — for any signage or caption text in non-English script.
- `strategic-news-analysis` — the source-hierarchy under which OSINT outlets like Bellingcat and ISW are graded.
