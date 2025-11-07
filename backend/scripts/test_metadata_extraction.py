"""测试元数据提取功能."""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.metadata_extraction_service import MetadataExtractionService
from loguru import logger


# 测试文本样本
TEST_SAMPLES = [
    {
        "name": "对话场景",
        "text": """
        "你为什么要这样对我？"李明愤怒地质问道。
        
        张华冷冷一笑，"因为你背叛了我们。"
        
        "我没有！"李明辩解道，但声音却有些颤抖。
        
        两人对峙着，空气中弥漫着紧张的气氛。
        """,
    },
    {
        "name": "动作场景",
        "text": """
        剑光一闪，张无忌飞身跃起，手中倚天剑划出一道优美的弧线。
        敌人惊呼一声，急忙闪避，却还是被剑气擦伤了肩膀。
        张无忌紧追不舍，连续施展七招太极剑法，步步紧逼。
        对方节节败退，眼看就要落败。
        """,
    },
    {
        "name": "描述场景",
        "text": """
        夕阳西下，晚霞染红了半边天空。
        远处的群山在暮色中显得格外苍茫。
        一条小溪从山间蜿蜒流淌，水面上泛着金色的光芒。
        空气中飘散着淡淡的花香，让人心旷神怡。
        """,
    },
    {
        "name": "心理场景",
        "text": """
        李华站在十字路口，内心充满了矛盾。
        是选择安稳的生活，还是追求自己的梦想？
        他想起了父母的期望，又想到了自己多年的坚持。
        这个决定，将会改变他的一生。他深深地叹了口气。
        """,
    },
    {
        "name": "悲伤场景",
        "text": """
        她跪在墓碑前，泪水止不住地流淌。
        "爷爷，我来看你了。"她哽咽着说。
        风吹过，带起几片落叶，仿佛在回应她的悲伤。
        她轻轻抚摸着墓碑上的名字，心如刀绞。
        """,
    },
    {
        "name": "温馨场景",
        "text": """
        妈妈端来热气腾腾的饺子，笑着说："快趁热吃。"
        一家人围坐在餐桌旁，谈笑风生。
        孩子们争着讲学校里的趣事，老人慈祥地听着。
        温暖的灯光下，这是最平凡也最幸福的时刻。
        """,
    },
]


async def test_metadata_extraction():
    """测试元数据提取功能."""
    
    logger.info("=" * 80)
    logger.info("开始测试元数据提取功能")
    logger.info("=" * 80)
    
    # 初始化服务
    service = MetadataExtractionService()
    
    if not service.client:
        logger.error("❌ API密钥未配置，无法进行测试")
        logger.info("请在 .env 文件中配置 ZAI_API_KEY 或 ZHIPU_API_KEY")
        return
    
    logger.info(f"✅ 服务初始化成功")
    logger.info(f"   - 元数据提取: {'启用' if service.enabled else '禁用'}")
    logger.info(f"   - 使用模型: {service.extraction_model}")
    logger.info("")
    
    # 测试每个样本
    total_tests = len(TEST_SAMPLES)
    successful_tests = 0
    
    for idx, sample in enumerate(TEST_SAMPLES, 1):
        logger.info(f"[{idx}/{total_tests}] 测试样本: {sample['name']}")
        logger.info("-" * 80)
        logger.info(f"文本内容:\n{sample['text'].strip()}")
        logger.info("")
        
        try:
            # 提取元数据
            metadata = await service.extract_metadata(sample['text'])
            
            if metadata:
                successful_tests += 1
                logger.info("✅ 元数据提取成功:")
                logger.info(f"   - 角色: {metadata.characters}")
                logger.info(f"   - 关键词: {metadata.keywords}")
                logger.info(f"   - 摘要: {metadata.summary}")
                logger.info(f"   - 场景类型: {metadata.scene_type}")
                logger.info(f"   - 情感基调: {metadata.emotional_tone}")
            else:
                logger.warning("⚠️  元数据提取失败（返回None）")
        
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
        
        logger.info("")
    
    # 汇总结果
    logger.info("=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)
    logger.info(f"总测试数: {total_tests}")
    logger.info(f"成功: {successful_tests}")
    logger.info(f"失败: {total_tests - successful_tests}")
    logger.info(f"成功率: {successful_tests / total_tests * 100:.1f}%")
    logger.info("")


async def test_batch_extraction():
    """测试批量提取功能."""
    
    logger.info("=" * 80)
    logger.info("测试批量元数据提取")
    logger.info("=" * 80)
    
    service = MetadataExtractionService()
    
    if not service.client:
        logger.error("❌ API密钥未配置，跳过批量测试")
        return
    
    # 准备批量文本
    texts = [sample['text'] for sample in TEST_SAMPLES]
    
    logger.info(f"准备批量提取 {len(texts)} 个文本的元数据...")
    logger.info("")
    
    try:
        # 批量提取
        results = await service.extract_metadata_batch(texts, batch_size=3)
        
        logger.info(f"✅ 批量提取完成")
        logger.info(f"   - 总数: {len(results)}")
        logger.info(f"   - 成功: {sum(1 for r in results if r)}")
        logger.info(f"   - 失败: {sum(1 for r in results if not r)}")
        logger.info("")
        
        # 显示部分结果
        for idx, (sample, metadata) in enumerate(zip(TEST_SAMPLES, results)):
            if metadata:
                logger.info(f"[{idx + 1}] {sample['name']}:")
                logger.info(f"    场景={metadata.scene_type}, 情感={metadata.emotional_tone}")
        
    except Exception as e:
        logger.error(f"❌ 批量提取失败: {e}")
    
    logger.info("")


async def test_rule_based_extraction():
    """测试基于规则的元数据提取（不调用LLM）."""
    
    logger.info("=" * 80)
    logger.info("测试基于规则的元数据提取（降级方案）")
    logger.info("=" * 80)
    
    service = MetadataExtractionService()
    
    # 测试第一个样本
    sample = TEST_SAMPLES[0]
    logger.info(f"测试样本: {sample['name']}")
    logger.info(f"文本: {sample['text'].strip()[:100]}...")
    logger.info("")
    
    try:
        metadata = await service.extract_simple_metadata(sample['text'])
        
        logger.info("✅ 规则提取成功:")
        logger.info(f"   - 角色: {metadata.characters}")
        logger.info(f"   - 关键词: {metadata.keywords}")
        logger.info(f"   - 摘要: {metadata.summary}")
        logger.info(f"   - 场景类型: {metadata.scene_type}")
        logger.info(f"   - 情感基调: {metadata.emotional_tone}")
    
    except Exception as e:
        logger.error(f"❌ 规则提取失败: {e}")
    
    logger.info("")


async def main():
    """主测试函数."""
    
    logger.info("🚀 元数据提取功能测试")
    logger.info("")
    
    # 1. 测试单个提取
    await test_metadata_extraction()
    
    # 2. 测试批量提取
    await test_batch_extraction()
    
    # 3. 测试规则提取（降级方案）
    await test_rule_based_extraction()
    
    logger.info("=" * 80)
    logger.info("✅ 所有测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

