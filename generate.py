#!/usr/bin/env python3
"""
neofetch tarzı GitHub profil kartı üretici  —  fatihsugar
--------------------------------------------------------
Çalıştır:   python generate.py
Çıktı:      dark_mode.svg  +  light_mode.svg

- GITHUB_TOKEN ortam değişkeni varsa repo / yıldız / takipçi / commit sayıları
  GitHub API'den canlı çekilir. GitHub Action bunu 6 saatte bir otomatik yapar
  ve SVG'leri "output" branch'ine koyar (main geçmişi temiz kalır).
"""
import datetime as dt
import html
import json
import os
import urllib.request
from pathlib import Path


HERE = Path(__file__).parent
USER = "fatihsugar"

# ───────────────────────── Buradan düzenle ─────────────────────────
# "Uptime" satırı bu tarihten bugüne geçen süreyi (yaşı) gösterir.
BIRTHDAY = "2000-06-19"

HOSTNAME = "fatih@svaceis"

INFO = [
    ("Status", "__STATUS__"),
    ("OS", "Fatih Seker"),
    ("Uptime", "__UPTIME__"),
    ("Host", "Migros, İstanbul, TR"),
    ("Kernel", "System Operations Specialist"),
    ("Shell", "bash, PowerShell"),
    ("IDE", "VS Code, Visual Studio"),
    None,
    ("Languages.Programming", "C, C++, C#, SQL"),
    ("Languages.Real", "Turkish, English"),
    ("Databases", "MSSQL, MySQL"),
    ("Engines", "Unity, Unreal Engine"),
    ("Tools", "Git, Linux, Docker"),
    None,
    ("Project", "Svaceis"),
    ("Motto", "Stay positive :)"),
]

CONTACT = [
    ("Web", "svaceis.com"),
    ("LinkedIn", "in/fatihsugar"),
    ("YouTube", "@fatihsugar"),
]
# ───────────────────────────────────────────────────────────────────

LINE_CHARS = 60           # sağ sütun satır genişliği (karakter)
FONT_SIZE = 15
LINE_H = 20
CHAR_W = FONT_SIZE * 0.6  # monospace karakter genişliği (yaklaşık)
ASCII_COLS = 42

THEMES = {
    "dark": dict(
        bg="#0d1117", bar="#161b22", border="#30363d", text="#c9d1d9",
        key="#ffa657", value="#a5d6ff", dim="#616e7f", accent="#3fb950",
        prompt_user="#3fb950", prompt_path="#58a6ff", add="#3fb950", del_="#f85149",
        ascii="#c9d1d9", g1="#3fb950", g2="#39c5cf", g3="#58a6ff",
    ),
    "light": dict(
        bg="#f6f8fa", bar="#eaeef2", border="#d0d7de", text="#24292f",
        key="#953800", value="#0a3069", dim="#8c959f", accent="#1a7f37",
        prompt_user="#1a7f37", prompt_path="#0969da", add="#1a7f37", del_="#cf222e",
        ascii="#24292f", g1="#1a7f37", g2="#0a7f8a", g3="#0969da",
    ),
}


