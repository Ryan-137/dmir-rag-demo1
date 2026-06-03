"""! @file orchestrator.py
@brief 用于 P0 冒烟验证的模拟 RAG 流水线编排。
"""

from __future__ import annotations

from time import perf_counter

from rag_core.contracts.enums import RagMode
from rag_core.contracts.models import ParsedDocument, RagAnswer, RagRequest, StageTrace
from rag_core.testing.fakes import MockChunker, MockDocumentParser, MockEmbedder, MockGenerator, NumpyFlatIndex


class FakeRagPipeline:
    """! @brief 使用模拟适配器的本地契约合规流水线。"""

    def __init__(
        self,
        parser: MockDocumentParser | None = None,
        chunker: MockChunker | None = None,
        embedder: MockEmbedder | None = None,
        index: NumpyFlatIndex | None = None,
        generator: MockGenerator | None = None,
    ):
        self.parser = parser or MockDocumentParser()
        self.chunker = chunker or MockChunker()
        self.embedder = embedder or MockEmbedder()
        self.index = index or NumpyFlatIndex()
        self.generator = generator or MockGenerator()

    def answer_text(self, document_text: str, request: RagRequest, title: str = "mock-paper") -> RagAnswer:
        """! @brief 解析内存文本，并通过模拟 RAG 回答请求。"""
        traces: list[StageTrace] = []

        start = perf_counter()
        document = self.parser.parse_text(document_text, title=title)
        traces.append(
            self._trace(
                "parse",
                start,
                {"title": title, "chars": len(document_text)},
                {"doc_id": document.doc_id, "blocks": len(document.blocks)},
            )
        )
        return self.answer_document(document, request, traces)

    def answer_document(
        self,
        document: ParsedDocument,
        request: RagRequest,
        prior_trace: list[StageTrace] | None = None,
    ) -> RagAnswer:
        """! @brief 基于已解析文档回答请求。"""
        traces = list(prior_trace or [])

        start = perf_counter()
        chunks = self.chunker.chunk(document)
        traces.append(
            self._trace(
                "chunk",
                start,
                {"doc_id": document.doc_id, "blocks": len(document.blocks)},
                {"chunks": len(chunks)},
            )
        )

        start = perf_counter()
        embeddings = self.embedder.embed(chunks)
        traces.append(
            self._trace(
                "embed",
                start,
                {"chunks": len(chunks)},
                {"embeddings": len(embeddings), "dim": embeddings[0].dim if embeddings else None},
            )
        )

        start = perf_counter()
        self.index.upsert(chunks, embeddings)
        traces.append(
            self._trace(
                "index",
                start,
                {"embeddings": len(embeddings)},
                {"backend": self.index.name},
            )
        )

        contexts = []
        if request.rag_mode != RagMode.LLM_ONLY:
            start = perf_counter()
            query_embedding = self.embedder.embed_query(request.query)
            contexts = self.index.search(query_embedding, top_k=request.top_k)
            traces.append(
                self._trace(
                    "search",
                    start,
                    {"query": request.query, "top_k": request.top_k},
                    {"hits": len(contexts), "best_score": contexts[0].score if contexts else None},
                )
            )

        start = perf_counter()
        answer = self.generator.generate(request, contexts)
        answer.trace = traces + [
            self._trace(
                "generate",
                start,
                {"query": request.query, "contexts": len(contexts)},
                {"citations": len(answer.citations), "warnings": len(answer.warnings)},
            )
        ]
        return answer

    @staticmethod
    def _trace(
        stage_name: str,
        started_at: float,
        input_summary: dict,
        output_summary: dict,
    ) -> StageTrace:
        """! @brief 构造带毫秒耗时的 StageTrace。"""
        return StageTrace(
            stage_name=stage_name,
            latency_ms=(perf_counter() - started_at) * 1000,
            input_summary=input_summary,
            output_summary=output_summary,
        )
