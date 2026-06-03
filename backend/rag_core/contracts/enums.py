"""! @file enums.py
@brief RAG 核心契约共享的枚举值。
"""

from enum import Enum


class BlockType(str, Enum):
    """! @brief 解析器输出的半结构化内容类别。"""

    TEXT = "text"
    TITLE = "title"
    TABLE = "table"
    FIGURE = "figure"
    FORMULA = "formula"
    CAPTION = "caption"


class ParserType(str, Enum):
    """! @brief 契约层支持的解析器类型。"""

    MOCK = "mock"
    PYMUPDF = "pymupdf"
    PYPDF = "pypdf"
    PDFPLUMBER = "pdfplumber"
    MARKDOWN = "markdown"
    OCR = "ocr"


class EmbeddingProvider(str, Enum):
    """! @brief 暴露给调用方的嵌入服务提供方标识。"""

    MOCK = "mock"
    OPENAI = "openai"
    QWEN_API = "qwen_api"
    QWEN_LOCAL = "qwen_local"
    HUGGINGFACE = "huggingface"


class IndexBackend(str, Enum):
    """! @brief 向量索引后端与 benchmark 基线。"""

    MOCK_NUMPY_FLAT = "mock_numpy_flat"
    NUMPY_FLAT = "numpy_flat"
    CHROMA_HNSW_FAST = "chroma_hnsw_fast"
    CHROMA_HNSW_BALANCED = "chroma_hnsw_balanced"
    CHROMA_HNSW_HIGH_RECALL = "chroma_hnsw_high_recall"


class RagMode(str, Enum):
    """! @brief 结课展示使用的问答模式。"""

    LLM_ONLY = "llm_only"
    BASIC_RAG = "basic_rag"
    OPTIMIZED_RAG = "optimized_rag"
