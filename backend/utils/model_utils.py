"""! @file model_utils.py
@brief HuggingFace 模型路径解析辅助函数。
"""

import os
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)

def get_huggingface_model_path(model_name: str) -> str:
    """! @brief 优先将 HuggingFace 模型名解析为可用的本地缓存路径。
    @param model_name Hub 模型标识，例如 sentence-transformers/all-MiniLM-L6-v2。
    @return 当 HF_MODEL_PATH 包含该模型时返回本地文件系统路径，否则返回 model_name。

    如果模型存在于本地，则将模型名转换为本地路径。
    
    参数:
        model_name: 模型名称，例如 "sentence-transformers/all-MiniLM-L6-v2"
        
    返回:
        str: 模型存在时返回本地路径，否则返回原始模型名
    """
    model_path = os.environ.get("HF_MODEL_PATH")
    if not model_path or not os.path.exists(model_path):
        logger.info(f"Using remote model: {model_name}")
        return model_name

    local_model_name = os.path.join(model_path, *model_name.split("/"))
    if os.path.exists(local_model_name):
        logger.info(f"Using local model: {local_model_name}")
        return local_model_name

    logger.info(f"Using remote model: {model_name}")
    return model_name
