"""
关系类型分类器 - 使用LLM识别实体间的具体关系类型

功能:
- 8种关系类型识别：师徒、盟友、敌对、亲属、恋人、同门、中立、共现
- Few-shot提示工程优化
- 智能章节采样
- 增强实体识别
- 并发批量处理
"""

import json
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.services.zhipu_client import get_zhipu_client
from app.services.batch_api_client import get_batch_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class RelationshipClassifier:
    """使用LLM识别角色间的关系类型"""
    
    RELATION_TYPES = [
        '师徒',      # 明确的师徒关系
        '盟友',      # 合作、友好关系
        '敌对',      # 对立、敌对关系
        '亲属',      # 家族、血缘关系
        '恋人',      # 恋爱关系
        '同门',      # 同一组织或门派
        '中立',      # 无明显关系倾向
        '共现'       # 仅共同出现，无明确关系
    ]
    
    def __init__(self):
        """初始化分类器"""
        self.llm_client = get_zhipu_client()
    
    async def classify_relationship(
        self,
        entity1: str,
        entity2: str,
        contexts: List[str],
        cooccurrence_count: int = 0,
        chapter_range: str = ""
    ) -> Dict:
        """
        使用GLM-4.5-Flash进行关系分类（已优化）
        
        优化点：
        1. Few-shot示例引导
        2. 详细的关系类型定义和关键词
        3. 更长的上下文（300字符）
        4. 更多片段（5个）
        5. 传递共现统计信息
        6. 降低temperature提高稳定性
        
        Args:
            entity1: 实体1名称
            entity2: 实体2名称
            contexts: 3-5个典型共现片段
            cooccurrence_count: 共现次数
            chapter_range: 章节范围
        
        Returns:
            {
                'relation_type': '师徒',
                'confidence': 0.9,
                'reasoning': '...'
            }
        """
        # 构建增强Prompt（更长上下文）
        context_text = ""
        for i, ctx in enumerate(contexts[:5], 1):
            context_text += f"\n【片段{i}】{ctx[:300]}\n"
        
        # Few-shot示例
        few_shot = """## 示例分析

示例1：
【片段】萧炎恭敬地对着戒指行礼："师父，弟子明白了。"药老微笑道："孩子，修炼不可急躁。"之后药老传授萧炎炼药心法...
【判断】师徒（置信度0.98）- 明确的师父称呼和传授关系

示例2：
【片段】萧炎和萧薰儿并肩而立，两人十指相扣。薰儿温柔地看着萧炎，眼中满是爱意...
【判断】恋人（置信度0.95）- 明显的亲密互动和感情表达

示例3：
【片段】魂天帝冷笑："萧炎，今日就是你的死期！"萧炎怒吼："魂族害我家族，不共戴天！"两人展开生死搏斗...
【判断】敌对（置信度0.99）- 明确的仇恨和生死对立

示例4：
【片段】萧炎走进拍卖会，看到主持人米特尔雅妃正在台上介绍物品。萧炎坐在角落里...
【判断】共现（置信度0.70）- 仅在同一场景，无实质互动

"""
        
        prompt = f"""{few_shot}

## 现在请分析以下关系

你是网络小说关系分析专家。请仔细分析"{entity1}"和"{entity2}"的关系类型。

**分析材料**
两个角色共同出现 {cooccurrence_count} 次（{chapter_range}），以下是典型场景：
{context_text}

**关系类型定义（请严格按照定义选择）**

1. **师徒**：明确的师承关系，有传授知识/技能的描述
   - 关键词：师父、徒弟、传授、指导、教导、拜师
   - 示例：药老传授萧炎炼药术

2. **盟友**：合作、互助、共同战斗的关系
   - 关键词：联手、合作、并肩作战、帮助、结盟
   - 示例：两人联手对抗敌人

3. **敌对**：明确的对立、仇恨、战斗关系
   - 关键词：敌人、对手、仇恨、战斗、对抗、你死我活
   - 示例：不共戴天的死敌

4. **亲属**：血缘、家族关系
   - 关键词：父子、兄弟、姐妹、亲人、家族
   - 示例：亲生父子、亲兄弟

5. **恋人**：明确的恋爱、情侣关系
   - 关键词：爱慕、恋人、情侣、喜欢、相爱、表白
   - 示例：互相爱慕的情侣

6. **同门**：同一门派、组织、势力
   - 关键词：同门、师兄弟、同派、同一宗门
   - 示例：同为云岚宗弟子

7. **中立**：认识但无明显关系倾向
   - 特征：偶尔交集，关系不明确，无明显情感倾向
   - 示例：见过几面的熟人

8. **共现**：仅在同一场景出现，无实质互动
   - 特征：只是同时在场，无对话或互动，纯粹的背景角色
   - 示例：同在一个宴会上但无交流

**分析步骤**
1. 仔细阅读所有片段
2. 识别关键词和互动模式
3. 判断最主要的关系类型（如果有多种，选择最核心的）
4. 评估判断的置信度

**输出格式（必须是纯JSON）**
{{"relation_type": "师徒", "confidence": 0.95, "reasoning": "药老多次指导萧炎修炼，明确的师徒传承关系"}}

请分析："""
        
        content = ""  # 初始化，避免在异常处理中未定义
        try:
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                messages=[{"role": "user", "content": prompt}],
                model="GLM-4.5-Flash",  # 免费高速模型
                max_tokens=512,  # 增加token限制，避免JSON被截断
                temperature=0.1,  # 降低随机性，提高稳定性
                thinking={"type": "disabled"}  # 禁用思考模式，直接输出JSON
            )
            
            content = response.get('content', '').strip()
            
            # 检查内容是否为空
            if not content:
                logger.warning(f"LLM返回空内容，使用默认值")
                return {
                    'relation_type': '共现',
                    'confidence': 0.5,
                    'reasoning': 'LLM返回空内容'
                }
            
            # 提取JSON（可能包含在代码块中）
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # 再次检查提取后的内容
            if not content:
                logger.warning(f"提取JSON后内容为空，使用默认值")
                return {
                    'relation_type': '共现',
                    'confidence': 0.5,
                    'reasoning': '提取JSON失败'
                }
            
            result = json.loads(content)
            
            # 验证结果
            if 'relation_type' not in result:
                logger.warning(f"LLM返回缺少relation_type，使用默认值")
                result['relation_type'] = '共现'
            if 'confidence' not in result:
                result['confidence'] = 0.5
            if 'reasoning' not in result:
                result['reasoning'] = '自动分类'
            
            return result
            
        except json.JSONDecodeError as e:
            # JSON解析失败，尝试修复被截断的JSON
            logger.warning(f"JSON解析失败: {e}, 尝试修复...")
            
            # 尝试提取部分信息
            try:
                # 使用正则提取relation_type
                import re
                relation_match = re.search(r'"relation_type"\s*:\s*"([^"]+)"', content)
                confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', content)
                
                if relation_match:
                    return {
                        'relation_type': relation_match.group(1),
                        'confidence': float(confidence_match.group(1)) if confidence_match else 0.5,
                        'reasoning': 'JSON被截断，部分解析'
                    }
            except:
                pass
            
            logger.error(f"无法修复JSON，内容: {content[:200]}")
            return {
                'relation_type': '共现',
                'confidence': 0.5,
                'reasoning': 'JSON解析失败，使用默认值'
            }
        except Exception as e:
            logger.error(f"关系分类失败: {e}")
            return {
                'relation_type': '共现',
                'confidence': 0.5,
                'reasoning': f'分类失败: {str(e)}'
            }
    
    async def classify_batch(
        self,
        tasks: List[Tuple],
        max_concurrency: Optional[int] = None,
        use_batch_api: bool = False
    ) -> Tuple[List[Dict], Dict]:
        """
        批量并发分类关系
        
        Args:
            tasks: [(entity1, entity2, contexts, count, chapters), ...]
            max_concurrency: 最大并发数（仅在use_batch_api=False时生效），默认使用配置值
            use_batch_api: 是否使用Batch API
        
        Returns:
            Tuple[List[Dict], Dict]: (分类结果列表, token统计)
        """
        # 🎯 智能判断：请求数 < 阈值时使用实时API
        if len(tasks) < settings.batch_api_threshold:
            logger.info(f"📊 关系分类: 请求数({len(tasks)}) < 阈值({settings.batch_api_threshold})，使用实时API")
            use_batch_api = False
        elif use_batch_api:
            logger.info(f"📊 关系分类: 请求数({len(tasks)}) ≥ 阈值({settings.batch_api_threshold})，使用Batch API")
        
        if use_batch_api:
            return await self._classify_batch_with_batch_api(tasks)
        
        # 使用速率限制的并发控制
        max_concurrency = max_concurrency or settings.graph_relation_concurrency
        
        logger.info(f"📊 分批处理 {len(tasks)} 对关系分类（并发数：{max_concurrency}，每批间隔1秒）...")
        
        # 分批处理，每批max_concurrency个任务
        results = []
        for batch_idx in range(0, len(tasks), max_concurrency):
            batch = tasks[batch_idx:batch_idx + max_concurrency]
            batch_num = batch_idx // max_concurrency + 1
            total_batches = (len(tasks) + max_concurrency - 1) // max_concurrency
            
            logger.info(f"  处理第 {batch_num}/{total_batches} 批 ({len(batch)} 个任务)...")
            
            # 批内任务并发执行
            batch_results = await asyncio.gather(
                *[self.classify_relationship(
                    entity1, entity2, contexts, count, 
                    f"第{min(chapters)}章-第{max(chapters)}章"
                  ) for entity1, entity2, contexts, count, chapters in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
            
            # 批次间延迟，避免持续高频请求
            if batch_idx + max_concurrency < len(tasks):
                await asyncio.sleep(1.0)
        
        logger.info(f"✅ 所有批次处理完成")
        
        # 处理异常结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"分类任务 {i} 失败: {result}")
                valid_results.append({
                    'relation_type': '共现',
                    'confidence': 0.5,
                    'reasoning': f'分类失败: {str(result)}'
                })
            else:
                valid_results.append(result)
        
        # 统计分类结果
        type_counts = {}
        for result in valid_results:
            rel_type = result['relation_type']
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        logger.info(f"✅ 关系分类完成，类型分布: {type_counts}")
        
        # 实时API模式：估算token消耗
        from app.utils.token_counter import get_token_counter
        token_counter = get_token_counter()
        
        total_input_tokens = 0
        for entity1, entity2, contexts, count, chapters in tasks:
            # 估算prompt token（包含指令+上下文）
            prompt = f"角色1：{entity1}\n角色2：{entity2}\n共现次数：{count}\n上下文：{''.join(contexts[:3])}"
            total_input_tokens += token_counter.count_tokens(prompt)
        
        # 估算输出token（关系分类结果较短，平均80 tokens）
        total_output_tokens = len(valid_results) * 80
        
        token_stats = {
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens
        }
        
        logger.info(f"📊 估算Token消耗: input={total_input_tokens}, output={total_output_tokens}, total={token_stats['total_tokens']}")
        
        return valid_results, token_stats
    
    async def _classify_batch_with_batch_api(
        self,
        tasks: List[Tuple]
    ) -> Tuple[List[Dict], Dict]:
        """
        使用Batch API批量分类关系
        
        Args:
            tasks: [(entity1, entity2, contexts, count, chapters), ...]
        
        Returns:
            Tuple[List[Dict], Dict]: (分类结果列表, token统计)
        """
        logger.info(f"🚀 使用Batch API分类 {len(tasks)} 对关系（无并发限制，免费）...")
        
        # 检查是否超过智谱AI Batch API限制（Chat模型：50,000个请求/批次）
        if len(tasks) > 50000:
            logger.error(f"❌ 关系对数({len(tasks)})超过Batch API限制(50,000)，这种情况极其罕见")
            # 理论上不会发生（需要数千个实体才可能），但添加防护
            logger.error(f"   建议：联系开发者或手动关闭Batch API模式")
            raise ValueError(f"关系对数超过Batch API限制: {len(tasks)} > 50,000")
        
        # 1. 构建Batch API任务
        batch_tasks = []
        task_mapping = {}  # custom_id -> task_index
        
        for i, (entity1, entity2, contexts, count, chapters) in enumerate(tasks):
            chapter_range = f"第{min(chapters)}章-第{max(chapters)}章"
            
            # 构建Prompt
            context_text = ""
            for j, ctx in enumerate(contexts[:5], 1):
                context_text += f"\n【片段{j}】{ctx[:300]}\n"
            
            few_shot = """## 示例分析

示例1：
【片段】萧炎恭敬地对着戒指行礼："师父，弟子明白了。"药老微笑道："孩子，修炼不可急躁。"之后药老传授萧炎炼药心法...
【判断】师徒（置信度0.98）- 明确的师父称呼和传授关系

示例2：
【片段】萧炎和萧薰儿并肩而立，两人十指相扣。薰儿温柔地看着萧炎，眼中满是爱意...
【判断】恋人（置信度0.95）- 明显的亲密互动和感情表达

示例3：
【片段】魂天帝冷笑："萧炎，今日就是你的死期！"萧炎怒吼："魂族害我家族，不共戴天！"两人展开生死搏斗...
【判断】敌对（置信度0.99）- 明确的仇恨和生死对立

示例4：
【片段】萧炎走进拍卖会，看到主持人米特尔雅妃正在台上介绍物品。萧炎坐在角落里...
【判断】共现（置信度0.70）- 仅在同一场景，无实质互动

"""
            
            prompt = f"""{few_shot}

## 现在请分析以下关系

你是网络小说关系分析专家。请仔细分析"{entity1}"和"{entity2}"的关系类型。

**分析材料**
两个角色共同出现 {count} 次（{chapter_range}），以下是典型场景：
{context_text}

**关系类型定义（请严格按照定义选择）**

1. **师徒**：明确的师承关系，有传授知识/技能的描述
   - 关键词：师父、徒弟、传授、指导、教导、拜师

2. **盟友**：合作、互助、共同战斗的关系
   - 关键词：联手、合作、并肩作战、帮助、结盟

3. **敌对**：明确的对立、仇恨、战斗关系
   - 关键词：敌人、对手、仇恨、战斗、对抗、你死我活

4. **亲属**：血缘、家族关系
   - 关键词：父子、兄弟、姐妹、亲人、家族

5. **恋人**：明确的恋爱、情侣关系
   - 关键词：爱慕、恋人、情侣、喜欢、相爱、表白

6. **同门**：同一门派、组织、势力
   - 关键词：同门、师兄弟、同派、同一宗门

7. **中立**：认识但无明显关系倾向
   - 特征：偶尔交集，关系不明确，无明显情感倾向

8. **共现**：仅在同一场景出现，无实质互动
   - 特征：只是同时在场，无对话或互动，纯粹的背景角色

**输出格式（必须是纯JSON）**
{{"relation_type": "师徒", "confidence": 0.95, "reasoning": "药老多次指导萧炎修炼，明确的师徒传承关系"}}

请分析："""
            
            custom_id = f"relation-{i}-{entity1}-{entity2}"
            task_mapping[custom_id] = i
            
            batch_tasks.append({
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v4/chat/completions",
                "body": {
                    "model": "glm-4-flash",  # 使用免费的Flash模型
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 200
                }
            })
        
        # 2. 提交Batch API
        batch_client = get_batch_client()
        
        def progress_callback(batch_id, status, progress, completed, total, failed):
            logger.info(f"📊 Batch API进度: {status} | {completed}/{total} ({progress*100:.1f}%) | 失败: {failed}")
        
        try:
            results_map, token_stats = await asyncio.to_thread(
                batch_client.submit_and_wait,
                batch_tasks,
                check_interval=30,  # 每30秒检查一次
                progress_callback=progress_callback
            )
        except Exception as e:
            logger.error(f"❌ Batch API调用失败: {e}")
            # 降级到默认值
            empty_stats = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            default_results = [{'relation_type': '共现', 'confidence': 0.5, 'reasoning': f'Batch API失败: {str(e)}'} for _ in tasks]
            return default_results, empty_stats
        
        # 3. 解析结果并按原顺序返回
        valid_results = []
        for i in range(len(tasks)):
            custom_id = f"relation-{i}-{tasks[i][0]}-{tasks[i][1]}"
            
            if custom_id in results_map:
                result = results_map[custom_id]
                
                if result['status'] == 'success':
                    try:
                        content = result['content'].strip()
                        
                        # 提取JSON
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        parsed = json.loads(content)
                        
                        # 验证结果
                        if 'relation_type' not in parsed:
                            parsed['relation_type'] = '共现'
                        if 'confidence' not in parsed:
                            parsed['confidence'] = 0.5
                        if 'reasoning' not in parsed:
                            parsed['reasoning'] = '自动分类'
                        
                        valid_results.append(parsed)
                    except Exception as e:
                        logger.warning(f"解析结果失败: {e}, 内容: {result['content'][:100]}")
                        valid_results.append({
                            'relation_type': '共现',
                            'confidence': 0.5,
                            'reasoning': f'解析失败: {str(e)}'
                        })
                else:
                    logger.warning(f"任务失败: {custom_id}, 错误: {result.get('error')}")
                    valid_results.append({
                        'relation_type': '共现',
                        'confidence': 0.5,
                        'reasoning': f'API错误: {result.get("error")}'
                    })
            else:
                logger.warning(f"缺少结果: {custom_id}")
                valid_results.append({
                    'relation_type': '共现',
                    'confidence': 0.5,
                    'reasoning': '缺少结果'
                })
        
        # 统计分类结果
        type_counts = {}
        for result in valid_results:
            rel_type = result['relation_type']
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        logger.info(f"✅ Batch API关系分类完成，类型分布: {type_counts}")
        logger.info(f"📊 关系分类Token统计: {token_stats}")
        
        return valid_results, token_stats
    
    def _smart_chapter_sampling(
        self,
        chapter_nums: List[int],
        max_samples: int = 5
    ) -> List[int]:
        """
        智能章节采样：早期+中期+后期+均匀分布
        
        优化点：
        - 覆盖关系的整个时间跨度
        - 优先采样首次出现、中期、末次出现
        - 避免均匀采样错过关键章节
        
        Args:
            chapter_nums: 章节列表
            max_samples: 最大采样数
        
        Returns:
            采样后的章节列表
        """
        if len(chapter_nums) <= max_samples:
            return chapter_nums
        
        # 取首、中、尾各1个
        result = [
            chapter_nums[0],  # 首次出现
            chapter_nums[len(chapter_nums)//2],  # 中期
            chapter_nums[-1],  # 最后出现
        ]
        
        # 剩余位置均匀采样
        remaining = max_samples - 3
        if remaining > 0:
            step = (len(chapter_nums) - 1) // (remaining + 1)
            for i in range(1, remaining + 1):
                idx = i * step
                if idx < len(chapter_nums) and chapter_nums[idx] not in result:
                    result.append(chapter_nums[idx])
        
        return sorted(set(result))
    
    def _extract_paragraph_with_entities(
        self,
        content: str,
        entity1: str,
        entity2: str,
        chapter_num: int
    ) -> Optional[str]:
        """
        提取包含两个实体的段落（增强版）
        
        优化点：
        - 支持别名匹配（如"萧炎"→"萧"）
        - 更长的上下文窗口（400字符）
        - 更大的搜索范围（800字符内）
        
        Args:
            content: 章节内容
            entity1: 实体1
            entity2: 实体2
            chapter_num: 章节号
        
        Returns:
            提取的段落，格式："[第X章] ..."
        """
        # 考虑实体别名模式
        entity1_patterns = [
            entity1,
            entity1[:2] if len(entity1) >= 2 else entity1,  # 姓氏
        ]
        
        entity2_patterns = [
            entity2,
            entity2[:2] if len(entity2) >= 2 else entity2,  # 姓氏
        ]
        
        # 查找同时包含两个实体的位置
        lines = content.split('\n')
        best_match = None
        max_score = 0
        
        for line in lines:
            score = 0
            has_entity1 = any(p in line for p in entity1_patterns)
            has_entity2 = any(p in line for p in entity2_patterns)
            
            if has_entity1:
                score += 1
            if has_entity2:
                score += 1
            
            if score == 2 and score >= max_score:
                # 找到包含两个实体的行
                idx = content.find(line)
                if idx != -1:
                    # 提取前后各150字符
                    start = max(0, idx - 150)
                    end = min(len(content), idx + len(line) + 150)
                    context = content[start:end].strip()
                    
                    # 限制长度为400字符
                    if len(context) > 400:
                        context = context[:400] + "..."
                    
                    best_match = f"[第{chapter_num}章] {context}"
                    max_score = score
        
        if best_match:
            return best_match
        
        # 如果没找到同时包含的行，尝试查找附近的（范围扩大到800）
        idx1 = -1
        idx2 = -1
        
        for pattern in entity1_patterns:
            idx1 = content.find(pattern)
            if idx1 != -1:
                break
        
        for pattern in entity2_patterns:
            idx2 = content.find(pattern)
            if idx2 != -1:
                break
        
        if idx1 != -1 and idx2 != -1 and abs(idx1 - idx2) < 800:
            start = max(0, min(idx1, idx2) - 100)
            end = min(len(content), max(idx1, idx2) + 200)
            context = content[start:end].strip()
            
            if len(context) > 400:
                context = context[:400] + "..."
            
            return f"[第{chapter_num}章] {context}"
        
        return None


# 全局实例
_relation_classifier = None

def get_relation_classifier() -> RelationshipClassifier:
    """获取关系分类器单例"""
    global _relation_classifier
    if _relation_classifier is None:
        _relation_classifier = RelationshipClassifier()
    return _relation_classifier

