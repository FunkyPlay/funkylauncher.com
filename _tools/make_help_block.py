"""Home page block "Как установить моды" (design: chat Дизайн, 24.11).
Shows only links to articles that are already published (their index.html exists).
Run after make_articles.py:  python _tools/make_help_block.py   (then rebuild en/index.html)
Block lives in index.html between <!-- help:start --> and <!-- help:end -->.
--all  : pretend every article exists (preview of the full block, does not check files)
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# game, modlist, [(ru slug, en slug, ru text, en text)]
GAMES = [
    ("Cyberpunk 2077", "Neon Nights", [
        ("kak-ustanovit-mody-cyberpunk-2077", "how-to-install-cyberpunk-2077-mods", "Как установить моды", "How to install mods"),
        ("cyberpunk-2077-vyletaet-s-modami", "cyberpunk-2077-crashing-with-mods", "Если игра вылетает", "If the game crashes"),
    ]),
    ("Starfield", "Nova Nights", [
        ("kak-ustanovit-mody-starfield", "how-to-install-starfield-mods", "Как установить моды", "How to install mods"),
        ("starfield-vyletaet-s-modami", "starfield-crashing-with-mods", "Если игра вылетает", "If the game crashes"),
    ]),
    ("Fallout 4", "Atomic Nights", [
        ("kak-ustanovit-mody-fallout-4", "how-to-install-fallout-4-mods", "Как установить моды", "How to install mods"),
        ("fallout-4-vyletaet-s-modami", "fallout-4-crashing-with-mods", "Если игра вылетает", "If the game crashes"),
    ]),
]
COMMON = [
    ("kak-udalit-mody", "how-to-remove-mods", "Как убрать моды", "How to remove mods"),
    ("voprosy", "faq", "Вопросы и ответы", "Questions and answers"),
]


def exists(path, all_):
    return all_ or os.path.isfile(os.path.join(ROOT, path, "index.html"))


def links(items, all_):
    ru = [(f"/{r}/", rt) for r, e, rt, et in items if exists(r, all_)]
    en = [(f"/en/{e}/", et) for r, e, rt, et in items if exists(f"en/{e}", all_)]
    return ru, en


def ul(cls, items):
    if not items:
        return ""
    lis = "".join(f'<li><a href="{h}">{html.escape(t)}</a></li>' for h, t in items)
    return f'\n        <ul class="{cls}">{lis}</ul>'


def block(all_=False):
    cards = []
    for game, modlist, items in GAMES:
        ru, en = links(items, all_)
        if not ru and not en:
            continue
        cards.append(f'      <div class="hw rv">\n        <div class="g">{game}</div>\n'
                     f'        <div class="m">{modlist}</div>{ul("ru", ru)}{ul("en", en)}\n      </div>')
    if not cards:
        return ""
    ru, en = links(COMMON, all_)
    common = ""
    if ru:
        common += ('    <p class="hwc ru">Общее: ' + " · ".join(f'<a href="{h}">{html.escape(t)}</a>' for h, t in ru)
                   + "</p>\n")
    if en:
        common += ('    <p class="hwc en">General: ' + " · ".join(f'<a href="{h}">{html.escape(t)}</a>' for h, t in en)
                   + "</p>\n")
    return ('  <section class="wrap" id="help">\n'
            '    <div class="kicker rv"><span class="ru">Помощь</span><span class="en">Help</span></div>\n'
            '    <h2 class="head rv"><span class="ru">Как установить <span class="grad">моды</span></span>'
            '<span class="en">How to install <span class="grad">mods</span></span></h2>\n'
            f'    <div class="hws n{len(cards)}">\n' + "\n".join(cards) + "\n    </div>\n" + common + "  </section>\n")


if __name__ == "__main__":
    all_ = "--all" in sys.argv
    path = os.path.join(ROOT, "index.html")
    src = open(path, encoding="utf-8").read()
    new, n = re.subn(r"<!-- help:start -->\n.*?<!-- help:end -->\n",
                     lambda m: "<!-- help:start -->\n" + block(all_) + "<!-- help:end -->\n", src, flags=re.S)
    if n != 1:
        sys.exit("markers <!-- help:start --> / <!-- help:end --> not found in index.html")
    open(path, "w", encoding="utf-8", newline="\n").write(new)
    print("help block:", "full preview" if all_ else "published articles only")
