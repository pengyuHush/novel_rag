"""
测试智谱AI API的实际并发限制
用于确定不同模型的真实并发上限
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from zhipuai import ZhipuAI
from app.core.config import settings

# 初始化客户端
client = ZhipuAI(api_key=settings.zhipu_api_key)


class ConcurrencyTester:
    """并发测试器"""
    
    def __init__(self, model: str, test_type: str = "chat"):
        self.model = model
        self.test_type = test_type  # "chat" or "embedding"
        self.results = []
    
    async def single_request(self, request_id: int) -> Dict:
        """发送单个请求"""
        start_time = time.time()
        
        try:
            if self.test_type == "chat":
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": f"测试请求#{request_id}：请用一句话介绍Python。"}
                    ],
                    temperature=0.1
                )
                content = response.choices[0].message.content
            else:  # embedding
                response = client.embeddings.create(
                    model=self.model,
                    input=[f"测试文本#{request_id}"]
                )
                content = f"embedding维度: {len(response.data[0].embedding)}"
            
            duration = time.time() - start_time
            
            return {
                'request_id': request_id,
                'status': 'success',
                'duration': duration,
                'content_preview': content[:50] if content else None
            }
        
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            # 判断是否是并发限制错误
            is_rate_limit = "429" in error_msg or "1302" in error_msg
            
            return {
                'request_id': request_id,
                'status': 'rate_limit' if is_rate_limit else 'error',
                'duration': duration,
                'error': error_msg[:200]
            }
    
    async def test_concurrency_level(
        self, 
        concurrency: int, 
        num_requests: int = 10
    ) -> Dict:
        """测试特定并发级别"""
        print(f"\n{'='*60}")
        print(f"🧪 测试并发数: {concurrency} | 总请求数: {num_requests}")
        print(f"{'='*60}")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def request_with_limit(req_id: int):
            async with semaphore:
                return await self.single_request(req_id)
        
        start_time = time.time()
        
        # 并发发送所有请求
        results = await asyncio.gather(
            *[request_with_limit(i) for i in range(num_requests)],
            return_exceptions=True
        )
        
        total_duration = time.time() - start_time
        
        # 统计结果
        success_count = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'success')
        rate_limit_count = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'rate_limit')
        error_count = sum(1 for r in results if isinstance(r, dict) and r['status'] == 'error')
        exception_count = sum(1 for r in results if not isinstance(r, dict))
        
        avg_duration = sum(r['duration'] for r in results if isinstance(r, dict)) / len(results)
        
        result = {
            'concurrency': concurrency,
            'num_requests': num_requests,
            'success_count': success_count,
            'rate_limit_count': rate_limit_count,
            'error_count': error_count,
            'exception_count': exception_count,
            'total_duration': total_duration,
            'avg_request_duration': avg_duration,
            'passed': rate_limit_count == 0 and exception_count == 0
        }
        
        # 打印结果
        status_emoji = "✅" if result['passed'] else "❌"
        print(f"\n{status_emoji} 测试结果:")
        print(f"  - 成功: {success_count}/{num_requests}")
        print(f"  - 并发限制错误: {rate_limit_count}")
        print(f"  - 其他错误: {error_count + exception_count}")
        print(f"  - 总耗时: {total_duration:.2f}秒")
        print(f"  - 平均请求耗时: {avg_duration:.2f}秒")
        
        if rate_limit_count > 0:
            print(f"\n⚠️ 触发并发限制！并发{concurrency}过高")
            # 显示第一个错误详情
            for r in results:
                if isinstance(r, dict) and r['status'] == 'rate_limit':
                    print(f"  错误详情: {r['error'][:150]}...")
                    break
        
        self.results.append(result)
        return result
    
    async def find_max_concurrency(
        self, 
        start: int = 1, 
        end: int = 10, 
        num_requests: int = 15
    ) -> int:
        """二分查找最大安全并发数"""
        print(f"\n{'#'*60}")
        print(f"🚀 开始测试模型: {self.model} ({self.test_type})")
        print(f"📊 测试范围: {start} - {end}")
        print(f"{'#'*60}")
        
        max_safe_concurrency = 0
        
        # 先测试一些关键点
        test_levels = [1, 2, 3, 5, 8, 10]
        test_levels = [c for c in test_levels if start <= c <= end]
        
        for concurrency in test_levels:
            result = await self.test_concurrency_level(concurrency, num_requests)
            
            if result['passed']:
                max_safe_concurrency = concurrency
                print(f"✅ 并发{concurrency}通过测试")
            else:
                print(f"❌ 并发{concurrency}失败，停止测试")
                break
            
            # 短暂等待，避免影响下一次测试
            await asyncio.sleep(2)
        
        return max_safe_concurrency
    
    def print_summary(self, max_concurrency: int):
        """打印测试总结"""
        print(f"\n{'='*60}")
        print(f"📋 测试总结 - {self.model}")
        print(f"{'='*60}")
        print(f"🎯 建议的最大并发数: {max_concurrency}")
        print(f"⚠️ 保守建议（留20%余量）: {max(1, int(max_concurrency * 0.8))}")
        print(f"\n详细结果:")
        
        for r in self.results:
            status = "✅ 通过" if r['passed'] else "❌ 失败"
            print(f"  并发{r['concurrency']:2d}: {status} | "
                  f"成功 {r['success_count']}/{r['num_requests']} | "
                  f"限流 {r['rate_limit_count']} | "
                  f"耗时 {r['total_duration']:.1f}s")
        
        print(f"\n{'='*60}\n")


async def main():
    """主测试函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         智谱AI API 并发限制测试工具                        ║
