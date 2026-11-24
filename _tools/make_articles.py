"""Build help articles (RU + EN pairs) from the Copywriter's file.
Run:  python _tools/make_articles.py [path-to-md]   then  python _tools/make_sitemap.py
Texts: Моддинг\\Контент\\Статьи для сайта.md

File format (one block per article, articles separated by a line "---"):

    # ru-slug | en-slug
    ## RU
    Заголовок: Как установить моды на Cyberpunk 2077
    Описание: одна-две фразы для поиска (до ~160 знаков)
    <text: paragraphs, "- " lists, "**Подзаголовок**" on its own line = h2,
     "?? Вопрос" line + next paragraph = question/answer (FAQ markup)>
    ## EN
    Title: How to install Cyberpunk 2077 mods
    Description: ...
    <text>

An article with only "## RU" is published only in Russian (no EN pair).
Blocks marked "[ЧЕРНОВИК]" in the heading line are skipped.
[ДОПОЛНИТЬ ...] / [УТОЧНИТЬ ...] notes are dropped, as in make_modlists.py.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_modlists import CSS, LISTS, ROOT, SITE, clean, inline, write  # noqa: E402

SRC = os.path.expanduser(r"~\OneDrive\Рабочий стол\CLAUDE\Моддинг\Контент\Статьи для сайта.md")

UI = {
    "ru": {"home": "/", "prefix": "/", "back": "← funkylauncher.com", "btn": "Скачать Funky Launcher",
           "btn_href": "/download/", "free": "Лаунчер бесплатный, сборку выбираешь в его библиотеке.",
           "lists": "Сборки", "title_key": "Заголовок", "desc_key": "Описание", "sub": "Funky Launcher — помощь",
           "fine": "Funky Launcher — независимый неофициальный проект. Он не связан с издателями и разработчиками игр, "
                   "с Nexus Mods и Wabbajack и не одобрен ими. Названия игр и товарные знаки принадлежат их владельцам."},
    "en": {"home": "/en/", "prefix": "/en/", "back": "← funkylauncher.com", "btn": "Download Funky Launcher",
           "btn_href": "/en/download/", "free": "The launcher is free; pick the modlist in its library.",
           "lists": "Modlists", "title_key": "Title", "desc_key": "Description", "sub": "Funky Launcher — help",
           "fine": "Funky Launcher is an independent, unofficial project. It is not affiliated with or endorsed by any "
                   "game publisher or developer, or by Nexus Mods or Wabbajack. All game names and trademarks belong "
                   "to their respective owners."},
}


def parse(md: str):
    arts = []
    for block in re.split(r"^---\s*$", md, flags=re.M):
        m = re.search(r"^# ([^\n|]+?)(?:\s*\|\s*([^\n]+?))?\s*$", block, re.M)
        if not m or "ЧЕРНОВИК" in m.group(0):
            continue
        ru_slug = m.group(1).strip().strip("/")
        en_slug = (m.group(2) or "").strip().strip("/") or None
        art = {"slug": {"ru": ru_slug, "en": en_slug}}
        for lang, tag in (("ru", "RU"), ("en", "EN")):
            sec = re.search(rf"^## {tag}\s*$(.*?)(?=^## (?:RU|EN)\s*$|\Z)", block, re.M | re.S)
            if not sec:
                continue
            body = sec.group(1)
            t = re.search(rf"^{UI[lang]['title_key']}:\s*(.+)$", body, re.M)
            d = re.search(rf"^{UI[lang]['desc_key']}:\s*(.+)$", body, re.M)
            if not t or not d:
                sys.exit(f"{ru_slug} {tag}: no title/description line")
            text = re.sub(rf"^(?:{UI[lang]['title_key']}|{UI[lang]['desc_key']}):.*$", "", body, flags=re.M)
            art[lang] = {"title": clean(t.group(1)), "desc": clean(d.group(1)), "text": text}
        if "ru" in art:
            arts.append(art)
    return arts


def render(text: str):
    out, faq, ul, q = [], [], False, None
    for raw in text.splitlines():
        line = clean(raw)
        if not line or line.startswith("<!--"):  # notes for the Copywriter, never published
            continue
        if line.startswith("- "):
            if not ul:
                out.append("  <ul>")
                ul = True
            out.append(f"    <li>{inline(line[2:])}</li>")
            continue
        if ul:
            out.append("  </ul>")
            ul = False
        if line.startswith("??"):
            q = line[2:].strip()
            out.append(f"  <h3>{html.escape(q)}</h3>")
        elif re.fullmatch(r"\*\*[^*]+\*\*", line):
            out.append(f"  <h2>{html.escape(line[2:-2])}</h2>")
        else:
            out.append(f"  <p>{inline(line)}</p>")
            if q:
                faq.append((q, re.sub(r"\*\*", "", line)))
                q = None
    if ul:
        out.append("  </ul>")
    return "\n".join(out), faq


TM = {  # slug word -> (RU, EN) trademark line
    "cyberpunk": ("Cyberpunk 2077 — товарный знак CD PROJEKT S.A.", "Cyberpunk 2077 is a trademark of CD PROJEKT S.A."),
    "starfield": ("Starfield — товарный знак Bethesda Softworks LLC.", "Starfield is a trademark of Bethesda Softworks LLC."),
    "fallout": ("Fallout — товарный знак Bethesda Softworks LLC.", "Fallout is a trademark of Bethesda Softworks LLC."),
}


def tm(lang, art) -> str:
    lines = [v[0 if lang == "ru" else 1] for k, v in TM.items() if k in art["slug"]["ru"]]
    return html.escape(" " + " ".join(lines)) if lines else ""


def page(lang, art):
    u, e = UI[lang], html.escape
    a = art[lang]
    slug = art["slug"][lang]
    url = f"{SITE}{u['prefix']}{slug}/"
    body, faq = render(a["text"])
    has_pair = art["slug"]["en"] and "en" in art
    alt = ""
    if has_pair:
        ru_url, en_url = f"{SITE}/{art['slug']['ru']}/", f"{SITE}/en/{art['slug']['en']}/"
        alt = (f'<link rel="alternate" hreflang="ru" href="{ru_url}">\n'
               f'<link rel="alternate" hreflang="en" href="{en_url}">\n'
               f'<link rel="alternate" hreflang="x-default" href="{en_url}">\n')
    switch = ""
    if has_pair:
        other = f"/en/{art['slug']['en']}/" if lang == "ru" else f"/{art['slug']['ru']}/"
        switch = (f'<span style="margin-left:auto"><a href="{other}" lang="{"en" if lang == "ru" else "ru"}">'
                  f'{"EN" if lang == "ru" else "RU"}</a></span>')
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
           "inLanguage": lang, "url": url, "mainEntityOfPage": url, "image": f"{SITE}/assets/og.jpg",
           "author": {"@type": "Organization", "name": "FunkyPlay", "url": SITE + "/"},
           "publisher": {"@type": "Organization", "name": "FunkyPlay", "url": SITE + "/",
                         "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/icon.png"}}}]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage",
                   "mainEntity": [{"@type": "Question", "name": q,
                                   "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq]})
    lists = " ".join(f'<a href="{u["prefix"]}{s}/">{n}</a>' for s, _, n, _, _ in LISTS)
    cta = (f'  <div class="cta"><a class="btn" href="{u["btn_href"]}">{e(u["btn"])}</a>\n'
           f'  <p class="free">{e(u["free"])}</p></div>')
    scripts = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False)}\n</script>'
                        for x in ld)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a['title'])} | Funky Launcher</title>
<meta name="description" content="{e(a['desc'])}">
<link rel="canonical" href="{url}">
{alt}<meta property="og:type" content="article">
<meta property="og:title" content="{e(a['title'])}">
<meta property="og:description" content="{e(a['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:locale" content="{'ru_RU' if lang == 'ru' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{scripts}
<style>
{CSS}
h1 {{ font-size: clamp(1.7rem, 1.2rem + 2.4vw, 2.6rem); line-height: 1.1; }}
h3 {{ font-size: 1.05rem; margin: 1.3rem 0 .3rem; }}
</style>
</head>
<body>
<main>
  <header><a href="{u['home']}"><img src="/assets/icon.png" alt="Funky Launcher"></a><a href="{u['home']}">{e(u['back'])}</a>
  {switch}</header>
  <p class="sub">{e(u['sub'])}</p>
  <h1><span>{e(a['title'])}</span></h1>
{body}
{cta}
  <h2>{e(u['lists'])}</h2>
  <p class="others">{lists}</p>
  <p class="small">{e(u['fine'])}{tm(lang, art)}</p>
</main>
<script src="/assets/support-chat.js" defer></script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "0bbf324ca83440c693bdeb9b1338dcdc"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    for art in parse(open(src, encoding="utf-8").read()):
        write(f"{art['slug']['ru']}/index.html", page("ru", art))
        if art["slug"]["en"] and "en" in art:
            write(f"en/{art['slug']['en']}/index.html", page("en", art))
