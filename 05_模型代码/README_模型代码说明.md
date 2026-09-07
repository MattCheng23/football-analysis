# 05_模型代码 说明（2026-09-06 审计标注）

> **状态：历史模型代码（V8.9/V9.5 继承）——仅作追溯参考，不参与当前体系。**

## 当前体系（2026-09-06）
- **模型=文档驱动**：整体层 `01_当前模型\整体模型_蒸馏定稿_V11.38.1_20260906.md`（V11.38.1-5D·单一权威）+ 联赛层 `联赛针对性优化蒸馏_20260906.md` + 参数表 v2.2 + 形态偏好表
- **执行工具**（常青脚本·存放于 `D:\Cola\_tmp_football\`）：check_batch_full.py（批检查）/ rollback_lite.py（滚动回测 15 行）/ attribution.py（归属统计）/ bump_version.py / verify_sun0906_deploy.py / league_calib.py / batch_distill.py / redblack_analyze.py / memory_tidy_check.py
- **分析流程**：pre-match-analysis + post-match-review 技能（双轨制：联赛层 λ/形态 + 整体层判定）

## 本目录文件
| 文件 | 状态 |
|---|---|
| football_model.py | v8.9/v9.5 继承的早期模型（V9.5 时代·约 8/17 前）——历史 |
| optimized_football_model.py | 同代优化版——历史 |
| backtest.py | 历史回测脚本——历史（当前回测=rollback_lite.py+attribution.py）|

**建议**：不需要清理（保留追溯）；未来若需"代码化模型"（泊松/λ 计算器）应新建在本目录并引用 `05_模型代码\` 相对路径（与 _tmp_football 解耦）。
