# TLB Hit Podcast Migration Plan

**Goal**: Move podcast hosting from Libsyn to self-hosted on tlbh.it (GitHub Pages now, Cloudflare later)

**Critical Rule**: This plan preserves subscriber continuity. GUIDs never change. Existing subscribers follow the 301 redirect seamlessly.

---

## Pre-Flight Checklist

Before starting, confirm:

- [ ] Artist order decision: "JF Bastien & Chris Leary" (JF first)
- [ ] Album name decision: "TLB Hit" (no emoji for compatibility)
- [ ] Keep `episodes/` directory name (not renaming)
- [ ] Have Libsyn login credentials
- [ ] Have Apple Podcasts Connect access
- [ ] Have Spotify for Podcasters access (if applicable)

---

## Critical Invariants (DO NOT BREAK)

| Rule | Requirement | Source |
|------|-------------|--------|
| **GUIDs** | Copy exactly from Libsyn, never change, emit with `isPermaLink="false"` | [Apple](https://podcasters.apple.com/support/823-podcast-requirements) |
| **Episode numbers** | `itunes:episode` must be positive integer 1-7 (not 0-6) | [podcast-standard.org](https://podcast-standard.org/podcast_standard/) |
| **Explicit flag** | Must be `"true"` or `"false"` (NOT yes/no) | [Apple](https://podcasters.apple.com/support/5440-explicit-content) |
| **301 Redirect** | Libsyn must return HTTP 301 to `https://tlbh.it/feed.xml` | [Apple](https://podcasters.apple.com/support/837-change-the-rss-feed-url) |
| **Redirect duration** | Keep for ≥4 weeks (can leave forever) | [Apple](https://podcasters.apple.com/support/837-change-the-rss-feed-url) |
| **Enclosure length** | Exact file size in bytes as positive integer | [Apple](https://podcasters.apple.com/support/823-podcast-requirements) |
| **XML namespaces** | Use `ET.register_namespace()` only, NOT manual xmlns attrs | Prevents duplicate declarations |

---

## Episode Data (Source of Truth from Libsyn)

```
Episode 0: mov fp, sp
  GUID: c685f738-397d-4b7b-9dc6-171eaf2b07de
  pubDate: Mon, 02 Nov 2020 01:21:16 +0000
  duration: 01:04:28
  file: tlbhit0.mp3 (49,954,944 bytes)

Episode 1: *(char*)0 = 0
  GUID: d5f882cd-bac2-4ede-a51a-daab8e61e51d
  pubDate: Mon, 23 Nov 2020 06:09:40 +0000
  duration: 00:43:52
  file: tlbhit1.mp3 (20,698,363 bytes)

Episode 2: https://tlbh.it^M
  GUID: 407713de-1c3f-4eac-940a-a28269788270
  pubDate: Sun, 21 Feb 2021 22:32:54 +0000
  duration: 00:56:35
  file: tlbhit2.mp3 (43,645,007 bytes)

Episode 3: __builtin_expect(!!(x), 0)
  GUID: a99864d9-d302-40d2-b257-b6258d26ffdf
  pubDate: Mon, 19 Apr 2021 03:05:47 +0000
  duration: 00:39:10
  file: tlbhit3.mp3 (29,671,009 bytes)

Episode 4: t-r-a-c-/e̅‾\-o-m-p-i-l-e
  GUID: 27fba042-5bc0-44d7-b3a9-4af5bf9d42f2
  pubDate: Fri, 06 May 2022 12:00:05 +0000
  duration: 00:37:48
  file: tlbhit4.mp3 (90,687,488 bytes)

Episode 5: parsers
  GUID: dbdfca99-ba05-4735-b8a4-6cb63faf3b8c
  pubDate: Thu, 23 Feb 2023 11:24:00 +0000
  duration: 00:41:40
  file: tlbhit5.mp3 (40,055,167 bytes)

Episode 6: ƑẍɄʑʑ҉⟆Ƒu𝔷𝔷⧫ᶳΩ𝓕𝕦𝘇𝘇֍⧩
  GUID: 964fa473-82c2-4c59-bd04-fd8aaf3fd0cd
  pubDate: Sun, 15 Dec 2024 01:10:00 +0000
  duration: 00:28:11
  file: tlbhit6.mp3 (54,275,117 bytes)
```

---

## Phase 1: Prepare Build Environment

### Step 1.1: Remove old venv, create new one

The `tlbhit/` directory is confirmed to be an old Python venv (has `pyvenv.cfg`, `bin/activate`).

```bash
cd /Users/jfb/s/TLBhit

# Remove old venv
rm -rf tlbhit/

# Create fresh venv with standard naming
python3 -m venv .venv
source .venv/bin/activate
pip install 'mistune>=3.0.0' pyyaml mutagen
pip freeze > requirements.txt
```

**Verification:**
```bash
source .venv/bin/activate
python -c "import mistune, yaml, mutagen; print('All imports OK')"
```
- [ ] Expected: "All imports OK"

### Step 1.2: Update .gitignore

```bash
echo ".venv/" >> .gitignore
```

**Verification:**
```bash
grep ".venv" .gitignore
```
- [ ] Expected: `.venv/` appears in output

---

## Phase 2: Add Episode Metadata to Markdown Files

### Step 2.1: Create and run slurp script

Create `scripts/slurp_libsyn.py`:

```python
#!/usr/bin/env python3
"""
One-time script to inject YAML frontmatter into episode markdown files.
Run once, then delete this script.
"""

import os
from pathlib import Path

EPISODES = [
    {
        "episode": 0,
        "md_file": "000_mov_fp_sp.md",
        "title": "mov fp, sp",
        "guid": "c685f738-397d-4b7b-9dc6-171eaf2b07de",
        "pubDate": "Mon, 02 Nov 2020 01:21:16 +0000",
        "duration": "01:04:28",
        "audio": "tlbhit0.mp3",
        "description": "The stack, and how it relates to TLB Hits.",
        "explicit": False,
    },
    {
        "episode": 1,
        "md_file": "001_deref_char_star_0_eq_0.md",
        "title": "*(char*)0 = 0",
        "guid": "d5f882cd-bac2-4ede-a51a-daab8e61e51d",
        "pubDate": "Mon, 23 Nov 2020 06:09:40 +0000",
        "duration": "00:43:52",
        "audio": "tlbhit1.mp3",
        "description": "The adventure of storing NUL to NULL!",
        "explicit": False,
    },
    {
        "episode": 2,
        "md_file": "002_https_tlbh_dot_it_CR.md",
        "title": "https://tlbh.it^M",
        "guid": "407713de-1c3f-4eac-940a-a28269788270",
        "pubDate": "Sun, 21 Feb 2021 22:32:54 +0000",
        "duration": "00:56:35",
        "audio": "tlbhit2.mp3",
        "description": "What happens when you type https://tlbh.it in your browser and press enter?",
        "explicit": False,
    },
    {
        "episode": 3,
        "md_file": "003_builtin_expect_bang_bang_x_0.md",
        "title": "__builtin_expect(!!(x), 0)",
        "guid": "a99864d9-d302-40d2-b257-b6258d26ffdf",
        "pubDate": "Mon, 19 Apr 2021 03:05:47 +0000",
        "duration": "00:39:10",
        "audio": "tlbhit3.mp3",
        "description": "Static vs runtime knowledge, compiler hints, C++20 annotations.",
        "explicit": False,
    },
    {
        "episode": 4,
        "md_file": "004_trace_compilers.md",
        "title": "t-r-a-c-/e̅‾\\-o-m-p-i-l-e",
        "guid": "27fba042-5bc0-44d7-b3a9-4af5bf9d42f2",
        "pubDate": "Fri, 06 May 2022 12:00:05 +0000",
        "duration": "00:37:48",
        "audio": "tlbhit4.mp3",
        "description": "Monitor. Compile. Bail. Repeat!",
        "explicit": False,
    },
    {
        "episode": 5,
        "md_file": "005_parsers.md",
        "title": "parsers",
        "guid": "dbdfca99-ba05-4735-b8a4-6cb63faf3b8c",
        "pubDate": "Thu, 23 Feb 2023 11:24:00 +0000",
        "duration": "00:41:40",
        "audio": "tlbhit5.mp3",
        "description": "Parsers?",
        "explicit": False,
    },
    {
        "episode": 6,
        "md_file": "006_fuzz.md",
        "title": "ƑẍɄʑʑ҉⟆Ƒu𝔷𝔷⧫ᶳΩ𝓕𝕦𝘇𝘇֍⧩",
        "guid": "964fa473-82c2-4c59-bd04-fd8aaf3fd0cd",
        "pubDate": "Sun, 15 Dec 2024 01:10:00 +0000",
        "duration": "00:28:11",
        "audio": "tlbhit6.mp3",
        "description": "Code coverage and fuzzing exploration, including MC/DC testing and AFL.",
        "explicit": False,
    },
]

def generate_frontmatter(ep):
    """Generate YAML frontmatter block."""
    explicit_str = "true" if ep["explicit"] else "false"
    return f'''---
episode: {ep["episode"]}
title: "{ep["title"]}"
guid: "{ep["guid"]}"
pubDate: "{ep["pubDate"]}"
duration: "{ep["duration"]}"
audio: "{ep["audio"]}"
description: "{ep["description"]}"
explicit: {explicit_str}
---
'''

def main():
    notes_dir = Path("episode_notes")

    for ep in EPISODES:
        md_path = notes_dir / ep["md_file"]
        if not md_path.exists():
            print(f"WARNING: {md_path} not found, skipping")
            continue

        content = md_path.read_text(encoding="utf-8")

        # Skip if already has frontmatter
        if content.startswith("---"):
            print(f"SKIP: {ep['md_file']} already has frontmatter")
            continue

        # Add frontmatter
        new_content = generate_frontmatter(ep) + content
        md_path.write_text(new_content, encoding="utf-8")
        print(f"OK: {ep['md_file']} - added frontmatter")

if __name__ == "__main__":
    main()
```

Run it:
```bash
mkdir -p scripts
# (create the file above)
python scripts/slurp_libsyn.py
```

**Verification:**
```bash
head -15 episode_notes/000_mov_fp_sp.md
```
- [ ] Expected: YAML frontmatter block with `guid: "c685f738-397d-4b7b-9dc6-171eaf2b07de"`

### Step 2.2: Cleanup

```bash
rm scripts/slurp_libsyn.py
rm -f episode_notes/006_fuzz.md~  # backup file
rmdir scripts 2>/dev/null || true  # remove if empty
```

---

## Phase 3: Normalize MP3 Metadata

### Step 3.1: Create and run normalize script

Create `scripts/normalize_mp3s.py`:

```python
#!/usr/bin/env python3
"""
One-time script to normalize MP3 ID3 tags.
Run once, then delete this script.
"""

from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, APIC

EPISODES = [
    {"episode": 0, "audio": "tlbhit0.mp3", "title": "Episode 0: mov fp, sp", "year": "2020"},
    {"episode": 1, "audio": "tlbhit1.mp3", "title": "Episode 1: *(char*)0 = 0", "year": "2020"},
    {"episode": 2, "audio": "tlbhit2.mp3", "title": "Episode 2: https://tlbh.it^M", "year": "2021"},
    {"episode": 3, "audio": "tlbhit3.mp3", "title": "Episode 3: __builtin_expect(!!(x), 0)", "year": "2021"},
    {"episode": 4, "audio": "tlbhit4.mp3", "title": "Episode 4: t-r-a-c-/e̅‾\\-o-m-p-i-l-e", "year": "2022"},
    {"episode": 5, "audio": "tlbhit5.mp3", "title": "Episode 5: parsers", "year": "2023"},
    {"episode": 6, "audio": "tlbhit6.mp3", "title": "Episode 6: ƑẍɄʑʑ҉⟆Ƒu𝔷𝔷⧫ᶳΩ𝓕𝕦𝘇𝘇֍⧩", "year": "2024"},
]

ARTIST = "JF Bastien & Chris Leary"
ALBUM = "TLB Hit"
GENRE = "Podcast"
COVER_PATH = Path("logo/tlbhit-logo.png")

def main():
    episodes_dir = Path("episodes")

    # Load cover art once
    cover_data = COVER_PATH.read_bytes() if COVER_PATH.exists() else None

    for ep in EPISODES:
        mp3_path = episodes_dir / ep["audio"]
        if not mp3_path.exists():
            print(f"WARNING: {mp3_path} not found, skipping")
            continue

        try:
            audio = MP3(mp3_path, ID3=ID3)
        except Exception:
            audio = MP3(mp3_path)
            audio.add_tags()

        tags = audio.tags

        # Clear existing tags and set new ones
        tags.delall("TIT2")  # Title
        tags.delall("TPE1")  # Artist
        tags.delall("TALB")  # Album
        tags.delall("TDRC")  # Year
        tags.delall("TRCK")  # Track
        tags.delall("TCON")  # Genre

        tags.add(TIT2(encoding=3, text=ep["title"]))
        tags.add(TPE1(encoding=3, text=ARTIST))
        tags.add(TALB(encoding=3, text=ALBUM))
        tags.add(TDRC(encoding=3, text=ep["year"]))
        tags.add(TRCK(encoding=3, text=str(ep["episode"] + 1)))  # 1-indexed
        tags.add(TCON(encoding=3, text=GENRE))

        # Add cover art if available
        if cover_data:
            tags.delall("APIC")
            tags.add(APIC(
                encoding=3,
                mime="image/png",
                type=3,  # Front cover
                desc="Cover",
                data=cover_data,
            ))

        audio.save()
        print(f"OK: {ep['audio']} - normalized tags")

if __name__ == "__main__":
    main()
```

Run it:
```bash
mkdir -p scripts
# (create the file above)
python scripts/normalize_mp3s.py
```

**Verification:**
```bash
exiftool -Title -Artist -Album -Year episodes/tlbhit0.mp3
exiftool -Title -Artist -Album -Year episodes/tlbhit6.mp3
```
- [ ] Expected: Both show Artist="JF Bastien & Chris Leary", Album="TLB Hit"

### Step 3.2: Cleanup

```bash
rm scripts/normalize_mp3s.py
rmdir scripts 2>/dev/null || true
```

---

## Phase 4: Rewrite Build System

### Step 4.1: Create new render.py

Replace `render.py` with this complete implementation:

```python
#!/usr/bin/env python3
"""
TLB Hit build script.
Generates HTML episode pages and podcast RSS feed.

Usage:
    source .venv/bin/activate
    python render.py
"""

import os
import re
from pathlib import Path
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

import yaml
import mistune

# === Namespaces ===
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
ATOM_NS = "http://www.w3.org/2005/Atom"

# === Channel Configuration ===
CHANNEL = {
    "title": "TLB Hit 💥",
    "link": "https://tlbh.it/",
    "description": "A podcast about systems & compilers by @jfbastien and @cdleary. The only podcast you listen to at 0.5×.",
    "language": "en",
    "author": "JF Bastien & Chris Leary",
    "copyright": "Chris Leary & JF Bastien",
    "image": "https://tlbh.it/logo/tlbhit-logo.png",
    "categories": ["Technology"],
    "explicit": "false",  # Must be "true" or "false" per Apple docs
    "feed_url": "https://tlbh.it/feed.xml",
    "audio_base_url": "https://tlbh.it/episodes",
}

EPISODE_NOTES_DIR = Path("episode_notes")
EPISODES_DIR = Path("episodes")


def parse_frontmatter(content):
    """Extract YAML frontmatter and markdown body from content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            body = parts[2]
            return fm, body
    return {}, content


def load_all_episodes():
    """Load all episode metadata from markdown frontmatter."""
    episodes = []

    for md_file in EPISODE_NOTES_DIR.glob("*.md"):
        if md_file.name.endswith("~"):  # Skip backup files
            continue

        content = md_file.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)

        if not fm.get("guid"):
            print(f"WARNING: {md_file.name} has no GUID in frontmatter, skipping RSS")
            continue

        fm["md_file"] = md_file.name
        fm["md_body"] = body
        fm["slug"] = md_file.stem
        episodes.append(fm)

    # Sort by episode number (stable, correct ordering)
    episodes.sort(key=lambda e: e.get("episode", 0))
    return episodes


def generate_html(episodes):
    """Generate HTML episode pages."""
    with open("episode_header.tmpl") as f:
        header_template = f.read()
    with open("episode_footer.tmpl") as f:
        footer_template = f.read()

    for ep in episodes:
        md_file = ep["md_file"]
        slug = ep["slug"]
        body = ep["md_body"]

        # Extract audio tag (don't escape it)
        audio_line = None
        lines = body.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("<audio "):
                audio_line = line
            else:
                new_lines.append(line)
        body_without_audio = "\n".join(new_lines)

        # Get title from first line or frontmatter
        title_line = ""
        if new_lines and new_lines[0].startswith("# "):
            title_line = new_lines[0]
            body_without_audio = "\n".join(new_lines[1:])

        # Render markdown
        title_html = mistune.html(title_line) if title_line else ""
        body_html = mistune.html(body_without_audio)

        # Prepare header with episode title
        display_title = ep.get("title", slug)
        this_header = header_template.replace("{episode_title}", f"Episode {ep.get('episode', '?')}: {display_title}")

        # Write HTML file
        html_path = Path(f"{slug}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<!-- DO NOT EDIT -- episode notes autogenerated by TLBHit's render.py -->\n")
            f.write(this_header)
            f.write(title_html)
            if audio_line:
                f.write(audio_line + "\n")
            f.write(body_html)
            f.write(footer_template)

        print(f"Generated {html_path}")


def generate_rss(episodes):
    """Generate podcast RSS feed."""

    # Register namespaces ONLY (do NOT set xmlns attrs manually)
    # This prevents duplicate namespace declarations in output
    ET.register_namespace("itunes", ITUNES_NS)
    ET.register_namespace("content", CONTENT_NS)
    ET.register_namespace("atom", ATOM_NS)

    # Root element - just version, namespaces added automatically
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    # === Channel metadata ===
    ET.SubElement(channel, "title").text = CHANNEL["title"]
    ET.SubElement(channel, "link").text = CHANNEL["link"]
    ET.SubElement(channel, "description").text = CHANNEL["description"]
    ET.SubElement(channel, "language").text = CHANNEL["language"]
    ET.SubElement(channel, "copyright").text = CHANNEL["copyright"]

    # Atom self-link (ensures xmlns:atom appears)
    ET.SubElement(channel, f"{{{ATOM_NS}}}link", {
        "href": CHANNEL["feed_url"],
        "rel": "self",
        "type": "application/rss+xml",
    })

    # iTunes channel tags
    ET.SubElement(channel, f"{{{ITUNES_NS}}}author").text = CHANNEL["author"]
    ET.SubElement(channel, f"{{{ITUNES_NS}}}explicit").text = CHANNEL["explicit"]
    ET.SubElement(channel, f"{{{ITUNES_NS}}}type").text = "episodic"
    ET.SubElement(channel, f"{{{ITUNES_NS}}}image", {"href": CHANNEL["image"]})

    # Categories
    for cat in CHANNEL["categories"]:
        ET.SubElement(channel, f"{{{ITUNES_NS}}}category", {"text": cat})

    # NEW FEED URL TAG - for migration (safe to leave forever)
    ET.SubElement(channel, f"{{{ITUNES_NS}}}new-feed-url").text = CHANNEL["feed_url"]

    # Channel dates (from episodes, sorted by episode number)
    if episodes:
        ET.SubElement(channel, "pubDate").text = episodes[0]["pubDate"]
        ET.SubElement(channel, "lastBuildDate").text = episodes[-1]["pubDate"]

    # === Episode items (newest first for display) ===
    for ep in reversed(episodes):
        item = ET.SubElement(channel, "item")

        # Title
        full_title = f"Episode {ep['episode']}: {ep['title']}"
        ET.SubElement(item, "title").text = full_title

        # Link to episode page
        ET.SubElement(item, "link").text = f"https://tlbh.it/{ep['slug']}.html"

        # GUID - CRITICAL: exact value from Libsyn, isPermaLink="false"
        guid_elem = ET.SubElement(item, "guid", {"isPermaLink": "false"})
        guid_elem.text = ep["guid"]

        # Dates
        ET.SubElement(item, "pubDate").text = ep["pubDate"]

        # Description (both RSS and content:encoded)
        desc = ep.get("description", "")
        ET.SubElement(item, "description").text = desc
        ET.SubElement(item, f"{{{CONTENT_NS}}}encoded").text = desc

        # Enclosure - CRITICAL: length must be exact bytes
        audio_filename = ep["audio"]
        audio_path = EPISODES_DIR / audio_filename
        if audio_path.exists():
            length_bytes = audio_path.stat().st_size
        else:
            print(f"WARNING: {audio_path} not found, using 0 for length")
            length_bytes = 0

        ET.SubElement(item, "enclosure", {
            "url": f"{CHANNEL['audio_base_url']}/{audio_filename}",
            "length": str(length_bytes),
            "type": "audio/mpeg",
        })

        # iTunes item tags
        ET.SubElement(item, f"{{{ITUNES_NS}}}duration").text = ep.get("duration", "00:00:00")

        # Episode number - CRITICAL: must be positive integer (1-indexed)
        itunes_ep_num = ep.get("episode", 0) + 1
        ET.SubElement(item, f"{{{ITUNES_NS}}}episode").text = str(itunes_ep_num)

        # Explicit - CRITICAL: must be "true" or "false" (not yes/no)
        explicit_val = ep.get("explicit", False)
        explicit_str = "true" if explicit_val else "false"
        ET.SubElement(item, f"{{{ITUNES_NS}}}explicit").text = explicit_str

        ET.SubElement(item, f"{{{ITUNES_NS}}}episodeType").text = "full"

    # Write with XML declaration
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write("feed.xml", encoding="UTF-8", xml_declaration=True)
    print("Generated feed.xml")


def main():
    print("Loading episodes...")
    episodes = load_all_episodes()
    print(f"Found {len(episodes)} episodes")

    print("\nGenerating HTML...")
    generate_html(episodes)

    print("\nGenerating RSS feed...")
    generate_rss(episodes)

    print("\nDone!")


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
source .venv/bin/activate
python render.py
```
- [ ] Expected: "Generated feed.xml" and HTML files for each episode

```bash
# Validate XML is well-formed
xmllint --noout feed.xml && echo "XML is well-formed"
```
- [ ] Expected: "XML is well-formed"

```bash
# Check no duplicate xmlns declarations
grep -o 'xmlns:itunes' feed.xml | wc -l
```
- [ ] Expected: 1 (exactly one occurrence)

```bash
# Check GUIDs are present with isPermaLink
grep -E 'guid isPermaLink="false"' feed.xml | head -3
```
- [ ] Expected: GUIDs with isPermaLink="false"

```bash
# Check explicit is "false" not "no"
grep 'itunes:explicit' feed.xml | head -3
```
- [ ] Expected: `<itunes:explicit>false</itunes:explicit>`

```bash
# Check episode numbers are 1-7
grep 'itunes:episode' feed.xml
```
- [ ] Expected: Numbers 1 through 7 (not 0 through 6)

---

## Phase 5: Update Site Links

### Step 5.1: Update RSS links in templates

Edit `episode_header.tmpl`:
```bash
sed -i '' 's|https://tlbhit.libsyn.com/rss|https://tlbh.it/feed.xml|g' episode_header.tmpl
```

Edit `index.html`:
```bash
sed -i '' 's|https://tlbhit.libsyn.com/rss|https://tlbh.it/feed.xml|g' index.html
```

**Verification:**
```bash
grep "feed.xml" episode_header.tmpl index.html
```
- [ ] Expected: Both files show `https://tlbh.it/feed.xml`

### Step 5.2: Update audio URLs in markdown files

For each episode markdown, change audio src from Libsyn to self-hosted:

```bash
for f in episode_notes/*.md; do
  sed -i '' 's|https://traffic.libsyn.com/secure/tlbhit/|https://tlbh.it/episodes/|g' "$f"
done
```

**Verification:**
```bash
grep -l "traffic.libsyn.com" episode_notes/*.md
```
- [ ] Expected: No output (no files contain old URL)

```bash
grep "tlbh.it/episodes" episode_notes/000_mov_fp_sp.md
```
- [ ] Expected: Audio tag with `https://tlbh.it/episodes/tlbhit0.mp3`

### Step 5.3: Regenerate all HTML

```bash
python render.py
```
- [ ] Expected: All HTML files regenerated

---

## Phase 6: Deploy and Verify

### Step 6.1: Commit and push

```bash
git add -A
git status  # Review changes
git commit -m "Self-host podcast: generate RSS feed, normalize MP3 metadata

- Add YAML frontmatter to episode markdown files
- Generate feed.xml with proper iTunes namespace
- Preserve GUIDs from Libsyn exactly (isPermaLink=false)
- Normalize MP3 ID3 tags for consistency
- Update RSS links to self-hosted feed
- Use itunes:explicit=false (not yes/no per Apple docs)
- Episode numbers 1-7 in RSS (positive integers required)"

git push
```

### Step 6.2: Wait for GitHub Pages deployment

Wait ~1-2 minutes for deployment.

### Step 6.3: Verify feed accessibility

```bash
curl -s -I https://tlbh.it/feed.xml | head -5
```
- [ ] Expected: `HTTP/2 200` and content type XML

```bash
curl -s https://tlbh.it/feed.xml | head -20
```
- [ ] Expected: Valid RSS with itunes namespace

### Step 6.4: Verify audio accessibility with byte-range support

```bash
curl -s -I https://tlbh.it/episodes/tlbhit0.mp3 | grep -E "(HTTP|Content-Type|Accept-Ranges|Content-Length)"
```
- [ ] Expected: HTTP 200, Content-Type: audio/mpeg, Accept-Ranges: bytes

```bash
# Test actual byte-range request (Apple requires this)
curl -s -I -H "Range: bytes=0-1" https://tlbh.it/episodes/tlbhit0.mp3 | head -3
```
- [ ] Expected: `HTTP/2 206` (Partial Content)

### Step 6.5: Validate with external tools

Use these validators (paste `https://tlbh.it/feed.xml`):
- [Podbase Validator](https://podba.se/validate/)
- [Cast Feed Validator](https://castfeedvalidator.com/)

Check for:
- [ ] No GUID errors
- [ ] No episode number errors (1-7 valid)
- [ ] No explicit tag errors
- [ ] Valid enclosure lengths
- [ ] All required iTunes tags present

---

## Phase 7: Configure Libsyn 301 Redirect

**IMPORTANT**: Only do this AFTER Phase 6 verification passes!

### Step 7.1: Log into Libsyn

Go to [libsyn.com](https://libsyn.com) and log in.

### Step 7.2: Navigate to Redirects

**Settings** → **Redirects** (or **Advanced** → **Redirects**)

### Step 7.3: Configure redirect

- **Feed Redirect URL**: `https://tlbh.it/feed.xml`
- **Use New Feed URL Tag**: Yes (if available)

Save changes.

### Step 7.4: Verify redirect is working

```bash
curl -s -I -L https://tlbhit.libsyn.com/rss 2>/dev/null | grep -E "(HTTP|Location)"
```
- [ ] Expected: `HTTP/1.1 301 Moved Permanently` and `Location: https://tlbh.it/feed.xml`

**CRITICAL**: Must be 301, not 302. If it shows 302, check Libsyn settings.

---

## Phase 8: Update Podcast Directories

### Step 8.1: Apple Podcasts Connect

1. Go to [podcastsconnect.apple.com](https://podcastsconnect.apple.com)
2. Find TLB Hit show
3. **Do NOT submit as new show** (would create duplicate)
4. Use "Update RSS Feed URL" if available
5. Otherwise, the 301 redirect will handle it automatically

### Step 8.2: Spotify for Podcasters (if applicable)

1. Go to [podcasters.spotify.com](https://podcasters.spotify.com)
2. Find TLB Hit show
3. Update RSS feed URL to `https://tlbh.it/feed.xml`

---

## Phase 9: Monitor (4+ Weeks)

- [ ] Keep Libsyn 301 redirect active for minimum 4 weeks
- [ ] Keep `<itunes:new-feed-url>` tag in feed.xml (safe to leave forever)
- [ ] Monitor Apple Podcasts Connect analytics weekly
- [ ] Check that episode plays continue normally
- [ ] Verify subscriber count is stable

After 4+ weeks with no issues:
- [ ] Can cancel Libsyn subscription (redirect persists after cancellation per Libsyn docs)
- [ ] Optionally remove `<itunes:new-feed-url>` tag (but no harm leaving it)

---

## Phase 10: Future Cloudflare Migration

**CRITICAL**: 6 of 7 MP3s exceed Cloudflare Pages' 25 MiB limit. R2 is REQUIRED.

| File | Size | Over 25 MiB? |
|------|------|--------------|
| tlbhit0.mp3 | 47.6 MB | YES |
| tlbhit1.mp3 | 19.7 MB | No |
| tlbhit2.mp3 | 41.6 MB | YES |
| tlbhit3.mp3 | 28.3 MB | YES |
| tlbhit4.mp3 | 86.5 MB | YES |
| tlbhit5.mp3 | 38.2 MB | YES |
| tlbhit6.mp3 | 51.8 MB | YES |

### Architecture for Cloudflare

```
Cloudflare Pages (tlbh.it)
├── index.html, *.html
├── feed.xml
├── logo/, fonts/

Cloudflare R2 (media.tlbh.it or similar)
└── episodes/tlbhit*.mp3
```

### When ready to migrate:

1. Create Cloudflare R2 bucket for audio files
2. Upload all MP3s to R2
3. Update `CHANNEL["audio_base_url"]` in render.py to R2 URL
4. Regenerate feed.xml
5. Set up Cloudflare Pages for HTML/feed
6. Point DNS to Cloudflare
7. GUIDs stay the same - no subscriber impact

---

## Rollback Plan

If something goes wrong after enabling Libsyn redirect:

1. Log into Libsyn
2. Remove/clear the Feed Redirect URL setting
3. Libsyn will resume serving the original feed
4. Investigate and fix issues
5. Re-enable redirect when ready

---

## Self-Evaluation: Risk Analysis

### What Could Go Wrong and How We Prevent It

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GUIDs accidentally changed | Low | **CRITICAL** - duplicates episodes | Hardcoded in slurp script from Libsyn data; verification step checks |
| Invalid XML (duplicate xmlns) | Low | Feed rejected | Use `ET.register_namespace()` only; verification counts xmlns occurrences |
| Episode numbers 0-6 instead of 1-7 | Medium | Validation failure | Explicit `+ 1` in code; verification step checks output |
| Explicit tag "yes/no" instead of "true/false" | Medium | Apple rejection | Hardcoded "true"/"false" strings; verification step checks |
| Libsyn returns 302 instead of 301 | Medium | Subscribers may not follow | Explicit curl check; manual verification in Libsyn UI |
| MP3 files not accessible | Low | Episodes won't play | Byte-range curl test before enabling redirect |
| Audio URLs not updated in markdown | Low | Still points to Libsyn | Verification grep checks for old URLs |

### Why This Plan Will Succeed

1. **Every step has verification**: No phase completes without confirming the expected outcome
2. **Rollback is simple**: Just remove Libsyn redirect setting to restore original behavior
3. **GUIDs are hardcoded**: Zero risk of them being regenerated or changed
4. **Apple requirements validated**: All three critical corrections from ChatGPT review are incorporated
5. **Namespace handling tested**: Python test proved Method 2 (register only) produces clean XML
6. **Phased approach**: Feed is fully tested BEFORE enabling Libsyn redirect

### Key Success Criteria

After Phase 6 (before enabling redirect):
- [ ] `feed.xml` passes external validators (Podbase, Cast Feed Validator)
- [ ] All 7 GUIDs match Libsyn exactly
- [ ] `itunes:episode` values are 1-7
- [ ] `itunes:explicit` values are "true" or "false"
- [ ] Byte-range requests return HTTP 206
- [ ] Single xmlns declaration per namespace

After Phase 7 (redirect enabled):
- [ ] `curl -I https://tlbhit.libsyn.com/rss` returns `301 Moved Permanently`
- [ ] Location header points to `https://tlbh.it/feed.xml`

After Phase 9 (4+ weeks):
- [ ] Subscriber counts stable in Apple/Spotify analytics
- [ ] No duplicate episode reports from users
- [ ] Safe to cancel Libsyn

---

## Final Checklist Before Starting

- [ ] Read through entire plan
- [ ] Understand each verification step
- [ ] Have all login credentials ready
- [ ] Have terminal ready with repo directory
- [ ] Commit any uncommitted changes first
- [ ] Ready to proceed with Phase 1
