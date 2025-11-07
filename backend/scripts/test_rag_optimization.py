"""测试RAG搜索优化效果的脚本."""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import RAGService
from app.schemas.search import SearchRequest
from app.core.config import settings
from loguru import logger


# 测试问题集
TEST_QUERIES = [
    # 事实性问题
    "主角第一次出现在哪里？",
    "主要人物是谁？",
    
    # 关系类问题
    "主角和其他人物是什么关系？",
    
    # 总结类问题
    "总结一下主要内容",
    
    # 分析类问题
    "主角的性格特点是什么？",
]


async def test_single_query(service: RAGService, query: str, novel_ids: list = None):
    """测试单个查询."""
    print(f"\n{'='*60}")
    print(f"测试问题: {query}")
    print(f"{'='*60}")
    
    request = SearchRequest(
        query=query,
        novel_ids=novel_ids or [],
        top_k=10,
        include_references=True
    )
    
    try:
        response = await service.search(request)
        
        print(f"\n✓ 查询成功")
        print(f"  - 响应时间: {response.elapsed:.2f}秒")
        
        if response.token_stats:
            print(f"\n📊 Token统计:")
            print(f"  - 总Token: {response.token_stats.total_tokens}")
            print(f"  - Embedding Token: {response.token_stats.embedding_tokens}")
            print(f"  - Chat Token: {response.token_stats.chat_tokens}")
            print(f"  - API调用次数: {response.token_stats.api_calls}")
            print(f"  - 预估费用: ¥{response.token_stats.estimated_cost:.4f}")
        
        print(f"\n💬 答案:")
        print(f"  {response.answer[:200]}...")
        
        print(f"\n📚 检索结果: {len(response.references)}个相关段落")
        for i, ref in enumerate(response.references[:3], 1):
            print(f"  {i}. 相关度={ref.relevance_score:.3f}")
            if ref.chapter_title:
                print(f"     章节: {ref.chapter_title}")
            print(f"     内容: {ref.content[:100]}...")
        
        return response
        
    except Exception as e:
        print(f"\n✗ 查询失败: {e}")
        logger.exception("Query failed")
        return None


async def compare_configurations():
    """对比不同配置的效果."""
    print("\n" + "="*80)
    print("RAG搜索优化效果测试")
    print("="*80)
    
    print(f"\n当前配置:")
    print(f"  - CHUNK_SIZE: {settings.CHUNK_SIZE}")
    print(f"  - CHUNK_OVERLAP: {settings.CHUNK_OVERLAP}")
    print(f"  - MAX_TOP_K: {settings.MAX_TOP_K}")
    print(f"  - MIN_RELEVANCE_SCORE: {settings.MIN_RELEVANCE_SCORE}")
    print(f"  - ENABLE_QUERY_REWRITE: {settings.ENABLE_QUERY_REWRITE}")
    print(f"  - ENABLE_RERANKING: {settings.ENABLE_RERANKING}")
    print(f"  - CONTEXT_EXPAND_WINDOW: {settings.CONTEXT_EXPAND_WINDOW}")
    
    service = RAGService()
    
    # 测试所有查询
    results = []
    for query in TEST_QUERIES:
        result = await test_single_query(service, query)
        if result:
            results.append(result)
        await asyncio.sleep(1)  # 避免API限流
    
    # 统计总体效果
    if results:
        print(f"\n{'='*80}")
        print("总体统计")
        print(f"{'='*80}")
        
        total_tokens = sum(r.token_stats.total_tokens for r in results if r.token_stats)
        total_cost = sum(r.token_stats.estimated_cost for r in results if r.token_stats)
        avg_time = sum(r.elapsed for r in results) / len(results)
        avg_refs = sum(len(r.references) for r in results) / len(results)
        avg_relevance = sum(
            sum(ref.relevance_score for ref in r.references) / len(r.references) 
            if r.references else 0 
            for r in results
        ) / len(results)
        
        print(f"\n测试查询数: {len(results)}")
        print(f"总Token消耗: {total_tokens}")
        print(f"总预估费用: ¥{total_cost:.4f}")
        print(f"平均响应时间: {avg_time:.2f}秒")
        print(f"平均检索结果数: {avg_refs:.1f}个")
        print(f"平均相关度: {avg_relevance:.3f}")


async def test_with_novel_id():
    """测试指定小说ID的搜索."""
    print("\n" + "="*80)
    print("测试指定小说ID搜索")
    print("="*80)
    
    print("\n请输入小说ID（留空表示搜索所有小说）:")
    novel_id = input("> ").strip()
    
    novel_ids = [novel_id] if novel_id else []
    
    print("\n请输入测试问题:")
    query = input("> ").strip()
    
    if query:
        service = RAGService()
        await test_single_query(service, query, novel_ids)


async def main():
    """主函数."""
    print("\nRAG搜索优化测试脚本")
    print("="*80)
    print("\n选择测试模式:")
    print("  1. 运行完整测试（使用预设问题集）")
    print("  2. 自定义问题测试")
    print("  3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        await compare_configurations()
    elif choice == "2":
        await test_with_novel_id()
    elif choice == "3":
        print("退出测试")
        return
    else:
        print("无效选择")
        return
    
    print("\n" + "="*80)
    print("测试完成!")
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        logger.exception("Test failed")