║                                                            ║
║  用途: 测试不同模型的实际最大并发数                         ║
║  参考: https://bigmodel.cn/usercenter/proj-mgmt/rate-limits ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 测试配置
    tests = [
        {
            'model': 'glm-4-flash',
            'test_type': 'chat',
            'description': 'GLM-4-Flash (聊天模型)',
            'start': 1,
            'end': 10,
            'requests': 15
        },
        {
            'model': 'embedding-3',
            'test_type': 'embedding',
            'description': 'Embedding-3 (向量化模型)',
            'start': 1,
            'end': 10,
            'requests': 15
        }
    ]
    
    all_results = {}
    
    for test_config in tests:
        print(f"\n\n{'*'*60}")
        print(f"开始测试: {test_config['description']}")
        print(f"{'*'*60}\n")
        
        tester = ConcurrencyTester(
            model=test_config['model'],
            test_type=test_config['test_type']
        )
        
        max_concurrency = await tester.find_max_concurrency(
            start=test_config['start'],
            end=test_config['end'],
            num_requests=test_config['requests']
        )
        
        tester.print_summary(max_concurrency)
        
        all_results[test_config['model']] = {
            'max_concurrency': max_concurrency,
            'safe_concurrency': max(1, int(max_concurrency * 0.8)),
            'results': tester.results
        }
        
        # 等待一段时间再测试下一个模型
        if test_config != tests[-1]:
            print("⏳ 等待5秒后测试下一个模型...\n")
            await asyncio.sleep(5)
    
    # 最终建议
    print(f"\n{'#'*60}")
    print(f"🎉 所有测试完成！")
    print(f"{'#'*60}")
    print(f"\n📝 建议的配置 (backend/app/core/config.py):\n")
    
    for model, result in all_results.items():
        if 'embedding' in model:
            print(f"# {model}")
            print(f"embedding_batch_size = {result['safe_concurrency']}  "
                  f"# 实测最大{result['max_concurrency']}，建议{result['safe_concurrency']}")
        elif 'glm-4-flash' in model or 'flash' in model:
            print(f"# {model}")
            print(f"graph_attribute_concurrency = {result['safe_concurrency']}  "
                  f"# 实测最大{result['max_concurrency']}，建议{result['safe_concurrency']}")
            print(f"graph_relation_concurrency = {result['safe_concurrency']}  "
                  f"# 实测最大{result['max_concurrency']}，建议{result['safe_concurrency']}")
    
    print(f"\n{'#'*60}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

