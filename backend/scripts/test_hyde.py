"""测试HyDE功能的简单脚本."""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import RAGService
from app.schemas.search import SearchRequest
from app.core.config import settings
from loguru import logger


async def test_hyde():
    """测试HyDE功能."""
    
    print("\n" + "="*80)
    print("HyDE (假设文档嵌入) 功能测试")
    print("="*80)
    
    print(f"\n当前配置:")
    print(f"  - ENABLE_HYDE: {settings.ENABLE_HYDE}")
    print(f"  - ENABLE_QUERY_REWRITE: {settings.ENABLE_QUERY_REWRITE}")
    
    if not settings.ENABLE_HYDE:
        print("\n⚠️  警告: ENABLE_HYDE=false，请在.env中设置为true后重试")
        return
    
    service = RAGService()
    
    # 测试问题（推理型问题更适合HyDE）
    test_queries = [
        "主角为什么要帮助配角？",
        "主角和配角是什么关系？",
        "故事的主要冲突是什么？",
    ]
    
    print("\n" + "-"*80)
    print("开始测试...")
    print("-"*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n【测试 {i}/{len(test_queries)}】")
        print(f"问题: {query}")
        print("-" * 40)
        
        # 生成假设答案
        hypothetical = await service._generate_hypothetical_answer(query)
        
        if hypothetical == query:
            print("❌ HyDE生成失败，返回了原问题")
        else:
            print(f"✅ HyDE生成成功")
            print(f"\n假设答案:")
            print(f"  {hypothetical[:150]}...")
            print(f"  (长度: {len(hypothetical)} 字符)")
        
        await asyncio.sleep(1)  # 避免API限流
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    
    print("\n💡 提示:")
    print("  - 如果生成成功，HyDE会用假设答案的向量进行检索")
    print("  - 假设答案的语义通常更接近真实答案")
    print("  - 特别适合'为什么'、'如何'等推理型问题")
    print("  - 每次搜索约增加500 tokens消耗")
    
    print("\n📚 完整文档:")
    print("  backend/RAG_SEARCH_OPTIMIZATION.md")


async def test_full_search():
    """测试完整搜索流程（包含HyDE）."""
    
    print("\n" + "="*80)
    print("完整搜索流程测试（HyDE模式）")
    print("="*80)
    
    service = RAGService()
    
    print("\n请输入测试问题（推荐推理型问题，如'为什么...'）:")
    query = input("> ").strip()
    
    if not query:
        print("未输入问题，测试结束")
        return
    
    print(f"\n正在搜索: {query}")
    print("-" * 80)
    
    request = SearchRequest(
        query=query,
        novel_ids=[],
        top_k=5,
        include_references=True
    )
    
    try:
        response = await service.search(request)
        
        print(f"\n✅ 搜索成功")
        print(f"  - 响应时间: {response.elapsed:.2f}秒")
        
        if response.token_stats:
            print(f"\n📊 Token统计:")
            print(f"  - 总Token: {response.token_stats.total_tokens}")
            print(f"  - Embedding Token: {response.token_stats.embedding_tokens}")
            print(f"  - Chat Token: {response.token_stats.chat_tokens}")
            print(f"  - 预估费用: ¥{response.token_stats.estimated_cost:.4f}")
        
        print(f"\n💬 答案:")
        print(f"  {response.answer}")
        
        print(f"\n📚 检索到 {len(response.references)} 个相关段落")
        
    except Exception as e:
        print(f"\n❌ 搜索失败: {e}")
        logger.exception("Search failed")


async def main():
    """主函数."""
    print("\nHyDE功能测试脚本")
    print("="*80)
    print("\n选择测试模式:")
    print("  1. 测试HyDE生成功能")
    print("  2. 测试完整搜索流程（包含HyDE）")
    print("  3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        await test_hyde()
    elif choice == "2":
        await test_full_search()
    elif choice == "3":
        print("退出测试")
        return
    else:
        print("无效选择")
        return


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        logger.exception("Test failed")

