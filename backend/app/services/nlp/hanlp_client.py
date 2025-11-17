"""
T085: HanLP客户端配置 (User Story 3: 知识图谱与GraphRAG)

HanLP: 多任务中文NLP工具
- 命名实体识别(NER): 识别人名、地名、组织名
- 词性标注: 辅助实体分类
- 依存句法分析: 辅助关系提取

使用模型: CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH
"""

import os
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


class HanLPClient:
    """HanLP客户端封装"""
    
    def __init__(self):
        self._hanlp = None
        self._initialized = False
    
    @staticmethod
    def _clean_entity_name(entity_name: str, strict: bool = True) -> Optional[str]:
        """
        清洗实体名称，去除特殊字符并过滤无效实体
        
        Args:
            entity_name: 原始实体名
            strict: True=严格模式(索引用), False=宽松模式(查询用)
        
        Returns:
            清洗后的实体名，如果无效则返回 None
        """
        if not entity_name:
            return None
        
        import re
        
        # 1-5. 基本清洗（换行、引号、空格等）- 两种模式都执行
        entity_name = entity_name.strip()
        
        # 去除前后的引号
        quote_chars = "'\"\u2018\u2019\u201c\u201d`´"  # '  "  '  '  "  "  `  ´
        entity_name = entity_name.strip(quote_chars).strip()
        
        # 替换换行符、制表符等为空格
        entity_name = entity_name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # 压缩连续空格为单个空格
        entity_name = re.sub(r'\s+', ' ', entity_name).strip()
        
        # 再次去除引号
        entity_name = entity_name.strip(quote_chars)
        
        # 基本验证
        if not entity_name or len(entity_name) < 2:
            return None
        
        if re.match(r'^[\d\W]+$', entity_name):
            return None
        
        # 6-9. 严格过滤 - 仅在 strict=True 时执行
        if strict:
            # 过滤章节标题模式
            chapter_patterns = [
                r'第[零一二三四五六七八九十百千万\d]+章',
                r'第[零一二三四五六七八九十百千万\d]+回',
                r'[Cc]hapter\s*\d+',
                r'^\d+[\.、\s]*章',
                r'卷[零一二三四五六七八九十百千万\d]+',
            ]
            
            for pattern in chapter_patterns:
                if re.search(pattern, entity_name):
                    logger.debug(f"过滤章节标题: {entity_name}")
                    return None
            
            # 过滤常见噪音词
            noise_words = [
                '作者', '本书', '本章', '正文', '番外', '序章', '楔子', '引子',
                '前言', '后记', '附录', '目录', '简介', '完本', '完结',
                'PS', 'VIP', '月票', '推荐票', '打赏'
            ]
            
            for noise in noise_words:
                if noise in entity_name:
                    logger.debug(f"过滤噪音词: {entity_name}")
                    return None
            
            # 过滤过长的实体
            if len(entity_name) > 10:
                logger.debug(f"过滤过长实体: {entity_name}")
                return None
            
            # 过滤包含引号的实体
            quote_chars_check = ["'", '"', '\u2018', '\u2019', '\u201c', '\u201d', '`', '´']
            has_quote = any(q in entity_name for q in quote_chars_check)
            if has_quote:
                logger.debug(f"过滤包含引号的实体: {entity_name}")
                return None
        else:
            # 宽松模式：只过滤明显的引号问题
            quote_chars_check = ["'", '"', '\u2018', '\u2019', '\u201c', '\u201d', '`', '´']
            has_quote = any(q in entity_name for q in quote_chars_check)
            if has_quote:
                return None
        
        return entity_name
    
    def _lazy_init(self):
        """延迟初始化HanLP(避免启动时加载大模型)"""
        if self._initialized:
            return
        
        try:
            import hanlp
            
            logger.info("正在加载HanLP模型...")
            logger.info("首次加载需要下载模型文件(约500MB),请耐心等待...")
            
            # 加载多任务模型
            self._hanlp = hanlp.load(
                hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH
            )
            
            self._initialized = True
            logger.info("✅ HanLP模型加载完成")
            
        except ImportError:
            logger.error("HanLP未安装,请运行: pip install hanlp")
            raise
        except Exception as e:
            logger.error(f"HanLP模型加载失败: {e}")
            raise
    
    def extract_entities(self, text: str, max_length: int = 512, strict: bool = True) -> dict:
        """
        提取命名实体
        
        Args:
            text: 输入文本
            max_length: 最大文本长度(HanLP限制),超过会截断
            strict: 严格清洗模式（索引时=True，查询时=False）
        
        Returns:
            {
                'characters': ['萧炎', '药老', ...],
                'locations': ['乌坦城', '迦南学院', ...],
                'organizations': ['云岚宗', '加玛帝国', ...]
            }
        
        参考: https://github.com/hankcs/HanLP
        """
        self._lazy_init()
        
        # 截断过长文本
        if len(text) > max_length:
            text = text[:max_length]
        
        # 空文本检查
        if not text or not text.strip():
            return {'characters': [], 'locations': [], 'organizations': []}
        
        try:
            # 执行 NER 任务（HanLP 多任务模型）
            # 参考: https://hanlp.hankcs.com/docs/api/hanlp/pretrained/mtl.html
            result = self._hanlp(text, tasks='ner')
            
            # 分类实体
            entities = {
                'characters': [],
                'locations': [],
                'organizations': []
            }
            
            # 尝试不同的 NER 字段名（根据训练数据集命名）
            # MSRA: 微软亚洲研究院数据集, PKU: 北京大学数据集, OntoNotes: OntoNotes数据集
            ner_results = None
            used_key = None
            
            for key in ['ner/msra', 'ner/pku', 'ner/ontonotes', 'ner']:
                if key in result:
                    ner_results = result[key]
                    used_key = key
                    break
            
            if not ner_results:
                # 如果没有标准的 NER 字段，尝试查找任何包含 'ner' 的字段
                ner_keys = [k for k in result.keys() if 'ner' in k.lower()]
                if ner_keys:
                    used_key = ner_keys[0]
                    ner_results = result[used_key]
                    logger.warning(f"使用非标准 NER 字段: {used_key}")
            
            if ner_results:
                logger.debug(f"HanLP 使用字段 '{used_key}' 返回 {len(ner_results)} 个实体")
                
                # 处理实体结果
                # HanLP 返回格式: [('萧炎', 'PER', start, end), ...] 或 [('萧炎', 'PER'), ...]
                for item in ner_results:
                    if not item:
                        continue
                    
                    # 提取实体名和类型
                    if isinstance(item, (list, tuple)):
                        if len(item) >= 2:
                            entity_name = str(item[0])
                            entity_type = str(item[1])
                        else:
                            continue
                    else:
                        logger.warning(f"未识别的实体格式: {type(item)}")
                        continue
                    
                    # 清洗实体名称
                    entity_name = self._clean_entity_name(entity_name, strict=strict)
                    if not entity_name:
                        continue
                    
                    # 根据 MSRA/PKU/OntoNotes 标注规范分类
                    # MSRA 标签: PER(人名), LOC(地名), ORG(组织名)
                    # OntoNotes 标签: PERSON, GPE(地缘政治实体), ORG, LOCATION 等
                    entity_type_upper = entity_type.upper()
                    
                    if entity_type_upper in ['PER', 'PERSON', 'NR']:  # 人名
                        entities['characters'].append(entity_name)
                    elif entity_type_upper in ['LOC', 'LOCATION', 'GPE', 'NS']:  # 地名
                        entities['locations'].append(entity_name)
                    elif entity_type_upper in ['ORG', 'ORGANIZATION', 'NT']:  # 组织名
                        entities['organizations'].append(entity_name)
                    else:
                        # 记录未映射的实体类型
                        logger.debug(f"未映射的实体类型: {entity_type} ({entity_name})")
                
                extracted_count = sum(len(v) for v in entities.values())
                if extracted_count > 0:
                    logger.debug(f"成功提取: 人名{len(entities['characters'])} 地名{len(entities['locations'])} 组织{len(entities['organizations'])}")
            else:
                logger.warning(f"HanLP 结果中没有 NER 字段，可用字段: {list(result.keys())}")
                # 输出结果样例帮助调试
                if result:
                    logger.debug(f"结果样例: {str(result)[:200]}")
            
            return entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            logger.error(f"输入文本长度: {len(text)}, 前100字符: {text[:100]}")
            logger.exception(e)  # 打印完整堆栈
            # 返回空结果而非抛出异常(降级处理)
            return {'characters': [], 'locations': [], 'organizations': []}
    
    def is_available(self) -> bool:
        """检查HanLP是否可用"""
        try:
            self._lazy_init()
            return True
        except:
            return False


# 全局单例
@lru_cache(maxsize=1)
def get_hanlp_client() -> HanLPClient:
    """获取HanLP客户端单例"""
    return HanLPClient()


# 简便方法
def extract_entities(text: str) -> dict:
    """提取实体的简便方法"""
    client = get_hanlp_client()
    return client.extract_entities(text)

