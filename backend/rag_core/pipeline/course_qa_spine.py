"""! @file course_qa_spine.py
@brief #8 阶段 A 的课程 QA 集成主链路。
@details 本模块只负责把已经冻结的 P0 fake pipeline 暴露成稳定服务边界。
真实 embedding、index、generation adapter 仍由 #2/#3/#4 独立实现，后续通过
同一个 RagRequest / RagAnswer contract 接入。
"""

from __future__ import annotations

from typing import Any

from rag_core.contracts.errors import ContractViolation, ProviderUnavailable
from rag_core.contracts.models import RagAnswer, RagRequest
from rag_core.pipeline.orchestrator import FakeRagPipeline
from rag_core.testing import (
    build_course_qa_document,
    load_course_qa_candidates,
    summarize_course_qa,
)

DEFAULT_PUBLIC_DATASET = "sample_data/course_qa_public.json"
DEFAULT_COLLECTION_ID = "course-qa-default"
DEFAULT_PROVIDER = "mock"
DEFAULT_MODEL = "mock-generator"
SPINE_NAME = "course-qa-fake-spine"


class CourseQaRagSpine:
    """! @brief 面向 `/rag/answer` 的最小课程 QA 集成服务。

    @details 阶段 A 固定使用公开课程 QA 数据和 fake/mock pipeline。这样前端和
    评测可以先接稳定接口，真实 adapter 后续只替换内部 provider 分发，不改变外部
    contract。
    """

    def __init__(self, dataset_path: str = DEFAULT_PUBLIC_DATASET):
        self.dataset_path = dataset_path

    def answer(self, request: RagRequest) -> RagAnswer:
        """! @brief 根据 RagRequest 返回契约合规的 RagAnswer。
        @param request 统一问答请求。
        @return fake/mock 主链路生成的 RagAnswer。
        @throws ContractViolation 请求 metadata 里包含隐藏评测标签时抛出。
        @throws ProviderUnavailable 阶段 A 收到非 mock provider/model 时抛出。
        """
        self._validate_stage_a_request(request)

        candidates = load_course_qa_candidates(
            dataset_path=self.dataset_path,
            category=self._optional_str(request.metadata.get("category")),
            max_questions=self._optional_positive_int(request.metadata.get("max_questions")),
        )
        dataset_summary = summarize_course_qa(candidates)
        document = build_course_qa_document(candidates, source=self.dataset_path)
        answer = FakeRagPipeline().answer_document(document, request)

        answer.metadata.update(
            {
                "integration_spine": SPINE_NAME,
                "integration_stage": "stage_a",
                "dataset_type": "course_qa_public",
                "dataset_path": self.dataset_path,
                "dataset_summary": dataset_summary,
                "collection_id": request.collection_id or DEFAULT_COLLECTION_ID,
                "provider": request.provider,
                "model": request.model,
                "rag_mode": request.rag_mode.value,
            }
        )
        if request.rag_mode.value == "optimized_rag":
            answer.warnings.append("阶段 A optimized_rag 暂时复用 fake 检索链路；query rewrite/rerank 由 #4 接入。")
        return answer

    @staticmethod
    def _validate_stage_a_request(request: RagRequest) -> None:
        """! @brief 校验阶段 A 支持范围和隐藏标签隔离规则。"""
        if _contains_forbidden_key(request.metadata, "answer_quality"):
            raise ContractViolation("answer_quality 只能由评测脚本在生成完成后读取，禁止进入 /rag/answer 请求")
        if request.provider != DEFAULT_PROVIDER or request.model != DEFAULT_MODEL:
            raise ProviderUnavailable(
                "阶段 A /rag/answer 只支持 provider=mock 且 model=mock-generator；"
                "真实 provider 由 #2/#3/#4 后续接入"
            )

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        """! @brief 将 metadata 可选字符串字段标准化。"""
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _optional_positive_int(value: Any) -> int | None:
        """! @brief 将 metadata 可选正整数字段标准化。"""
        if value is None:
            return None
        try:
            number = int(value)
        except (TypeError, ValueError) as exc:
            raise ContractViolation("metadata.max_questions 必须为正整数") from exc
        if number <= 0:
            raise ContractViolation("metadata.max_questions 必须为正整数")
        return number


def _contains_forbidden_key(value: Any, forbidden_key: str) -> bool:
    """! @brief 递归检查请求结构中是否包含禁止进入 RAG 的字段名。"""
    if isinstance(value, dict):
        return any(
            key == forbidden_key or _contains_forbidden_key(item, forbidden_key)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_key(item, forbidden_key) for item in value)
    return False
