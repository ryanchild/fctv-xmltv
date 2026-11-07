# Fort Collins TV (FCTV) Guide Downloader

Fetches Fort Collins TV guide data from the Cablecast JSON API (`reflect-vod-fcgov.cablecast.tv`) and converts it to XMLTV format.

The guide and playlist are **automatically updated and committed by GitHub Actions** twice daily directly to the repository and published to GitHub Releases, so you don't need to run or host any containers.

---

## 📺 Direct raw.githubusercontent.com URLs (Recommended)

These URLs serve the files directly without HTTP redirects, which offers maximum compatibility across IPTV players and media servers (e.g. Channels DVR, TiviMate, OTT Navigator, Jellyfin, Plex, Emby, TVHeadend):

| Resource | Direct `raw.githubusercontent.com` URL | Description |
| :--- | :--- | :--- |
| **XMLTV Guide (XML)** | `https://raw.githubusercontent.com/ryanchild/fctv-xmltv/master/fctv.xml` | Raw uncompressed XMLTV guide |
| **XMLTV Guide (Compressed)** | `https://raw.githubusercontent.com/ryanchild/fctv-xmltv/master/fctv.xml.gz` | Gzip-compressed XMLTV guide (bandwidth friendly) |
| **M3U Playlist** | `https://raw.githubusercontent.com/ryanchild/fctv-xmltv/master/fctv.m3u` | M3U playlist pointing to the FCTV live stream |

*The `tvg-id` in `fctv.m3u` matches the `FCTV` channel ID in `fctv.xml`, enabling automatic channel-to-EPG mapping in your player.*

---

## 📦 GitHub Release URLs (Alternative)

If you prefer GitHub Releases:

- **XMLTV Guide (XML):** `https://github.com/ryanchild/fctv-xmltv/releases/latest/download/fctv.xml`
- **XMLTV Guide (GZ):** `https://github.com/ryanchild/fctv-xmltv/releases/latest/download/fctv.xml.gz`
- **M3U Playlist:** `https://github.com/ryanchild/fctv-xmltv/releases/latest/download/fctv.m3u`

---

## ⚙️ How It Works (GitHub Actions)

A GitHub Actions workflow ([`.github/workflows/generate-guide.yml`](.github/workflows/generate-guide.yml)) runs twice daily (11:15 UTC and 23:15 UTC, ~4:15 AM and 4:15 PM Mountain Time):
1. Fetches the schedule for today and the next two days from Cablecast.
2. Generates `fctv.xml` and compresses `fctv.xml.gz`.
3. Commits and pushes the updated files directly to the `master` branch using `[skip ci]` (powering the `raw.githubusercontent.com` URLs).
4. Updates the rolling `latest` GitHub Release assets.
5. If upstream Cablecast returns no data (e.g. temporary downtime), the workflow aborts to protect your existing guide from being overwritten with empty data.

---

## 💻 Local Usage

To run the guide generator locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the guide generator (defaults to ./fctv.xml)
python src/fctv_guide.py

# Or specify a custom output path
python src/fctv_guide.py /path/to/custom_guide.xml
```
