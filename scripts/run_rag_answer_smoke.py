#!/usr/bin/env python3
"""! @file run_rag_answer_smoke.py
@brief 不启动 uvicorn，直接通过 FastAPI TestClient 冒烟调用 `/rag/answer`。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from main import app
from rag_core.contracts.enums import RagMode


def parse_args() -> argparse.Namespace:
    """! @brief 解析 `/rag/answer` 冒烟脚本参数。"""
    parser = argparse.ArgumentParser(description="通过 FastAPI TestClient 调用 /rag/answer。")
    parser.add_argument("--query", default="什么是自然语言处理？")
    parser.add_argument("--rag-mode", choices=[mode.value for mode in RagMode], default=RagMode.BASIC_RAG.value)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    """! @brief CLI 入口。"""
    args = parse_args()
    payload = {
        "query": args.query,
        "rag_mode": args.rag_mode,
        "top_k": args.top_k,
        "collection_id": "course-qa-default",
        "provider": "mock",
        "model": "mock-generator",
        "require_citations": True,
        "metadata": {},
    }
    response = TestClient(app).post("/rag/answer", json=payload)
    response.raise_for_status()
    print(json.dumps(response.json(), ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
