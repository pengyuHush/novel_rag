"""
测试时间线功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json

def test_timeline(novel_id: int):
    """测试时间线 API"""
    print(f"\n{'='*60}")
    print(f"测试小说 {novel_id} 的时间线功能")
    print(f"{'='*60}\n")
    
    # 测试时间线 API
    url = f"http://localhost:8000/api/graph/timeline/{novel_id}"
    
    print(f"🔍 请求URL: {url}")
    
    try:
        response = requests.get(url, params={'max_events': 50})
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ 时间线数据获取成功！")
            print(f"\n📊 元数据:")
            print(f"   总事件数: {data['metadata']['total_events']}")
            print(f"   章节范围: {data['metadata']['chapter_range']}")
            
            events = data['events']
            if events:
                print(f"\n📅 前10个事件:")
                for i, event in enumerate(events[:10], 1):
                    print(f"\n   {i}. 第{event['chapterNum']}章 (序号:{event['narrativeOrder']})")
                    print(f"      描述: {event['description']}")
                    print(f"      类型: {event.get('eventType', 'N/A')}")
                    print(f"      重要性: {event.get('importance', 'N/A')}")
                
                # 检查数据格式
                print(f"\n✅ 数据格式检查:")
                first_event = events[0]
                required_fields = ['chapterNum', 'narrativeOrder', 'description']
                for field in required_fields:
                    if field in first_event:
                        print(f"   ✓ {field}: {type(first_event[field]).__name__}")
                    else:
                        print(f"   ✗ {field}: 缺失")
                
                # 统计事件类型
                event_types = {}
                for event in events:
                    event_type = event.get('eventType', 'unknown')
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                
                print(f"\n📈 事件类型统计:")
                for event_type, count in sorted(event_types.items(), key=lambda x: -x[1]):
                    print(f"   {event_type}: {count}")
            else:
                print("\n⚠️  没有事件数据")
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            print(f"   {response.text}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        novel_id = int(sys.argv[1])
    else:
        # 默认测试第一本小说
        novel_id = 1
    
    test_timeline(novel_id)