# ─────────────────────────── GitHub verisi ───────────────────────────
def _get(url, token, data=None):
    req = urllib.request.Request(url, data=data)
    req.add_header("User-Agent", "profile-generator")
    if token:
        req.add_header("Authorization", f"bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    # PROFILE_TOKEN (isteğe bağlı): gizli repoları ve gizli commit'leri de saymak için
    # "repo" okuma izinli kişisel token. Yoksa sadece herkese açık veriler kullanılır.
    pat = os.getenv("PROFILE_TOKEN")
    token = pat or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    stats = dict(full=bool(pat), repos="—", private=None, stars="—", followers="—",
                 commits=None, contribs="—", public_contribs=None, private_contribs=None,
                 created=None)
    try:
        u = _get(f"https://api.github.com/users/{USER}", token)
        stats["followers"] = u["followers"]
        stats["repos"] = u["public_repos"]
        stats["created"] = u["created_at"][:10]
        repos = _get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner", token)
        stats["stars"] = sum(r["stargazers_count"] for r in repos if not r["fork"])
        if token:
            q = {"query": "query($l:String!){user(login:$l){"
                          "repositories(ownerAffiliations:OWNER){totalCount} "
                          "contributionsCollection{totalCommitContributions restrictedContributionsCount "
                          "contributionCalendar{totalContributions}}}}",
                 "variables": {"l": USER}}
            g = _get("https://api.github.com/graphql", token, json.dumps(q).encode())
            user = g["data"]["user"]
            cc = user["contributionsCollection"]
            total = cc["contributionCalendar"]["totalContributions"]
            restricted = cc["restrictedContributionsCount"]
            stats["contribs"] = total
            if restricted and not pat:  # PAT ile gizliler zaten "görünür" sayılır
                stats["private_contribs"] = restricted
                stats["public_contribs"] = total - restricted
            if pat:  # token sahibi = profil sahibi → gizli veriler de görünür
                stats["commits"] = cc["totalCommitContributions"]
                all_repos = user["repositories"]["totalCount"]
                stats["private"] = max(all_repos - stats["repos"], 0)
    except Exception as e:  # internet yoksa kart yine de üretilir
        print("GitHub API okunamadı:", e)
    return stats


def uptime(created):
    start = BIRTHDAY or created
    if not start:
        return "since day one"
    a = dt.date.fromisoformat(start)
    t = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).date()  # İstanbul
    y = t.year - a.year
    m = t.month - a.month
    d = t.day - a.day
    if d < 0:
        m -= 1
        prev = (t.replace(day=1) - dt.timedelta(days=1))
        d += prev.day
    if m < 0:
        y -= 1
        m += 12
    s = lambda n, w: f"{n} {w}{'s' if n != 1 else ''}"
    txt = f"{s(y, 'year')}, {s(m, 'month')}, {s(d, 'day')}"
    return txt if BIRTHDAY else txt + " on GitHub"


# ─────────────────────────── Logo (ASCII) ───────────────────────────
# Svaceis logosu — logo.jpg'den bir kere üretildi, buraya gömüldü.
LOGO = [
    '                            .#+:',
    '                             -#%#+:',
    '                            -+:#@@@.',
    '                            .#@%%%@-',
    '                             -@%%@-',
    '             .-+++===--:::..:%%%@-',
    '         .-+#%@@@@@@@@@@@@@@@@@@=',
    '     :=*#@@@@@#+-:----====++++*=',
    ' .+*%@@@@@#+-',
    ' *@@@%%*=.  .-+*   *#***.',
    ' %%%%@#    %@@@@:  %@@@%  .##+-',
    '-@%%%%+    -@@@%+  #%%%=  *@@@#',
    '-%@@@@@#=   ::..   #%%%. =@%@#  :',
    '  :+#%=:. .:-=+#%. %@@* .%%@#  +@*',
    '     . :*%%@@@@%+  :=*: %@@#  *@@%.',
    '      .%@@@%%+-::-.     -+*..%@%= .-',
    '      =@@%%@#*#%@@%*-.      .++. +%@%-',
    '       -#@@%@@@@%%@@@%-  ----.  :%@%@@*.',
    '         =%@@%%%%%%%%@. +@@@@+    -%%%@%=',
    '           =#%@@@@%%%*  %@@%*:   .=%%@@@#:',
    '             .:=*%@@@- +%*-.   .+%@@@%+:',
    '                  .-=        .+%@@@#=.',
    '                   ..:::--==*@@@@#-',
    '              .*@%%@@%%%%%%%#**+:',
    '            :*@%=...',
    '           .%@=',
    '             *%.',
    '              +=',
]


# ─────────────────────────── SVG ───────────────────────────
def esc(s):
    return html.escape(str(s), quote=False)


