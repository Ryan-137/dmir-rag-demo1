# Issue #4 Agent 指示：Qwen LLM API/local and optimized generation

你正在为 RAG Demo 项目完成 GitHub Issue #4。目标是实现 Qwen LLM API/local adapter，并补 query rewrite、grounded prompt、citation formatting 和缺证据拒答。

## Owner

`cheng1608`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `backend/rag_core/llms/`
- `backend/rag_core/retrieval/`
- `backend/rag_core/generation/`
- `tests/contract/`
- `tests/unit/`
- `docs/agent_instructions/issue-04-cheng1608/AGENTS.md`

## 硬性限制

1. 不得在缺少证据时自由发挥；optimized mode 必须可以拒答。
2. prompt 必须尽量使用中文，要求模型输出中文 Markdown。
3. citation 格式必须来自 `RagAnswer.citations`，不得自造前端私有格式。
4. 单元测试不得依赖真实 API、网络或模型下载。
5. 代码注释必须使用中文 Doxygen 风格。
6. 第一阶段 prompt 只允许使用 `sample_data/course_qa_public.json` 检索到的证据；不得读取 `answer_quality` 标签。
7. prompt 和 context packing 必须同时适配课程 QA 证据与后续论文证据，论文阶段不另开新的生成 Issue。

## 实施顺序

1. 读取 #1 的 `Generator` Protocol、`RagRequest`、`RagAnswer`、`Citation` contract。
2. 实现中文 grounded prompt：要求模型只基于课程 QA 检索证据回答，并在缺证据时拒答。
3. 实现 `QwenApiGenerator` 和 `QwenLocalGenerator` 的 adapter skeleton。
4. 实现 query rewrite、context packing、citation formatting 的纯函数，并为它们写 unit tests。
5. 使用 mock provider 测试 `answer_markdown`、`citations`、`warnings`、`trace`。
6. 为阶段 B 预留论文证据格式处理，支持 page、section、table、caption metadata 进入引用和回答约束。

## 验收命令

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
```

## PR 输出

PR 中必须写明：

- 中文 prompt 内容或 prompt 模板位置。
- 缺证据拒答策略。
- API/local/mock provider 切换方式。
- citation 输出示例。
- 课程 QA 证据与论文证据共用 prompt 模板的方式。
