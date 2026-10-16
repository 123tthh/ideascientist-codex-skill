# 论文与项目核查

核查日期：2026-10-16。

## 一手来源

- 论文：[IdeaScientist: Orchestrating Agents for Grounded Scientific Ideation](https://arxiv.org/abs/2610.04074)，Jiarui Liu 等；v1 于 2026-10-02 发布，检查版本 v2 于 2026-10-09 更新。
- [论文正文](https://arxiv.org/html/2610.04074v2)：§3 方法、§4 数据、§5 评测、附录 A 角色与输出接口。
- [官方代码](https://github.com/jiarui-liu/IdeaScientist)，本次核对提交 `82a98a08772eab08d11fd097445afa4a8eaaa5b3`。
- [Svalbard Idea Vault](https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault)。论文与仓库均链接到此数据集。

## 可复用的方法

输入是问题定义和当前方法未满足的挑战。Gap finder 针对同问题检索，定位方法不足；innovator 从不同问题设置寻找可迁移机制；report writer 把直觉变成方案。Orchestrator 跟踪计划，reader 提供定向正文摘要，reviewer 尝试推翻来源解释、创新差异和迁移条件。原版通过工具权限隔离角色及全文访问。

训练版分别训练三个产出角色的 LoRA，采用异步 GRPO 和角色级奖励。奖励包括无参考质量、有参考一致性、引用 F1，并有结构和证据门槛。复制提示或工作流不会获得这些训练权重。

论文提到 277 万条分解后的研究 idea；底层文献库约 470 万篇，约 280 万篇有全文。筛选出的 14,977 篇目标论文分为 14,500 训练、200 验证、277 测试，不能把约 15K 说成全部是独立测试样本。表 1 的结果来自自动评测，指标并不等价于实验成功率、论文接收率或本插件效果。

历史评测使用 2026-01-01 截止的检索材料，并隐藏目标论文；作者还讨论模型记忆污染。真实当前选题可用最新文献，但这种使用不属于原实验的历史回测。

## 本地适配与原版的对应

| 原版 | 本插件 |
|---|---|
| 五种角色与 orchestrator，工具级权限隔离 | 当前 Codex 按阶段执行，保留产物接口；不承诺上下文隔离 |
| Vault BM25、正文读取器、语义空间 | 宿主搜索／浏览器／用户本地论文，使用可核实的来源 |
| Vault 整数 ID | 本地 P001 等编号及 URL／路径账本 |
| report writer JSON 字段 | 同字段结构的 JSON Schema，以及中文可读方案 |
| 角色专属 GRPO 权重 | 当前宿主模型，不加载或冒称作者权重 |
| 论文的 LLM judges、novelty evaluation | 反驳式审查和机械引用检查，未复现论文指标 |

优点是无需额外模型服务就能使用核心研究流程。限制是检索覆盖、训练效果、角色隔离和评测可比性均不同。

本地版本还加入用户指定的构思原则：不追求绝对原创，优先发展用户已有 idea，通过深入的最近邻比较识别有意义的新增贡献；只有证据表明严重重合且难以区分时才停止 novelty 论证。这是本地适配的行为要求，不是对原论文结论的转述。

## 原项目发布状态

仓库包含 harness、vault 构建、reward、training、evaluation、serving 与六个入口脚本。README 明确说数据不提交在仓库中，训练适配器和参考产物通过代码复现；本次核查未确认独立可下载的已训练适配器。README 也明确排除了消融实验分支、人工研究和 LaTeX 表格生成器。

数据集网页可访问，但核查时自动 Viewer 显示日期转换错误（例如年份字符串 `2026` 被当成 timestamp）。这是预览构建错误，不能据此判定所有原始文件损坏；也不能把网页可访问等同于本地 Vault 已准备完成。

进一步读取发布数据集的 README 发现，其实际说明为 **2,669,631 条**，split 为 train 14,149、validation 195、test 272、corpus 2,655,015，与论文数字不同。原始发布路径为 `records/<split>/*.jsonl.zst`，包含模型生成的 `problem_definition`、`intuition`、`proposal_masked` 等字段，不发布论文原文。不能直接当成上游 SQLite 和全文索引，也不能声称这个发布版本已严格复现论文数据。差异原因本次未确认。模型生成标注只用作发现线索，核心机制结论仍核对论文原文。

## 来源与许可

项目源码 [LICENSE](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/LICENSE) 声明 CC BY-NC 4.0；论文页面和数据集卡片显示 CC BY 4.0。它们是不同对象的许可，不应混用。本包参考并改写了角色流程、转换了报告字段结构，保留项目非商业许可与作者署名，标明是非官方本地适配。未打包语料、模型权重或原版运行服务。
