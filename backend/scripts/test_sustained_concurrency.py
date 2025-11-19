"""
测试持续高频请求场景下的并发限制
模拟实际项目中的连续批次处理
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from zhipuai import ZhipuAI
from app.core.config import settings

client = ZhipuAI(api_key=settings.zhipu_api_key)


async def test_sustained_load(
    model: str,
    test_type: str,
    concurrency: int,
    num_batches: int = 10,
    requests_per_batch: int = 20
):
    """
    测试持续负载下的并发控制
    
    Args:
        model: 模型名称
        test_type: "chat" 或 "embedding"
        concurrency: 并发数
        num_batches: 批次数
        requests_per_batch: 每批请求数
    """
    print(f"\n{'='*70}")
    print(f"🔥 持续负载测试")
    print(f"{'='*70}")
    print(f"模型: {model}")
    print(f"并发数: {concurrency}")
    print(f"批次数: {num_batches}")
    print(f"每批请求数: {requests_per_batch}")
    print(f"总请求数: {num_batches * requests_per_batch}")
    print(f"{'='*70}\n")
    
    total_success = 0
    total_rate_limit = 0
    total_errors = 0
    
    start_time = time.time()
    
    for batch_idx in range(num_batches):
        print(f"📦 处理批次 {batch_idx + 1}/{num_batches}...")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def single_request(req_id: int):
            async with semaphore:
                try:
                    if test_type == "chat":
                        response = await asyncio.to_thread(
                            client.chat.completions.create,
                            model=model,
                            messages=[{"role": "user", "content": f"请说一个字：{req_id}"}],
                            temperature=0.1
                        )
                        return {'status': 'success'}
                    else:  # embedding
                        response = await asyncio.to_thread(
                            client.embeddings.create,
                            model=model,
                            input=[f"测试文本{req_id}"]
                        )
                        return {'status': 'success'}
                
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "1302" in error_msg:
                        return {'status': 'rate_limit', 'error': error_msg}
                    else:
                        return {'status': 'error', 'error': error_msg}
        
        # 执行本批次
        batch_start = time.time()
        results = await asyncio.gather(
            *[single_request(batch_idx * requests_per_batch + i) 
              for i in range(requests_per_batch)],
            return_exceptions=True
        )
        batch_duration = time.time() - batch_start
        
        # 统计结果
        batch_success = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'success')
        batch_rate_limit = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'rate_limit')
        batch_errors = sum(1 for r in results if not isinstance(r, dict) or 
                          (isinstance(r, dict) and r['status'] == 'error'))
        
        total_success += batch_success
        total_rate_limit += batch_rate_limit
        total_errors += batch_errors
        
        status_emoji = "✅" if batch_rate_limit == 0 else "❌"
        print(f"  {status_emoji} 批次 {batch_idx + 1}: "
              f"成功 {batch_success}/{requests_per_batch} | "
              f"限流 {batch_rate_limit} | "
              f"耗时 {batch_duration:.2f}s")
        
        if batch_rate_limit > 0:
            print(f"  ⚠️ 触发限流！详情: {[r.get('error', '')[:80] for r in results if isinstance(r, dict) and r['status'] == 'rate_limit'][0]}")
        
        # 批次间短暂延迟（模拟实际项目）
        if batch_idx < num_batches - 1:
            await asyncio.sleep(0.5)
    
    total_duration = time.time() - start_time
    
    # 最终统计
    print(f"\n{'='*70}")
    print(f"📊 测试完成")
    print(f"{'='*70}")
    print(f"总请求数: {num_batches * requests_per_batch}")
    print(f"成功: {total_success} ({total_success/(num_batches*requests_per_batch)*100:.1f}%)")
    print(f"限流错误: {total_rate_limit} ({total_rate_limit/(num_batches*requests_per_batch)*100:.1f}%)")
    print(f"其他错误: {total_errors} ({total_errors/(num_batches*requests_per_batch)*100:.1f}%)")
    print(f"总耗时: {total_duration:.2f}秒")
    print(f"平均吞吐: {(num_batches * requests_per_batch) / total_duration:.2f} 请求/秒")
    
    if total_rate_limit == 0:
        print(f"\n✅ 测试通过！并发{concurrency}在持续负载下安全")
    else:
        print(f"\n❌ 测试失败！并发{concurrency}在持续负载下会触发限流")
    
    print(f"{'='*70}\n")
    
    return total_rate_limit == 0


async def find_safe_concurrency(model: str, test_type: str):
    """逐步测试找出安全的并发数"""
    print(f"\n{'#'*70}")
    print(f"🎯 寻找安全并发数: {model} ({test_type})")
    print(f"{'#'*70}\n")
    
    test_levels = [1, 2, 3, 5, 8]
    safe_concurrency = 1
    
    for concurrency in test_levels:
        passed = await test_sustained_load(
            model=model,
            test_type=test_type,
            concurrency=concurrency,
            num_batches=5,  # 5批次
            requests_per_batch=15  # 每批15个
        )
        
        if passed:
            safe_concurrency = concurrency
            print(f"✅ 并发{concurrency}通过持续负载测试\n")
        else:
            print(f"❌ 并发{concurrency}在持续负载下失败\n")
            break
        
        # 等待API冷却
        if concurrency < test_levels[-1]:
            print("⏳ 等待5秒后继续测试...\n")
            await asyncio.sleep(5)
    
    return safe_concurrency


async def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          智谱AI 持续负载并发测试工具                              ║
║                                                                    ║
║  用途: 测试持续高频请求场景下的真实并发限制                       ║
║  模拟: 实际项目中的连续批次处理                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # 测试配置
    tests = [
        {
            'model': 'glm-4-flash',
            'test_type': 'chat',
            'description': 'GLM-4-Flash (聊天模型)'
        },
        {
            'model': 'embedding-3',
            'test_type': 'embedding',
            'description': 'Embedding-3 (向量化模型)'
        }
    ]
    
    results = {}
    
    for test_config in tests:
        safe_concurrency = await find_safe_concurrency(
            model=test_config['model'],
            test_type=test_config['test_type']
        )
        
        results[test_config['model']] = safe_concurrency
        
        print(f"✅ {test_config['description']}: 安全并发数 = {safe_concurrency}\n")
        
        # 等待API冷却
        await asyncio.sleep(5)
    
    # 最终建议
    print(f"\n{'#'*70}")
    print(f"🎉 所有测试完成！")
    print(f"{'#'*70}\n")
    print(f"📝 建议的配置 (持续负载场景):\n")
    
    for model, safe_val in results.items():
        if 'embedding' in model:
            print(f"embedding_batch_size = {safe_val}  # {model} 持续负载安全值")
        elif 'glm-4-flash' in model or 'flash' in model:
            print(f"graph_attribute_concurrency = {safe_val}  # {model} 持续负载安全值")
            print(f"graph_relation_concurrency = {safe_val}  # {model} 持续负载安全值")
    
    print(f"\n💡 提示: 实际项目建议在安全值基础上再降低20-30%以确保稳定性")
    print(f"{'#'*70}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

