#!/usr/bin/env python3
"""
Build vedabase.zim from vedabase.md

Requires: python-libzim (pip install libzim)

The source file (vedabase.md) is a large markdown file with books separated
by ============ lines. Each book contains chapters and verses.

This script:
1. Parses vedabase.md into individual articles (one per book section)
2. Converts markdown formatting (*italics*) to HTML <em> tags
3. Builds a ZIM file with proper metadata for Kiwix compatibility
"""

import re
import sys
import html
from datetime import date
from pathlib import Path

from libzim.writer import Creator, Item, StringProvider, FileProvider, Hint, Compression


# -- Configuration --
SOURCE_FILE = Path(__file__).parent / "vedabase.md"
OUTPUT_FILE = Path(__file__).parent / "vedabase.zim"

METADATA = {
    "Title": "Vedabase",
    "Description": "Complete works of A.C. Bhaktivedanta Swami Prabhupada",
    "Language": "eng",
    "Creator": "A.C. Bhaktivedanta Swami Prabhupada",
    "Publisher": "The Bhaktivedanta Book Trust",
    "Date": date.today().isoformat(),
    "Name": "vedabase",
}

CSS = """
body { font-family: Georgia, serif; max-width: 50em; margin: 2em auto; padding: 0 1em;
       line-height: 1.7; color: #333; background: #fefefe; }
h1 { color: #8B0000; border-bottom: 2px solid #8B0000; padding-bottom: 0.3em; }
h2 { color: #5C3317; margin-top: 1.5em; }
h3 { color: #6B4226; }
p { text-align: justify; }
a { color: #8B0000; }
.toc { column-count: 2; }
.toc a { display: block; padding: 0.15em 0; }
em { font-style: italic; }
"""


class ZimItem(Item):
    """A single article/page in the ZIM file."""

    def __init__(self, path, title, content, mimetype="text/html", is_front=True):
        super().__init__()
        self._path = path
        self._title = title
        self._content = content
        self._mimetype = mimetype
        self._is_front = is_front

    def get_path(self):
        return self._path

    def get_title(self):
        return self._title

    def get_mimetype(self):
        return self._mimetype

    def get_contentprovider(self):
        return StringProvider(self._content)

    def get_hints(self):
        return {Hint.FRONT_ARTICLE: self._is_front}


def italics_to_em(text):
    """Convert markdown *text* to <em>text</em>, avoiding tag attributes."""
    parts = re.split(r'(<[^>]+>)', text)
    result = []
    for part in parts:
        if part.startswith('<'):
            result.append(part)
        else:
            part = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', part)
            result.append(part)
    return ''.join(result)


def slugify(text):
    """Create a URL-safe slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')[:80]


def md_to_html(text, title):
    """Convert a markdown section to a styled HTML page."""
    escaped = html.escape(text)
    # Restore markdown formatting after escaping
    lines = escaped.split('\n')
    html_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append('')
            continue

        # Convert *italic* to <em>
        stripped = italics_to_em(stripped)

        if not in_paragraph:
            html_lines.append('<p>')
            in_paragraph = True

        html_lines.append(stripped)

    if in_paragraph:
        html_lines.append('</p>')

    body = '\n'.join(html_lines)

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head><body>
<h1>{html.escape(title)}</h1>
{body}
</body></html>"""


def parse_books(source_path):
    """Parse vedabase.md into book sections separated by ====... lines."""
    text = source_path.read_text(encoding='utf-8')
    # Split on the separator pattern
    separator = re.compile(r'\n={10,}\n(.+?)\n={10,}\n', re.DOTALL)

    books = []
    parts = separator.split(text)

    # First part is header/intro before any book
    if parts[0].strip():
        books.append(("Introduction", parts[0].strip()))

    # Remaining parts alternate: book_title, book_content
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if title and content:
            books.append((title, content))

    return books


def build_main_page(books):
    """Build the main index page with links to all books."""
    links = []
    for title, _ in books:
        slug = slugify(title)
        links.append(f'<a href="{slug}">{html.escape(title)}</a>')

    toc = '\n'.join(links)
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Vedabase</title>
<style>{CSS}</style>
</head><body>
<h1>Vedabase</h1>
<p>Complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda</p>
<h2>Contents</h2>
<div class="toc">
{toc}
</div>
</body></html>"""


def main():
    if not SOURCE_FILE.exists():
        print(f"Error: {SOURCE_FILE} not found")
        print(f"Copy vedabase.md to {SOURCE_FILE} before building.")
        sys.exit(1)

    print("Parsing vedabase.md...")
    books = parse_books(SOURCE_FILE)
    print(f"Found {len(books)} sections")

    # Remove old output if exists
    OUTPUT_FILE.unlink(missing_ok=True)

    print("Building ZIM file...")
    with Creator(str(OUTPUT_FILE)).config_compression(Compression.zstd) as creator:
        # Add metadata
        for key, value in METADATA.items():
            creator.add_metadata(key, value)

        # Add CSS
        creator.add_item(ZimItem("style.css", "Stylesheet", CSS,
                                 mimetype="text/css", is_front=False))

        # Add main page
        main_html = build_main_page(books)
        creator.add_item(ZimItem("mainPage", "Vedabase", main_html))
        creator.set_mainpath("mainPage")

        # Add each book as an article
        for title, content in books:
            slug = slugify(title)
            article_html = md_to_html(content, title)
            creator.add_item(ZimItem(slug, title, article_html))
            print(f"  Added: {title} ({slug})")

    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\nDone! Created {OUTPUT_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
