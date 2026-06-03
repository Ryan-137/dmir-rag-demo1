"""! @file __init__.py
@brief 契约测试与冒烟演示使用的模拟实现。
"""

from rag_core.testing.fakes import (
    MockChunker,
    MockDocumentParser,
    MockEmbedder,
    MockGenerator,
    NumpyFlatIndex,
)

__all__ = [
    "MockChunker",
    "MockDocumentParser",
    "MockEmbedder",
    "MockGenerator",
    "NumpyFlatIndex",
]
