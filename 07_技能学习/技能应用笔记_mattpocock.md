# 技能应用笔记 · mattpocock/skills 学习内化

> 来源：`D:\Cola\skills`（安装版 22 技能）与 `D:\Cola\mattpocock-skills`（完整仓库 41 技能，同源于 github.com/mattpocock/skills）
> 学习日期：2026-08-15
> 用途：将这套工程方法论内化为日常作业规范

---

## 一、技能地图

### engineering（工程技术）
| 技能 | 一句话 |
|------|--------|
| **wayfinder** | 大工程拆分为"决策票据地图"，逐个消解迷雾直到路径清晰 |
| **to-spec** | 把模糊需求钉成可验收规格 |
| **to-tickets** | 规格 → 可执行票据 |
| **triage** | 分类分诊：什么该做、什么不做、什么出范围 |
| **implement** | 按规格实现：TDD→类型检查→单测→全测→code-review→提交 |
| **tdd** | 红灯→绿灯循环；只在**商定接缝**处写测试 |
| **code-review** | 双轴并行审查：**标准轴**（编码规范+Fowler 异味基线）+ **规格轴**（是否实现了需求的点） |
| **diagnosing-bugs** | 五阶段：反馈环（最关键）→复现最小化→多假说→探针→修复+回归测试 |
| **research** | 后台代理查一手资料（官方文档/源码/规范），写成带引用的 md |
| **prototype** | 廉价粗糙原型提升讨论保真度 |
| **domain-modeling** | 用 ADR 格式做领域建模决策 |
| **codebase-design / improve-codebase-architecture** | 设计两次 / 架构改进（HTML 报告） |
| **resolving-merge-conflicts** | 冲突解决流程 |
| **setup-matt-pocock-skills** | 仓库技能安装（含 issue tracker 配置） |

### productivity（生产力）
| 技能 | 一句话 |
|------|--------|
| **grilling / grill-me / grill-with-docs** | 一问一答的深度追问，榨出模糊需求真相 |
| **handoff** | 清晰交接：给下一个 agent/人的上下文包 |
| **teach** | 教用户理解复杂概念的格式（mission/glossary/resources） |
| **writing-great-skills** | 写技能的元技能（见下） |
| **wayfinder 关联** |（在 engineering） |

---

## 二、核心方法论语录（已内化）

### 1. 诊断问题：先是反馈环，其余都是机械
> "有一个**紧致**的通过/失败信号，你就能找到原因；没有它，盯代码再多也没用。"
- 构建复现循环的优先序：失败测试 → curl → CLI fixture → Playwright → 重放轨迹 → 一次性 harness → fuzz → bisect → 差分 → HITL 脚本
- 循环要**紧**：快（秒级）、确定性、能精确命中症状（能变红）
- 3-5 个可证伪假说**并列出来再动手**，每个假说必须能说出"如果 X 是原因，那么改 Y 会让 bug 消失/加重"
- 回归测试要写在"正确接缝"上；没有正确接缝本身就是发现
- 日志打唯一前缀 `[DEBUG-xxxx]`，结尾一次 grep 清干净

### 2. 代码审查：双轴分离，互不掩盖
- **标准轴**：编码规范 + Fowler 12 种坏味道（Mysterious Name / Duplicated Code / Feature Envy / Data Clumps / Primitive Obsession / Repeated Switches / Shotgun Surgery / Divergent Change / Speculative Generality / Message Chains / Middle Man / Refused Bequest）
- **规格轴**：只问"实现了需求没有"——缺的、多的（scope creep）、做错的
- 两个子代理并行、独立上下文，报告并列不合并排序

### 3. TDD：只测商定接缝
- 测试走公共接口（seam），不碰内部实现
- 反模式：**水平切片**（先写完全部测试再写实现——测的是想象的行为）；**同义反复**断言（期望值由代码自身算出）
- 红灯→绿灯→（重构归 review 阶段，不在循环内）

### 4. 需求：grill 出真需求 → 钉规格 → 拆票据
- 用一问一答（grilling）把模糊词追到底
- 规格定"可验收"；票据定到一次 agent 会话装得下（~100K token）

### 5. 大工程：wayfinder 决策地图
- 地图=索引不是仓库；票据=决策问题不是执行切片
- **战争迷雾**：不能精确表述的问题先写进"Not yet specified"，能表述的立票据
- 范围外的工作写"Out of scope"，永不毕业

### 6. 写技能（writing-great-skills）
- 技能的根美德是**可预测性**（过程一致，不是输出一致）
- 信息层级：步骤（带可检查的完成标准）→ 文内参考 → 外部参考（渐进披露）
- 避免：提前完成、重复、沉积、臃肿、无操作（no-op）、否定式指令（用正面表述）

---

## 三、应用承诺（我如何用在工作里）

| 场景 | 过去做法 | 现在改成 |
|------|----------|----------|
| 用户报 bug | 先猜原因再验证 | 先建红色复现循环 → 最小化 → 3-5 假说并列 → 探针验证 |
| 写代码 | 直接实现 | 先商定接缝→TDD 纵向切片→review 双轴 |
| 实现需求 | 按印象做 | to-spec 先钉可验收标准 |
| 复杂研究 | 主线程慢慢搜 | research 技能：后台子代理查一手资料写 md |
| 大任务 | 一股脑做 | wayfinder：拆决策票据，逐张解决 |
| 审查代码 | 凭经验挑问题 | 12 异味基线 + 规格对照，并行双轴 |
| 交接 | 口头说明 | handoff：写上下文包 |
| 追问需求 | 一次问完 | grilling：一问一答深挖 |

---

## 四、与现有足球分析工作的结合

- 每日多场预测 = 可并行子代理的 batch 分析（research/拆票思想）
- 模型规则库迭代 = 版本化 + 复盘反馈环（可借用 diagnosing-bugs 的"反馈环优先"）
- 规则冲突仲裁 = code-review 的味道基线思路（先列再裁）