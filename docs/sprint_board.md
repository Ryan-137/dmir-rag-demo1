# RAG Demo 一周冲刺任务看板

v1.0 | 2026-06-03

## 本周目标

本周目标不是把所有想法都做完，而是确保结课展示可运行、可解释、可量化。

| 优先级 | 定义 | 本周必须做到什么 |
| --- | --- | --- |
| P0 | 系统可运行 | fake pipeline、Basic RAG、CI、固定 demo 数据必须可用 |
| P1 | 满足老师要求 | 新论文验证、API/local 模型、React 功能、PDF 解析、Chroma 索引、检索优化 |
| P2 | 展示质量 | trace、citation、benchmark、评测报告、对比表 |
| P3 | 扩展优化 | 更多模型、更多 OCR 方案、UI 美化、更多论文 |

## 每日节奏

| 时间 | 目标 | 负责人 | 验收/关卡 |
| --- | --- | --- | --- |
| D0：今天 | 冻结标准与任务 | `answerend42` | 合并 docs、Issue/PR 模板；开 8 个任务 issue |
| D1 | contracts + fake pipeline | `answerend42` | Pydantic models、Protocol、MockParser/MockEmbedder/NumpyFlat/MockGenerator；CI 跑 contract tests |
| D2 | 各模块 adapter 雏形 | 全员 | 每人只在自己目录提交 adapter skeleton + contract test + fixture |
| D3 | Basic RAG 端到端 | `answerend42` + 各模块负责人 | 上传 PDF -> 解析 -> chunk -> embedding -> Chroma -> search -> generate -> markdown 展示 |
| D4 | 优化与基准 | `KeeperHihi`, `cheng1608`, `Ryan-137` | Chroma HNSW profile benchmark；query rewrite/rerank/context packing；三模式评测脚本 |
| D5 | 数据与前端展示 | `Magicpjl`, `yourskenny`, `Ryan-137` | 论文数据集、QA/evidence、trace panel、eval dashboard，固定 5 个演示问题 |
| D6 | 锁定 demo | 全员 | 只修 bug 不扩功能；生成最终报告表；每人准备自己负责模块的 1 分钟说明 |
| D7：展示前 | 排练与兜底 | `answerend42` + 全员 | 录屏/截图/本地缓存模型与索引；准备 fallback 问题和离线结果 |

## 第一批 GitHub Issues

### 1. Freeze contracts and fake RAG pipeline

- Owner: `answerend42`
- ALLOWED_PATHS: `backend/rag_core/contracts/`, `backend/rag_core/testing/`, `backend/rag_core/pipeline/`, `tests/contract/`, `scripts/run_smoke_pipeline.py`, `docs/interfaces.md`
- 工作内容：新增 Pydantic models、Protocol、MockParser、MockEmbedder、NumpyFlat、MockGenerator 和 smoke pipeline。
- Definition of Done：`pytest tests/contract` 通过；`python scripts/run_smoke_pipeline.py --mode fake` 输出 `RagAnswer`；`docs/interfaces.md` 更新。
- 风险控制：不要依赖真实模型、真实 Chroma 或网络。

### 2. Chroma HNSW profiles and vector benchmark

- Owner: `KeeperHihi`
- ALLOWED_PATHS: `backend/rag_core/vector_indexes/`, `benchmarks/`, `tests/contract/`, `tests/unit/`
- 工作内容：实现 `chroma_hnsw_fast`、`chroma_hnsw_balanced`、`chroma_hnsw_high_recall`、`NumpyFlat` exact；统一 `SearchHit.score`。
- Definition of Done：`bench_chroma.py` 输出 `build_time`、p50/p95 latency、recall@3/5/10；与 NumpyFlat 对齐。
- 风险控制：不要声称 Chroma 支持 Milvus 式多算法；用 HNSW profile 表述。

### 3. Qwen embedding API/local adapters

