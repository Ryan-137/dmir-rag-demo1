"""! @file models.py
@brief 定义跨模块 RAG 契约的 Pydantic 模型。
@details 这些模型刻意保持小而稳定。模块内部可以使用自己的结构，
但跨模块传递的数据必须满足这些契约或其序列化形式。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from rag_core.contracts.enums import BlockType, RagMode

CONTRACT_VERSION = "0.1.0"


class ContractModel(BaseModel):
    """! @brief 契约模型共用的 Pydantic 配置。"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ContentBlock(ContractModel):
    """! @brief 文档解析器输出的半结构化内容单元。"""

    block_id: str = Field(min_length=1)
    block_type: BlockType
    text: str
    page_number: int | None = Field(default=None, ge=1)
    bbox: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(ContractModel):
    """! @brief 解析器输出，供分块器与评测夹具使用。"""

    contract_version: str = CONTRACT_VERSION
    doc_id: str = Field(min_length=1)
    title: str = ""
    markdown: str = ""
    blocks: list[ContentBlock] = Field(default_factory=list)
    parser_name: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk(ContractModel):
    """! @brief 传给嵌入与索引模块的最小可检索文本单元。"""

    chunk_id: str = Field(min_length=1)
    doc_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source: str = Field(min_length=1)
    block_ids: list[str] = Field(default_factory=list)
    block_types: list[BlockType] = Field(default_factory=list)
    token_count: int = Field(ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingVector(ContractModel):
    """! @brief 文本块或查询的向量表示。"""

    item_id: str = Field(min_length=1)
    vector: list[float] = Field(min_length=1)
    dim: int = Field(gt=0)
    model: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_dimension(self) -> "EmbeddingVector":
        """! @brief 确保声明维度与实际向量长度一致。"""
        if self.dim != len(self.vector):
            raise ValueError("EmbeddingVector.dim must match len(vector)")
        return self


class SearchHit(ContractModel):
    """! @brief 检索命中结果；score 必须越大越相关。"""

    chunk_id: str = Field(min_length=1)
    doc_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    score: float
    rank: int = Field(ge=1)
    source: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagRequest(ContractModel):
    """! @brief 统一问答请求。"""

    query: str = Field(min_length=1)
    rag_mode: RagMode = RagMode.BASIC_RAG
    top_k: int = Field(default=5, ge=1, le=50)
    collection_id: str = "default"
    model: str = "mock-generator"
    provider: str = "mock"
    require_citations: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class Citation(ContractModel):
    """! @brief 有证据支撑的回答所使用的证据引用。"""

    doc_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    page_number: int | None = Field(default=None, ge=1)
    section_path: list[str] = Field(default_factory=list)
    quote: str = ""
    source: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class StageTrace(ContractModel):
    """! @brief 单个流水线阶段的记录，供前端和评测展示。"""

    stage_name: str = Field(min_length=1)
    latency_ms: float = Field(ge=0)
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class RagAnswer(ContractModel):
    """! @brief 前端与评测脚本共同消费的统一回答对象。"""

    contract_version: str = CONTRACT_VERSION
    answer_markdown: str
    citations: list[Citation] = Field(default_factory=list)
    retrieved_hits: list[SearchHit] = Field(default_factory=list)
    trace: list[StageTrace] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
