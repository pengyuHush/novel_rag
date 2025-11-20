"""
实体属性提取器 - 从上下文中提取实体属性

功能:
- 提取角色性别
- 提取角色阵营/势力
- 提取角色职业/身份
- 提取角色实力等级
"""

import json
import asyncio
import logging
from typing import List, Dict, Optional, Tuple

from app.services.zhipu_client import get_zhipu_client
from app.services.batch_api_client import get_batch_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class EntityAttributeExtractor:
    """提取实体的属性（性别、阵营等）"""
    
    def __init__(self):
        """初始化属性提取器"""
        self.llm_client = get_zhipu_client()
    
    async def extract_attributes(
        self,
        entity_name: str,
        entity_type: str,
        contexts: List[str]
    ) -> Dict:
        """
        从上下文中提取实体属性
        
        Args:
            entity_name: 实体名称
            entity_type: 实体类型（characters/locations/organizations）
            contexts: 实体出现的典型上下文（3-5个片段）
        
        Returns:
            {
                "性别": "男",
                "阵营": "主角方",
                "职业": "炼药师",
                "实力": "斗圣"
            }
        """
        if entity_type != 'characters':
            return {}  # 仅处理角色
        
        if not contexts or len(contexts) == 0:
            return {}
        
        # 构建提示词
        context_text = ""
        for i, ctx in enumerate(contexts[:3], 1):
            context_text += f"\n【片段{i}】{ctx[:200]}\n"
        
        prompt = f"""你是网络小说角色分析专家。请从以下文本中提取"{entity_name}"的基本属性。

文本片段：
{context_text}

请提取以下属性（如文本中未明确提及则省略该字段）：
- **性别**：男/女/未知
- **阵营**：角色所属的势力、门派或阵营
- **职业**：角色的职业、身份或角色定位
- **实力**：角色的实力等级、修为境界

**要求**：
1. 只提取文本中明确提到的信息
2. 不要推测或猜测
3. 如果某个属性完全没有提及，不要包含该字段
4. 保持简洁，每个属性不超过10个字

**输出格式（必须是纯JSON）**：
{{"性别": "男", "阵营": "萧家", "职业": "炼药师", "实力": "斗者"}}

如果没有任何属性信息，输出空对象：{{}}

请分析："""
        
        content = ""  # 初始化，避免在异常处理中未定义
        try:
            response = await asyncio.to_thread(
                self.llm_client.chat_completion,
                messages=[{"role": "user", "content": prompt}],
                model="GLM-4.5-Flash",
                max_tokens=256,  # 增加token限制，避免JSON被截断
                temperature=0.3,
                thinking={"type": "disabled"}  # 禁用思考模式，直接输出JSON
            )
            
            content = response.get('content', '').strip()
            
            # 检查空响应
            if not content:
                logger.warning(f"LLM返回空内容，实体: {entity_name}")
                return {}
            
            # 提取JSON（可能包含在代码块中）
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # 再次检查提取后是否为空
            if not content:
                logger.warning(f"提取JSON后为空，原始内容: {response.get('content', '')[:100]}")
                return {}
            
            attributes = json.loads(content)
            
            # 验证并清理属性
            valid_attributes = {}
            if isinstance(attributes, dict):
                for key, value in attributes.items():
                    if value and isinstance(value, str) and len(value) <= 20:
                        valid_attributes[key] = value
            
            return valid_attributes
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}, 内容: {content[:100]}")
            return {}
        except Exception as e:
            logger.error(f"属性提取失败: {e}")
            return {}
    
    async def extract_batch(
        self,
        tasks: List[tuple],
        max_concurrency: Optional[int] = None,
        use_batch_api: bool = False
    ) -> Tuple[List[Dict], Dict]:
        """
        批量提取实体属性
        
        Args:
            tasks: [(entity_name, entity_type, contexts), ...]
            max_concurrency: 最大并发数（仅在use_batch_api=False时生效），默认使用配置值
            use_batch_api: 是否使用Batch API
        
        Returns:
            Tuple[List[Dict], Dict]: (属性字典列表, token统计)
        """
        if use_batch_api:
            return await self._extract_batch_with_batch_api(tasks)
        
        # 使用速率限制的并发控制
        max_concurrency = max_concurrency or settings.graph_attribute_concurrency
        
        logger.info(f"📊 分批处理 {len(tasks)} 个实体属性提取（并发数：{max_concurrency}，每批间隔1秒）...")
        
        # 分批处理，每批max_concurrency个任务
        results = []
        for batch_idx in range(0, len(tasks), max_concurrency):
            batch = tasks[batch_idx:batch_idx + max_concurrency]
            batch_num = batch_idx // max_concurrency + 1
            total_batches = (len(tasks) + max_concurrency - 1) // max_concurrency
            
            logger.info(f"  处理第 {batch_num}/{total_batches} 批 ({len(batch)} 个任务)...")
            
            # 批内任务并发执行
            batch_results = await asyncio.gather(
                *[self.extract_attributes(entity_name, entity_type, contexts) 
                  for entity_name, entity_type, contexts in batch],
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
                logger.error(f"属性提取任务 {i} 失败: {result}")
                valid_results.append({})
            else:
                valid_results.append(result)
        
        # 统计提取结果
        extracted_count = sum(1 for r in valid_results if r)
        logger.info(f"✅ 属性提取完成，成功提取 {extracted_count}/{len(tasks)} 个实体的属性")
        
        # 实时API模式：估算token消耗
        from app.utils.token_counter import get_token_counter
        token_counter = get_token_counter()
        
        total_input_tokens = 0
        for entity_name, entity_type, contexts in tasks:
            # 估算prompt token（包含指令+上下文）
            prompt = f"角色名：{entity_name}\n类型：{entity_type}\n上下文：{''.join(contexts)}"
            total_input_tokens += token_counter.count_tokens(prompt)
        
        # 估算输出token（属性通常较短，平均100 tokens）
        total_output_tokens = extracted_count * 100
        
        token_stats = {
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens
        }
        
        logger.info(f"📊 估算Token消耗: input={total_input_tokens}, output={total_output_tokens}, total={token_stats['total_tokens']}")
        
        return valid_results, token_stats
    
    async def _extract_batch_with_batch_api(
        self,
        tasks: List[tuple]
    ) -> Tuple[List[Dict], Dict]:
        """
        使用Batch API批量提取属性
        
        Args:
            tasks: [(entity_name, entity_type, contexts), ...]
        
        Returns:
            Tuple[List[Dict], Dict]: (属性字典列表, token统计)
        """
        logger.info(f"🚀 使用Batch API提取 {len(tasks)} 个实体的属性（无并发限制，免费）...")
        
        # 检查是否超过智谱AI Batch API限制（Chat模型：50,000个请求/批次）
        if len(tasks) > 50000:
            logger.error(f"❌ 实体数量({len(tasks)})超过Batch API限制(50,000)，这种情况极其罕见")
            # 理论上不会发生（小说通常只有几百个实体），但添加防护
            logger.error(f"   建议：联系开发者或手动关闭Batch API模式")
            raise ValueError(f"实体数量超过Batch API限制: {len(tasks)} > 50,000")
        
        # 1. 构建Batch API任务
        batch_tasks = []
        
        for i, (entity_name, entity_type, contexts) in enumerate(tasks):
            if entity_type != 'characters':
                continue  # 仅处理角色
            
            # 构建Prompt
            context_text = ""
            for j, ctx in enumerate(contexts[:3], 1):
                context_text += f"\n【片段{j}】{ctx[:200]}\n"
            
            prompt = f"""你是网络小说角色分析专家。请从以下文本中提取"{entity_name}"的基本属性。

文本片段：
{context_text}

请提取以下属性（如文本中未明确提及则省略该字段）：
- **性别**：男/女/未知
- **阵营**：角色所属的势力、门派或阵营
- **职业**：角色的职业、身份或角色定位
- **实力**：角色的实力等级、修为境界

**要求**：
1. 只提取文本中明确提到的信息
2. 不要推测或猜测
3. 如果某个属性完全没有提及，不要包含该字段
4. 保持简洁，每个属性不超过10个字

**输出格式（必须是纯JSON）**：
{{"性别": "男", "阵营": "萧家", "职业": "炼药师", "实力": "斗者"}}

如果没有任何属性信息，输出空对象：{{}}

请分析："""
            
            custom_id = f"attribute-{i}-{entity_name}"
            
            batch_tasks.append({
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v4/chat/completions",
                "body": {
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                }
            })
        
        if not batch_tasks:
            logger.info("没有需要提取属性的角色")
            empty_stats = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            return [{}] * len(tasks), empty_stats
        
        # 2. 提交Batch API
        batch_client = get_batch_client()
        
        def progress_callback(batch_id, status, progress, completed, total, failed):
            logger.info(f"📊 Batch API进度: {status} | {completed}/{total} ({progress*100:.1f}%) | 失败: {failed}")
        
        try:
            results_map, token_stats = await asyncio.to_thread(
                batch_client.submit_and_wait,
                batch_tasks,
                check_interval=30,
                progress_callback=progress_callback
            )
        except Exception as e:
            logger.error(f"❌ Batch API调用失败: {e}")
            empty_stats = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            return [{}] * len(tasks), empty_stats
        
        # 3. 解析结果并按原顺序返回
        valid_results = []
        for i, (entity_name, entity_type, contexts) in enumerate(tasks):
            if entity_type != 'characters':
                valid_results.append({})
                continue
            
            custom_id = f"attribute-{i}-{entity_name}"
            
            if custom_id in results_map:
                result = results_map[custom_id]
                
                if result['status'] == 'success':
                    try:
                        content = result['content'].strip()
                        
                        if not content:
                            valid_results.append({})
                            continue
                        
                        # 提取JSON
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        if not content:
                            valid_results.append({})
                            continue
                        
                        attributes = json.loads(content)
                        
                        # 验证并清理属性
                        valid_attrs = {}
                        if isinstance(attributes, dict):
                            for key, value in attributes.items():
                                if value and isinstance(value, str) and len(value) <= 20:
                                    valid_attrs[key] = value
                        
                        valid_results.append(valid_attrs)
                    except Exception as e:
                        logger.warning(f"解析属性失败: {e}")
                        valid_results.append({})
                else:
                    valid_results.append({})
            else:
                valid_results.append({})
        
        # 统计提取结果
        extracted_count = sum(1 for r in valid_results if r)
        logger.info(f"✅ Batch API属性提取完成，成功提取 {extracted_count}/{len(tasks)} 个实体的属性")
        logger.info(f"📊 属性提取Token统计: {token_stats}")
        
        return valid_results, token_stats


# 全局实例
_attribute_extractor = None

def get_attribute_extractor() -> EntityAttributeExtractor:
    """获取属性提取器单例"""
    global _attribute_extractor
    if _attribute_extractor is None:
        _attribute_extractor = EntityAttributeExtractor()
    return _attribute_extractor

