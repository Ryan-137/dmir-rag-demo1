# Issue #7 Agent 指示：QA/evidence dataset and evaluation report

你正在为 RAG Demo 项目完成 GitHub Issue #7。目标是准备目标新论文、干扰论文、QA/evidence 标注和三模式评测报告。

## Owner

`Ryan-137`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `eval/`
- `scripts/run_eval.py`
- `sample_data/`
- `docs/`
- `docs/agent_instructions/issue-07-Ryan-137/AGENTS.md`

## 硬性限制

1. 不得把临场手工结果伪装成自动评测结果。
2. 大 PDF 或大型 corpus 不要直接提交主仓库；优先提交 metadata、下载脚本和小 sample。
3. 评测问题必须能区分 LLM-only 与 RAG，不要设计常识题。
4. 输出报告不得包含 API key、绝对路径、个人隐私。
5. 文档、评测说明和展示问题尽量使用中文。

## 实施顺序

1. 选择目标新论文和 20-50 篇相关干扰论文的 metadata。
2. 准备 20-30 个 QA/evidence，覆盖专有概念、方法对比、指标、实验结果。
3. 设计至少 5 个现场稳定展示问题。
4. 实现 `run_eval.py` 的 mock/small 模式，输出 JSON/CSV/Markdown。
5. 三模式指标至少包含 correctness、citation_hit、groundedness、latency。

## 验收命令

```shell
python scripts/run_eval.py --modes all --limit 5
```

## PR 输出

PR 中必须写明：

- 数据集来源与体积。
- QA/evidence 格式。
- 5 个现场问题。
- 指标定义和小样例结果。
