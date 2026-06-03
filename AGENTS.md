# RAG Demo Agent 全局指示

本仓库采用 contract-first 协作方式。任何 Codex、Claude Code、Cursor Agent 或其他代码 Agent 开工前，必须先读本文件，再读对应 Issue 的 `docs/agent_instructions/.../AGENTS.md`。

## 全局硬性规则

1. 只修改 Issue 指定的 `ALLOWED_PATHS`。
2. 不得修改 `backend/rag_core/contracts/`，除非 Issue 明确要求。
3. 不得删除 fake/mock fallback。
4. 不得提交 API key、模型权重、大型二进制文件、临时缓存。
5. 单元测试不得依赖真实网络、真实 API、真实模型下载。
6. 代码注释必须使用中文 Doxygen 风格。
7. 面向 LLM 的 prompt、mock 输出、展示文案尽量使用中文。
8. `SearchHit.score` 必须越大越相关。
9. 第一阶段默认测试数据是 `sample_data/course_qa_public.json`。
10. `answer_quality` 档次只允许评测脚本读取，禁止进入 RAG 索引、prompt、trace 或前端展示。
11. 新论文 RAG 任务已经并入现有 Issue 的阶段 B；不要等课程 QA 完成后再要求新开 Issue。

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/contribution.md`
- `docs/sprint_board.md`
- `docs/agent_instructions/README.md`
- `sample_data/course_qa_public.json`

## P0 验收命令

```shell
python -m compileall backend/rag_core scripts/run_smoke_pipeline.py
pytest tests/contract
python scripts/run_smoke_pipeline.py --mode fake --pretty
```

## PR 输出要求

PR 必须写清：

- 修改文件列表。
- 测试命令和结果。
- 是否修改契约。
- 风险点和 fallback。
- 使用 Agent 时是否严格遵守 `ALLOWED_PATHS`。
