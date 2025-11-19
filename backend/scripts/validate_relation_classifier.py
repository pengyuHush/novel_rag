"""
关系类型识别验证脚本

功能：
1. 从现有图谱中抽样关系对
2. 使用GLM-4.5-Flash进行关系分类
3. 人工标注验证
4. 生成统计报告
"""

import sys
import os
import json
import random
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# 添加项目路径
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# 添加 backend 目录到 Python 路径
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# 设置工作目录为 backend 目录
os.chdir(BACKEND_DIR)

import networkx as nx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from sqlalchemy.orm import Session

from app.db.init_db import get_db_session
from app.models.database import Novel, Chapter
from app.services.graph.graph_builder import GraphBuilder
from app.core.config import settings
from app.utils.encoding_detector import EncodingDetector


console = Console()


class RelationClassifier:
    """关系类型分类器（使用GLM-4.5-Flash）"""
    
    RELATION_TYPES = ['师徒', '盟友', '敌对', '亲属', '恋人', '同门', '中立', '共现']
    
    def __init__(self, api_key: str):
        """初始化分类器"""
        self.api_key = api_key
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=api_key)
        except ImportError:
            console.print("[red]错误: 未安装 zhipuai SDK，请运行: pip install zhipuai[/red]")
            sys.exit(1)
    
    async def classify(
        self,
        entity1: str,
        entity2: str,
        contexts: List[str],
        cooccurrence_count: int = 0,
        chapter_range: str = ""
    ) -> Dict:
        """
        分类关系类型
        
        Args:
            entity1: 实体1
            entity2: 实体2
            contexts: 上下文列表（3-5个片段）
            cooccurrence_count: 共现次数
            chapter_range: 章节范围
        
        Returns:
            {
                'relation_type': str,
                'confidence': float,
                'reasoning': str
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
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",  # 使用免费高速模型
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1  # 降低随机性
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 提取JSON（处理可能的Markdown代码块）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # 验证关系类型
            if result.get('relation_type') not in self.RELATION_TYPES:
                result['relation_type'] = '共现'
            
            return result
            
        except Exception as e:
            console.print(f"[yellow]警告: 分类失败 - {e}[/yellow]")
            return {
                'relation_type': '共现',
                'confidence': 0.5,
                'reasoning': f'分类失败: {str(e)}'
            }


class RelationValidator:
    """关系验证器"""
    
    def __init__(
        self,
        novel_id: int,
        sample_size: int = 30,
        min_cooccurrence: int = 5,
        output_file: str = "results/validation_results.json"
    ):
        """初始化验证器"""
        self.novel_id = novel_id
        self.sample_size = sample_size
        self.min_cooccurrence = min_cooccurrence
        self.output_file = output_file
        
        self.graph_builder = GraphBuilder()
        self.classifier = RelationClassifier(settings.zhipu_api_key)
        
        self.db: Optional[Session] = None
        self.novel: Optional[Novel] = None
        self.graph: Optional[nx.MultiDiGraph] = None
        
        # 结果存储
        self.results = []
        self.sampled_relations = []
    
    def initialize(self):
        """初始化数据库和图谱"""
        console.print("[cyan]初始化验证器...[/cyan]")
        
        # 创建输出目录
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 数据库
        self.db = next(get_db_session())
        self.novel = self.db.query(Novel).filter(Novel.id == self.novel_id).first()
        
        if not self.novel:
            console.print(f"[red]错误: 未找到小说 ID={self.novel_id}[/red]")
            sys.exit(1)
        
        console.print(f"[green]✓[/green] 小说: {self.novel.title}")
        
        # 加载图谱
        self.graph = self.graph_builder.load_graph(self.novel_id)
        
        if not self.graph:
            console.print(f"[red]错误: 未找到小说的知识图谱[/red]")
            sys.exit(1)
        
        console.print(f"[green]✓[/green] 图谱: {self.graph.number_of_nodes()}节点, {self.graph.number_of_edges()}边")
    
    def sample_relations(self) -> List[Dict]:
        """采样关系对"""
        console.print(f"\n[cyan]采样关系对（最小共现次数: {self.min_cooccurrence}）...[/cyan]")
        
        candidates = []
        
        # 遍历图谱的所有边
        for u, v, data in self.graph.edges(data=True):
            cooccurrence_count = data.get('cooccurrence_count', 0)
            
            if cooccurrence_count >= self.min_cooccurrence:
                # 提取共现章节
                start_chapter = data.get('start_chapter')
                end_chapter = data.get('end_chapter')
                
                # 查询共现章节列表（从数据库）
                chapters = self.db.query(Chapter).filter(
                    Chapter.novel_id == self.novel_id,
                    Chapter.chapter_num >= start_chapter,
                    Chapter.chapter_num <= (end_chapter or 9999)
                ).all()
                
                chapter_nums = [ch.chapter_num for ch in chapters]
                
                candidates.append({
                    'entity1': u,
                    'entity2': v,
                    'cooccurrence_count': cooccurrence_count,
                    'strength': data.get('strength', 0.5),
                    'start_chapter': start_chapter,
                    'end_chapter': end_chapter,
                    'chapter_nums': chapter_nums[:10],  # 限制章节数量
                    'relation_type_current': data.get('relation_type', '共现')
                })
        
        console.print(f"[green]✓[/green] 找到 {len(candidates)} 对候选关系")
        
        # 随机采样
        if len(candidates) > self.sample_size:
            self.sampled_relations = random.sample(candidates, self.sample_size)
        else:
            self.sampled_relations = candidates
        
        console.print(f"[green]✓[/green] 采样 {len(self.sampled_relations)} 对关系")
        
        return self.sampled_relations
    
    def _smart_chapter_sampling(self, chapter_nums: List[int], max_samples: int = 5) -> List[int]:
        """智能采样：早期+中期+后期+均匀分布"""
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
                if i * step < len(chapter_nums):
                    result.append(chapter_nums[i * step])
        
        return sorted(set(result))
    
    def extract_context(
        self,
        entity1: str,
        entity2: str,
        chapter_nums: List[int],
        max_contexts: int = 5
    ) -> List[str]:
        """
        提取关系对的共现上下文
        
        Args:
            entity1: 实体1
            entity2: 实体2
            chapter_nums: 章节列表
            max_contexts: 最大上下文数量
        
        Returns:
            上下文列表
        """
        contexts = []
        
        # 智能采样章节（早期+中期+后期）
        selected_chapters = self._smart_chapter_sampling(chapter_nums, max_contexts)
        
        for chapter_num in selected_chapters:
            try:
                chapter = self.db.query(Chapter).filter(
                    Chapter.novel_id == self.novel_id,
                    Chapter.chapter_num == chapter_num
                ).first()
                
                if not chapter:
                    continue
                
                # 读取章节内容
                content = self._read_chapter_content(chapter)
                
                # 提取包含两个实体的段落
                context = self._extract_paragraph_with_entities(
                    content, entity1, entity2, chapter_num
                )
                
                if context:
                    contexts.append(context)
                
                if len(contexts) >= max_contexts:
                    break
                    
            except Exception as e:
                console.print(f"[yellow]警告: 提取章节{chapter_num}失败 - {e}[/yellow]")
                continue
        
        return contexts
    
    def _read_chapter_content(self, chapter: Chapter) -> str:
        """读取章节内容（复用 chapters.py 逻辑）"""
        file_path = self.novel.file_path
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"小说文件不存在: {file_path}")
        
        # 检测编码
        detection = EncodingDetector.detect_file_encoding(file_path)
        encoding = detection['encoding']
        
        if encoding and encoding.lower() in ['gb2312', 'gb18030']:
            encoding = 'gbk'
        
        # 读取章节内容
        with open(file_path, 'r', encoding=encoding or 'utf-8', errors='ignore') as f:
            all_content = f.read()
            chapter_content = all_content[chapter.start_pos:chapter.end_pos]
        
        return chapter_content
    
    def _extract_paragraph_with_entities(
        self,
        content: str,
        entity1: str,
        entity2: str,
        chapter_num: int
    ) -> Optional[str]:
        """提取包含两个实体的段落（增强版）"""
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
        
        # 如果没找到同时包含的行，尝试查找附近的
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
            
            # 限制长度为400字符
            if len(context) > 400:
                context = context[:400] + "..."
            
            return f"[第{chapter_num}章] {context}"
        
        return None
    
    async def validate_relation(
        self,
        relation: Dict,
        index: int,
        total: int
    ) -> Optional[Dict]:
        """
        验证单个关系
        
        Args:
            relation: 关系数据
            index: 当前索引
            total: 总数
        
        Returns:
            验证结果
        """
        entity1 = relation['entity1']
        entity2 = relation['entity2']
        
        # 清屏并显示进度
        console.clear()
        
        # 显示标题
        title = f"关系类型识别验证 ({index}/{total})"
        console.print(Panel(title, style="bold cyan", box=box.DOUBLE))
        
        # 显示关系信息
        console.print(f"\n[bold]关系对:[/bold] {entity1} <-> {entity2}")
        console.print(f"[bold]共现次数:[/bold] {relation['cooccurrence_count']}次")
        console.print(f"[bold]共现章节:[/bold] 第{relation['start_chapter']}章 - 第{relation['end_chapter']}章")
        console.print(f"[bold]当前图谱标记:[/bold] {relation['relation_type_current']}")
        
        # 提取上下文（增加到5个）
        console.print("\n[cyan]正在提取上下文...[/cyan]")
        contexts = self.extract_context(
            entity1, entity2, relation['chapter_nums'], max_contexts=5
        )
        
        if not contexts:
            console.print("[yellow]警告: 未找到有效上下文，跳过此关系对[/yellow]")
            return None
        
        # 显示上下文
        console.print("\n[bold cyan]上下文片段:[/bold cyan]")
        for i, ctx in enumerate(contexts, 1):
            console.print(f"\n[dim]【上下文{i}】[/dim]")
            console.print(ctx[:400] + "..." if len(ctx) > 400 else ctx)
        
        # 调用AI分类（传递共现次数和章节范围）
        console.print("\n[cyan]正在调用AI分类...[/cyan]")
        chapter_range = f"第{relation['start_chapter']}-{relation['end_chapter']}章"
        prediction = await self.classifier.classify(
            entity1, 
            entity2, 
            contexts,
            cooccurrence_count=relation['cooccurrence_count'],
            chapter_range=chapter_range
        )
        
        # 显示AI预测
        console.print("\n" + "━" * 60)
        console.print(
            f"[bold green]AI预测:[/bold green] {prediction['relation_type']} "
            f"[dim](置信度: {prediction['confidence']:.2f})[/dim]"
        )
        if prediction.get('reasoning'):
            console.print(f"[dim]理由: {prediction['reasoning']}[/dim]")
        console.print("━" * 60)
        
        # 显示选项
        console.print("\n[bold]请选择正确的关系类型:[/bold]")
        for i, rel_type in enumerate(RelationClassifier.RELATION_TYPES, 1):
            console.print(f"  {i}. {rel_type}")
        
        console.print("\n[dim]输入选项:[/dim]")
        console.print("  [cyan]1-8[/cyan]: 选择关系类型")
        console.print("  [cyan]a[/cyan]: 同意AI预测")
        console.print("  [cyan]s[/cyan]: 跳过当前关系对")
        console.print("  [cyan]q[/cyan]: 退出并保存")
        console.print("  [cyan]h[/cyan]: 显示帮助")
        
        # 获取用户输入
        while True:
            choice = Prompt.ask("\n请输入选项", default="a").strip().lower()
            
            if choice == 'q':
                return 'quit'
            elif choice == 's':
                return None
            elif choice == 'a':
                ground_truth = prediction['relation_type']
                break
            elif choice == 'h':
                self._show_help()
                continue
            elif choice.isdigit() and 1 <= int(choice) <= 8:
                ground_truth = RelationClassifier.RELATION_TYPES[int(choice) - 1]
                break
            else:
                console.print("[red]无效输入，请重试[/red]")
        
        # 构建结果
        result = {
            'entity1': entity1,
            'entity2': entity2,
            'cooccurrence_count': relation['cooccurrence_count'],
            'contexts': contexts,
            'predicted_type': prediction['relation_type'],
            'ground_truth': ground_truth,
            'confidence': prediction['confidence'],
            'reasoning': prediction.get('reasoning', ''),
            'is_correct': prediction['relation_type'] == ground_truth,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _show_help(self):
        """显示帮助信息"""
        help_table = Table(title="帮助信息", box=box.ROUNDED)
        help_table.add_column("命令", style="cyan")
        help_table.add_column("说明", style="white")
        
        help_table.add_row("1-8", "选择对应的关系类型编号")
        help_table.add_row("a", "同意AI的预测结果")
        help_table.add_row("s", "跳过当前关系对（不计入统计）")
        help_table.add_row("q", "退出验证并保存当前结果")
        help_table.add_row("h", "显示此帮助信息")
        
        console.print(help_table)
        Prompt.ask("\n按Enter继续")
    
    async def run_validation(self, resume: bool = False):
        """运行验证流程"""
        # 检查是否续传
        if resume and os.path.exists(self.output_file):
            console.print(f"[cyan]从 {self.output_file} 加载已有结果...[/cyan]")
            with open(self.output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                self.results = saved_data.get('results', [])
            console.print(f"[green]✓[/green] 已加载 {len(self.results)} 条结果")
        
        start_index = len(self.results)
        
        # 验证每个关系
        for i, relation in enumerate(self.sampled_relations[start_index:], start=start_index + 1):
            result = await self.validate_relation(
                relation,
                i,
                len(self.sampled_relations)
            )
            
            if result == 'quit':
                console.print("\n[yellow]用户退出验证[/yellow]")
                break
            elif result is None:
                continue
            else:
                self.results.append(result)
                # 实时保存
                self.save_results()
        
        # 生成报告
        self.generate_report()
    
    def save_results(self):
        """保存结果"""
        data = {
            'novel_id': self.novel_id,
            'novel_title': self.novel.title,
            'sample_size': self.sample_size,
            'min_cooccurrence': self.min_cooccurrence,
            'total_validated': len(self.results),
            'results': self.results,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self):
        """生成统计报告"""
        if not self.results:
            console.print("[yellow]没有验证结果[/yellow]")
            return
        
        console.clear()
        console.print(Panel("验证结果统计", style="bold green", box=box.DOUBLE))
        
        # 计算总体准确率
        correct_count = sum(1 for r in self.results if r['is_correct'])
        total_count = len(self.results)
        accuracy = correct_count / total_count if total_count > 0 else 0
        
        # 总体统计
        summary_table = Table(title="总体统计", box=box.ROUNDED)
        summary_table.add_column("指标", style="cyan")
        summary_table.add_column("值", style="white")
        
        summary_table.add_row("总验证数", str(total_count))
        summary_table.add_row("预测正确", str(correct_count))
        summary_table.add_row("预测错误", str(total_count - correct_count))
        summary_table.add_row("准确率", f"{accuracy:.2%}")
        
        console.print(summary_table)
        
        # 按关系类型统计
        console.print("\n")
        type_stats = {}
        for result in self.results:
            pred_type = result['predicted_type']
            if pred_type not in type_stats:
                type_stats[pred_type] = {'correct': 0, 'total': 0}
            type_stats[pred_type]['total'] += 1
            if result['is_correct']:
                type_stats[pred_type]['correct'] += 1
        
        type_table = Table(title="按关系类型统计", box=box.ROUNDED)
        type_table.add_column("关系类型", style="cyan")
        type_table.add_column("预测次数", style="white")
        type_table.add_column("正确次数", style="green")
        type_table.add_column("准确率", style="yellow")
        
        for rel_type, stats in sorted(type_stats.items()):
            acc = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            type_table.add_row(
                rel_type,
                str(stats['total']),
                str(stats['correct']),
                f"{acc:.2%}"
            )
        
        console.print(type_table)
        
        # 置信度分析
        console.print("\n")
        correct_confidences = [r['confidence'] for r in self.results if r['is_correct']]
        incorrect_confidences = [r['confidence'] for r in self.results if not r['is_correct']]
        
        conf_table = Table(title="置信度分析", box=box.ROUNDED)
        conf_table.add_column("类别", style="cyan")
        conf_table.add_column("平均置信度", style="white")
        
        if correct_confidences:
            conf_table.add_row("正确预测", f"{sum(correct_confidences)/len(correct_confidences):.3f}")
        if incorrect_confidences:
            conf_table.add_row("错误预测", f"{sum(incorrect_confidences)/len(incorrect_confidences):.3f}")
        
        console.print(conf_table)
        
        # 混淆矩阵（简化版）
        console.print("\n")
        console.print("[bold]错误案例:[/bold]")
        for i, result in enumerate(self.results, 1):
            if not result['is_correct']:
                console.print(
                    f"  {i}. {result['entity1']} <-> {result['entity2']}: "
                    f"预测[{result['predicted_type']}] vs 真实[{result['ground_truth']}]"
                )
        
        console.print(f"\n[green]✓[/green] 结果已保存到: {self.output_file}")
    
    def cleanup(self):
        """清理资源"""
        if self.db:
            self.db.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="关系类型识别验证脚本")
    parser.add_argument("--novel_id", type=int, required=True, help="小说ID")
    parser.add_argument("--sample_size", type=int, default=30, help="采样数量（默认30）")
    parser.add_argument("--min_cooccurrence", type=int, default=5, help="最小共现次数（默认5）")
    parser.add_argument("--resume", action="store_true", help="续传模式（从上次中断处继续）")
    parser.add_argument("--output", type=str, default="results/validation_results.json", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = RelationValidator(
        novel_id=args.novel_id,
        sample_size=args.sample_size,
        min_cooccurrence=args.min_cooccurrence,
        output_file=args.output
    )
    
    try:
        # 初始化
        validator.initialize()
        
        # 采样关系
        validator.sample_relations()
        
        # 运行验证
        await validator.run_validation(resume=args.resume)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断验证[/yellow]")
        validator.save_results()
        validator.generate_report()
    except Exception as e:
        console.print(f"\n[red]错误: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        validator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

