"""Build sitemap.xml from every published page that is not noindex.
Run after adding or changing pages:  python _tools/make_sitemap.py
RU page /x/ pairs with EN page /en/x/ (hreflang). lastmod = last git commit of the file.
"""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://funkylauncher.com"


def pages():
    out = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_")) and d != "assets"]
        for f in files:
            if not f.endswith(".html") or f.startswith("_"):
                continue
            full = os.path.join(dirpath, f)
            text = open(full, encoding="utf-8").read()
            if "noindex" in text or 'http-equiv="refresh"' in text:
                continue
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            url = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            out.append((url, rel))
    return sorted(out, key=lambda p: (p[0].startswith("/en/"), p[0]))


def lastmod(rel):
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def pair(url, urls):
    if url.startswith("/en/"):
        ru, en = url[3:], url
    else:
        ru, en = url, "/en" + url
    return (ru if ru in urls else None), (en if en in urls else None)


if __name__ == "__main__":
    items = pages()
    urls = {u for u, _ in items}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url, rel in items:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE}{url}</loc>")
        lm = lastmod(rel)
        if lm:
            lines.append(f"    <lastmod>{lm}</lastmod>")
        ru, en = pair(url, urls)
        if ru and en:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="ru" href="{SITE}{ru}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>')
            lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en}"/>')
        lines.append("  </url>")
    lines.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("sitemap:", len(items), "pages")
    for u, _ in items:
        print(" ", u)
