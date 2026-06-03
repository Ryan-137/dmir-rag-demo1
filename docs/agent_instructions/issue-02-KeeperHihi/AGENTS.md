# Issue #2 Agent 指示：Chroma HNSW profiles and vector benchmark

你正在为 RAG Demo 项目完成 GitHub Issue #2。目标是实现 Chroma HNSW 参数配置和 NumpyFlat 精确基线，并给出可复现的向量检索 benchmark。

## Owner

`KeeperHihi`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `backend/rag_core/vector_indexes/`
- `benchmarks/`
- `tests/contract/`
- `tests/unit/`
- `docs/agent_instructions/issue-02-KeeperHihi/AGENTS.md`

## 硬性限制

1. 不得修改 `backend/rag_core/contracts/`，除非 Issue 明确要求并由 `answerend42` review。
2. 不得改变 `SearchHit` 字段语义；`score` 必须越大越相关。
3. 不得声称 Chroma 支持 Milvus 式多算法；只能表述为 HNSW profiles。
4. benchmark 可以本地/手动运行，不要阻塞普通单元测试。
5. 代码注释必须使用中文 Doxygen 风格。

## 实施顺序

1. 读取 #1 的 `VectorIndex` Protocol 和 `SearchHit` contract。
2. 实现 `NumpyFlat` exact baseline，用作 recall 上界。
3. 实现 `chroma_hnsw_fast`、`chroma_hnsw_balanced`、`chroma_hnsw_high_recall` 配置。
4. 编写 score conversion 测试，确保 Chroma distance 在 adapter 内转成“越大越相关”。
5. 编写 `bench_chroma.py`，输出 build_time、p50/p95 latency、recall@3/5/10。

## 验收命令

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
python benchmarks/bench_chroma.py --profile all
```

## PR 输出

PR 中必须写明：

- 每个 HNSW profile 的参数。
- NumpyFlat baseline 的用途。
- benchmark 小数据结果。
- 没有跑真实大 benchmark 时的原因。
