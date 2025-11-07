"""直接测试智谱AI API调用."""

import os
import sys
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))

from zhipuai import ZhipuAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_api():
    """测试API调用."""
    
    print("\n" + "="*80)
    print("智谱AI API 直接测试")
    print("="*80)
    
    # 获取API Key
    api_key = os.getenv("ZAI_API_KEY") or os.getenv("ZHIPU_API_KEY")
    
    if not api_key:
        print("\n❌ 未找到API Key，请在.env中设置ZAI_API_KEY或ZHIPU_API_KEY")
        return
    
    print(f"\n✅ API Key已找到: {api_key[:10]}...")
    
    # 初始化客户端
    client = ZhipuAI(api_key=api_key)
    print("✅ 客户端初始化成功")
    
    # 测试1: 简单问题
    print("\n" + "-"*80)
    print("【测试1】简单问题")
    print("-"*80)
    
    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {"role": "user", "content": "你好，1+1等于几？"}
            ],
            max_tokens=50,
        )
        
        print(f"✅ API调用成功")
        print(f"  Response: {response}")
        if response.choices:
            content = response.choices[0].message.content
            print(f"  Content: {content}")
        else:
            print(f"  ⚠️  No choices in response")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return
    
    # 测试2: 类似HyDE的prompt（第一个版本）
    print("\n" + "-"*80)
    print("【测试2】HyDE风格prompt - 版本1")
    print("-"*80)
    
    query = "主角是谁？"
    
    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是小说分析助手。请将用户的简短问题扩展成一段包含上下文和可能答案形式的描述。"
                },
                {
                    "role": "user",
                    "content": f"""请将下面的问题扩展成一段更详细的描述，包含可能的答案形式和相关背景。

原问题：{query}

扩展描述："""
                }
            ],
            temperature=0.8,
            max_tokens=200,
        )
        
        print(f"✅ API调用成功")
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content
            if content:
                print(f"  Content length: {len(content)}")
                print(f"  Content: {content}")
            else:
                print(f"  ⚠️  Content is empty!")
                print(f"  Full response: {response}")
        else:
            print(f"  ⚠️  No choices or message in response")
            print(f"  Full response: {response}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 最简单的prompt
    print("\n" + "-"*80)
    print("【测试3】最简单prompt")
    print("-"*80)
    
    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {
                    "role": "user",
                    "content": f"请用50-100字扩写这个问题，添加更多细节和上下文：\n\n{query}\n\n扩写："
                }
            ],
            temperature=0.7,
            max_tokens=150,
        )
        
        print(f"✅ API调用成功")
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content
            if content:
                print(f"  Content length: {len(content)}")
                print(f"  Content: {content}")
            else:
                print(f"  ⚠️  Content is empty!")
                print(f"  Full response: {response}")
        else:
            print(f"  ⚠️  No choices or message in response")
            print(f"  Full response: {response}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试4: 使用glm-4-flash
    print("\n" + "-"*80)
    print("【测试4】使用glm-4-flash模型")
    print("-"*80)
    
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "user",
                    "content": f"请用50-100字扩写这个问题：{query}"
                }
            ],
            temperature=0.7,
            max_tokens=150,
        )
        
        print(f"✅ API调用成功")
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content
            if content:
                print(f"  Content length: {len(content)}")
                print(f"  Content: {content}")
            else:
                print(f"  ⚠️  Content is empty!")
                print(f"  Full response: {response}")
        else:
            print(f"  ⚠️  No choices or message in response")
            print(f"  Full response: {response}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
    
    print("\n💡 建议:")
    print("  1. 如果测试1成功，说明API连接正常")
    print("  2. 如果测试2-3失败（返回空），可能是prompt或模型的问题")
    print("  3. 如果测试4成功，建议在rag_service.py中改用glm-4-flash")
    print("  4. 如果所有测试都返回空，请检查API账户配置或联系智谱支持")


if __name__ == "__main__":
    try:
        test_api()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()

