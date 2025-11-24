"""
关系演变追踪器 - 追踪实体间关系随时间的演变

功能:
- 将关系时间跨度分段
- 检测每段的关系类型
- 识别关系类型变化节点
- 去重优化
"""

import logging
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session

from app.services.graph.relation_classifier import RelationshipClassifier
from app.models.database import Novel

logger = logging.getLogger(__name__)


class RelationshipEvolutionTracker:
    """追踪关系随时间的演变"""
    
    def __init__(self):
        """初始化演变追踪器"""
        self.classifier = RelationshipClassifier()
    
    async def track_evolution(
        self,
        entity1: str,
        entity2: str,
        all_chapters: List[int],
        novel: Novel,
        db: Session
    ) -> List[Dict]:
        """
        将章节分段，检测每段的关系类型
        
        Args:
            entity1: 实体1名称
            entity2: 实体2名称
            all_chapters: 所有共现章节列表
            novel: 小说对象
            db: 数据库会话
        
        Returns:
            [
                {"chapter": 10, "type": "陌生", "confidence": 0.8},
                {"chapter": 50, "type": "朋友", "confidence": 0.9},
                {"chapter": 120, "type": "盟友", "confidence": 0.95}
            ]
        """
        if not all_chapters:
            return []
        
        # 分段策略：按章节数量动态分段
        total_span = max(all_chapters) - min(all_chapters)
        
        if total_span <= 50:
            segments = 2  # 早期/后期
        elif total_span <= 200:
            segments = 3  # 早期/中期/后期
        else:
            segments = 5  # 细粒度分段
        
        segment_size = len(all_chapters) // segments
        if segment_size == 0:
            segment_size = 1
        
        evolution = []
        
        logger.debug(f"追踪 {entity1}-{entity2} 的演变，分{segments}段，每段约{segment_size}章")
        
        for i in range(segments):
            start_idx = i * segment_size
            end_idx = start_idx + segment_size if i < segments - 1 else len(all_chapters)
            segment_chapters = all_chapters[start_idx:end_idx]
            
            if not segment_chapters:
                continue
            
            # 智能采样该段的章节（取3个样本）
            sampled_chapters = self.classifier._smart_chapter_sampling(segment_chapters, max_samples=3)
            
            # 提取该段的上下文
            from app.services.indexing_service import get_indexing_service
            indexing_service = get_indexing_service()
            
            contexts = await indexing_service._extract_cooccurrence_contexts(
                entity1, entity2, sampled_chapters, novel, db
            )
            
            if not contexts:
                logger.debug(f"段{i+1}无法提取上下文，跳过")
                continue
            
            # 分类该段的关系类型
            chapter_range = f"第{min(segment_chapters)}章-第{max(segment_chapters)}章"
            classification = await self.classifier.classify_relationship(
                entity1, entity2, contexts, len(segment_chapters), chapter_range
            )
            
            # 记录演变点（使用该段的起始章节）
            evolution.append({
                "chapter": segment_chapters[0],
                "type": classification['relation_type'],
                "confidence": classification['confidence']
            })
            
            logger.debug(f"段{i+1}（第{segment_chapters[0]}章）: {classification['relation_type']} (置信度{classification['confidence']:.2f})")
        
        # 去重：只保留关系类型变化的节点
        deduplicated = []
        if evolution:
            deduplicated.append(evolution[0])  # 保留起始点
            
            for i in range(1, len(evolution)):
                if evolution[i]['type'] != evolution[i-1]['type']:
                    deduplicated.append(evolution[i])
        
        logger.info(f"✅ {entity1}-{entity2} 演变追踪完成: {len(evolution)}段 -> {len(deduplicated)}个变化点")
        
        return deduplicated
    
    async def track_batch(
        self,
        tasks: List[Tuple],
        novel: Novel,
        db: Session,
        use_batch_api: bool = False
    ) -> Tuple[Dict[Tuple[str, str], List[Dict]], Dict]:
        """
        批量追踪多对关系的演变（支持 Batch API）
        
        Args:
            tasks: [(entity1, entity2, chapters), ...]
            novel: 小说对象
            db: 数据库会话
            use_batch_api: 是否使用 Batch API
        
        Returns:
            Tuple[Dict, Dict]: (演变结果字典, token统计)
            - {(entity1, entity2): evolution_list, ...}
            - token统计
        """
        from app.core.config import settings
        
        # 第1步：收集所有需要分类的段
        logger.info(f"🔍 开始追踪 {len(tasks)} 对关系的演变...")
        
        all_classification_tasks = []  # [(entity1, entity2, contexts, count, chapter_range, segment_info), ...]
        segment_mapping = []  # 记录每个分类任务对应的关系对和段索引
        
        for entity1, entity2, all_chapters in tasks:
            if not all_chapters:
                segment_mapping.append([])
                continue
            
            # 分段策略
            total_span = max(all_chapters) - min(all_chapters)
            if total_span <= 50:
                segments = 2
            elif total_span <= 200:
                segments = 3
            else:
                segments = 5
            
            segment_size = len(all_chapters) // segments
            if segment_size == 0:
                segment_size = 1
            
            relation_segments = []
            
            for i in range(segments):
                start_idx = i * segment_size
                end_idx = start_idx + segment_size if i < segments - 1 else len(all_chapters)
                segment_chapters = all_chapters[start_idx:end_idx]
                
                if not segment_chapters:
                    continue
                
                # 智能采样
                sampled_chapters = self.classifier._smart_chapter_sampling(segment_chapters, max_samples=3)
                
                # 提取上下文
                from app.services.indexing_service import get_indexing_service
                indexing_service = get_indexing_service()
                
                contexts = await indexing_service._extract_cooccurrence_contexts(
                    entity1, entity2, sampled_chapters, novel, db
                )
                
                if not contexts:
                    continue
                
                chapter_range = f"第{min(segment_chapters)}章-第{max(segment_chapters)}章"
                
                # 添加到批量任务
                all_classification_tasks.append((
                    entity1, entity2, contexts, len(segment_chapters), chapter_range
                ))
                
                # 记录段信息
                relation_segments.append({
                    'task_index': len(all_classification_tasks) - 1,
                    'start_chapter': segment_chapters[0],
                    'segment_chapters': segment_chapters
                })
            
            segment_mapping.append(relation_segments)
        
        logger.info(f"📊 共收集 {len(all_classification_tasks)} 个分类任务")
        
        # 第2步：批量分类（支持 Batch API 和智能阈值）
        if len(all_classification_tasks) == 0:
            return {}, {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        
        # 🎯 智能判断：请求数 < 阈值时使用实时API
        if len(all_classification_tasks) < settings.batch_api_threshold:
            logger.info(f"📊 演变追踪分类: 请求数({len(all_classification_tasks)}) < 阈值({settings.batch_api_threshold})，使用实时API")
            use_batch_api = False
        elif use_batch_api:
            logger.info(f"📊 演变追踪分类: 请求数({len(all_classification_tasks)}) ≥ 阈值({settings.batch_api_threshold})，使用Batch API")
        
        classifications, token_stats = await self.classifier.classify_batch(
            all_classification_tasks,
            use_batch_api=use_batch_api
        )
        
        # 第3步：组织结果
        results = {}
        task_idx = 0
        
        for (entity1, entity2, all_chapters), relation_segments in zip(tasks, segment_mapping):
            if not relation_segments:
                results[(entity1, entity2)] = []
                continue
            
            evolution = []
            for segment_info in relation_segments:
                classification = classifications[segment_info['task_index']]
                evolution.append({
                    "chapter": segment_info['start_chapter'],
                    "type": classification['relation_type'],
                    "confidence": classification['confidence']
                })
            
            # 去重：只保留关系类型变化的节点
            deduplicated = []
            if evolution:
                deduplicated.append(evolution[0])
                for i in range(1, len(evolution)):
                    if evolution[i]['type'] != evolution[i-1]['type']:
                        deduplicated.append(evolution[i])
            
            results[(entity1, entity2)] = deduplicated
            logger.info(f"✅ {entity1}-{entity2} 演变追踪完成: {len(evolution)}段 -> {len(deduplicated)}个变化点")
        
        return results, token_stats


# 全局实例
_evolution_tracker = None

def get_evolution_tracker() -> RelationshipEvolutionTracker:
    """获取演变追踪器单例"""
    global _evolution_tracker
    if _evolution_tracker is None:
        _evolution_tracker = RelationshipEvolutionTracker()
    return _evolution_tracker