- Owner: `irishibi`
- ALLOWED_PATHS: `backend/rag_core/embeddings/`, `tests/contract/`, `tests/unit/`, `scripts/compare_embeddings.py`
- 工作内容：实现 `QwenApiEmbedder`、`QwenLocalEmbedder`、`MockEmbedder`；支持批处理和维度记录。
- Definition of Done：contract test 验证向量数量、维度、metadata；`compare_embeddings.py` 可跑小数据。
- 风险控制：unit test 不调用真实 API；API key 只读环境变量。

### 4. Qwen LLM API/local and optimized generation

- Owner: `cheng1608`
- ALLOWED_PATHS: `backend/rag_core/llms/`, `backend/rag_core/retrieval/`, `backend/rag_core/generation/`, `tests/contract/`, `tests/unit/`
- 工作内容：实现 `QwenApiGenerator`、`QwenLocalGenerator`、query rewrite、grounded prompt、citation formatting。
- Definition of Done：同一 `RagRequest` 可切换 provider；输出 `answer_markdown` + `citations` + `warnings`。
- 风险控制：禁止把缺证据问题直接自由发挥；optimized mode 必须可拒答。

### 5. Research paper parser and chunker

- Owner: `Magicpjl`
- ALLOWED_PATHS: `backend/rag_core/parsers/`, `backend/rag_core/chunkers/`, `tests/contract/`, `tests/unit/`, `sample_data/`
- 工作内容：Parser 输出 `ParsedDocument`；新增 PDF->Markdown 路线、`research_paper_chunker`。
- Definition of Done：样例 PDF 能输出 markdown、blocks、chunks；chunk 保留 page/section/block_type。
- 风险控制：OCR/Docling 作为可选增强，不阻塞 Basic RAG。

### 6. Frontend trace/config/eval dashboard

- Owner: `yourskenny`
- ALLOWED_PATHS: `frontend/src/components/rag/`, `frontend/src/pages/`, `frontend/src/config/`, `frontend/src/**/*.test.*`
- 工作内容：新增 `MarkdownAnswer`、`RetrievalTracePanel`、`PipelineConfigPanel`、`EvaluationDashboard`。
- Definition of Done：`npm run build` 通过；可显示 retrieved_hits、citations、trace、三模式评测表。
- 风险控制：前端不得依赖后端私有文件结构，只读 `RagAnswer` schema。

### 7. QA/evidence dataset and evaluation report

- Owner: `Ryan-137`
- ALLOWED_PATHS: `eval/`, `scripts/run_eval.py`, `sample_data/`, `docs/`
- 工作内容：准备目标新论文、相关干扰论文、20-30 个 QA、evidence 标注。
- Definition of Done：`run_eval.py` 输出 JSON/CSV/Markdown；至少 5 个现场展示问题稳定。
- 风险控制：评测问题必须能区分 LLM-only 与 RAG，而不是常识问题。

### 8. Integration and demo lock

- Owner: `answerend42` + 全员
- ALLOWED_PATHS: `backend/`, `frontend/`, `scripts/`, `eval/`, `docs/`
- 工作内容：统一 `/rag/answer`；固定模型、数据、索引、问题；生成最终报告。
- Definition of Done：展示前 24 小时只修 bug；准备录屏、截图、离线结果 fallback。
- 风险控制：任何 P3 扩展不得影响主线 demo。

## 固定演示问题建议

| 问题类型 | 示例问题 | 期望现象 |
| --- | --- | --- |
| 专有概念 | UCOSA 在论文中解决了什么预算约束问题？ | LLM-only 易编造；RAG 应检索方法部分 |
| 方法对比 | OB-CaaS 与 LB-CaaS 的差别是什么？ | Basic RAG 能答定义；Optimized RAG 应给出更完整对比 |
| 评价指标 | NEP x AR 指标在论文中表示什么？ | 需要目标论文证据，不应凭常识猜 |
| 实验结果 | UCOSA 相比 random selection 和 offline selection 表现如何？ | Optimized RAG 应给出具体数字或相对结论 |
| 检索挑战 | 在一组相似 RAG 论文中，哪篇论文提出 Chunk-as-a-Service？ | 展示 corpus 中定位目标论文的能力 |