def kv_line(key, value, c, value_parts=None):
    """'. Key: ....... value' satırı — noktalar sağa yaslar."""
    val_len = len(value) if value_parts is None else sum(len(t) for t, _ in value_parts)
    dots = LINE_CHARS - (2 + len(key) + 2) - val_len - 1
    dots = "." * max(dots, 2)
    out = (f'<tspan fill="{c["dim"]}">. </tspan><tspan fill="{c["key"]}">{esc(key)}</tspan>'
           f'<tspan fill="{c["text"]}">:</tspan><tspan fill="{c["dim"]}"> {dots} </tspan>')
    if value_parts is None:
        out += f'<tspan fill="{c["value"]}">{esc(value)}</tspan>'
    else:
        out += "".join(f'<tspan fill="{col}">{esc(t)}</tspan>' for t, col in value_parts)
    return out


def section(title, c):
    dashes = "─" * (LINE_CHARS - len(title) - 3 - 4)
    return (f'<tspan fill="{c["text"]}">- {esc(title)} </tspan>'
            f'<tspan fill="{c["dim"]}">{dashes}-—-</tspan>')


def render(theme, stats, art):
    c = THEMES[theme]
    pad = 28
    art_w = ASCII_COLS * CHAR_W
    rx = pad + art_w + 36                  # sağ sütun x
    W = int(rx + LINE_CHARS * CHAR_W + pad)

    right = []
    right.append(f'<tspan fill="{c["accent"]}" font-weight="bold">{esc(HOSTNAME)}</tspan>'
                 f'<tspan fill="{c["dim"]}"> {"─" * (LINE_CHARS - len(HOSTNAME) - 5)}-—-</tspan>')
    for item in INFO:
        if item is None:
            right.append(f'<tspan fill="{c["dim"]}">.</tspan>')
            continue
        k, v = item
        if v == "__STATUS__":
            right.append(kv_line(k, "", c, [("● ", c["accent"]), ("Online · Building", c["value"])]))
        elif v == "__UPTIME__":
            right.append(kv_line(k, uptime(stats["created"]), c))
        else:
            right.append(kv_line(k, v, c))
    right.append("")
    right.append(section("Contact", c))
    for k, v in CONTACT:
        right.append(kv_line(k, v, c))
    right.append("")
    right.append(section("GitHub Stats", c))
    repo_parts = [(f'{stats["repos"]}', c["value"]), (" public", c["dim"])]
    if stats["private"]:
        repo_parts += [(" {", c["dim"]), ("Private", c["key"]),
                       (f': {stats["private"]}', c["value"]), ("}", c["dim"])]
    right.append(kv_line("Repos", "", c, repo_parts))
    right.append(kv_line("Stars", str(stats["stars"]), c))
    right.append(kv_line("Followers", str(stats["followers"]), c))
    if stats["commits"] is not None:
        right.append(kv_line("Commits (last year)", str(stats["commits"]), c))
    contrib_parts = [(f'{stats["contribs"]}', c["add"])]
    if stats["private_contribs"] is not None:
        contrib_parts += [(" (", c["dim"]), (f'{stats["public_contribs"]} public', c["value"]),
                          (", ", c["dim"]), (f'{stats["private_contribs"]} private', c["value"]),
                          (")", c["dim"])]
    right.append(kv_line("Contributions (last year)", "", c, contrib_parts))

    top = 40                                  # başlık çubuğu
    y0 = top + 30                             # ilk komut satırı
    body_y = y0 + LINE_H + 12
    rows = max(len(right), len(art))
    art = [""] * ((rows - len(art)) // 2) + art
    colors_y = body_y + rows * LINE_H + 10
    end_prompt_y = colors_y + 46
    H = end_prompt_y + 26

    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="\'JetBrains Mono\', Consolas, \'DejaVu Sans Mono\', \'Courier New\', monospace" '
             f'font-size="{FONT_SIZE}px">')
    s.append("<style>.blink{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
             ".type{animation:t 1.6s steps(8) forwards;clip-path:inset(0 100% 0 0)}"
             "@keyframes t{to{clip-path:inset(0 0 0 0)}}"
             ".fade{opacity:0;animation:f .6s ease-out 1.7s forwards}@keyframes f{to{opacity:1}}</style>")
    s.append(f'<defs><linearGradient id="lg" x1="0" y1="0" x2="0.35" y2="1">'
             f'<stop offset="0" stop-color="{c["g1"]}"/><stop offset=".55" stop-color="{c["g2"]}"/>'
             f'<stop offset="1" stop-color="{c["g3"]}"/></linearGradient></defs>')
    s.append(f'<rect width="{W}" height="{H}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>')
    # Başlık çubuğu
    s.append(f'<path d="M12 0.5h{W-24}a11.5 11.5 0 0 1 11.5 11.5v{top-12}h-{W-1}v-{top-12}A11.5 11.5 0 0 1 12 0.5z" '
             f'fill="{c["bar"]}"/>')
    s.append(f'<line x1="0" y1="{top}" x2="{W}" y2="{top}" stroke="{c["border"]}"/>')
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        s.append(f'<circle cx="{22 + i * 20}" cy="{top/2}" r="6" fill="{col}"/>')
    s.append(f'<text x="{W/2}" y="{top/2 + 5}" text-anchor="middle" fill="{c["dim"]}" font-size="13px">'
             f'{esc(HOSTNAME)}: ~ — bash — {W}×{H}</text>')
    # Komut satırı
    prompt = (f'<tspan fill="{c["prompt_user"]}" font-weight="bold">{esc(HOSTNAME)}</tspan>'
              f'<tspan fill="{c["text"]}">:</tspan><tspan fill="{c["prompt_path"]}" font-weight="bold">~</tspan>'
              f'<tspan fill="{c["text"]}">$ </tspan>')
    plen = len(HOSTNAME) + 4
    s.append(f'<text x="{pad}" y="{y0}" xml:space="preserve">{prompt}</text>')
    s.append(f'<text class="type" x="{pad + plen * CHAR_W}" y="{y0}" fill="{c["text"]}">neofetch</text>')
    # Gövde
    s.append('<g class="fade">')
    s.append(f'<text x="{pad}" y="{body_y}" fill="url(#lg)" font-weight="bold" xml:space="preserve">')
    for i, line in enumerate(art):
        s.append(f'<tspan x="{pad}" y="{body_y + i * LINE_H}">{esc(line)}</tspan>')
    s.append("</text>")
    s.append(f'<text x="{rx}" y="{body_y}" xml:space="preserve">')
    for i, line in enumerate(right):
        s.append(f'<tspan x="{rx}" y="{body_y + i * LINE_H}">{line}</tspan>')
    s.append("</text>")
    # neofetch renk blokları
    palette = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"]
    for i, col in enumerate(palette):
        s.append(f'<rect x="{rx + i * 30}" y="{colors_y}" width="30" height="18" fill="{col}"/>')
    s.append("</g>")
    # Son komut satırı + yanıp sönen imleç
    s.append(f'<text class="fade" x="{pad}" y="{end_prompt_y}" xml:space="preserve">{prompt}'
             f'<tspan fill="{c["dim"]}">echo "Thanks for visiting!" </tspan></text>')
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).strftime("%d.%m.%Y %H:%M")
    s.append(f'<text class="fade" x="{W - pad}" y="{end_prompt_y}" text-anchor="end" fill="{c["dim"]}" '
             f'font-size="12px">last update: {now} (UTC+3)</text>')
    cx = pad + (plen + len('echo "Thanks for visiting!" ')) * CHAR_W
    s.append(f'<rect class="blink" x="{cx}" y="{end_prompt_y - 14}" width="{CHAR_W:.1f}" height="18" '
             f'fill="{c["accent"]}"/>')
    s.append("</svg>")
    return "\n".join(s)


def main():
    stats = fetch_stats()
    art = list(LOGO)
    for theme in THEMES:
        out = HERE / f"{theme}_mode.svg"
        out.write_text(render(theme, stats, art), encoding="utf-8")
        print("yazıldı:", out.name)


if __name__ == "__main__":
    main()
