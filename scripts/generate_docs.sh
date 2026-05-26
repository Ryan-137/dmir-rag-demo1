#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v doxygen >/dev/null 2>&1; then
  echo "未安装 Doxygen。可使用以下命令安装：brew install doxygen" >&2
  exit 127
fi

mkdir -p build/doxygen
doxygen Doxyfile
echo "Doxygen HTML 已生成：$ROOT_DIR/build/doxygen/html/index.html"
