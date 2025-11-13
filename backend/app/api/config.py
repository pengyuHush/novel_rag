"""
配置管理 API

提供模型列表、API连接测试等配置相关功能
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.zhipu_client import get_zhipu_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["config"])


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    category: str
    max_tokens: int
    price_input: float
    price_output: float
    description: str
    is_default: bool = False


class ModelListResponse(BaseModel):
    """模型列表响应"""
    models: list[ModelInfo]
    default_model: str


class ConnectionTestRequest(BaseModel):
    """连接测试请求"""
    api_key: str


class ConnectionTestResponse(BaseModel):
    """连接测试响应"""
    success: bool
    message: str
    model_tested: str


@router.get("/models", response_model=ModelListResponse)
async def get_models():
    """
    获取支持的模型列表
    
    Returns:
        ModelListResponse: 模型列表和默认模型
    """
    try:
        models = []
        
        for model_name in settings.supported_models:
            metadata = settings.model_metadata.get(model_name)
            
            if metadata:
                models.append(ModelInfo(
                    **metadata,
                    is_default=(model_name == settings.zhipu_default_model)
                ))
        
        logger.info(f"✅ 获取模型列表成功: {len(models)} 个模型")
        
        return ModelListResponse(
            models=models,
            default_model=settings.zhipu_default_model
        )
        
    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败: {str(e)}"
        )


@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_connection(request: ConnectionTestRequest):
    """
    测试API Key连接
    
    Args:
        request: 包含API Key的请求
    
    Returns:
        ConnectionTestResponse: 连接测试结果
    """
    try:
        # 创建临时客户端测试连接
        from zhipuai import ZhipuAI
        
        test_client = ZhipuAI(api_key=request.api_key)
        
        # 发送一个简单的测试请求（使用免费模型）
        test_model = "GLM-4.5-Flash"
        
        response = test_client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "user", "content": "测试连接，请回复'OK'"}
            ],
            max_tokens=10
        )
        
        if response.choices and response.choices[0].message:
            logger.info("✅ API连接测试成功")
            return ConnectionTestResponse(
                success=True,
                message="连接测试成功！API Key有效。",
                model_tested=test_model
            )
        else:
            raise Exception("未收到有效响应")
            
    except Exception as e:
        logger.error(f"❌ API连接测试失败: {e}")
        return ConnectionTestResponse(
            success=False,
            message=f"连接测试失败：{str(e)}",
            model_tested=test_model if 'test_model' in locals() else "未知"
        )


@router.get("/current")
async def get_current_config():
    """
    获取当前配置信息（脱敏）
    
    Returns:
        dict: 当前配置
    """
    try:
        # 返回脱敏的配置信息
        masked_api_key = (
            settings.zhipu_api_key[:8] + "****" + settings.zhipu_api_key[-4:]
            if settings.zhipu_api_key and len(settings.zhipu_api_key) > 12
            else "未配置"
        )
        
        return {
            "api_key": masked_api_key,
            "default_model": settings.zhipu_default_model,
            "supported_models_count": len(settings.supported_models),
            "max_tokens_per_query": settings.max_tokens_per_query,
            "max_context_chunks": settings.max_context_chunks,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "top_k_retrieval": settings.top_k_retrieval,
            "top_k_rerank": settings.top_k_rerank,
        }
        
    except Exception as e:
        logger.error(f"❌ 获取当前配置失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )

