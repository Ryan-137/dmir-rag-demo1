"""! @file fakes.py
@brief 满足契约的模拟适配器，用于测试和演示兜底。
@details 这些实现具备确定性、只在本地运行，并刻意保持小而清晰。
即使真实服务提供方或模型不可用，它们也必须保留。
"""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

from rag_core.contracts.enums import BlockType, RagMode
from rag_core.contracts.errors import EmptyCorpus, VectorDimensionMismatch
from rag_core.contracts.models import (
    Chunk,
    Citation,
    ContentBlock,
    EmbeddingVector,
    ParsedDocument,
    RagAnswer,
    RagRequest,
    SearchHit,
    StageTrace,
)

_TOKEN_PATTERN = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def stable_id(prefix: str, *parts: object, length: int = 12) -> str:
    """! @brief 基于确定性内容生成稳定短 ID。"""
    digest = hashlib.sha1("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:length]}"


def tokenize(text: str) -> list[str]:
    """! @brief 为模拟打分切分英文、数字和中文片段。"""
    return [token.lower() for token in _TOKEN_PATTERN.findall(text)]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """! @brief 在不依赖外部数值库的情况下计算余弦相似度。"""
    if len(left) != len(right):
        raise VectorDimensionMismatch("Vectors must have the same dimension")
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class MockDocumentParser:
    """! @brief 将纯文本视为 Markdown 内容块的确定性解析器。"""

    name = "mock-parser"

    def parse(self, file_path: str) -> ParsedDocument:
        """! @brief 将 UTF-8 文本或 Markdown 文件解析为 ParsedDocument。"""
        path = Path(file_path)
        text = path.read_text(encoding="utf-8") if path.exists() else file_path
        title = path.stem if path.exists() else "mock-document"
        return self.parse_text(text=text, title=title, source=str(path))

    def parse_text(self, text: str, title: str = "mock-document", source: str = "memory") -> ParsedDocument:
        """! @brief 将内存文本解析为稳定的 title/text blocks。"""
        clean_text = text.strip()
        if not clean_text:
            raise EmptyCorpus("MockDocumentParser received empty text")

        doc_id = stable_id("doc", title, clean_text)
        blocks: list[ContentBlock] = []
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", clean_text) if part.strip()]
        for index, paragraph in enumerate(paragraphs, start=1):
            block_type = BlockType.TITLE if index == 1 and len(paragraph) <= 120 else BlockType.TEXT
            blocks.append(
                ContentBlock(
                    block_id=stable_id("block", doc_id, index, paragraph),
                    block_type=block_type,
                    text=paragraph,
                    page_number=1,
                    metadata={"source": source, "paragraph_index": index},
                )
            )

        return ParsedDocument(
            doc_id=doc_id,
            title=title,
            markdown=clean_text,
            blocks=blocks,
            parser_name=self.name,
            metadata={"source": source, "block_count": len(blocks)},
        )


class MockChunker:
    """! @brief 用于可预测契约测试的一内容块一文本块分块器。"""

    name = "mock-chunker"

    def chunk(self, document: ParsedDocument) -> list[Chunk]:
        """! @brief 将每个非空内容 block 转换为一个 Chunk。"""
        chunks: list[Chunk] = []
        for index, block in enumerate(document.blocks, start=1):
            text = block.text.strip()
            if not text:
                continue
            metadata = dict(block.metadata)
            metadata.update(
                {
                    "page_numbers": [block.page_number] if block.page_number else [],
                    "section_path": [document.title] if document.title else [],
                    "block_type": block.block_type.value,
                    "parser_name": document.parser_name,
                }
            )
            chunks.append(
                Chunk(
                    chunk_id=stable_id("chunk", document.doc_id, block.block_id, index),
                    doc_id=document.doc_id,
                    text=text,
                    source=document.metadata.get("source", document.title or document.doc_id),
                    block_ids=[block.block_id],
                    block_types=[block.block_type],
                    token_count=max(1, len(tokenize(text))),
                    metadata=metadata,
                )
            )
        if not chunks:
            raise EmptyCorpus("MockChunker produced no chunks")
        return chunks


class MockEmbedder:
    """! @brief 通过 hashing 生成确定性本地向量的 embedder。"""

    name = "mock-embedder"

    def __init__(self, dim: int = 16, model: str = "mock-hashing-embedder"):
        if dim <= 0:
            raise ValueError("dim must be positive")
        self.dim = dim
        self.model = model

    def embed(self, chunks: list[Chunk]) -> list[EmbeddingVector]:
        """! @brief 按输入顺序为文本块生成嵌入向量。"""
        return [
            EmbeddingVector(
                item_id=chunk.chunk_id,
                vector=self._embed_text(chunk.text),
                dim=self.dim,
                model=self.model,
                provider="mock",
                metadata={"doc_id": chunk.doc_id, "source": chunk.source},
            )
            for chunk in chunks
        ]

    def embed_query(self, query: str) -> EmbeddingVector:
        """! @brief 使用与文本块相同的 hashing 空间为查询生成向量。"""
        return EmbeddingVector(
            item_id=stable_id("query", query),
            vector=self._embed_text(query),
            dim=self.dim,
            model=self.model,
            provider="mock",
            metadata={"query": query},
        )

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in tokenize(text):
            digest = hashlib.sha1(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], byteorder="big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class NumpyFlatIndex:
    """! @brief 作为模拟检索基线的精确内存向量索引。"""

    name = "mock-numpy-flat"

    def __init__(self):
        self._chunks: dict[str, Chunk] = {}
        self._embeddings: dict[str, EmbeddingVector] = {}
        self._dim: int | None = None

    def upsert(self, chunks: list[Chunk], embeddings: list[EmbeddingVector]) -> None:
        """! @brief 存储文本块和嵌入向量，并强制一个文本块对应一个向量。"""
        if not chunks:
            raise EmptyCorpus("NumpyFlatIndex received no chunks")
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")

        for chunk, embedding in zip(chunks, embeddings):
            if chunk.chunk_id != embedding.item_id:
                raise ValueError("Embedding item_id must match Chunk chunk_id")
            if self._dim is None:
                self._dim = embedding.dim
            elif self._dim != embedding.dim:
                raise VectorDimensionMismatch("All indexed embeddings must share one dimension")
            self._chunks[chunk.chunk_id] = chunk
            self._embeddings[embedding.item_id] = embedding

    def search(self, query_embedding: EmbeddingVector, top_k: int) -> list[SearchHit]:
        """! @brief 按精确余弦相似度检索，并按 score 降序返回。"""
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if not self._embeddings:
            raise EmptyCorpus("NumpyFlatIndex has no embeddings")
        if self._dim != query_embedding.dim:
            raise VectorDimensionMismatch("Query dimension does not match index dimension")

        query_text = str(query_embedding.metadata.get("query", "")).strip()
        scored = []
        for chunk_id, embedding in self._embeddings.items():
            chunk = self._chunks[chunk_id]
            lexical_bonus = 1.0 if query_text and query_text in chunk.text else 0.0
            scored.append((cosine_similarity(query_embedding.vector, embedding.vector) + lexical_bonus, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)

        hits: list[SearchHit] = []
        for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
            hits.append(
                SearchHit(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    text=chunk.text,
                    score=score,
                    rank=rank,
                    source=chunk.source,
                    metadata=chunk.metadata,
                )
            )
        return hits


class MockGenerator:
    """! @brief 会引用检索命中文本块的有证据支撑模拟生成器。"""

    name = "mock-generator"

    def generate(self, request: RagRequest, contexts: list[SearchHit]) -> RagAnswer:
        """! @brief 根据检索上下文生成确定性 Markdown 回答。"""
        warnings: list[str] = []
        citations: list[Citation] = []

        if request.rag_mode == RagMode.LLM_ONLY:
            answer = "## 纯模型模拟回答\n\n该模式刻意不使用检索证据，因此无法核验课程 QA 参考证据。"
            warnings.append("纯模型模式没有检索证据")
        elif not contexts:
            answer = "## 无法生成有证据支撑的回答\n\n没有检索到相关证据，因此模拟生成器拒绝回答。"
            warnings.append("没有检索上下文")
        else:
            bullets = []
            for hit in contexts:
                page_numbers = hit.metadata.get("page_numbers") or []
                page_number = page_numbers[0] if page_numbers else None
                section_path = hit.metadata.get("section_path") or []
                citations.append(
                    Citation(
                        doc_id=hit.doc_id,
                        chunk_id=hit.chunk_id,
                        page_number=page_number,
                        section_path=section_path,
                        quote=hit.text[:240],
                        source=hit.source,
                    )
                )
                bullets.append(f"- 排名 {hit.rank}，相关性 {hit.score:.3f}：{hit.text}")
            answer = "## 有证据支撑的模拟回答\n\n" + "\n".join(bullets)

        return RagAnswer(
            answer_markdown=answer,
            citations=citations if request.require_citations else [],
            retrieved_hits=contexts,
            warnings=warnings,
            trace=[
                StageTrace(
                    stage_name="generate",
                    latency_ms=0.0,
                    input_summary={"query": request.query, "context_count": len(contexts)},
                    output_summary={"citation_count": len(citations), "warning_count": len(warnings)},
                )
            ],
            metadata={"generator": self.name, "rag_mode": request.rag_mode.value},
        )
