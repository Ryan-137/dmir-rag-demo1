"""! @file __init__.py
@brief RAG 核心模块的公开契约导出。
"""

from rag_core.contracts.enums import BlockType, EmbeddingProvider, IndexBackend, ParserType, RagMode
from rag_core.contracts.errors import (
    ContractViolation,
    EmptyCorpus,
    ProviderUnavailable,
    RagCoreError,
    VectorDimensionMismatch,
)
from rag_core.contracts.models import (
    CONTRACT_VERSION,
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
from rag_core.contracts.protocols import Chunker, DocumentParser, Embedder, Generator, VectorIndex

__all__ = [
    "CONTRACT_VERSION",
    "BlockType",
    "Chunk",
    "Chunker",
    "Citation",
    "ContentBlock",
    "ContractViolation",
    "DocumentParser",
    "Embedder",
    "EmbeddingProvider",
    "EmbeddingVector",
    "EmptyCorpus",
    "Generator",
    "IndexBackend",
    "ParsedDocument",
    "ParserType",
    "ProviderUnavailable",
    "RagAnswer",
    "RagCoreError",
    "RagMode",
    "RagRequest",
    "SearchHit",
    "StageTrace",
    "VectorDimensionMismatch",
    "VectorIndex",
]
