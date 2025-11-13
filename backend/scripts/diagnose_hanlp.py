"""
HanLP 实体提取诊断工具

运行方式:
  cd backend
  python scripts/diagnose_hanlp.py
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("\n" + "="*60)
print("HanLP 实体提取诊断工具")
print("="*60 + "\n")

# 测试1: 检查 HanLP 是否安装
print("【测试1】检查 HanLP 是否安装...")
try:
    import hanlp
    print("✅ HanLP 已安装")
    print(f"   版本: {hanlp.__version__}")
except ImportError as e:
    print("❌ HanLP 未安装")
    print(f"   错误: {e}")
    print("\n解决方案:")
    print("  poetry add hanlp")
    sys.exit(1)

# 测试2: 检查模型是否可用
print("\n【测试2】检查 HanLP 模型...")
try:
    print("   正在加载模型...")
    model = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
    print("✅ 模型加载成功")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    print("\n可能原因:")
    print("  1. 首次运行需要下载模型（约500MB）")
    print("  2. 网络连接问题")
    print("  3. 磁盘空间不足")
    sys.exit(1)

# 测试3: 测试简单的实体提取
print("\n【测试3】测试实体提取...")
test_texts = [
    "萧炎是云岚宗的弟子，他在乌坦城长大。",
    "张三在北京大学学习计算机科学。",
    "小明、小红和小刚是好朋友。",
    "李白是唐代著名诗人，出生于四川江油。",  # 历史人物
]

for i, text in enumerate(test_texts, 1):
    print(f"\n   测试文本 {i}: {text}")
    try:
        result = model(text, tasks='ner')
        print(f"   返回字段: {list(result.keys())}")
        
        # 尝试获取 NER 结果
        ner_results = None
        ner_key = None
        for key in ['ner/msra', 'ner/pku', 'ner/ontonotes', 'ner']:
            if key in result:
                ner_results = result[key]
                ner_key = key
                break
        
        if ner_results:
            print(f"   NER 字段: {ner_key}")
            print(f"   识别到 {len(ner_results)} 个实体:")
            
            # 输出原始格式
            print(f"   原始结果: {ner_results[:3]}...")  # 显示前3个
            
            # 解析实体
            for item in ner_results:
                if isinstance(item, (list, tuple)):
                    if len(item) >= 2:
                        entity_name = item[0]
                        entity_type = item[1]
                        extra_info = item[2:] if len(item) > 2 else ""
                        print(f"     - {entity_name} ({entity_type}) {extra_info}")
                    else:
                        print(f"     - 格式异常: {item}")
                else:
                    print(f"     - 未识别格式: {type(item)} = {item}")
        else:
            print(f"   ⚠️ 未找到 NER 结果")
            print(f"   可用字段详情:")
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"     {key}: {type(value[0])} x {len(value)}")
                else:
                    print(f"     {key}: {type(value)}")
            
    except Exception as e:
        print(f"   ❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()

# 测试4: 测试客户端封装
print("\n【测试4】测试 HanLPClient 封装...")
try:
    from app.services.nlp.hanlp_client import get_hanlp_client
    
    client = get_hanlp_client()
    
    if not client.is_available():
        print("❌ HanLPClient 不可用")
        sys.exit(1)
    
    print("✅ HanLPClient 可用")
    
    # 测试提取
    test_text = "萧炎是云岚宗的弟子，他在乌坦城长大，后来加入了迦南学院。"
    print(f"\n   测试文本: {test_text}")
    
    entities = client.extract_entities(test_text)
    print(f"\n   提取结果:")
    print(f"     角色: {entities.get('characters', [])}")
    print(f"     地点: {entities.get('locations', [])}")
    print(f"     组织: {entities.get('organizations', [])}")
    
    total = sum(len(v) for v in entities.values())
    if total > 0:
        print(f"\n✅ 成功提取 {total} 个实体")
    else:
        print(f"\n⚠️ 未提取到任何实体")
        print("\n可能原因:")
        print("  1. 实体类型映射不正确")
        print("  2. 文本过短或不包含命名实体")
        print("  3. 模型对中文支持有限")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试5: 测试小说文本片段
print("\n【测试5】测试小说文本片段...")
print("\n请粘贴一段小说文本进行测试（按 Ctrl+C 跳过）:")
print("示例: 萧炎站在云岚宗的大殿中，望着面前的纳兰嫣然。")
print("-" * 60)

try:
    user_text = input()
    if user_text.strip():
        from app.services.nlp.hanlp_client import get_hanlp_client
        client = get_hanlp_client()
        entities = client.extract_entities(user_text)
        
        print(f"\n提取结果:")
        print(f"  角色: {entities.get('characters', [])}")
        print(f"  地点: {entities.get('locations', [])}")
        print(f"  组织: {entities.get('organizations', [])}")
        
        total = sum(len(v) for v in entities.values())
        print(f"\n共提取 {total} 个实体")
except KeyboardInterrupt:
    print("\n跳过自定义文本测试")
except Exception as e:
    print(f"\n测试失败: {e}")

print("\n" + "="*60)
print("诊断完成")
print("="*60 + "\n")

