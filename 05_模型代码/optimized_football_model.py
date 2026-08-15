"""继承自 football_model.py 的数据驱动优化模型。"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

from football_model import (
    Confidence,
    Direction,
    League,
    MatchInput,
    Prediction,
    half_full_top3_for_direction,
    score_top3_for_direction,
)
from backtest import (
    LEAGUE_RESULT_NAMES,
    RESULT_FILES,
    _cold_score,
    _expected_goals_from_results,
    _freq_template_top3,
    _league_direction_from_prediction,
    _resolve_direction,
    _template_top3_for_direction,
    build_half_full_templates,
)


class OptimizedFootballModel:
    def __init__(self, workspace: Optional[str] = None) -> None:
        self.workspace = workspace
        self.results = self._load_results()
        self.half_full_templates = build_half_full_templates(self.results)
        self.expected_goals = self._expected_goals_by_league()
        self.total_lines = self._total_lines()

    def _load_results(self) -> Dict[League, list]:
        from pathlib import Path
        import re

        root = Path(self.workspace) if self.workspace else Path(".")
        results: Dict[League, list] = {}
        result_line = re.compile(
            r"^(?P<date>\d{4}-\d{2}-\d{2}) \| (?P<teams>.+?) \| (?P<half>\d+\-\d+) \| (?P<full>\d+\-\d+)$"
        )
        for league, filename in RESULT_FILES.items():
            path = root / filename
            rows = []
            for line in path.read_text(encoding="utf-8").splitlines():
                match = result_line.match(line.strip())
                if not match:
                    continue
                home, away, neutral = self._parse_teams(match.group("teams"))
                from backtest import MatchResult
                rows.append(
                    MatchResult(
                        date=match.group("date"),
                        home_team=home,
                        away_team=away,
                        half=match.group("half"),
                        full=match.group("full"),
                        league=league,
                        neutral=neutral,
                    )
                )
            results[league] = rows
        return results

    @staticmethod
    def _parse_teams(text: str) -> Tuple[str, str, bool]:
        neutral = "(中)" in text
        text = text.replace("(中)", "")
        home, away = text.split(" vs ")
        return home.strip(), away.strip(), neutral

    def _expected_goals_by_league(self) -> Dict[League, float]:
        return {league: _expected_goals_from_results(rows) for league, rows in self.results.items()}

    def _total_lines(self) -> Dict[League, float]:
        mapping = {
            League.KOR: 2.25,
            League.SWE: 3.0,
            League.FIN: 2.5,
            League.NOR: 2.75,
            League.BRA: 2.25,
            League.MLS: 3.0,
            League.UCL: 2.5,
            League.UEL: 2.5,
        }
        return mapping

    def league_results(self, league: League) -> list:
        return self.results[league]

    def score_top3(self, match: MatchInput) -> List[str]:
        direction = self.predict_direction(match)
        league_rows = self.results[match.league]
        round_rows = league_rows
        if match.league in {League.UCL, League.UEL} and match.round_type in {"首回合", "次回合"}:
            round_rows = [row for row in league_rows if row.date == match.round_type]
        counters: Dict[Direction, Counter] = Counter()
        for row in round_rows:
            counters[row.actual_direction][row.full] += 1
        counter = counters[direction]
        if not counter:
            counter = Counter(row.full for row in league_rows if row.actual_direction == direction)
        top3 = _freq_template_top3(counter)
        if len(top3) < 3:
            fallback = _template_top3_for_direction(direction, match.league, match.round_type)
            top3 = (top3 + [score for score in fallback if score not in top3])[:3]
        return top3

    def predict_direction(self, match: MatchInput) -> Direction:
        league_rows = self.results[match.league]
        round_rows = league_rows
        if match.league in {League.UCL, League.UEL} and match.round_type in {"首回合", "次回合"}:
            round_rows = [row for row in league_rows if row.date == match.round_type]
        return _resolve_direction(round_rows, match.round_type)

    def half_full_top3(self, match: MatchInput) -> List[str]:
        key = (match.league, match.round_type, self.predict_direction(match))
        fallback_key = (match.league, None, self.predict_direction(match))
        templates = self.half_full_templates.get(key) or self.half_full_templates.get(fallback_key)
        if templates:
            return templates[:3]
        return half_full_top3_for_direction(self.predict_direction(match))

    def cold_score(self, match: MatchInput) -> str:
        league_rows = self.results[match.league]
        counter: Dict[Direction, Counter] = Counter(row.actual_direction for row in league_rows)
        league_direction_counters: Dict[Direction, Counter] = {direction: Counter() for direction in counter}
        for row in league_rows:
            league_direction_counters[row.actual_direction][row.full] += 1
        return _cold_score(self.predict_direction(match), league_direction_counters)

    def total_choice(self, match: MatchInput) -> str:
        direction = self.predict_direction(match)
        expected_goals = self.expected_goals[match.league]
        line = self.total_lines[match.league]
        if expected_goals >= line + 0.15:
            return f"大 {line}球"
        if expected_goals <= line - 0.15:
            return f"小 {line}球"
        if match.league in {League.UCL, League.UEL} and match.round_type == "次回合":
            return f"大 {line}球"
        return f"小 {line}球"

    def confidence(self, match: MatchInput) -> Confidence:
        direction_counts = {direction: len([row for row in self.results[match.league] if row.actual_direction == direction]) for direction in [Direction.HOME, Direction.DRAW, Direction.AWAY]}
        max_count = max(direction_counts.values(), default=0)
        total = max(sum(direction_counts.values()), 1)
        if max_count / total >= 0.45:
            return Confidence.B
        return Confidence.C

    def analyze(self, match: MatchInput) -> Prediction:
        direction = self.predict_direction(match)
        notes = [
            "数据驱动优化模型：基于当前赛果库统计",
            f"方向={direction.value}，平局基线={self._draw_baseline(match.league):.0%}",
            f"预期进球={self.expected_goals[match.league]:.2f}，大小球线={self.total_lines[match.league]}",
        ]
        return Prediction(
            league=match.league,
            direction=direction,
            confidence=self.confidence(match),
            score_top3=self.score_top3(match),
            cold_score=self.cold_score(match),
            cold_prob="概率等级：中等偏低",
            half_full_top3=self.half_full_top3(match),
            total_choice=self.total_choice(match),
            note="；".join(notes),
            checks={},
        )

    def _draw_baseline(self, league: League) -> float:
        rows = self.results[league]
        if not rows:
            return 0.25
        return sum(1 for row in rows if row.actual_direction == Direction.DRAW) / len(rows)


def format_prediction(prediction: Prediction, match: MatchInput) -> str:
    round_info = f" | {match.round_type}" if match.round_type else ""
    lines = [
        f"【{prediction.league.value}】{match.home_team} vs {match.away_team}{round_info}",
        f"方向：{prediction.direction.value}（{prediction.confidence}）",
        f"比分TOP3：① {prediction.score_top3[0]} ② {prediction.score_top3[1]} ③ {prediction.score_top3[2]}",
        f"冷门比分：{prediction.cold_score}（{prediction.cold_prob}）｜冷门逻辑：基于当前联赛低频率比分",
        f"半全场TOP3：① {prediction.half_full_top3[0]} ② {prediction.half_full_top3[1]} ③ {prediction.half_full_top3[2]}",
        f"大小球：{prediction.total_choice}",
        f"核心逻辑：{prediction.note}",
    ]
    return "\n".join(lines)


def demo() -> None:
    model = OptimizedFootballModel()
    match = MatchInput(league=League.UCL, home_team="凯拉特", away_team="奥莫尼亚", round_type="首回合")
    prediction = model.analyze(match)
    print(format_prediction(prediction, match))
    print("\n---\n")
    match2 = MatchInput(league=League.BRA, home_team="科林蒂安", away_team="奎尔梅斯", round_type=None)
    prediction2 = model.analyze(match2)
    print(format_prediction(prediction2, match2))


if __name__ == "__main__":
    demo()
