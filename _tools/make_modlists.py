"""Build modlist pages from the Copywriter's file:
    /neon-nights/  /nova-nights/  /atomic-nights/   (RU)
    /en/neon-nights/ ...                            (EN)
    /starfield/ and /en/starfield/ -> redirect to Nova Nights
Run:  python _tools/make_modlists.py [path-to-md]
Texts: Моддинг\\Контент\\Описания сборок — короткое и полное.md
(sections "# N. NAME (Game)", "## Короткое описание", "## Полное описание — RU", "## Full description — EN").
[ДОПОЛНИТЬ ...] / [УТОЧНИТЬ ...] notes are dropped automatically.
_tools/ is not published (GitHub Pages skips folders starting with "_").
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.expanduser(r"~\OneDrive\Рабочий стол\CLAUDE\Моддинг\Контент\Описания сборок — короткое и полное.md")
SITE = "https://funkylauncher.com"

LISTS = [  # slug, md heading name, game (RU, EN), big image
    ("neon-nights", "NEON NIGHTS", "Neon Nights", ("Cyberpunk 2077", "Cyberpunk 2077"), "ml-neon.jpg"),
    ("nova-nights", "NOVA NIGHTS", "Nova Nights", ("Starfield", "Starfield"), "ml-nova.jpg"),
    ("atomic-nights", "ATOMIC NIGHTS", "Atomic Nights", ("Fallout 4", "Fallout 4"), "ml-atomic.jpg"),
]

UI = {
    "ru": {"badge": "Доступно в Funky Launcher", "sub": "сборка модов для {g}", "btn": "Скачать Funky Launcher",
           "btn_href": "/download/", "free": "Лаунчер бесплатный. Сборку выбираешь в библиотеке лаунчера.",
           "other": "Другие сборки", "back": "← funkylauncher.com", "home": "/", "prefix": "/",
           "title": "{n} — сборка модов для {g} | Funky Launcher"},
    "en": {"badge": "Available in Funky Launcher", "sub": "a modlist for {g}", "btn": "Download Funky Launcher",
           "btn_href": "/en/download/", "free": "The launcher is free. Pick the modlist in the launcher's library.",
           "other": "Other modlists", "back": "← funkylauncher.com", "home": "/en/", "prefix": "/en/",
           "title": "{n} — a modlist for {g} | Funky Launcher"},
}

NOTE = re.compile(r"\s*\[(?:ДОПОЛНИТЬ|УТОЧНИТЬ)[^\]]*\]")
URL = re.compile(r"(https?://[^\s<)]+)")


def clean(s: str) -> str:
    return NOTE.sub("", s).strip()


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return URL.sub(lambda m: f'<a href="{m.group(1)}" rel="noopener">{m.group(1)}</a>', s)


def parse(md: str) -> dict:
    out = {}
    for _, head, *_ in LISTS:
        m = re.search(rf"^# \d+\. {head}.*?$(.*?)(?=^# \d+\. |^## Что решает|\Z)", md, re.M | re.S)
        if not m:
            sys.exit(f"section {head} not found")
        body = m.group(1)
        short = re.search(r"^\*\*RU:\*\*([^\n]+)$.*?^\*\*EN:\*\*([^\n]+)$", body, re.M | re.S)
        ru = re.search(r"^## Полное описание — RU\s*$(.*?)(?=^## )", body, re.M | re.S)
        en = re.search(r"^## Full description — EN\s*$(.*?)(?=^---|\Z)", body, re.M | re.S)
        out[head] = {"ru": (clean(short.group(1)), ru.group(1)), "en": (clean(short.group(2)), en.group(1))}
    return out


def render(body: str) -> str:
    html_out, ul = [], False
    for raw in body.splitlines():
        line = clean(raw)
        if not line:
            continue
        if line.startswith("- "):
            if not ul:
                html_out.append("  <ul>")
                ul = True
            html_out.append(f"    <li>{inline(line[2:])}</li>")
            continue
        if ul:
            html_out.append("  </ul>")
            ul = False
        if re.fullmatch(r"\*\*[^*]+\*\*", line):
            html_out.append(f"  <h2>{html.escape(line[2:-2])}</h2>")
        else:
            html_out.append(f"  <p>{inline(line)}</p>")
    if ul:
        html_out.append("  </ul>")
    return "\n".join(html_out)


CSS = """:root { --bg: #07070d; --card: #11111c; --line: #24243a; --text: #fff; --muted: #b3b3c6; --pink: #ff3fd2; --cyan: #7ae8ff; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { min-height: 100vh; color: var(--text); font: 1.02rem/1.6 "Segoe UI", system-ui, sans-serif; padding: 1.5rem 16px 3rem;
  background:
    radial-gradient(60vw 50vh at 100% 0%, rgba(255,63,210,.18), transparent 70%),
    radial-gradient(50vw 50vh at 0% 100%, rgba(122,232,255,.13), transparent 70%),
    var(--bg); background-attachment: fixed; }
