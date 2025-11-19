"""
Batch API功能测试

用于验证Batch API是否正常工作
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.batch_api_client import get_batch_client


async def test_batch_api():
    """测试Batch API基本功能"""
    print("🧪 开始测试Batch API...")
    
    # 1. 创建测试任务
    test_tasks = []
    for i in range(5):
        test_tasks.append({
            "custom_id": f"test-{i}",
            "method": "POST",
            "url": "/v4/chat/completions",
            "body": {
                "model": "glm-4-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": f"请用一句话介绍中国第{i+1}大城市。要求：只输出城市名和简介，不超过20字。"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }
        })
    
    print(f"✅ 创建了 {len(test_tasks)} 个测试任务")
    
    # 2. 提交Batch API
    batch_client = get_batch_client()
    
    def progress_callback(batch_id, status, progress, completed, total, failed):
        print(f"📊 进度: {status} | {completed}/{total} ({progress*100:.1f}%) | 失败: {failed}")
    
    try:
        print("🚀 提交Batch API请求...")
        results = await asyncio.to_thread(
            batch_client.submit_and_wait,
            test_tasks,
            check_interval=10,  # 每10秒检查一次
            progress_callback=progress_callback
        )
        
        # 3. 打印结果
        print("\n✅ Batch API测试完成！\n")
        print("=" * 60)
        for custom_id, result in results.items():
            if result['status'] == 'success':
                print(f"✅ {custom_id}: {result['content'][:100]}")
            else:
                print(f"❌ {custom_id}: {result.get('error', '未知错误')}")
        print("=" * 60)
        
        # 统计
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        print(f"\n📊 统计: 成功 {success_count}/{len(test_tasks)}")
        
        if success_count == len(test_tasks):
            print("\n🎉 Batch API测试成功！所有任务都完成了。")
            return True
        else:
            print("\n⚠️ Batch API部分失败，请检查错误信息。")
            return False
            
    except Exception as e:
        print(f"\n❌ Batch API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Batch API 功能测试")
    print("=" * 60)
    print("⏰ 预计耗时: 1-5分钟（取决于API处理速度）")
    print("💡 提示: 请确保已配置ZHIPU_API_KEY环境变量\n")
    
    success = asyncio.run(test_batch_api())
    
    if success:
        print("\n✅ 测试通过！可以放心使用Batch API进行图谱构建。")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！请检查API密钥和网络连接。")
        sys.exit(1)

