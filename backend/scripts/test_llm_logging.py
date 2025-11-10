"""测试LLM API日志功能."""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.rag_service import RAGService
from app.schemas.search import SearchRequest
from loguru import logger

# 配置日志格式
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


async def test_embeddings_logging():
    """测试Embeddings API日志."""
    print("\n" + "="*80)
    print("【测试1】Embeddings API 日志")
    print("="*80)
    
    service = RAGService()
    
    try:
        texts = [
            "这是第一段测试文本，用于生成向量。",
            "这是第二段测试文本，也用于生成向量。",
        ]
        
        result = await service.embed_texts(texts)
        
        print(f"\n✅ 成功生成 {len(result.vectors)} 个向量")
        print(f"   维度: {len(result.vectors[0]) if result.vectors else 0}")
        print(f"   Token使用: {result.usage.total_tokens}")
        print("\n💡 提示：查看上方日志中的 [LLM API CALL] 条目，可以看到详细的入参和出参")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


async def test_chat_logging():
    """测试Chat API日志（非流式）."""
    print("\n" + "="*80)
    print("【测试2】Chat API 日志（非流式）")
    print("="*80)
    
    service = RAGService()
    
    try:
        question = "请简单介绍一下自己"
        context = ["我是一个AI助手，专门用于分析小说内容。"]
        
        answer, usage = await service._generate_answer(question, context)
        
        print(f"\n✅ 成功生成答案")
        print(f"   答案长度: {len(answer)} 字符")
        if usage:
            print(f"   Token使用: {usage.total_tokens}")
        print(f"\n答案预览: {answer[:100]}...")
        print("\n💡 提示：查看上方日志中的 [LLM API CALL] 条目")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


async def test_stream_logging():
    """测试Chat Stream API日志."""
    print("\n" + "="*80)
    print("【测试3】Chat Stream API 日志（流式）")
    print("="*80)
    
    service = RAGService()
    
    try:
        question = "请用一句话介绍RAG技术"
        context = ["RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术。"]
        
        print("\n开始流式生成...")
        thinking_parts = []
        answer_parts = []
        
        async for event in service._generate_answer_stream(question, context):
            if event['type'] == 'thinking':
                thinking_parts.append(event['content'])
                print("🤔", end="", flush=True)
            elif event['type'] == 'answer':
                answer_parts.append(event['content'])
                print(event['content'], end="", flush=True)
            elif event['type'] == 'usage':
                print(f"\n\n📊 Token使用: {event['data']['total_tokens']}")
        
        print("\n\n✅ 流式生成完成")
        print(f"   思考过程长度: {len(''.join(thinking_parts))} 字符")
        print(f"   答案长度: {len(''.join(answer_parts))} 字符")
        print("\n💡 提示：查看上方日志中的 [LLM API CALL] 和 [STREAM SUMMARY] 条目")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


async def test_query_rewriting_logging():
    """测试查询改写日志."""
    print("\n" + "="*80)
    print("【测试4】查询改写 API 日志")
    print("="*80)
    
    service = RAGService()
    
    try:
        original_query = "主角是谁？"
        
        rewritten = await service._rewrite_query(original_query)
        
        print(f"\n✅ 查询改写完成")
        print(f"   原查询: {original_query}")
        print(f"   改写数量: {len(rewritten)}")
        for i, q in enumerate(rewritten, 1):
            print(f"   改写{i}: {q}")
        print("\n💡 提示：查看上方日志中 task='query_rewriting' 的条目")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


async def main():
    """运行所有测试."""
    
    print("\n" + "="*80)
    print("LLM API 日志功能测试")
    print("="*80)
    
    # 检查API Key
    api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
    if not api_key:
        print("\n❌ 未配置API Key，请在.env中设置 ZAI_API_KEY 或 ZHIPU_API_KEY")
        return
    
    print(f"\n✅ API Key已配置: {api_key[:10]}...")
    
    # 运行测试
    await test_embeddings_logging()
    await asyncio.sleep(1)
    
    await test_chat_logging()
    await asyncio.sleep(1)
    
    await test_stream_logging()
    await asyncio.sleep(1)
    
    await test_query_rewriting_logging()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print("\n📝 所有API调用的详细日志已输出，包括：")
    print("   - 请求参数（已脱敏处理）")
    print("   - 响应内容（截断到500字符）")
    print("   - Token使用统计")
    print("   - 调用耗时")
    print("\n📖 详细说明请查看: backend/docs/LLM_API_LOGGING.md")


if __name__ == "__main__":
    asyncio.run(main())

