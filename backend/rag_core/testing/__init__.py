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
from rag_core.testing.qa_dataset import (
    DEFAULT_COURSE_QA_PATH,
    COURSE_QA_LABELS_PATH,
    CourseQaCandidate,
    build_course_qa_document,
    default_course_qa_query,
    load_course_qa_candidates,
    load_course_qa_quality_labels,
    summarize_course_qa,
)

__all__ = [
    "DEFAULT_COURSE_QA_PATH",
    "COURSE_QA_LABELS_PATH",
    "CourseQaCandidate",
    "MockChunker",
    "MockDocumentParser",
    "MockEmbedder",
    "MockGenerator",
    "NumpyFlatIndex",
    "build_course_qa_document",
    "default_course_qa_query",
    "load_course_qa_candidates",
    "load_course_qa_quality_labels",
    "summarize_course_qa",
]