main { max-width: 52rem; margin: 0 auto; }
header { display: flex; align-items: center; gap: .7rem; margin-bottom: 2rem; }
header img { width: 34px; height: 34px; }
a { color: var(--cyan); text-underline-offset: 3px; overflow-wrap: anywhere; }
.badge { display: inline-block; padding: .25rem .7rem; border: 1px solid var(--cyan); border-radius: 999px; color: var(--cyan);
  font-weight: 700; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 1rem; }
h1 { font: 700 clamp(2.2rem, 1.4rem + 4vw, 3.6rem)/1 "Bahnschrift", "Arial Narrow", sans-serif; font-stretch: 75%;
  text-transform: uppercase; transform: skewX(-9deg); margin-bottom: .5rem; }
h1 span { background: linear-gradient(90deg, var(--pink), var(--cyan)); -webkit-background-clip: text; background-clip: text; color: transparent; padding-right: .06em; }
.sub { color: var(--muted); font-size: 1.1rem; margin-bottom: 1.2rem; }
h2 { font-size: 1.25rem; margin: 1.8rem 0 .6rem; }
.pic { width: 100%; height: auto; border-radius: 16px; border: 1px solid var(--line); margin: 1.2rem 0 .5rem; }
p, li { color: var(--muted); max-width: 72ch; margin: .5rem 0; }
p b, li b { color: var(--text); }
ul { margin-left: 1.3rem; }
.cta { margin: 1.4rem 0; }
.btn { display: inline-block; margin: .3rem 0 .6rem; padding: 1rem 1.8rem; border-radius: 12px; background: var(--pink); color: #14000f;
  font-weight: 800; text-decoration: none; box-shadow: 0 10px 40px -10px rgba(255,63,210,.8); }
.btn:focus-visible, a:focus-visible { outline: 3px solid var(--cyan); outline-offset: 3px; }
.free { font-size: .92rem; margin-top: 0; }
.others { display: flex; flex-wrap: wrap; gap: .6rem 1.2rem; margin-top: .4rem; }
.small { font-size: .8rem; opacity: .8; margin-top: 2.5rem; }"""


def page(lang, slug, name, game, img, short, body) -> str:
    u, e = UI[lang], html.escape
    url = f"{SITE}{u['prefix']}{slug}/"
    others = " ".join(f'<a href="{u["prefix"]}{s}/">{n}</a>' for s, _, n, _, _ in LISTS if s != slug)
    content = render(body)
    # the last paragraph is the disclaimer: show it small
    content = re.sub(r"  <p>([^\n]*?(?:неофициальная|unofficial)[^\n]*)</p>\s*$", r'  <p class="small">\1</p>', content)
    cta = (f'  <div class="cta"><a class="btn" href="{u["btn_href"]}">{e(u["btn"])}</a>\n'
           f'  <p class="free">{e(u["free"])}</p></div>')
    content = content.replace("  <h2>", cta + "\n  <h2>", 1) if "<h2>" in content else content + "\n" + cta
    title = u["title"].format(n=name, g=game)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(short)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ru" href="{SITE}/{slug}/">
<link rel="alternate" hreflang="en" href="{SITE}/en/{slug}/">
<link rel="alternate" hreflang="x-default" href="{SITE}/en/{slug}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(short)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/{img}">
<meta property="og:locale" content="{'ru_RU' if lang == 'ru' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<style>
{CSS}
</style>
</head>
<body>
<main>
  <header><a href="{u['home']}"><img src="/assets/icon.png" alt="Funky Launcher"></a><a href="{u['home']}">{e(u['back'])}</a>
  <span style="margin-left:auto"><a href="{'/en/' if lang == 'ru' else '/'}{slug}/" lang="{'en' if lang == 'ru' else 'ru'}">{'EN' if lang == 'ru' else 'RU'}</a></span></header>
  <div class="badge">{e(u['badge'])}</div>
  <h1><span>{e(name)}</span></h1>
  <p class="sub">{e(u['sub'].format(g=game))}</p>
  <img class="pic" src="/assets/{img}" alt="{e(name)} — {e(game)}" width="1600" height="900">
{content}
  <h2>{e(u['other'])}</h2>
  <p class="others">{others}</p>
</main>
<script src="/assets/support-chat.js" defer></script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "0bbf324ca83440c693bdeb9b1338dcdc"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def redirect(to: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Nova Nights</title>
<link rel="canonical" href="{SITE}{to}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={to}"></head>
<body><p><a href="{to}">Nova Nights</a></p></body></html>
"""


def write(rel: str, text: str):
    out = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("written", rel)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    data = parse(open(src, encoding="utf-8").read())
    for slug, head, name, games, img in LISTS:
        for i, lang in enumerate(("ru", "en")):
            short, body = data[head][lang]
            rel = f"{slug}/index.html" if lang == "ru" else f"en/{slug}/index.html"
            write(rel, page(lang, slug, name, games[i], img, short, body))
    write("starfield/index.html", redirect("/nova-nights/"))
    write("en/starfield/index.html", redirect("/en/nova-nights/"))
