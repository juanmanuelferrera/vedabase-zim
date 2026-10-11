"""Rebuild the published vedabase.zim with corrected openZIM metadata.
Copies every entry from SRC into DST, adds Illustration/Tags/Scraper/LongDescription,
fixes Name to the openZIM convention and enables full-text indexing."""
import sys, io, datetime
from PIL import Image
from libzim.reader import Archive
from libzim.writer import Creator, Item, StringProvider, Hint, Compression

SRC, DST, ICON = sys.argv[1], sys.argv[2], sys.argv[3]

class CopyItem(Item):
    def __init__(self, path, title, mimetype, content, front):
        super().__init__(); self.p, self.t, self.m, self.c, self.f = path, title, mimetype, content, front
    def get_path(self): return self.p
    def get_title(self): return self.t
    def get_mimetype(self): return self.m
    def get_contentprovider(self): return StringProvider(self.c)
    def get_hints(self): return {Hint.FRONT_ARTICLE: self.f}

src = Archive(SRC)
img = Image.open(ICON).convert("RGBA").resize((48, 48), Image.LANCZOS)
buf = io.BytesIO(); img.save(buf, format="PNG"); icon48 = buf.getvalue()

meta = {
    "Name": "vedabase_en_all",
    "Title": "Vedabase Original Edition",                      # <= 30 chars
    "Description": "Complete works of Srila Prabhupada - Original Edition",  # <= 80 chars
    "LongDescription": ("The complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupada "
        "in their original, pre-1978 unrevised editions: Bhagavad-gita As It Is, Srimad-Bhagavatam, "
        "Sri Caitanya-caritamrta, Krsna Book, Nectar of Devotion and 24 other books, plus lectures, "
        "conversations and letters, with full Sanskrit diacritics. 8,817 chapters and articles. "
        "Source: https://vedabase.vedicvault.org"),
    "Language": "eng",
    "Creator": "A.C. Bhaktivedanta Swami Prabhupada",
    "Publisher": "Vedic Vault",
    "Date": datetime.date.today().isoformat(),
    "Tags": "religion;philosophy;hinduism;vaishnavism;_category:religion;_ftindex:yes;_pictures:no;_videos:no;_details:yes",
    "Scraper": "vedabase-zim 1.1 (python-libzim)",
    "Source": "https://vedabase.vedicvault.org",
}
assert len(meta["Title"]) <= 30 and len(meta["Description"]) <= 80 and len(meta["LongDescription"]) <= 4000

n = 0
with Creator(DST).config_compression(Compression.zstd).config_indexing(True, "eng") as c:
    for k, v in meta.items(): c.add_metadata(k, v)
    c.add_illustration(48, icon48)
    main_path = src.main_entry.get_item().path if src.has_main_entry else None
    for i in range(src.all_entry_count):
        e = src._get_entry_by_id(i)
        if e.is_redirect:
            continue
        it = e.get_item()
        if not it.mimetype.startswith("text/html"):  # source has only HTML content; skips metadata/index pseudo-entries
            continue
        c.add_item(CopyItem(e.path, e.title, it.mimetype, it.content.tobytes(), it.mimetype.startswith("text/html")))
        n += 1
    if main_path: c.set_mainpath(main_path)
print("copied", n, "items ->", DST)
