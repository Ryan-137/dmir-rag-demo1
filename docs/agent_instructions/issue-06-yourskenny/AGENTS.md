# Issue #6 Agent 指示：Frontend trace/config/eval dashboard

你正在为 RAG Demo 项目完成 GitHub Issue #6。目标是在现有 React/Vite 前端里展示 Markdown 答案、检索证据、trace、配置面板和三模式评测表。

## Owner

`yourskenny`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `frontend/src/components/rag/`
- `frontend/src/pages/`
- `frontend/src/config/`
- `frontend/src/**/*.test.*`
- `docs/agent_instructions/issue-06-yourskenny/AGENTS.md`

## 硬性限制

1. 前端只能读取 `RagAnswer` schema，不得依赖后端私有临时文件结构。
2. 不要重写全站，优先扩展现有页面和组件。
3. 文案尽量中文，展示字段名可以保留必要英文术语。
4. 涉及前端改动必须通过 `npm run build`。

## 实施顺序

1. 读取 `docs/interfaces.md` 中的 `RagAnswer`、`SearchHit`、`Citation`、`StageTrace` 字段。
2. 新增 `MarkdownAnswer`，展示 `answer_markdown` 和 warnings。
3. 新增 `RetrievalTracePanel`，展示 `retrieved_hits`、score、rank、source。
4. 新增 `PipelineConfigPanel`，配置 rag_mode、top_k、provider/model。
5. 新增 `EvaluationDashboard`，展示 LLM-only / Basic RAG / Optimized RAG 三模式指标。
6. 使用 mock `RagAnswer` 做前端渲染验证。

## 验收命令

```shell
cd frontend
npm run build
```

## PR 输出

PR 中必须写明：

- 新增组件列表。
- mock `RagAnswer` 示例或截图。
- 是否需要后端新增字段。
- build 结果。
