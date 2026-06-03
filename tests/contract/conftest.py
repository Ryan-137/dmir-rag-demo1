"""! @file conftest.py
@brief RAG 核心契约测试的 pytest 配置。
"""

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
