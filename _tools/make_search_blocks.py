"""Add the Copywriter's search text (Google) to the modlist pages, RU + EN (task 26.11, design: chat Дизайн).
Run:  python _tools/make_search_blocks.py [path-to-md]      (make_modlists.py runs it by itself at the end)
Texts: Моддинг\\Контент\\Тексты для страниц сборок — поиск (26.11).md
  "## 1. /neon-nights/ — RU" + a ``` block:  "## " = h2, "### " = question (h3), other lines = paragraphs.
  Questions after the "Частые вопросы" / "FAQ" heading also go into FAQPage JSON-LD.
Placed after the "Что меняется в игре" section (before the next h2), between <!-- search:start/end --> markers;
running it again replaces the block, it does not duplicate it.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.expanduser(r"~\OneDrive\Рабочий стол\CLAUDE\Моддинг\Контент\Тексты для страниц сборок — поиск (26.11).md")
AFTER = {"ru": "Что меняется в игре", "en": "What changes in the game"}
H3_CSS = "h3 { font-size: 1.05rem; color: var(--text); margin: 1.2rem 0 .3rem; }"


def parse(md):
    out = {}
    for m in re.finditer(r"^## \d+\. /([a-z-]+)/ — (RU|EN)\s*\n```\n(.*?)\n```", md, re.M | re.S):
        out[(m.group(1), m.group(2).lower())] = m.group(3)
    return out


def render(text):
    html_out, faq, in_faq, q = [], [], False, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("### "):
            q = line[4:].strip()
            html_out.append(f"  <h3>{html.escape(q)}</h3>")
        elif line.startswith("## "):
            head = line[3:].strip()
            in_faq = head.lower() in ("частые вопросы", "faq")
            html_out.append(f"  <h2>{html.escape(head)}</h2>")
        else:
            html_out.append(f"  <p>{html.escape(line, quote=False)}</p>")
            if in_faq and q:
                faq.append((q, line))
            q = None
    return "\n".join(html_out), faq


def apply(page_html, text, lang):
    body, faq = render(text)
    page_html = re.sub(r"\n?<!-- search:(?:start|end|ld) -->.*?<!-- /search -->", "", page_html, flags=re.S)
    m = re.search(rf"  <h2>{re.escape(html.escape(AFTER[lang]))}</h2>\n.*?(?=  <h2>)", page_html, re.S)
    if not m:
        raise SystemExit(f"'{AFTER[lang]}' section not found")
    block = f"<!-- search:start -->\n{body}\n<!-- /search -->\n"
    page_html = page_html[:m.end()] + block + page_html[m.end():]
    if faq:
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": lang,
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
        script = (f'<!-- search:ld --><script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False)}\n'
                  f"</script><!-- /search -->\n")
        page_html = page_html.replace("<style>", script + "<style>", 1)
    if H3_CSS not in page_html:
        page_html = page_html.replace("</style>", H3_CSS + "\n</style>", 1)
    return page_html


def run(src=SRC):
    if not os.path.isfile(src):
        print("search texts not found, skipped:", src)
        return
    for (slug, lang), text in parse(open(src, encoding="utf-8").read()).items():
        rel = f"{slug}/index.html" if lang == "ru" else f"en/{slug}/index.html"
        path = os.path.join(ROOT, rel)
        new = apply(open(path, encoding="utf-8").read(), text, lang)
        open(path, "w", encoding="utf-8", newline="\n").write(new)
        print("search block", rel)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else SRC)
