# Issue #5 Agent 指示：Research paper parser and chunker

你正在为 RAG Demo 项目完成 GitHub Issue #5。目标是增强研究论文解析和分块，让 parser 输出 `ParsedDocument`，chunker 保留 page/section/table/caption 元数据。

## Owner

`Magicpjl`

## 必读文档

- `docs/agent_rules.md`
- `docs/interfaces.md`
- `docs/agent_instructions/issue-01-answerend42/AGENTS.md`

## ALLOWED_PATHS

- `backend/rag_core/parsers/`
- `backend/rag_core/chunkers/`
- `tests/contract/`
- `tests/unit/`
- `sample_data/`
- `docs/agent_instructions/issue-05-Magicpjl/AGENTS.md`

## 硬性限制

1. 不得修改 embedding、index、generation 内部实现。
2. OCR/Docling 只能作为可选增强，不得阻塞 Basic RAG。
3. 输出必须对齐 `ParsedDocument`、`ContentBlock`、`Chunk` contract。
4. chunk metadata 必须尽量保留 `page_numbers`、`section_path`、`block_type`。
5. 代码注释必须使用中文 Doxygen 风格。

## 实施顺序

1. 读取 #1 的 `DocumentParser`、`Chunker` Protocol。
2. 第一阶段默认数据是 `sample_data/course_qa_public.json`，PDF/论文解析不得阻塞默认 QA 流水线。
3. 再实现 PDF->Markdown 或轻量 Markdown parser 的 skeleton。
4. 实现 `research_paper_chunker`，优先按 section/table/caption 保留结构。
5. 用小样例 PDF 或 Markdown fixture 写 contract tests。
6. 对复杂版式/OCR 标记可选路线，不作为普通 PR 的硬依赖。

## 验收命令

```shell
python -m compileall backend
pytest tests/contract tests/unit -m "not integration and not benchmark"
```

## PR 输出

PR 中必须写明：

- parser 方法与 fallback。
- 输出的 block 类型。
- chunk metadata 示例。
- 复杂 PDF/OCR 尚未覆盖的风险。
