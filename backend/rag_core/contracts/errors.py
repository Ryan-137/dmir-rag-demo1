"""! @file errors.py
@brief 契约与服务提供方边界使用的项目级异常。
"""


class RagCoreError(Exception):
    """! @brief RAG 核心模块失败的基础异常。"""


class ContractViolation(RagCoreError):
    """! @brief 实现不满足共享契约时抛出。"""


class ProviderUnavailable(RagCoreError):
    """! @brief 外部或本地服务提供方不可用时抛出。"""


class EmptyCorpus(RagCoreError):
    """! @brief 检索或索引没有可用内容时抛出。"""


class VectorDimensionMismatch(ContractViolation):
    """! @brief 嵌入向量维度不兼容时抛出。"""
