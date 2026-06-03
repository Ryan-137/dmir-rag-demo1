# Issue #1 Agent 指示：Freeze contracts and fake RAG pipeline

你正在为 RAG Demo 项目完成 GitHub Issue #1。目标是冻结第一版契约，并提供本地可跑的 fake pipeline，让其他成员可以按同一接口并行开发。

## Owner

`answerend42`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/sprint_board.md`

## ALLOWED_PATHS

- `backend/rag_core/contracts/`
- `backend/rag_core/testing/`
- `backend/rag_core/pipeline/`
- `tests/contract/`
- `scripts/run_smoke_pipeline.py`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## 硬性限制

1. 不得依赖真实模型、真实 Chroma、真实 API 或网络。
2. 不得删除 fake/mock fallback。
3. 跨模块数据必须使用 Pydantic model 或其序列化结果。
4. `SearchHit.score` 必须越大越相关。
5. 代码注释必须使用中文 Doxygen 风格。
6. 面向 LLM 或展示的 prompt/回答模板尽量使用中文。

## 实施顺序

1. 定义 `ParsedDocument`、`ContentBlock`、`Chunk`、`EmbeddingVector`、`SearchHit`、`RagRequest`、`RagAnswer`、`StageTrace`。
2. 定义 `DocumentParser`、`Chunker`、`Embedder`、`VectorIndex`、`Generator` Protocol。
3. 实现 `MockDocumentParser`、`MockChunker`、`MockEmbedder`、`NumpyFlatIndex`、`MockGenerator`。
4. 实现 `FakeRagPipeline` 串联 parse/chunk/embed/index/search/generate。
5. 实现 `scripts/run_smoke_pipeline.py --mode fake`。
6. 增加 `tests/contract`，保证 fake pipeline 输出 `RagAnswer`。

## 验收命令

```shell
python -m compileall backend/rag_core scripts/run_smoke_pipeline.py
pytest tests/contract
python scripts/run_smoke_pipeline.py --mode fake --pretty
```

## PR 输出

PR 中必须写明：

- 修改文件列表。
- 上述测试命令及结果。
- 当前 contract 版本。
- 还没有覆盖的真实 adapter 风险。
