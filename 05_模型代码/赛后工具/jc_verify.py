# -*- coding: utf-8 -*-
"""② 双源核验：竞彩官方文件赛果查询/比对（赛果录入时核对权威值）
用法：
  python jc_verify.py list <日期 YYYY-MM-DD>          # 列出该日竞彩全部赛果
  python jc_verify.py find <关键词>                    # 按队名/编号搜索（如 "玛丽港" 或 "周五001"）
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

JC = r"D:\Cola\足球分析学习\04_赛果数据\竞彩赛果_20260715-0815.txt"
pat = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|\s*(\S+)\s*\|\s*(.+?)\s+vs\s+(.+?)\s*\|\s*(\d+):(\d+)\s*\|\s*(\d+):(\d+)")

def load():
    rows = []
    with open(JC, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("日期"):
                continue
            m = pat.match(line)
            if not m:
                continue
            date, lg, no, home, away, h1, h2, f1, f2 = m.groups()
            rows.append({"date": date, "lg": lg, "no": no, "home": home.strip(), "away": away.strip(),
                         "ht": f"{h1}:{h2}", "ft": f"{f1}:{f2}"})
    return rows

def main():
    args = sys.argv[1:]
    if not args:
        print("用法：jc_verify.py list <日期> | jc_verify.py find <关键词>")
        return
    rows = load()
    cmd = args[0]
    if cmd == "list" and len(args) > 1:
        d = args[1]
        hit = [r for r in rows if r["date"] == d]
        print(f"== 竞彩 {d} 共 {len(hit)} 场 ==")
        for r in hit:
            print(f"  {r['no']} | {r['lg']} | {r['home']} vs {r['away']} | 半场 {r['ht']} | 全场 {r['ft']}")
    elif cmd == "find" and len(args) > 1:
        kw = args[1]
        hit = [r for r in rows if kw in r["home"] or kw in r["away"] or kw in r["no"] or kw in r["lg"]]
        print(f"== 搜索「{kw}」{len(hit)} 场 ==")
        for r in hit:
            print(f"  {r['date']} {r['no']} | {r['lg']} | {r['home']} vs {r['away']} | 半场 {r['ht']} | 全场 {r['ft']}")
    else:
        print("用法：jc_verify.py list <日期> | jc_verify.py find <关键词>")

if __name__ == "__main__":
    main()
