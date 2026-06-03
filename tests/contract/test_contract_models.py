"""! @file test_contract_models.py
@brief 第一版冻结 RAG schema 的契约模型测试。
"""

import pytest
from pydantic import ValidationError

from rag_core.contracts import (
    CONTRACT_VERSION,
    BlockType,
    Chunk,
    Citation,
    ContentBlock,
    EmbeddingVector,
    ParsedDocument,
    RagAnswer,
    RagMode,
    RagRequest,
    SearchHit,
    StageTrace,
)


def test_parsed_document_and_answer_include_contract_version():
    block = ContentBlock(block_id="b1", block_type=BlockType.TEXT, text="hello", page_number=1)
    document = ParsedDocument(doc_id="doc1", title="Doc", markdown="hello", blocks=[block], parser_name="mock")
    assert document.contract_version == CONTRACT_VERSION
    assert document.model_dump(mode="json")["blocks"][0]["block_type"] == "text"

    hit = SearchHit(chunk_id="c1", doc_id="doc1", text="hello", score=0.9, rank=1, source="doc.md")
    citation = Citation(doc_id="doc1", chunk_id="c1", page_number=1, quote="hello", source="doc.md")
    answer = RagAnswer(answer_markdown="hello", citations=[citation], retrieved_hits=[hit])
    assert answer.contract_version == CONTRACT_VERSION
    assert answer.model_dump(mode="json")["citations"][0]["chunk_id"] == "c1"


def test_embedding_vector_dimension_is_checked():
    vector = EmbeddingVector(item_id="c1", vector=[0.1, 0.2], dim=2, model="mock", provider="mock")
    assert vector.dim == 2

    with pytest.raises(ValidationError):
        EmbeddingVector(item_id="bad", vector=[0.1, 0.2], dim=3, model="mock", provider="mock")


def test_request_chunk_hit_and_trace_validate_boundaries():
    request = RagRequest(query="什么是自然语言处理？", rag_mode=RagMode.BASIC_RAG, top_k=3)
    assert request.rag_mode == RagMode.BASIC_RAG

    chunk = Chunk(
        chunk_id="chunk1",
        doc_id="doc1",
        text="自然语言处理研究如何让机器处理、理解和生成自然语言。",
        source="course_qa_public.json",
        block_ids=["b1"],
        block_types=[BlockType.TEXT],
        token_count=4,
        metadata={"page_numbers": [1], "section_path": ["自然语言处理课程知识问答"]},
    )
    assert chunk.metadata["page_numbers"] == [1]

    hit = SearchHit(chunk_id=chunk.chunk_id, doc_id=chunk.doc_id, text=chunk.text, score=0.7, rank=1, source=chunk.source)
    assert hit.score > 0

    trace = StageTrace(stage_name="search", latency_ms=1.2, output_summary={"hits": 1})
    assert trace.output_summary["hits"] == 1

    with pytest.raises(ValidationError):
        RagRequest(query="", top_k=0)
