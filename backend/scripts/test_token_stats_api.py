"""
测试Token统计API
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json

def test_token_stats_api():
    """测试Token统计API"""
    print("\n" + "="*60)
    print("测试Token统计API")
    print("="*60 + "\n")
    
    url = "http://localhost:8000/api/stats/tokens"
    
    # 测试不同的时间段参数
    for period in ['all', 'month', 'week', 'day']:
        print(f"\n📊 测试 period={period}")
        print("-" * 40)
        
        try:
            response = requests.get(url, params={'period': period})
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ 请求成功")
                print(f"\n总统计:")
                print(f"  total_tokens: {data['total_tokens']}")
                print(f"  total_cost: ¥{data['total_cost']:.4f}")
                print(f"  period: {data['period']}")
                
                # 按模型分类
                print(f"\n按模型分类 (by_model):")
                if data['by_model']:
                    for model_name, stats in data['by_model'].items():
                        print(f"  {model_name}:")
                        print(f"    totalTokens: {stats.get('totalTokens', 0)}")
                        print(f"    totalCost: ¥{stats.get('totalCost', 0):.4f}")
                        print(f"    usageCount: {stats.get('usageCount', 0)}")
                else:
                    print("  ⚠️  没有数据")
                
                # 按操作分类
                print(f"\n按操作分类 (by_operation):")
                if data['by_operation']:
                    for operation_type, stats in data['by_operation'].items():
                        operation_name = '索引' if operation_type == 'index' else '查询'
                        print(f"  {operation_name} ({operation_type}):")
                        print(f"    totalTokens: {stats.get('totalTokens', 0)}")
                        print(f"    totalCost: ¥{stats.get('totalCost', 0):.4f}")
                        print(f"    operationCount: {stats.get('operationCount', 0)}")
                else:
                    print("  ⚠️  没有数据")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   {response.text}")
        
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_token_stats_api()

