"""! @file qa_dataset.py
@brief 将课程 QA 默认测试数据转换为契约文档的工具。
@details 默认输入来自老师要求的上一项目 QA 数据，但 RAG 系统只允许看到
问题和候选答案文本。answer_quality 档次属于评测标签，禁止进入索引、
prompt、trace 或前端展示。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rag_core.contracts.enums import BlockType
from rag_core.contracts.errors import EmptyCorpus
from rag_core.contracts.models import ContentBlock, ParsedDocument
from rag_core.testing.fakes import stable_id

DEFAULT_COURSE_QA_PATH = Path(__file__).resolve().parents[3] / "sample_data" / "course_qa_public.json"
COURSE_QA_LABELS_PATH = Path(__file__).resolve().parents[3] / "eval" / "labels" / "course_qa_quality_labels.json"


@dataclass(frozen=True)
class CourseQaCandidate:
    """! @brief 可进入 RAG 系统的课程 QA 候选答案，不包含质量档次。"""

    category: str
    qa_id: int
    question: str
    answer_id: str
    answer: str


def load_course_qa_candidates(
    dataset_path: str | Path = DEFAULT_COURSE_QA_PATH,
    category: str | None = None,
    max_questions: int | None = None,
) -> list[CourseQaCandidate]:
    """! @brief 读取不含质量档次的课程 QA 公开输入。
    @param dataset_path 公开 QA JSON 文件路径。
    @param category 可选课程主题；为空时读取全部主题。
    @param max_questions 可选最大问题数，用于快速冒烟测试。
    @return 按公开文件顺序排列的候选答案列表。
    @throws EmptyCorpus 数据文件为空或筛选后没有样例时抛出。
    """
    path = Path(dataset_path)
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    items = _extract_public_items(raw_data)

    candidates: list[CourseQaCandidate] = []
    question_count = 0
    for item in items:
        group_name = str(item.get("category", "")).strip()
        if category and group_name != category:
            continue
        question = str(item.get("question", "")).strip()
        if not group_name or not question:
            continue
        question_count += 1
        qa_id = int(item.get("qa_id", item.get("id", question_count)))
        for answer in item.get("answers", []):
            text = str(answer.get("answer", "")).strip()
            if not text:
                continue
            candidates.append(
                CourseQaCandidate(
                    category=group_name,
                    qa_id=qa_id,
                    question=question,
                    answer_id=str(answer.get("answer_id") or stable_id("ans", group_name, qa_id, text)),
                    answer=text,
                )
            )
        if max_questions is not None and question_count >= max_questions:
            break

    if not candidates:
        raise EmptyCorpus("课程 QA 公开输入筛选后没有可用候选答案")
    return candidates


def build_course_qa_document(
    candidates: list[CourseQaCandidate],
    title: str = "课程 QA 默认测试数据",
    source: str = "sample_data/course_qa_public.json",
) -> ParsedDocument:
    """! @brief 将课程 QA 候选答案转换为 ParsedDocument。
    @param candidates 不含质量档次的候选答案列表。
    @param title 文档标题。
    @param source 数据来源路径。
    @return 可交给分块器、嵌入器和索引器的契约文档。
    @throws EmptyCorpus candidates 为空时抛出。
    """
    if not candidates:
        raise EmptyCorpus("无法用空 QA 候选答案构造文档")

    doc_seed = "\n".join(f"{candidate.category}:{candidate.qa_id}:{candidate.answer_id}" for candidate in candidates)
    doc_id = stable_id("course-qa", title, doc_seed)
    blocks = [
        ContentBlock(
            block_id=stable_id("qa-block", doc_id, candidate.category, candidate.qa_id, candidate.answer_id),
            block_type=BlockType.TEXT,
            text=_format_candidate_text(candidate),
            metadata={
                "category": candidate.category,
                "qa_id": candidate.qa_id,
                "question": candidate.question,
                "answer_id": candidate.answer_id,
            },
        )
        for candidate in candidates
    ]

    return ParsedDocument(
        doc_id=doc_id,
        title=title,
        markdown="\n\n".join(block.text for block in blocks),
        blocks=blocks,
        parser_name="course-qa-loader",
        metadata={"source": source, "dataset_type": "course_qa_public", "candidate_count": len(candidates)},
    )


def default_course_qa_query(candidates: list[CourseQaCandidate]) -> str:
    """! @brief 从课程 QA 候选答案中取默认查询问题。"""
    if not candidates:
        raise EmptyCorpus("无法从空 QA 候选答案中选择默认问题")
    return candidates[0].question


def summarize_course_qa(candidates: list[CourseQaCandidate]) -> dict[str, Any]:
    """! @brief 汇总课程 QA 候选答案数量，供 trace 和 CLI 输出使用。"""
    category_counts: dict[str, int] = {}
    question_keys = set()
    for candidate in candidates:
        category_counts[candidate.category] = category_counts.get(candidate.category, 0) + 1
        question_keys.add((candidate.category, candidate.qa_id))
    return {"question_count": len(question_keys), "candidate_count": len(candidates), "categories": category_counts}


def load_course_qa_quality_labels(labels_path: str | Path = COURSE_QA_LABELS_PATH) -> dict[str, int]:
    """! @brief 读取评测专用质量标签，禁止在 RAG 流水线中调用。
    @param labels_path 质量标签 JSON 文件路径。
    @return answer_id 到 answer_quality 的映射。
    """
    raw_data = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    return {str(row["answer_id"]): int(row["answer_quality"]) for row in raw_data.get("labels", [])}


def _extract_public_items(raw_data: Any) -> list[dict[str, Any]]:
    """! @brief 兼容公开数据结构，拒绝直接使用带质量档次的原始结构。"""
    if isinstance(raw_data, dict) and raw_data.get("dataset") == "course_qa_public":
        items = raw_data.get("items", [])
        if isinstance(items, list):
            return items
    raise EmptyCorpus("请使用 sample_data/course_qa_public.json 作为 RAG 默认输入")


def _format_candidate_text(candidate: CourseQaCandidate) -> str:
    """! @brief 将单条候选答案格式化为可检索文本，不暴露质量档次。"""
    return f"课程主题：{candidate.category}\n问题：{candidate.question}\n候选答案：{candidate.answer}"
