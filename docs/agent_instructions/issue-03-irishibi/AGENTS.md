# Issue #3 Agent 指示：Qwen embedding API/local adapters

你正在为 RAG Demo 项目完成 GitHub Issue #3。目标是实现 Qwen embedding 的 API 和本地 adapter，并与 `EmbeddingVector` contract 对齐。

## Owner

`irishibi`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `backend/rag_core/embeddings/`
- `tests/contract/`
- `tests/unit/`
- `scripts/compare_embeddings.py`
- `docs/agent_instructions/issue-03-irishibi/AGENTS.md`

## 硬性限制

1. 单元测试不得调用真实 API、下载真实模型或访问网络。
2. API key 只能从环境变量读取，禁止写入源码、日志、fixture、结果文件。
3. 输出必须是 `EmbeddingVector` 或其序列化结果。
4. `EmbeddingVector.dim` 必须等于实际向量长度。
5. 代码注释必须使用中文 Doxygen 风格。
6. 面向 LLM 或展示的说明文本尽量使用中文。
7. 第一阶段默认输入是 `sample_data/course_qa_public.json`；不得读取 `answer_quality` 标签。

## 实施顺序

1. 读取 #1 的 `Embedder` Protocol 和 `EmbeddingVector` contract。
2. 实现 `MockEmbedder` 或复用 P0 fake embedder 作为测试兜底。
3. 实现 `QwenApiEmbedder`，只从环境变量读取 key。
4. 实现 `QwenLocalEmbedder`，模型不可用时抛出项目级 provider 异常。
5. 用课程 QA public 候选答案增加 contract tests，验证数量、维度、provider、model、metadata。
6. 编写 `scripts/compare_embeddings.py --mode mock`，真实模式作为可选 integration。

## 验收命令

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
python scripts/compare_embeddings.py --mode mock
```

## PR 输出

PR 中必须写明：

- API/local/mock 三种路径的差异。
- 是否需要环境变量。
- 测试是否完全离线。
- 真实 API 或本地模型没有跑通时的 fallback。
