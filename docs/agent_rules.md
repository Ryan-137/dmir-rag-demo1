# RAG Demo 工程协作与 AI Agent 约束规范

v1.0 | 2026-06-03 | 面向一周冲刺与结课展示

## 一句话规则

任何代码改动都必须能回答三个问题：

- 我改的是哪个 contract 的实现？
- 我只改了哪些允许路径？
- 我如何证明没有破坏其他模块？

## 路径所有权

| 路径 | Owner | 允许做什么 | 禁止做什么 |
| --- | --- | --- | --- |
| `backend/rag_core/contracts/` | `answerend42` | 定义 schema、Protocol、错误类型 | 未经 review 不得改字段语义、删除字段、改变 score 语义 |
| `backend/rag_core/parsers/` | `Magicpjl` | 实现 parser adapter 和 parser tests | 不得修改 embedding/index/generation 内部实现 |
| `backend/rag_core/embeddings/` | `irishibi` | 实现 API/local embedder | 不得把 API key 写进代码或日志 |
| `backend/rag_core/vector_indexes/` | `KeeperHihi` | 实现 Chroma/NumpyFlat/BM25 索引与 benchmark | 不得改变 `SearchHit` contract |
| `backend/rag_core/llms/`, `backend/rag_core/retrieval/` | `cheng1608` | 实现 LLM adapter、query rewrite、prompt、citation | 不得输出未受支持的引用格式 |
| `frontend/src/components/rag/` | `yourskenny` | 实现展示组件、配置和 dashboard | 不得绕开后端 contract 直接假设内部文件格式 |
| `eval/`, `scripts/run_eval.py` | `Ryan-137` | QA/evidence、评测指标与报告 | 不得把临场手工结果伪装成自动评测结果 |
| `.github/`, `docs/` | `answerend42` | CI、PR/Issue 模板、规范文档 | 不得降低 CI 门禁 |

## Contract 修改规则

- contract 版本采用 `CONTRACT_VERSION = "0.1.0"`，所有 `RagAnswer`/`ParsedDocument` 输出都包含版本。
- 模块内可以用内部数据结构，但跨模块输入输出必须是 Pydantic model 或 `model_dump()` 后的 schema。
- 新增字段必须有默认值或明确迁移方案；删除字段必须先经过 ADR。
- 所有 score 统一为“越大越相关”；distance、loss、rank score 等只能在 adapter 内转换。
- 所有跨层异常必须包装为项目错误类型，不能把底层库异常直接丢给前端。

最小 Protocol 示例：

```python
class VectorIndex(Protocol):
    name: str

    def upsert(self, chunks: list[Chunk], embeddings: list[EmbeddingVector]) -> None: ...
    def search(self, query_embedding: EmbeddingVector, top_k: int) -> list[SearchHit]: ...


class Generator(Protocol):
    name: str

    def generate(self, request: RagRequest, contexts: list[SearchHit]) -> RagAnswer: ...
```

## Doxygen 风格注释规范

- 文件：写 `@file`、`@brief`，必要时写 `@details`。
- 公共类：写 `@brief`、职责、状态和副作用。
- 公共函数：写 `@brief`、`@param`、`@return`、`@throws`。
- 复杂算法：用 `@details` 或短行内注释解释关键约束。
- 禁止注释废话、过期注释和逐行翻译。

## AI Agent 任务模板

任何成员使用 Claude Code、Codex、Cursor Agent 或其他工具时，必须把下面模板贴到任务开头，并在 PR 中确认没有越权改动。

```text
你正在为 RAG Demo 项目完成 GitHub Issue #<id>。

允许修改路径（ALLOWED_PATHS）：
- <path 1>
- <path 2>

硬性限制：
1. 不得修改 backend/rag_core/contracts/，除非本 issue 明要求。
2. 不得修改其他成员负责目录。
3. 不得删除现有功能、重命名公共接口、修改 CI 门禁。
4. 不得提交 API Key、模型权重、大型二进制文件、临时缓存。
5. 任何外部服务调用必须可 mock；unit test 不得依赖网络。
6. 完成后必须运行指定测试，并输出：修改文件列表、测试命令、风险点。

任务目标：<写清输入、输出、验收标准>
```

## Agent 禁止行为

| 禁止行为 | 处理方式 |
| --- | --- |
| 自动全仓重构、格式化所有文件 | 立即中止；只允许格式化自己改动的文件 |
| 为了通过测试而改 contract 或改测试断言 | 必须开独立 PR，由 `answerend42` review |
| 把 provider/model/API key 写死 | 改为 config/env；测试用 mock provider |
| 删除 fallback/mock | 禁止。fake pipeline 是项目兜底能力 |
| 生成不可解释的大量代码 | 拆成小 PR；每个 PR 必须有说明和测试 |

## 测试先行标准

真实模型、OCR 和大 benchmark 不进普通单元测试。

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
python scripts/run_smoke_pipeline.py --mode fake
cd frontend && npm run build
```

## 安全与数据规范

- API key 只允许存在于本地 `.env` 或 GitHub Secrets；不得写入源码、测试 fixture、日志、评测结果 JSON。
- PDF 和论文数据如果体积较大，不要直接提交到主仓库；可提交下载脚本、metadata 和小型 sample。
- 课程 QA 默认输入必须使用 `sample_data/course_qa_public.json`；`eval/labels/course_qa_quality_labels.json` 只允许评测脚本在生成完成后读取。
- `answer_quality` 禁止进入 RAG 索引、LLM prompt、retrieved hits、trace 和前端展示。
- 新论文 RAG 任务已经并入现有 Issue 的阶段 B；课程 QA 跑通后继续按原 Issue 推进论文 corpus、论文 QA/evidence 和最终评测。
- 生成结果、benchmark 结果允许作为 `eval/results/` 下的小 JSON/CSV 提交，但应去除密钥、绝对路径和个人信息。
- 本地模型权重、Chroma 数据目录、临时文件必须加入 `.gitignore`。
- 微信群聊导出只作为内部项目计划依据，正式展示材料不出现微信头像、wxid 等隐私字段。
