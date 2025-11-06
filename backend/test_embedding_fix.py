"""测试embedding修复是否正常工作."""

import asyncio

from loguru import logger

from app.core.config import settings
from app.services.rag_service import RAGService


async def test_embedding():
    """测试embedding功能."""
    logger.info("=" * 60)
    logger.info("测试智谱AI Embedding配置")
    logger.info("=" * 60)

    # 显示配置
    logger.info(f"CHUNK_SIZE: {settings.CHUNK_SIZE} 字符")
    logger.info(f"CHUNK_OVERLAP: {settings.CHUNK_OVERLAP} 字符")
    logger.info(f"EMBEDDING_BATCH_SIZE: {settings.EMBEDDING_BATCH_SIZE}")
    logger.info("")

    # 创建RAG服务
    rag = RAGService()

    if not rag.client:
        logger.error("❌ 智谱AI客户端未配置")
        logger.error("请设置环境变量 ZAI_API_KEY 或 ZHIPU_API_KEY")
        return

    logger.info("✅ 智谱AI客户端已配置")
    logger.info("")

    # 测试1: 单个短文本
    logger.info("测试1: 单个短文本 (100字符)")
    try:
        test_text_1 = "这是一段测试文本。" * 10  # 100字符左右
        logger.info(f"文本长度: {len(test_text_1)} 字符")
        embeddings_1 = await rag.embed_texts([test_text_1])
        logger.info(f"✅ 成功生成embedding，向量维度: {len(embeddings_1[0])}")
    except Exception as e:
        logger.error(f"❌ 失败: {e}")
    logger.info("")

    # 测试2: 单个长文本 (接近限制)
    logger.info("测试2: 单个长文本 (800字符，等于CHUNK_SIZE)")
    try:
        test_text_2 = "这是一段较长的测试文本，用于测试是否能处理接近限制的文本。" * 20  # 约800字符
        logger.info(f"文本长度: {len(test_text_2)} 字符")
        embeddings_2 = await rag.embed_texts([test_text_2])
        logger.info(f"✅ 成功生成embedding，向量维度: {len(embeddings_2[0])}")
    except Exception as e:
        logger.error(f"❌ 失败: {e}")
    logger.info("")

    # 测试3: 批量文本 (使用配置的batch_size)
    logger.info(f"测试3: 批量文本 ({settings.EMBEDDING_BATCH_SIZE}个文本)")
    try:
        test_texts_3 = [f"这是第{i+1}段测试文本。" * 20 for i in range(settings.EMBEDDING_BATCH_SIZE)]
        total_chars = sum(len(t) for t in test_texts_3)
        logger.info(f"文本数量: {len(test_texts_3)}")
        logger.info(f"总字符数: {total_chars}")
        logger.info(f"平均长度: {total_chars // len(test_texts_3)} 字符")
        embeddings_3 = await rag.embed_texts(test_texts_3)
        logger.info(f"✅ 成功生成{len(embeddings_3)}个embeddings")
    except Exception as e:
        logger.error(f"❌ 失败: {e}")
    logger.info("")

    # 测试4: 超长文本 (应该被自动截断)
    logger.info("测试4: 超长文本 (3500字符，应该被自动截断到3000)")
    try:
        test_text_4 = "这是一段超长的测试文本，应该会被自动截断。" * 150  # 约3500字符
        original_length = len(test_text_4)
        logger.info(f"原始长度: {original_length} 字符")
        embeddings_4 = await rag.embed_texts([test_text_4])
        logger.info(f"✅ 成功生成embedding (文本已被截断)")
        logger.info(f"⚠️  建议减小CHUNK_SIZE以避免截断")
    except Exception as e:
        logger.error(f"❌ 失败: {e}")
    logger.info("")

    # 测试5: 模拟真实场景 (多个800字符的chunk)
    logger.info(f"测试5: 模拟真实场景 ({settings.EMBEDDING_BATCH_SIZE}个800字符的chunk)")
    try:
        # 模拟真实的小说chunk
        sample_text = """
        在那个风雨交加的夜晚，主人公终于来到了传说中的古堡前。
        城堡的大门紧闭，四周一片寂静，只有风声和雨声在耳边回荡。
        他深吸一口气，推开了那扇沉重的大门，开始了他的冒险之旅。
        """ * 20  # 每个约800字符

        test_texts_5 = [sample_text for _ in range(settings.EMBEDDING_BATCH_SIZE)]
        logger.info(f"文本数量: {len(test_texts_5)}")
        logger.info(f"每个文本长度: {len(test_texts_5[0])} 字符")

        embeddings_5 = await rag.embed_texts(test_texts_5)
        logger.info(f"✅ 成功生成{len(embeddings_5)}个embeddings")
        logger.info(f"✅ 配置正常，可以处理真实的小说文本")
    except Exception as e:
        logger.error(f"❌ 失败: {e}")
        logger.error(f"⚠️  如果失败，请尝试:")
        logger.error(f"   1. 减小CHUNK_SIZE (当前: {settings.CHUNK_SIZE})")
        logger.error(f"   2. 减小EMBEDDING_BATCH_SIZE (当前: {settings.EMBEDDING_BATCH_SIZE})")
    logger.info("")

    logger.info("=" * 60)
    logger.info("测试完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_embedding())

