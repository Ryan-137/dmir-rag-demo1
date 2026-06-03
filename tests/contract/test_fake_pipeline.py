"""! @file test_fake_pipeline.py
@brief 本地模拟适配器与 P0 冒烟流水线的契约测试。
"""

from rag_core.contracts import CONTRACT_VERSION, RagMode, RagRequest, SearchHit
from rag_core.pipeline import FakeRagPipeline
from rag_core.testing import (
    DEFAULT_COURSE_QA_PATH,
    MockChunker,
    MockDocumentParser,
    MockEmbedder,
    MockGenerator,
    NumpyFlatIndex,
    build_course_qa_document,
    default_course_qa_query,
    load_course_qa_candidates,
    load_course_qa_quality_labels,
)


SAMPLE_TEXT = """机器学习核心问答

问题：什么是机器学习？
候选答案：机器学习是让计算机系统从数据中学习规律，并用模型对未知样本进行预测、分类或决策的方法。

问题：监督学习和无监督学习有什么区别？
候选答案：监督学习使用带标签数据学习输入到输出的映射，无监督学习在无标签数据中发现结构或分组。
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
    query_embedding = embedder.embed_query("什么是机器学习？")
    hits = index.search(query_embedding, top_k=2)
    assert all(isinstance(hit, SearchHit) for hit in hits)
    assert [hit.rank for hit in hits] == list(range(1, len(hits) + 1))
    assert hits == sorted(hits, key=lambda hit: hit.score, reverse=True)


def test_fake_pipeline_returns_grounded_rag_answer():
    request = RagRequest(query="什么是机器学习？", rag_mode=RagMode.BASIC_RAG, top_k=2)
    answer = FakeRagPipeline().answer_text(SAMPLE_TEXT, request, title="sample-paper")

    assert answer.contract_version == CONTRACT_VERSION
    assert "有证据支撑的模拟回答" in answer.answer_markdown
    assert answer.retrieved_hits
    assert answer.citations
    assert [stage.stage_name for stage in answer.trace] == ["parse", "chunk", "embed", "index", "search", "generate"]


def test_fake_pipeline_llm_only_skips_retrieval_and_warns():
    request = RagRequest(query="什么是机器学习？", rag_mode=RagMode.LLM_ONLY, top_k=2)
    answer = FakeRagPipeline(generator=MockGenerator()).answer_text(SAMPLE_TEXT, request, title="sample-paper")

    assert not answer.retrieved_hits
    assert not answer.citations
    assert "纯模型模式" in answer.warnings[0]
    assert "search" not in [stage.stage_name for stage in answer.trace]


def test_course_qa_dataset_is_default_smoke_input():
    candidates = load_course_qa_candidates(DEFAULT_COURSE_QA_PATH, max_questions=5)
    assert candidates[0].question == "什么是自然语言处理？"
    assert not hasattr(candidates[0], "answer_quality")

    document = build_course_qa_document(candidates)
    assert document.metadata["dataset_type"] == "course_qa_public"
    assert document.blocks[0].metadata["category"] == "自然语言处理课程知识问答"
    assert "answer_quality" not in document.model_dump_json()

    request = RagRequest(query=default_course_qa_query(candidates), rag_mode=RagMode.BASIC_RAG, top_k=2)
    answer = FakeRagPipeline().answer_document(document, request)

    assert answer.retrieved_hits
    assert answer.citations
    assert answer.retrieved_hits[0].metadata["question"]
    assert "answer_quality" not in answer.model_dump_json()


def test_course_qa_quality_labels_are_eval_only():
    candidates = load_course_qa_candidates(DEFAULT_COURSE_QA_PATH, max_questions=1)
    labels = load_course_qa_quality_labels()

    assert candidates[0].answer_id in labels
    assert "answer_quality" not in candidates[0].__dict__
