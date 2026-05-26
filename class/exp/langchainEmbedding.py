"""运行 LangChain HuggingFace 嵌入模型的最小示例。"""

import argparse
import os
import time
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = ROOT_DIR / "class" / "note" / "README.md"
DEFAULT_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def resolve_model_path(model_name: str) -> str:
    """优先使用仓库内或环境变量指定的本地 HuggingFace 模型目录。"""
    search_roots = [
        os.environ.get("HF_MODEL_PATH"),
        str(ROOT_DIR / "hf_model_path"),
    ]
    for root in search_roots:
        if not root:
            continue
        candidate = Path(root).joinpath(*model_name.split("/"))
        if candidate.exists():
            return str(candidate)
    return model_name


def load_chunks(data_file: Path, chunk_size: int, max_chunks: int):
    """读取文本文件并切分为用于嵌入的文档块。"""
    raw_documents = TextLoader(str(data_file), encoding="utf-8").load()
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0,
        separator="\n\n",
    )
    documents = text_splitter.split_documents(raw_documents)
    return documents[:max_chunks]


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 LangChain 嵌入模型示例")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--chunk-size", type=int, default=350)
    parser.add_argument("--max-chunks", type=int, default=16)
    args = parser.parse_args()

    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

    model_path = resolve_model_path(args.model_name)
    documents = load_chunks(args.data_file, args.chunk_size, args.max_chunks)
    texts = [doc.page_content for doc in documents]

    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    start = time.perf_counter()
    vectors = embeddings.embed_documents(texts)
    elapsed = time.perf_counter() - start

    print(f"数据文件: {args.data_file}")
    print(f"模型: {model_path}")
    print(f"文本块数量: {len(texts)}")
    print(f"向量维度: {len(vectors[0]) if vectors else 0}")
    print(f"嵌入耗时: {elapsed:.4f} 秒")
    print(f"第一个向量前 10 维: {vectors[0][:10] if vectors else []}")


if __name__ == "__main__":
    main()
