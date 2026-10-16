# 可选：运行官方 IdeaScientist

仅在用户明确要求原版运行或复现时使用；默认本地 skill 不需要这些服务。以下依据提交 `82a98a08772eab08d11fd097445afa4a8eaaa5b3` 的 README、pyproject 和脚本核查，未执行全链路运行。

## 运行前核查

1. 选定实际源码目录；从官方仓库读取当前 README 与变更。Python 要求 3.10+。
2. 在独立虚拟环境安装 core（numpy、requests、pyyaml）；语料构建、embedding、分析是不同 extra，不要自动把全部 GPU 依赖安装到用户现有环境。
3. 检查 `IDEA_VAULT_DB` 对应 SQLite 的 `papers`、`paper_full_text`、`metadata_results_masked`、`citations`；验证有可用记录。下载的 JSONL 数据不能直接改名成 `.db`；需依据实际字段导入、取得正文并重建索引，不能臆造现成转换命令。
4. 检查 `IDEASCIENTIST_KEYWORD_INDEX` 中存在非空 `papers_fts`、`papers_meta`。上游不会在请求路径自动建索引；可在准备好数据后运行 `python -m ideascientist.vault.index keyword`。
5. 核查 OpenAI-compatible 模型端点及真实模型 ID、工具调用、上下文上限。当前 Codex 登录不等于提供这个外部端点的凭证。确认密钥只存环境变量，不记录值；付费 API、下载大语料、GPU 训练需符合用户实际授权范围。

## 官方运行命令

在官方仓库及专用环境中：

```bash
python -m pip install -e .
python scripts/run_ideation.py --problem-file problem.txt --run-dir runs
```

`problem.txt` 同时包含 `Problem definition:` 和 `Challenge:`。可用参数包括 `--model`、`--problem-id`、`--query-paper-id`、`--max-turns` 和 `--max-sub-turns`。默认总轮数 100、子代理上限 40，内部角色上限还会进一步限制；先小范围检查服务和预算，再决定完整运行。

| 环境变量 | 作用／官方默认 |
|---|---|
| `IDEASCIENTIST_BASE_URL` | 模型端点，默认 `http://localhost:8000/v1` |
| `IDEASCIENTIST_MODEL` | 实际部署的模型名称；README 示例为 Qwen3.6-27B |
| `IDEASCIENTIST_API_KEY` | 外部服务凭证，本地无鉴权服务可不设 |
| `IDEA_VAULT_DB` | Vault 数据库路径 |
| `IDEASCIENTIST_KEYWORD_INDEX` | BM25 索引路径 |
| `IDEASCIENTIST_CUTOFF_DATE` | 默认 `2026-01-01`，原版检索的时间限制 |
| `CONTEXT_WINDOW` | 服务实际支持的上下文上限 |
| `IDEASCIENTIST_TEXT_TOOLS` | 当工具解析器不兼容时按 README 使用文本工具调用模式 |

注意：本次代码中 keyword search 用年份作保守截止过滤；不要假设将截止日期改为年中就得到精确到日的检索。需要一般日期边界时先检查并测试 `harness/corpus.py` 的相关路径。

生产角色主要使用 BM25 keyword search。向量检索／完整 novelty 评测还涉及 embedding 索引和 query server；不能混淆 core ideation 的最低依赖与完整评测所需资源。

## 语义检索与训练

需要 embeddings 时，再安装 `.[embed]`、准备相应权重与向量索引，按官方方法启用：

```bash
python -m ideascientist.serving.query_server --port 8100
```

`EMBEDDING_BASE_URL` 指向该 query server；它包含 query-side instruction，不能随意替换成普通 pooling 端点而声称等价。

训练入口是 `scripts/train_role.py`，角色配置在 `ideascientist/training/`。训练框架、模型、数据和计算预算须逐项落实。仓库存在训练代码不表示已经训练，也不表示已下载或获得论文 checkpoint。

原版产物位于 `runs/<timestamp>_<slug>/outputs/`，包括 `problem.md`、`plan.md`、`papers/`、`gaps.md`、`candidates.md`、`scores.md`、`report.json`；日志另存。应以真实退出状态、产物、引用核查和服务日志判断完成，不能仅凭进程启动成功。
