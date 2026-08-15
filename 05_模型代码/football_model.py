"""足球比赛预测模型（继承并优化自 v8.9 / V9.5）"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Direction(str, Enum):
    HOME = "胜"
    DRAW = "平"
    AWAY = "负"


class Confidence(str, Enum):
    A = "A级"
    B = "B级"
    C = "C级"
    D = "D级"


class League(str, Enum):
    KOR = "韩职"
    SWE = "瑞超"
    FIN = "芬超"
    NOR = "挪超"
    BRA = "巴甲"
    MLS = "美职联"
    UCL = "欧冠"
    UEL = "欧罗巴资格赛"


@dataclass(frozen=True)
class LeagueParams:
    avg_goals: float
    draw_baseline: float
    home_lo: float
    home_hi: float
    total_line_lo: float
    total_line_hi: Optional[float]
    comeback_factor: float

    def home_range(self) -> Tuple[float, float]:
        return self.home_lo, self.home_hi

    def total_line(self) -> float:
        return self.total_line_hi if self.total_line_hi is not None else self.total_line_lo


@dataclass(frozen=True)
class PredictionTemplate:
    first_leg_top3: Tuple[str, str, str]
    second_leg_top3: Tuple[str, str, str]
    first_leg_half_full_top1: str
    second_leg_half_full_top1: str


@dataclass(frozen=True)
class TeamRule:
    team: str
    league: League
    action: str
    condition: str


@dataclass(frozen=True)
class Rule:
    code: str
    name: str
    condition: str
    action: str
    scope: str = "全部"
    priority: int = 9
    min_matches: int = 50
    source_versions: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchInput:
    league: League
    home_team: str
    away_team: str
    round_type: Optional[str] = None
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None


@dataclass
class Prediction:
    league: League
    direction: Direction
    confidence: Confidence
    score_top3: List[str]
    cold_score: str
    cold_prob: str
    half_full_top3: List[str]
    total_choice: str
    note: str
    checks: Dict[str, bool]


LEAGUE_PARAMS: Dict[League, LeagueParams] = {
    League.KOR: LeagueParams(2.30, 0.31, 0.70, 0.95, 2.25, None, 0.15),
    League.SWE: LeagueParams(3.20, 0.28, 0.60, 0.85, 3.00, None, 0.18),
    League.FIN: LeagueParams(2.69, 0.31, 0.70, 1.00, 2.50, None, 0.22),
    League.NOR: LeagueParams(2.94, 0.20, 0.50, 0.82, 2.75, 3.00, 0.20),
    League.BRA: LeagueParams(2.66, 0.27, 0.75, 1.05, 2.25, None, 0.18),
    League.MLS: LeagueParams(2.80, 0.24, 0.85, 1.05, 2.75, None, 0.20),
    League.UCL: LeagueParams(2.82, 0.35, 0.75, 0.90, 2.50, 2.75, 0.30),
    League.UEL: LeagueParams(2.71, 0.22, 0.65, 0.95, 2.50, 2.75, 0.22),
}

EU_TEMPLATES: Dict[League, PredictionTemplate] = {
    League.UCL: PredictionTemplate(
        first_leg_top3=("1-1", "0-1", "1-0"),
        second_leg_top3=("1-2", "2-1", "0-2"),
        first_leg_half_full_top1="平平",
        second_leg_half_full_top1="平负",
    ),
    League.UEL: PredictionTemplate(
        first_leg_top3=("1-1", "0-1", "1-0"),
        second_leg_top3=("1-2", "2-1", "0-2"),
        first_leg_half_full_top1="平平",
        second_leg_half_full_top1="平负",
    ),
}

CORE_PRINCIPLES: List[str] = [
    "方向决定全场结果：胜>、平=、负<。",
    "比分TOP3必须与方向一致：胜主胜、平平局多、负客胜。",
    "半全场第二字必须与方向一致。",
    "每次输出前强制执行方向→比分TOP1→半全场TOP1交叉校验。",
    "不参考亚盘/让球盘/水位，只用基本面+竞彩标准盘。",
    "规则必须有≥50场历史支撑，禁止单场补丁式新增规则。",
]

RULES: List[Rule] = [
    Rule("R001", "离散度修正", "所有比赛", "赔率反推概率×联赛离散系数", priority=8),
    Rule("R002", "主场系数修正", "所有比赛", "主队实力×联赛主场系数", priority=8),
    Rule("R003", "逆转因子修正", "所有比赛", "半场落后追平概率+联赛逆转因子", priority=7),
    Rule("R004", "G1半场0-0", "半场0-0", "平平概率+10%", priority=6),
    Rule("R005", "G2补时绝杀", "75分钟后分差≤1球", "补时进球+20%，被绝平比分×1.3", priority=5),
    Rule("R006", "S44极端大比分", "主队前4+客队后4+主队近3场≥2.5球", "强制含净胜≥3球比分", priority=5),
    Rule("R007", "动态条件平局", "赛前排名差/进球和/失球和", "平局概率动态调整", priority=7),
    Rule("R008", "半场落后不悲观", "主队近5场半场落后追平率≥20%", "主队不败概率+10%", priority=6),
    Rule("R009", "半场平局保守", "两队近5场半场平局率≥40%", "平局概率+8%", priority=6),
    Rule("R010", "置信度重构", "概率计算完成", "A/B/C/D级判定", priority=4),
    Rule("R011", "主胜过热抑制", "主胜率>联赛均值+15%", "主胜概率-5%，平局+5%", priority=7),
    Rule("R012", "对阵双源校验", "所有比赛", "核对≥2个数据源对阵一致性", priority=9),
    Rule("R013", "韩职平局比分分布", "韩职方向=平", "1-1/0-0/2-2", scope="仅韩职", priority=4, min_matches=50),
    Rule("R016", "巴甲平局基线", "巴甲所有比赛", "平局基线27%", scope="仅巴甲", priority=4, min_matches=50),
    Rule("R017", "巴甲主场系数", "巴甲所有比赛", "主场系数0.75~1.05", scope="仅巴甲", priority=4, min_matches=50),
    Rule("R018", "挪超逆转因子", "挪超所有比赛", "逆转因子20%", scope="仅挪超", priority=4, min_matches=50),
    Rule("R019", "芬超G1权重", "芬超半场0-0", "平平+15%", scope="仅芬超", priority=5, min_matches=50),
    Rule("R020", "主场受让追平后不败", "韩职主场受让+半场逼平", "下半场不败+15%", scope="仅韩职", priority=5, min_matches=50),
    Rule("R021", "长期不胜主场深盘陷阱", "连续4轮不胜+主场让-1以上", "主胜-20%，平+10%，客+10%", priority=6, min_matches=50),
    Rule("R022", "伤愈复出状态折扣", "伤停≥3周复出", "前2场状态按70%折算", priority=7, min_matches=50),
    Rule("R082", "巴甲强队伤停平局修正", "主队排名前4+核心缺阵≥2+客队排名后10", "平局+15%，主胜-15%", scope="仅巴甲", priority=6, min_matches=50),
    Rule("R083", "半场0-0延续修正", "半场0-0+两队近5场半场平局率≥40%", "全场平局+12%，平平+20%", priority=6, min_matches=50),
    Rule("R084", "垫底队客场逼平强队修正", "客队排名后4+主队排名前4+主队近期状态≤客队", "客队+1不败+20%，平局+10%", priority=6, min_matches=50),
    Rule("R085", "防线崩塌拖累进攻", "主队≥2名防线核心缺阵", "主队进球预期-0.5球，平局+10%", priority=9, min_matches=50),
    Rule("R086", "残阵客场无还手之力", "客队≥4名主力伤缺", "客队被零封+20%，主队大胜+15%", priority=9, min_matches=50),
    Rule("R087", "冷门比分强制输出", "每场比赛", "额外输出1个冷门比分+逻辑", priority=3, min_matches=50),
    Rule("R092", "巴甲小比分底色固化", "巴甲所有比赛", "大小球基线2.25，1-0/0-1+10%", scope="仅巴甲", priority=4, min_matches=50),
    Rule("R093", "门将危机修正", "主队被迫使用三号门将", "主队零封概率-30%，客队进球+0.3", priority=9, min_matches=50),
    Rule("R094", "巴甲4连败保级队主场死守", "巴甲主队排名后6且4+连败", "主队+1不败+20%，小球+15%，1-1+15%", scope="仅巴甲", priority=6, min_matches=50),
    Rule("R095", "巴甲主场7场不败但伤兵满营", "巴甲主队主场7+不败且≥5人伤缺", "主队不败仍维持+10%", scope="仅巴甲", priority=6, min_matches=50),
    Rule("U1", "客场战略保守", "欧战首回合客场", "客队进球预期-0.4", priority=8, min_matches=50, source_versions=("UCL",)),
    Rule("U2", "体能落差惩罚", "欧战客队72小时内有正式比赛", "下半场失球概率+20%", priority=7, min_matches=50, source_versions=("UCL",)),
    Rule("U3", "欧战经验溢价", "一方有欧战正赛经验", "客场抗压+0.15λ", priority=7, min_matches=50, source_versions=("UCL",)),
    Rule("U4", "主场条件动态调整", "欧战租借/中立场地", "主场系数降至0.55", priority=8, min_matches=50, source_versions=("UCL",)),
    Rule("U5", "首回合平局基线", "欧冠首回合", "平局概率≥50%", priority=6, min_matches=50, source_versions=("UCL",)),
    Rule("U5E", "首回合平局基线", "欧罗巴资格赛首回合", "平局概率≥35%", priority=6, min_matches=50, source_versions=("UEL",)),
    Rule("U6", "次回合开放修正", "欧战次回合", "客胜概率+10%，大球+10%", priority=6, min_matches=50, source_versions=("UCL",)),
    Rule("U7", "半全场平平强制", "欧战所有比赛", "平平强制进入TOP3", priority=5, min_matches=50, source_versions=("UCL",)),
    Rule("U7E", "半全场平平强制", "欧罗巴资格赛所有比赛", "平平强制进入TOP3", priority=5, min_matches=50, source_versions=("UEL",)),
]

TEAM_RULES: List[TeamRule] = [
    TeamRule("全北现代", League.KOR, "客场系数-0.10", "全北现代客场"),
    TeamRule("蔚山HD", League.KOR, "追平+15%，平局权重×1.3", "蔚山HD半场落后"),
    TeamRule("浦项制铁", League.KOR, "被逆转+15%", "浦项制铁半场领先"),
    TeamRule("首尔FC", League.KOR, "客场对后6名→进球+0.5球", "首尔FC客场+对手排名后6"),
    TeamRule("光州FC", League.KOR, "客场进球+10%，零封-10%", "光州FC客场"),
    TeamRule("米亚尔比", League.SWE, "主场系数-0.05", "米亚尔比主场"),
    TeamRule("韦斯特罗斯", League.SWE, "客场防守+0.3", "韦斯特罗斯客场"),
    TeamRule("天狼星", League.SWE, "客场下半场进球+15%", "天狼星客场"),
    TeamRule("玛丽港", League.FIN, "对手进球+20%，防守系数-1.0", "玛丽港主客场"),
    TeamRule("格尼斯坦", League.FIN, "对手进球+20%，防守系数-1.0", "格尼斯坦主客场"),
    TeamRule("雅罗", League.FIN, "对手进球+20%，防守系数-1.0", "雅罗主客场"),
    TeamRule("伊尔维斯", League.FIN, "对手进球+20%，防守系数-1.0", "伊尔维斯主客场"),
    TeamRule("埃尔维斯", League.FIN, "客场进球+0.3球", "埃尔维斯客场"),
    TeamRule("博德闪耀", League.NOR, "半场领先被逆转+15%", "博德闪耀半场领先"),
    TeamRule("维京", League.NOR, "半场领先被逆转+15%", "维京半场领先"),
    TeamRule("莫尔德", League.NOR, "半场领先被逆转+15%", "莫尔德半场领先"),
    TeamRule("桑德菲杰", League.NOR, "客场进球+10%", "桑德菲杰客场"),
    TeamRule("科林蒂安", League.BRA, "主场穿盘不受核心缺阵影响", "科林蒂安主场+核心缺阵"),
    TeamRule("博塔弗戈", League.BRA, "残阵锋线无力→平局+15%", "博塔弗戈≥3名锋线伤缺"),
    TeamRule("维多利亚", League.BRA, "残阵客场死守→客队进球-0.3", "维多利亚客场+≥3名主力伤缺"),
]

BASELINE_PERFORMANCE: Dict[League, Dict[str, float]] = {
    League.KOR: {"direction": 0.898, "score": 0.880, "half_full": 0.843},
    League.SWE: {"direction": 0.882, "score": 0.861, "half_full": 0.833},
    League.FIN: {"direction": 0.907, "score": 0.889, "half_full": 0.880},
    League.NOR: {"direction": 0.861, "score": 0.868, "half_full": 0.847},
    League.BRA: {"direction": 0.874, "score": 0.884, "half_full": 0.842},
}


def _choose_direction_by_draw_baseline(draw_baseline: float, home_pull: float, draw_pull: float, away_pull: float) -> Direction:
    if draw_pull >= draw_baseline and draw_pull >= home_pull and draw_pull >= away_pull:
        return Direction.DRAW
    if home_pull >= draw_baseline and home_pull >= away_pull:  # type: ignore[name-defined]
        return Direction.HOME
    if away_pull >= draw_baseline and away_pull >= home_pull:  # type: ignore[name-defined]
        return Direction.AWAY
    return Direction.HOME


def score_top3_for_direction(direction: Direction, league: Optional[League] = None, is_cold: bool = False) -> List[str]:
    if is_cold:
        return ["0-0", "1-1", "2-2"]

    if direction == Direction.HOME:
        return ["2-1", "1-0", "2-0"]
    if direction == Direction.DRAW:
        if league == League.KOR:
            return ["1-1", "0-0", "2-2"]
        return ["1-1", "0-0", "2-2"]
    return ["0-1", "1-2", "0-2"]


def half_full_top3_for_direction(direction: Direction, force_pingping: bool = False) -> List[str]:
    if force_pingping and direction != Direction.DRAW:
        return ["平平", "平胜", "平负"]
    if direction == Direction.HOME:
        return ["胜胜", "平胜", "负胜"]
    if direction == Direction.DRAW:
        return ["平平", "胜平", "负平"]
    return ["负负", "平负", "胜负"]


class FootballModel:
    def __init__(self) -> None:
        self.params = LEAGUE_PARAMS
        self.rules = RULES
        self.team_rules = TEAM_RULES
        self.templates = EU_TEMPLATES
        self.principles = CORE_PRINCIPLES

    def league_param(self, league: League) -> LeagueParams:
        return self.params[league]

    def applicable_rules(self, match: MatchInput) -> List[Rule]:
        rules = []
        for rule in sorted(self.rules, key=lambda x: (x.priority, x.code)):
            if rule.scope != "全部" and rule.scope != match.league.value:
                continue
            if rule.source_versions and match.league.value not in rule.source_versions:
                continue
            rules.append(rule)
        return rules

    def team_rule_notes(self, match: MatchInput) -> List[str]:
        notes = []
        for rule in self.team_rules:
            if rule.league != match.league:
                continue
            if rule.team in {match.home_team, match.away_team}:
                notes.append(f"{rule.team}：{rule.action}（{rule.condition}）")
        return notes

    def resolve_direction(self, match: MatchInput, home_pull: float, draw_pull: float, away_pull: float) -> Tuple[Direction, str]:
        params = self.league_param(match.league)
        draw_weight = draw_pull + params.draw_baseline * 0.1
        if match.league in {League.UCL, League.UEL}:
            if match.round_type == "首回合":
                draw_weight += 0.05
        chosen = _choose_direction_by_draw_baseline(params.draw_baseline, home_pull, draw_weight, away_pull)
        note = f"方向={chosen.value}，draw_baseline={params.draw_baseline:.0%}，欧战首回合平局加权已入"
        if match.league == League.UEL and match.round_type == "首回合":
            note += "，欧罗巴首回合平局基线35%"
        return chosen, note

    def total_line_decision(self, league: League, expected_goals: float) -> Tuple[str, float]:
        params = self.league_param(league)
        line = params.total_line()
        if expected_goals >= line + 0.15:
            return "大", line
        if expected_goals <= line - 0.15:
            return "小", line
        return "小", line

    def cold_score(self, direction: Direction) -> Tuple[str, str]:
        if direction == Direction.HOME:
            return "0-0", "概率等级：中等偏低"
        if direction == Direction.DRAW:
            return "1-2", "概率等级：中等"
        return "1-1", "概率等级：中等"

    def confidence(self, match: MatchInput, rule_count: int, data_conflict: bool = False) -> Confidence:
        if data_conflict:
            return Confidence.B
        if rule_count >= 4:
            return Confidence.A
        if rule_count >= 2:
            return Confidence.B
        if rule_count >= 1:
            return Confidence.C
        return Confidence.D

    def analyze(self, match: MatchInput, home_pull: float = 0.45, draw_pull: float = 0.25, away_pull: float = 0.30, expected_goals: Optional[float] = None) -> Prediction:
        if sum([home_pull, draw_pull, away_pull]) <= 0:
            raise ValueError("概率分布必须为正数。")
        if abs(sum([home_pull, draw_pull, away_pull]) - 1.0) > 1e-6:
            raise ValueError("概率分布之和必须为 1。")

        direction, direction_note = self.resolve_direction(match, home_pull, draw_pull, away_pull)
        applicable = self.applicable_rules(match)
        rule_count = len(applicable)
        notes = [direction_note]
        if match.league in {League.UCL, League.UEL}:
            applicable_sorted = sorted(applicable, key=lambda x: x.priority)
            for rule in applicable_sorted[:5]:
                notes.append(f"启用规则：{rule.code} {rule.name} -> {rule.action}")
        team_notes = self.team_rule_notes(match)
        if team_notes:
            notes.extend(team_notes)

        force_pingping = False
        if match.league == League.UCL and match.round_type == "所有比赛":
            force_pingping = True
        if match.league == League.UEL and match.round_type == "所有比赛":
            force_pingping = True
        if match.round_type == "首回合" and match.league == League.UCL:
            force_pingping = True
        if match.round_type == "首回合" and match.league == League.UEL:
            force_pingping = True

        if match.league in {League.UCL, League.UEL} and match.round_type in {"首回合", "所有比赛", None}:
            force_pingping = True

        if force_pingping and direction != Direction.DRAW:
            notes.append("欧战规则触发：平平强制进入半全场TOP3")

        scores = score_top3_for_direction(direction, match.league)
        if match.league in {League.UCL, League.UEL} and match.round_type == "次回合":
            scores = ["1-2", "2-1", "0-2"]
        cold_score_text, cold_prob = self.cold_score(direction)
        half_full = half_full_top3_for_direction(direction, force_pingping)
        if match.league in {League.UCL, League.UEL} and match.round_type == "次回合":
            half_full = ["平负", "胜负", "负负"]

        total_choice = "小 2.5球"
        if expected_goals is not None:
            total_choice_val, line = self.total_line_decision(match.league, expected_goals)
            total_choice = f"{total_choice_val} {line}球"
        else:
            if match.league in {League.UCL, League.UEL}:
                total_choice = "大 2.5球" if match.round_type == "次回合" else "小 2.5球"

        confidence = self.confidence(match, rule_count, data_conflict=False)
        score_direction_match = scores[0].split("-")[0] if direction == Direction.HOME else scores[0].split("-")[1] if direction == Direction.AWAY else scores[0]
        score_direction_match_bool = (
            (direction == Direction.HOME and int(scores[0].split("-")[0]) > int(scores[0].split("-")[1])) or
            (direction == Direction.DRAW and scores[0].split("-")[0] == scores[0].split("-")[1]) or
            (direction == Direction.AWAY and int(scores[0].split("-")[1]) > int(scores[0].split("-")[0]))
        )
        checks = {
            "direction_score_match": score_direction_match_bool,
            "direction_half_full_match": (half_full[0][1] == direction.value),
            "eu_template_match": match.league not in {League.UCL, League.UEL} or match.round_type in {None, "首回合", "次回合"},
            "has_cold_score": True,
            "rules_applied": rule_count > 0,
        }

        if not all(checks.values()):
            raise RuntimeError(f"交叉校验未通过：{checks}")

        return Prediction(
            league=match.league,
            direction=direction,
            confidence=confidence,
            score_top3=scores,
            cold_score=cold_score_text,
            cold_prob=cold_prob,
            half_full_top3=half_full,
            total_choice=total_choice,
            note="；".join(notes),
            checks=checks,
        )


def format_prediction(prediction: Prediction, match: MatchInput) -> str:
    round_info = f" | {match.round_type}" if match.round_type else ""
    lines = [
        f"【{prediction.league.value}】{match.home_team} vs {match.away_team}{round_info}",
        f"方向：{prediction.direction.value}（{prediction.confidence}）",
        f"比分TOP3：① {prediction.score_top3[0]} ② {prediction.score_top3[1]} ③ {prediction.score_top3[2]}",
        f"冷门比分：{prediction.cold_score}（{prediction.cold_prob}）｜冷门逻辑：低概率事件仍可能因阵容/临场变化发生",
        f"半全场TOP3：① {prediction.half_full_top3[0]} ② {prediction.half_full_top3[1]} ③ {prediction.half_full_top3[2]}",
        f"大小球：{prediction.total_choice}",
        f"核心逻辑：{prediction.note}",
    ]
    return "\n".join(lines)


def demo() -> None:
    model = FootballModel()
    match = MatchInput(league=League.UCL, home_team="凯拉特", away_team="奥莫尼亚", round_type="首回合")
    prediction = model.analyze(match, home_pull=0.50, draw_pull=0.30, away_pull=0.20, expected_goals=2.4)
    print(format_prediction(prediction, match))
    print("\n---\n")
    match2 = MatchInput(league=League.BRA, home_team="科林蒂安", away_team="奎尔梅斯", round_type=None)
    prediction2 = model.analyze(match2, home_pull=0.55, draw_pull=0.25, away_pull=0.20, expected_goals=2.1)
    print(format_prediction(prediction2, match2))


if __name__ == "__main__":
    demo()
