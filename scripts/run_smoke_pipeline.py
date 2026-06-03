#!/usr/bin/env python3
"""! @file run_smoke_pipeline.py
@brief 在不使用网络和真实模型的情况下运行契约优先模拟 RAG 流水线。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from rag_core.contracts.enums import RagMode
from rag_core.contracts.models import RagRequest
from rag_core.pipeline import FakeRagPipeline
from rag_core.testing import (
    build_course_qa_document,
    default_course_qa_query,
    load_course_qa_candidates,
    summarize_course_qa,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行本地模拟 RAG 冒烟流水线。")
    parser.add_argument("--mode", choices=["fake"], default="fake", help="P0 冒烟测试只允许使用模拟模式。")
    parser.add_argument("--rag-mode", choices=[mode.value for mode in RagMode], default=RagMode.BASIC_RAG.value)
    parser.add_argument("--dataset", default="sample_data/course_qa_public.json", help="课程 QA 默认测试数据路径。")
    parser.add_argument("--category", default=None, help="可选课程主题；为空时使用全部主题。")
    parser.add_argument("--max-questions", type=int, default=20, help="冒烟测试最多读取的问题数。")
    parser.add_argument("--query", default=None, help="可选查询；为空时使用课程 QA 数据中的第一条问题。")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--pretty", action="store_true", help="格式化输出 JSON。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = load_course_qa_candidates(
        dataset_path=args.dataset,
        category=args.category,
        max_questions=args.max_questions,
    )
    query = args.query or default_course_qa_query(candidates)
    document = build_course_qa_document(candidates, source=args.dataset)
    request = RagRequest(
        query=query,
        rag_mode=RagMode(args.rag_mode),
        top_k=args.top_k,
        collection_id="course-qa-smoke",
        model="mock-generator",
        provider="mock",
        require_citations=True,
        metadata={"dataset_summary": summarize_course_qa(candidates)},
    )
    answer = FakeRagPipeline().answer_document(document, request)
    answer.metadata["dataset_summary"] = summarize_course_qa(candidates)
    answer.metadata["dataset_path"] = args.dataset
    print(json.dumps(answer.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
