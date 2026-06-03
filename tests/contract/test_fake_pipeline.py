"""! @file test_fake_pipeline.py
@brief 本地模拟适配器与 P0 冒烟流水线的契约测试。
"""

from rag_core.contracts import CONTRACT_VERSION, RagMode, RagRequest, SearchHit
from rag_core.pipeline import FakeRagPipeline
from rag_core.testing import MockChunker, MockDocumentParser, MockEmbedder, MockGenerator, NumpyFlatIndex


SAMPLE_TEXT = """Budget-Constrained Online Retrieval-Augmented Generation

UCOSA 解决 Chunk-as-a-Service 模型中的预算约束在线检索问题。

OB-CaaS 和 LB-CaaS 是论文中对比的两个预算感知变体。
"""


def test_fake_adapters_satisfy_contracts_and_score_descending():
    parser = MockDocumentParser()
    document = parser.parse_text(SAMPLE_TEXT, title="sample-paper")
    assert document.contract_version == CONTRACT_VERSION
    assert document.blocks

    chunks = MockChunker().chunk(document)
    assert chunks[0].doc_id == document.doc_id
    assert chunks[0].metadata["page_numbers"] == [1]

    embedder = MockEmbedder(dim=8)
    embeddings = embedder.embed(chunks)
    assert len(embeddings) == len(chunks)
    assert embeddings[0].dim == 8

    index = NumpyFlatIndex()
    index.upsert(chunks, embeddings)
    query_embedding = embedder.embed_query("UCOSA 解决了什么问题？")
    hits = index.search(query_embedding, top_k=2)
    assert all(isinstance(hit, SearchHit) for hit in hits)
    assert [hit.rank for hit in hits] == list(range(1, len(hits) + 1))
    assert hits == sorted(hits, key=lambda hit: hit.score, reverse=True)


def test_fake_pipeline_returns_grounded_rag_answer():
    request = RagRequest(query="UCOSA 解决了什么问题？", rag_mode=RagMode.BASIC_RAG, top_k=2)
    answer = FakeRagPipeline().answer_text(SAMPLE_TEXT, request, title="sample-paper")

    assert answer.contract_version == CONTRACT_VERSION
    assert "有证据支撑的模拟回答" in answer.answer_markdown
    assert answer.retrieved_hits
    assert answer.citations
    assert [stage.stage_name for stage in answer.trace] == ["parse", "chunk", "embed", "index", "search", "generate"]


def test_fake_pipeline_llm_only_skips_retrieval_and_warns():
    request = RagRequest(query="UCOSA 解决了什么问题？", rag_mode=RagMode.LLM_ONLY, top_k=2)
    answer = FakeRagPipeline(generator=MockGenerator()).answer_text(SAMPLE_TEXT, request, title="sample-paper")

    assert not answer.retrieved_hits
    assert not answer.citations
    assert "纯模型模式" in answer.warnings[0]
    assert "search" not in [stage.stage_name for stage in answer.trace]
