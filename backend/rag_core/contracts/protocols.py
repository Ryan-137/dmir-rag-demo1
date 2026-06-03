"""! @file protocols.py
@brief 每个真实 adapter 必须满足的 Protocol 定义。
"""

from __future__ import annotations

from typing import Protocol

from rag_core.contracts.models import Chunk, EmbeddingVector, ParsedDocument, RagAnswer, RagRequest, SearchHit


class DocumentParser(Protocol):
    """! @brief 将文件转换为 ParsedDocument。"""

    name: str

    def parse(self, file_path: str) -> ParsedDocument:
        """! @brief 将文件路径解析为满足契约的文档。"""


class Chunker(Protocol):
    """! @brief 将 ParsedDocument 转换为可检索 chunks。"""

    name: str

    def chunk(self, document: ParsedDocument) -> list[Chunk]:
        """! @brief 将已解析文档切分为稳定 chunks。"""


class Embedder(Protocol):
    """! @brief 为文本块和查询生成嵌入向量。"""

    name: str

    def embed(self, chunks: list[Chunk]) -> list[EmbeddingVector]:
        """! @brief 按输入顺序为文本块生成嵌入向量。"""

    def embed_query(self, query: str) -> EmbeddingVector:
        """! @brief 为用户查询生成检索向量。"""


class VectorIndex(Protocol):
    """! @brief 存储并检索文本块嵌入向量。"""

    name: str

    def upsert(self, chunks: list[Chunk], embeddings: list[EmbeddingVector]) -> None:
        """! @brief 新增或更新文本块嵌入向量。"""

    def search(self, query_embedding: EmbeddingVector, top_k: int) -> list[SearchHit]:
        """! @brief 返回按相关性 score 降序排列的 top-k 命中。"""


class Generator(Protocol):
    """! @brief 基于请求和 contexts 生成最终 RagAnswer。"""

    name: str

    def generate(self, request: RagRequest, contexts: list[SearchHit]) -> RagAnswer:
        """! @brief 生成有证据支撑的 Markdown、引用、警告和追踪记录。"""
