"""对比普通嵌入和缓存嵌入的耗时。"""

import argparse
import os
import shutil
import time
from pathlib import Path

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = ROOT_DIR / "class" / "note" / "README.md"
DEFAULT_CACHE_DIR = ROOT_DIR / "build" / "langchain-embedding-cache"
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


def build_vector_store(documents, embedder):
    """构建向量库，用于触发文档嵌入。"""
    try:
        return FAISS.from_documents(documents, embedder), "FAISS"
    except ImportError:
        return InMemoryVectorStore.from_documents(documents, embedder), "InMemoryVectorStore"


def vector_store_size(vector_store) -> int:
    """获取不同向量库实现中的文档数量。"""
    if hasattr(vector_store, "index"):
        return vector_store.index.ntotal
    return len(vector_store.store)


def main() -> None:
    parser = argparse.ArgumentParser(description="验证 CacheBackedEmbeddings 缓存加速")
    parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--chunk-size", type=int, default=350)
    parser.add_argument("--max-chunks", type=int, default=16)
    parser.add_argument("--keep-cache", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

    if args.cache_dir.exists() and not args.keep_cache:
        shutil.rmtree(args.cache_dir)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    model_path = resolve_model_path(args.model_name)
    documents = load_chunks(args.data_file, args.chunk_size, args.max_chunks)

    embed_model = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    store = LocalFileStore(str(args.cache_dir))
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=embed_model,
        document_embedding_cache=store,
        namespace=args.model_name,
        key_encoder="sha256",
    )

    first_start = time.perf_counter()
    first_db, store_name = build_vector_store(documents, cached_embedder)
    first_elapsed = time.perf_counter() - first_start

    second_start = time.perf_counter()
    second_db, _ = build_vector_store(documents, cached_embedder)
    second_elapsed = time.perf_counter() - second_start

    speedup = first_elapsed / second_elapsed if second_elapsed > 0 else float("inf")
    print(f"数据文件: {args.data_file}")
    print(f"模型: {model_path}")
    print(f"向量库: {store_name}")
    print(f"缓存目录: {args.cache_dir}")
    print(f"文本块数量: {len(documents)}")
    print(f"首次构建向量库耗时: {first_elapsed:.4f} 秒")
    print(f"第二次构建向量库耗时: {second_elapsed:.4f} 秒")
    print(f"缓存加速倍数: {speedup:.2f}x")
    print(f"两次向量库文档数: {vector_store_size(first_db)} / {vector_store_size(second_db)}")


if __name__ == "__main__":
    main()
