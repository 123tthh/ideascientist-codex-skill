# IdeaScientist Codex Skill

面向 Codex 的 IdeaScientist 非官方本地适配：可作为独立 skill 或 skills-only 插件使用。

把 [IdeaScientist 论文](https://arxiv.org/abs/2610.04074) 的证据驱动科研构思流程接入 Codex：定位方法缺口，发展或迁移机制，深入比较最近邻工作，再写成可证伪研究方案。

这是非官方、skills-only 本地插件。使用当前 Codex 模型及宿主现有工具，不需要额外 API key、GPU 或常驻服务。额外附带 Python 报告检查器（需要 jsonschema）；未打包或运行作者训练权重和百万级 Idea Vault。

## 使用

安装后在新任务中选择 IdeaScientist 插件或 `$ideascientist`，例如：

> 用 $ideascientist 阅读当前项目和相关论文，围绕长时序交互动作生成寻找一个有证据的方法缺口，借鉴其他领域机制，并给出一周内可执行的最小证伪实验。

> 用 $ideascientist 检查我的 idea 的 novelty：优先保留并发展它，深入阅读一批最近邻论文，给出真实差异及一段有说服力的 novelty 论证；如果严重撞车，请明确指出。

> 用 $ideascientist 基于这些论文形成研究 proposal。算力是一张 GPU，先确认最近邻和数据可得性，所有未做的实验写成计划。

输入尽量包含任务、具体失败案例、现有方案、数据／算力限制。不必先填写完整表单；skill 会从上下文提取已有信息。

完整输出包括正文证据摘要、gap、候选、审查意见、`proposal.md`、`report.json` 与 `sources.json`。默认结果写入使用时工作区的 `ideascientist-runs/`。找不到有根据的创新时，会交付负面发现及原因。

## 构思与 novelty 原则

- 不以“绝对原创”或“完全没有先例”为门槛。已有相关尝试仍可以推进、完善或深化，判断重点是明确且有意义的新增贡献和进一步探索空间。
- 对用户已有 idea，优先保留和发展其核心；先系统调研并深入阅读最近邻论文，比较问题设定、关键机制、技术细节和贡献边界，再用一个连贯段落说明新增了什么、为什么有意义。
- 不强行制造 novelty。只有深入比较后确认核心问题、关键方法和主要贡献存在难以绕过的高度重合，才停止为当前版本论证，并具体列出撞车工作、重合之处和差异不足的原因。证据暂不充分时说明待核实项。

完整原则和执行方法见 [SKILL.md](skills/ideascientist/SKILL.md)。仅检查 novelty 时可交付最近邻比较和论证，不必扩展成完整 proposal。

## 文件

- `skills/ideascientist/SKILL.md`：主工作流。
- `skills/ideascientist/references/paper-and-project.md`：论文、代码、数据与适配边界。
- `skills/ideascientist/references/upstream-runtime.md`：可选官方运行要求。
- `skills/ideascientist/assets/report.schema.json`：结构化方案格式。
- `skills/ideascientist/scripts/audit_report.py`：结构与引用记录检查。

## 安装方式

### 作为独立 skill 安装

克隆本仓库，将完整 skill 目录复制到 Codex 用户技能目录。以下命令适用于默认的 `~/.codex/skills` 位置；如果自定义了 Codex 配置目录，请使用对应位置。

```bash
git clone https://github.com/123tthh/ideascientist-codex-skill.git
mkdir -p ~/.codex/skills
cp -R ideascientist-codex-skill/skills/ideascientist ~/.codex/skills/
```

复制前确认目标中没有需要保留的同名 skill。保留目录中的 references、assets 和 scripts。安装后开启新任务使 skill 被发现；若 UI 尚未刷新，重启桌面应用。

### 作为本地插件安装

本包同时包含 portable `plugin.json` 和 Codex 兼容清单 `.codex-plugin/plugin.json`。可以通过 Codex 的 plugin-creator 把完整插件目录登记到个人 marketplace；本仓库本身未提供 marketplace 目录，不能直接当作 marketplace URL 安装。向 Codex 提供克隆后的目录，并要求“将这个本地插件安装到我的个人 marketplace”即可。

标准个人安装通常把源目录放在 `~/plugins/ideascientist`，登记在 `~/.agents/plugins/marketplace.json`。

查看插件：`codex plugin list`。从已注册的 personal marketplace 安装：`codex plugin add ideascientist@personal`。只有在 marketplace 顶层名称确实为 personal 时使用这个名字。可用 `codex plugin remove ideascientist@personal` 卸载；具体参数以已安装 CLI 的帮助为准。

独立 skill 与插件安装二选一；已安装同名插件的机器无需再复制独立 skill。

## 报告检查与测试

科研构思工作流不需要额外 Python 服务。附带的自动报告检查器需要 Python 3.10+ 和 `jsonschema`，可在独立环境安装：

```bash
cd ideascientist-codex-skill
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python skills/ideascientist/scripts/audit_report.py /path/to/ideascientist-run
```

历史回测检查追加 `--cutoff YYYY-MM-DD`，截止当天不包含在允许范围内。12 个测试使用合成数据，覆盖缺失引用、摘要冒充正文、重复来源、日期边界等情形；它们不证明研究方案有效。

## 许可与限制

来源：[官方仓库](https://github.com/jiarui-liu/IdeaScientist)，核对提交 `82a98a08772eab08d11fd097445afa4a8eaaa5b3`。角色流程已为宿主工具改写，报告结构转换为 JSON Schema，新增本地引用账本与检查器，未宣称由原作者发布。

本包按 CC BY-NC 4.0 提供，保留原项目署名和非商业条款，见 `LICENSE` 与 `NOTICE.md`。论文结果不等于本插件效果；生成的 proposal 需要实验验证。自动检查不能证明论文事实、原创性或科学正确性。
