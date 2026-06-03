# Issue #7 Agent 指示：Course QA evaluation report

你正在为 RAG Demo 项目完成 GitHub Issue #7。第一阶段目标不是找新论文，而是基于老师要求的课程 QA 数据实现三模式评测报告。

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
2. RAG 默认输入只能使用 `sample_data/course_qa_public.json`。
3. `answer_quality` 只能从 `eval/labels/course_qa_quality_labels.json` 在生成后读取，禁止进入索引、prompt、trace 或前端展示。
4. 输出报告不得包含 API key、绝对路径、个人隐私。
5. 文档、评测说明和展示问题尽量使用中文。
6. 新论文和干扰论文属于后续扩展，本 Issue 第一阶段不要求寻找论文。

## 实施顺序

1. 读取 `sample_data/course_qa_public.json` 作为系统可见输入。
2. 读取 `eval/labels/course_qa_quality_labels.json` 作为评测专用隐藏标签。
3. 设计至少 5 个课程 QA 现场稳定展示问题。
4. 实现 `run_eval.py` 的 mock/small 模式，输出 JSON/CSV/Markdown。
5. 三模式指标至少包含 citation_hit、label_distribution、groundedness、latency。
6. 写测试确认 `answer_quality` 不会出现在 RAG 请求、检索命中、trace 或前端展示数据中。

## 验收命令

```shell
python scripts/run_eval.py --modes all --limit 5
```

## PR 输出

PR 中必须写明：

- 课程 QA public 输入与隐藏 labels 的隔离方式。
- 评测 JSON/CSV/Markdown 格式。
- 5 个现场问题。
- 指标定义和小样例结果。
