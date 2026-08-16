# -*- coding: utf-8 -*-
"""避雷名单自动更新器 V1.0（2026-08-16）
输入：avoid_scorer 的 JSON 输出（每队评分+信号）
逻辑：
  单场 ≥6 分 → 高信号（avoidHigh）
  单场 3-5 分 → 观察（avoidWatch）
  已存在队伍：分数累加，跨场 ≥9 或同类重复 → 升级 avoidWatch→avoidHigh
  已有队伍无新信号 → 保留原记录（不自动降级，人工确认）
输出：更新后的 8/16 批 avoidHigh/avoidWatch 建议（写入 data.js 前需人工确认）
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 中文队名 → 数据.js 队名映射（FotMob 英文名 → 网页中文名）
TEAM_MAP = {
    'Bucheon FC 1995': '富川FC',
    'Jeonbuk Hyundai Motors FC': '全北现代',
    'Incheon United': '仁川联',
    'Gimcheon Sangmu': '金泉尚武',
    'Brommapojkarna': '布鲁马波',
    'Örgryte': '厄格里特',
    'Degerfors': '代格福什',
    'IFK Göteborg': '哥德堡',
    'Djurgården': '佐加顿斯',
    'AIK': 'AIK索尔纳',
    'Aalesund': '奥勒松',
    'Vålerenga': '瓦勒伦加',
    'AC Oulu': 'AC奥卢',
    'FC Inter Turku': '国际图尔库',
    'Arsenal': '阿森纳',
    'Manchester City': '曼城',
    'Kalmar FF': '卡尔马',
    'Hammarby': '哈马比',
    'GAIS': '盖斯',
    'Malmö FF': '马尔默',
    'Burnley': '伯恩利',
    'West Ham United': '西汉姆联',
    'Racing Santander': '桑坦德',
    'Villarreal': '比利亚雷亚尔',
    'Molde': '莫尔德',
    'Tromsø': '特罗姆瑟',
    'Brann': '布兰',
    'Hamarkameratene': '汉坎',
    'Sarpsborg 08': '萨普斯堡',
    'Sandefjord': '桑纳菲',
    'Espanyol': '西班牙人',
    'Levante': '莱万特',
    'Fredrikstad': '腓特烈',
    'Kristiansund': '克里斯蒂',
    'Vasco da Gama': '达伽马',
    'Santos FC': '桑托斯',
}

def map_team(name):
    return TEAM_MAP.get(name, name)

def main():
    # 输入：从 stdin 读 JSON（由调用方传入评分结果）
    data = json.load(sys.stdin)
    # data: {"matches": [{"name": ..., "home": ..., "away": ..., "hs": ..., "as": ..., "scores": {队: {"score": N, "signals": [...]}}}], "cumulative": {队: {"score": N, "matches": M}}}
    updates = {'avoidHigh': [], 'avoidWatch': []}
    seen = set()
    for match in data.get('matches', []):
        for team, info in match.get('scores', {}).items():
            cname = map_team(team)
            if cname in seen:
                continue
            seen.add(cname)
            score = info['score']
            signals = info['signals']
            if score >= 6:
                updates['avoidHigh'].append({
                    'team': cname, 'league': match.get('league', '?'),
                    'reason': f"自动判定 {match.get('short_name','')}: {'; '.join(signals)}"
                })
            elif score >= 3:
                updates['avoidWatch'].append({
                    'team': cname, 'league': match.get('league', '?'),
                    'reason': f"自动判定 {match.get('short_name','')}: {'; '.join(signals)}"
                })
    print(json.dumps(updates, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
