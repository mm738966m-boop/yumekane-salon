#!/usr/bin/env python3
"""サロン人数の自動更新
LINEオープンチャット招待ページから公開メンバー数を取得し、
index.html の人数表示・進捗バー・次のマイルストーン・町の絵を更新する。
"""
import re, shutil, sys, urllib.request, pathlib

INVITE = "https://line.me/ti/g2/sn8DRIkFRU2tPxzmUQ0ZHq5kn9RtTGrYlJhFfw"
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
MILESTONES = [100, 300, 500, 1000]

def fetch_count():
    req = urllib.request.Request(INVITE, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r"Members?[^0-9]{0,20}([0-9,]{1,6})", html, re.I)
    if not m:
        m = re.search(r"メンバー[^0-9]{0,20}([0-9,]{1,6})", html)
    return int(m.group(1).replace(",", "")) if m else None

def main():
    n = fetch_count()
    if not n or n < 1:
        print("count unavailable; skip")
        return 0
    s = INDEX.read_text(encoding="utf-8")
    before = s

    s = re.sub(r"いま<b>\d+人</b>", f"いま<b>{n}人</b>", s)
    s = re.sub(r"<b>\d+番目</b>", f"<b>{n+1}番目</b>", s)
    pct = min(100.0, round(n / 10, 1))
    s = re.sub(r'class="goal-fill" style="width:[\d.]+%"',
               f'class="goal-fill" style="width:{pct}%"', s)

    # 次のマイルストーンをハイライト
    s = s.replace(' class="ms is-next"', ' class="ms"')
    nxt = next((m for m in MILESTONES if n < m), None)
    if nxt:
        label = f"{nxt:,}人で" if nxt >= 1000 else f"{nxt}人で"
        s = re.sub(rf'class="ms">({re.escape(label)})',
                   rf'class="ms is-next">\1', s, count=1)

    # 町の絵：到達済みの最大マイルストーン版に切り替え
    tier = max([0] + [m for m in MILESTONES if n >= m])
    src = ROOT / f"hero_v{tier}.jpg"
    if src.exists():
        shutil.copy(src, ROOT / "hero.jpg")

    if s != before:
        INDEX.write_text(s, encoding="utf-8")
        print(f"updated: {n}人 / tier={tier}")
    else:
        print(f"no change: {n}人")
    return 0

if __name__ == "__main__":
    sys.exit(main())
