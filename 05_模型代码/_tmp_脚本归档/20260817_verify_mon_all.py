# -*- coding: utf-8 -*-
"""8月17批 6 场赛果核验：FT 状态/比分/事件/stats/红牌（完赛后用）"""
import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MATCHES = {
    "001 赫尔火花vs坦山猫": "mon_5147626.json",
    "002 赫根vs哈尔姆斯": "mon_5107567.json",
    "003 加的夫vs雷克斯": "mon_5836765.json",
    "004 拉科vs埃尔切": "mon_5868014.json",
    "005 卡萨皮亚vs本菲卡": "mon_5887595.json",
    "006 巴西国际vs里莫": "mon_5103590.json",
}

def show(fn, label):
    d = json.load(open(rf"D:\Cola\_tmp_football\{fn}", encoding='utf-8'))
    print(f"########## {label} ##########")
    mf = d.get('content', {}).get('matchFacts')
    if not mf:
        print("  no matchFacts（未开赛/无数据）")
        return
    evs = (mf.get('events') or {}).get('events') or []
    ht = ft = None
    goals, cards = [], []
    for e in evs:
        t = e.get('type')
        if t == 'Half':
            hs = e.get('halfStrShort')
            if hs == 'HT':
                ht = (e.get('homeScore'), e.get('awayScore'))
            elif hs == 'FT':
                ft = (e.get('homeScore'), e.get('awayScore'))
        elif t in ('Goal', 'OwnGoal'):
            p = e.get('player') or {}
            goals.append(f"{e.get('timeStr')}' {'H' if e.get('isHome') else 'A'} {p.get('name','')} {e.get('homeScore')}:{e.get('awayScore')} {e.get('situation','')}")
        elif t == 'Card':
            p = e.get('player') or {}
            cards.append(f"{e.get('timeStr')}' {'H' if e.get('isHome') else 'A'} {p.get('name','')} {e.get('cardType') or ''}")
    on = (mf.get('events') or {}).get('ongoing')
    hdr = d.get('header', {}).get('status', {})
    print(f"  ongoing={on} HT={ht} FT={ft} reds={hdr.get('numberOfHomeRedCards',0)}:{hdr.get('numberOfAwayRedCards',0)}")
    for g in goals:
        print(f"  进球: {g}")
    for c in cards:
        print(f"  牌: {c}")
    # stats
    for grp in d.get('content', {}).get('stats', {}).get('Periods', {}).get('All', {}).get('stats', []):
        if not isinstance(grp, dict):
            continue
        for s in grp.get('stats', []):
            if isinstance(s, dict) and s.get('title') in ('Ball possession', 'Expected goals (xG)', 'Total shots', 'Shots on target', 'Big chances', 'Corner kicks', 'Yellow cards', 'Red cards'):
                print(f"  {s.get('title')}: {s.get('stats')}")
    print()

for label, fn in MATCHES.items():
    try:
        show(fn, label)
    except Exception as e:
        print(f"########## {label} ERR {e}")
