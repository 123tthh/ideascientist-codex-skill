# 证据与成果约定

## 完整运行目录

```text
problem.md        问题、挑战、约束、日期模式
plan.md           当前轴、决策、候选版本和下一步
search-log.md     查询、日期、命中范围、正文可访问性、排除原因
papers/P001.md    正文阅读问题、答案、章节／页码、未解问题
sources.json      来源账本
gaps.md           已有方法与证据支持的缺口
candidates.md     候选及源机制到目标问题的映射
scores.md         最近邻比较、novelty 论证或撞车结论、survive / revise / reject
report.json       通过审查后形成的结构化方案
proposal.md       面向用户的研究方案和最小实验
```

零缺口或候选经证据审查无法成立时无需创建报告。交付真实发现和下一步，不用空白模板冒充成果。单独检查用户 idea 的 novelty 时，保留原始构思、阅读证据和审查结果即可，不强制生成完整方案。

## 最近邻比较与 novelty 结论

为一批最接近的论文建立比较表，按证据支持的实际内容填写：论文与正文定位、核心问题／假设、关键方法／技术细节、主要贡献及边界、与当前 idea 的重合、真实差异、差异为何有意义、还需核实或验证什么。检索数量随覆盖情况调整，不以找到一篇相似论文就停止。

默认保留并发展用户构思，按以下情况交付：

- **存在实质贡献**：用一个连贯段落说明“现有 A/B 做到什么 → 当前 idea 具体新增或推进什么 → 为什么这有意义 → 成立条件与待验证内容”，引用具名最近邻。这个结构是表达参考，不是允许凭空填写的论证模板。
- **仍可发展但证据不足**：说明已成立的差异、未确认之处、下一步阅读或修改；标为 `revise`，不要将未知等同于无新颖性，也不要把潜在差异包装成已证实贡献。
- **严重撞车**：停止为当前版本编写肯定的 novelty claim，具体指出与哪些论文在核心问题、关键方法、主要贡献上高度重合，以及为什么剩余差异不足以支撑可信贡献。新的改进建议与原版本的结论分开。

仅有相似工作不构成 `reject`。推进既有思想、弥补局限、揭示机制或以新视角形成可验证的新理解都可有价值；只换名称或叙述不构成实质贡献。机器引用检查不裁决这些科学判断。

## 来源账本

`sources.json` 是 JSON 数组；一个来源一个稳定编号。以下字段说明用于填写真实数据，不是可以当成已读证据的示例文献：

| 字段 | 含义 |
|---|---|
| `id` | `P001`、`P002` 等，稳定且唯一 |
| `title` | 已核对的真实标题 |
| `location` | 官方网页 URL，或用户本地原文的绝对路径 |
| `version_date` | 实际读到的版本公开日期，YYYY-MM-DD；未知为 null |
| `read_status` | `body_read`、`abstract_only` 或 `unavailable` |
| `digest` | 相对运行目录的阅读摘要路径，如 `papers/P001.md` |
| `evidence` | 数组，每条含 `claim`（原文支持什么）和 `locator`（章节、页码、定理、代码路径等） |

`body_read` 表示读过支撑所引用机制或限制的正文段落，不表示逐字读完全文。阅读摘要需明确本次阅读的覆盖范围。摘要里区分原文明示、读者推断、仍待验证的内容。

来源日期用正文版本的公开日期。历史回测不能以早期首发日期为较新的正文放行；日期未知的材料不能用于严格回测结论。当前文献模式允许日期未知，但说明局限。

来源可以是论文或官方实现；代码证据明确指向仓库、提交和文件，不能把实现细节说成论文已验证的科学结论。全文不可访问时保留线索，不能用摘要支撑细粒度方法缺口。

## 报告引用

`report.json` 的字符串中写 `[P001]`；多个来源写 `[P001][P002]`。`related_work[].citations` 是裸编号数组，如 `["P001", "P002"]`。这是本地映射编号，不是原版 Vault 整数 ID，不能直接用于上游自动评测。

所有报告引用都必须在账本中有 `body_read` 记录、可定位的证据和现存摘要。未引用的待查资料可留在账本里，但不得把它们计为正文证据。每条关键文献事实仍要人工核对是否被相应证据支持；脚本不作语义裁决。

## 结构化报告

`assets/report.schema.json` 保留上游 report writer 的字段结构，去掉原始论文条目的文末 references 块；来源由独立账本解析。顶层字段为：

`title`、`topic_relevance`、`one_sentence_thesis`、`core_problem`、`key_novelty`、`problem_definition`、`key_terms`、`related_work`、`method`、`model_details`、`comparison_to_sota`、`proposed_evaluation`、`falsifiable_predictions`、`limitations`。

其中：

- `method.modules` 明确模块、输入输出及实现说明；`pseudocode` 写拟实现算法。
- `model_details.training` 可以明确“无需训练”及原因；计划超参数说明选择依据。
- `proposed_evaluation.benchmarks[].newly_constructed` 为布尔值，标记是否拟构建。
- `falsifiable_predictions` 不为空，每项同时提供 `pillar`、`prediction`、`kill_condition`。
- 不编造测得数值、引用、运行记录或评分；尚未决策的选择写出候选与决策依据。

`proposal.md` 提供可读版本，可采用“问题 → 最近邻与缺口 → 源机制和映射 → 方法 → 最小证伪实验 → 完整评测 → 风险”的顺序。行文按任务复杂度调整，无需复制 JSON 的每个标题。

## 自动检查

```bash
python3 <skill>/scripts/audit_report.py <run-directory>
python3 <skill>/scripts/audit_report.py <run-directory> --cutoff 2026-01-01
```

需要 Python 3.10+ 和 `jsonschema`（当前安装环境已具备）。缺少依赖时可在用户允许的环境安装 `jsonschema>=4.18,<5`，或人工核对并如实报告未执行脚本。

检查失败先修复记录、报告或证据缺口，不能把 `abstract_only` 改成 `body_read` 来消除错误，除非实际补读了正文。退出码 0 表示机械检查通过，1 表示输入或结构／引用问题，2 表示依赖缺失；不输出“科学验证通过”。
