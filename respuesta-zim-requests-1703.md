Thanks @Popolechien — both issues are real, and rather than ask you to live with them I rebuilt the ZIM from source. The new file is at the same URL, same name:

https://pub-9ebe02965a9f4aeb9c5d3d9741790d2d.r2.dev/vedabase_en_all_2026-10.zim

- 61,575,844 bytes
- sha256 `472fc06581d35152b0661bcf50ad6d28d1a3b10806b472f939d7a71deed8eee6`
- `Date` 2026-10-16, `Scraper` "vedabase-zim 2.0"

**The incomplete section title** (`b0`, "Observing the Armies on the"): the old builder capped every entry title at 80 characters, cutting 447 of them mid-word. Titles are now written in full — `bg/1` reads "Chapter 1: Observing the Armies on the Battlefield of Kurukṣetra", `sb/2/7` reads "SB 2.7: Scheduled Incarnations with Specific Functions". The longest title in the file is 277 characters and none is truncated.

**The Table of Contents** (`b20c0`, Light of the Bhāgavata): that book was a single 120 KB page with its contents as plain text and only two links in it. It is now a linked index plus one page per chapter — 49 chapters under `lob/`. Lectures and letters are likewise indexed by year instead of being titled with their first sentence.

The reason I couldn't just patch it: the file you have on staging was a copy of a March build whose generator I had lost. The new one is generated from the live site's own database export by `build_zim_d1.py` in the repo (https://github.com/juanmanuelferrera/vedabase-zim).

@benoit74 — this also fixes the metadata point properly rather than by redirect: `Source` in the new file is `https://vedabase.cc`, where the old one still said `vedabase.vedicvault.org`.

Two things worth knowing before you re-fetch:

1. The archive grew from 8,817 to 31,332 articles (40 MB → 62 MB). The old build was missing most of the spoken material: there are now 6,582 letters and 3,705 lectures and conversations, each on its own page.
2. It is a full rebuild, so internal paths changed (`b0c1` is now `bg/1/1`). Any deep link into the staging copy will need to be re-resolved.

Three short books the old file contained are not in this one (Teachings of Lord Kapila, Teachings of Prahlāda Mahārāja, Second Chance): they are not yet in the site's database, and I would rather the ZIM be exactly what vedabase.cc serves. They will come back when they are added there.

What I verified: 30,959 content pages against 30,959 database rows (counted two ways), 0 broken internal links, no duplicate entry titles, title and full-text indexes present, search for "Kurukṣetra armies" returns `bg/1` first, suggestions for "Observing the" return `bg/1`. Checks were run against the file as served from the download URL, not only my local copy.

What I have not run: `zimcheck` — I don't have zim-tools on this machine at the moment. If you would rather have a clean `zimcheck -A` before publishing, say so and I will install it and post the output.

Happy to rebuild again if anything else turns up.
