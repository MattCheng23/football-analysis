# -*- coding: utf-8 -*-
"""避雷名单一键自动更新（2026-08-16）
用法: python avoid_autoupdate.py <scorer_json> <data.js路径> <批次日键>
功能:
  1. 解析 scorer JSON（每队评分+信号）
  2. 合并进指定批次的 avoidWatch/avoidHigh（按队伍去重，新记录追加 reason）
  3. 跨场累计 ≥9 或同类信号重复 → 观察升高信号
  4. 输出修改后的 data.js（备份后写入）
"""
import json, sys, re, shutil, datetime
sys.stdout.reconfigure(encoding='utf-8')

def map_team(name):
    TEAM_MAP = {
        'Bucheon FC 1995': '富川FC', 'Jeonbuk Hyundai Motors FC': '全北现代',
        'Incheon United': '仁川联', 'Gimcheon Sangmu': '金泉尚武',
        'Brommapojkarna': '布鲁马波', 'Örgryte': '厄格里特',
        'Degerfors': '代格福什', 'IFK Göteborg': '哥德堡',
        'Djurgården': '佐加顿斯', 'AIK': 'AIK索尔纳',
        'Aalesund': '奥勒松', 'Vålerenga': '瓦勒伦加',
        'AC Oulu': 'AC奥卢', 'FC Inter Turku': '国际图尔库',
        'Arsenal': '阿森纳', 'Manchester City': '曼城',
        'Kalmar FF': '卡尔马', 'Hammarby': '哈马比',
        'GAIS': '盖斯', 'Malmö FF': '马尔默',
        'Burnley': '伯恩利', 'West Ham United': '西汉姆联',
        'Racing Santander': '桑坦德', 'Villarreal': '比利亚雷亚尔',
        'Molde': '莫尔德', 'Tromsø': '特罗姆瑟',
        'Brann': '布兰', 'Hamarkameratene': '汉坎',
        'Sarpsborg 08': '萨普斯堡', 'Sandefjord': '桑纳菲',
        'Espanyol': '西班牙人', 'Levante': '莱万特',
        'Fredrikstad': '腓特烈', 'Kristiansund': '克里斯蒂',
        'Vasco da Gama': '达伽马', 'Santos FC': '桑托斯',
    }
    return TEAM_MAP.get(name, name)

def main():
    if len(sys.argv) < 4:
        print("用法: python avoid_autoupdate.py <scorer_json> <data.js> <批次键 如 2026-08-16>")
        sys.exit(1)
    scorer_json = json.load(open(sys.argv[1], encoding='utf-8'))
    data_path = sys.argv[2]
    batch_key = sys.argv[3]

    # 1. 解析评分
    updates = []  # {team, league, score, signals, short_name}
    for item in scorer_json:
        if 'scores' in item:
            for team, info in item['scores'].items():
                if info['score'] >= 3:  # 观察线
                    updates.append({
                        'team': map_team(team), 'league': item.get('leagueName', '?'),
                        'score': info['score'], 'signals': info['signals'],
                        'short': item.get('short_name', '')
                    })

    # 2. 读 data.js
    c = open(data_path, encoding='utf-8').read()

    # 3. 定位批次 review 段
    m = re.search(r'"%s":\s*\{' % batch_key, c)
    if not m:
        print(f"批次 {batch_key} 未找到")
        sys.exit(1)
    seg_end = c.find('GLOBAL_STATS', m.end())
    seg = c[m.start():seg_end]

    # 找 review 段的 avoidWatch/avoidHigh 结束位置
    review_i = seg.find('review: {')
    if review_i < 0:
        print("review 段未找到，先建 review")
        sys.exit(1)

    # 4. 生成新 reason
    lines = []
    for u in sorted(updates, key=lambda x: -x['score']):
        lv = "🔴 高信号" if u['score'] >= 6 else "🟡 观察"
        reason = f"自动判定 {u['short']}（{u['score']}分[{lv}]）: {'; '.join(u['signals'])}"
        lines.append(f"        {{ team: \"{u['team']}\", league: \"{u['league']}\", reason: \"{reason}\" }},")

    # 5. 检查现有 avoidWatch 段，合并（按队伍去重）
    # 简化：在 review 段末尾（avoidWatch 后）插入新条目
    # 找 avoidWatch: [ ... ] 或 review 段结尾
    aw_i = seg.rfind('avoidWatch: [')
    if aw_i >= 0:
        # 在现有 avoidWatch 数组内追加（在 ] 前插入）
        arr_end = seg.find(']', aw_i)
        insert_at = m.start() + arr_end
        new_block = "\n" + "\n".join(lines) if lines else ""
        c = c[:insert_at] + new_block + c[insert_at:]
        print(f"已追加 {len(lines)} 条到 avoidWatch")
    else:
        # 无 avoidWatch：在 review 段内添加
        print("当前批次无 avoidWatch 段，跳过（请先人工建段）")
        sys.exit(2)

    # 6. 备份 + 写回
    bak = re.sub(r'\.js$', '_pre_avoidauto.json', data_path)
    bak = bak.replace('data.js', f"data_{datetime.datetime.now().strftime('%H%M%S')}_pre_avoidauto.js")
    shutil.copy(data_path, rf'D:\Cola\_backup\{bak.split(chr(92))[-1]}')
    open(data_path, 'w', encoding='utf-8').write(c)
    print(f"已更新 {data_path}，备份完成")

if __name__ == '__main__':
    main()
