"""Test Zhipu AI API connectivity and key validity."""

import sys
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

from app.core.config import settings
from zai import ZhipuAiClient


async def main():
    print("🔍 测试 Zhipu AI API 配置\n")
    
    api_key = settings.ZAI_API_KEY or settings.ZHIPU_API_KEY
    
    if not api_key:
        print("❌ 错误：未配置 API Key")
        print("   请在 .env 文件中设置 ZAI_API_KEY 或 ZHIPU_API_KEY")
        return
    
    print(f"✅ API Key 已配置: {api_key[:20]}...")
    
    try:
        client = ZhipuAiClient(api_key=api_key)
        
        # Test embedding
        print("\n📊 测试 Embedding API...")
        test_text = "这是一个测试文本"
        
        response = await asyncio.to_thread(
            client.embeddings.create,
            model="embedding-3",
            input=test_text
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Embedding 成功")
        print(f"   维度: {len(embedding)}")
        print(f"   前5个值: {embedding[:5]}")
        
        # Test chat
        print("\n💬 测试 Chat API...")
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="glm-4-plus",
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Chat 成功")
        print(f"   回答: {answer}")
        
        print("\n🎉 所有测试通过！API 配置正确。")
        
    except Exception as e:
        print(f"\n❌ API 调用失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        print("\n💡 可能的原因:")
        print("   1. API Key 无效或已过期")
        print("   2. 网络连接问题")
        print("   3. API 配额不足")
        print("   4. 服务暂时不可用")


if __name__ == "__main__":
    asyncio.run(main())

