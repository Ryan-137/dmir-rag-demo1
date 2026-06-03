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


SAMPLE_DOCUMENT = """Budget-Constrained Online Retrieval-Augmented Generation

Chunk-as-a-Service 模型研究有限 chunk 预算下的在线检索问题。
UCOSA 在预算约束下选择 chunks，并与 random selection 和 offline selection 做对比。

OB-CaaS 在在线已知预算时优化检索。LB-CaaS 使用学习到的预算感知策略。
NEP x AR 指标结合 normalized evidence precision 与 answer recall，用于衡量有证据支撑的回答质量。
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行本地模拟 RAG 冒烟流水线。")
    parser.add_argument("--mode", choices=["fake"], default="fake", help="P0 冒烟测试只允许使用模拟模式。")
    parser.add_argument("--rag-mode", choices=[mode.value for mode in RagMode], default=RagMode.BASIC_RAG.value)
    parser.add_argument("--query", default="UCOSA 在 Chunk-as-a-Service 中解决了什么问题？")
    parser.add_argument("--top-k", type=int, default=2)
    parser.add_argument("--pretty", action="store_true", help="格式化输出 JSON。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request = RagRequest(
        query=args.query,
        rag_mode=RagMode(args.rag_mode),
        top_k=args.top_k,
        collection_id="smoke-demo",
        model="mock-generator",
        provider="mock",
        require_citations=True,
    )
    answer = FakeRagPipeline().answer_text(SAMPLE_DOCUMENT, request, title="chunk-as-a-service")
    print(json.dumps(answer.model_dump(mode="json"), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
