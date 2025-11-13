"""
文件编码检测工具
"""

import chardet
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class EncodingDetector:
    """文件编码检测器"""
    
    @staticmethod
    def detect_file_encoding(
        file_path: str,
        sample_size: int = 10000
    ) -> Dict[str, any]:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            sample_size: 采样大小（字节）
        
        Returns:
            Dict: {
                'encoding': 'utf-8',
                'confidence': 0.99,
                'language': 'Chinese'
            }
        """
        try:
            with open(file_path, 'rb') as f:
                # 读取样本
                raw_data = f.read(sample_size)
                
                # 检测编码
                result = chardet.detect(raw_data)
                
                logger.info(f"✅ 检测到编码: {result['encoding']} (置信度: {result['confidence']:.2f})")
                return result
                
        except Exception as e:
            logger.error(f"❌ 编码检测失败: {e}")
            # 默认返回UTF-8
            return {
                'encoding': 'utf-8',
                'confidence': 0.5,
                'language': ''
            }
    
    @staticmethod
    def read_text_file(
        file_path: str,
        encoding: Optional[str] = None
    ) -> str:
        """
        读取文本文件（自动检测编码）
        
        Args:
            file_path: 文件路径
            encoding: 指定编码（如不指定则自动检测）
        
        Returns:
            str: 文件内容
        """
        # 如果未指定编码，自动检测
        if encoding is None:
            detection = EncodingDetector.detect_file_encoding(file_path)
            encoding = detection['encoding']
            
            # 常见编码别名处理
            if encoding.lower() in ['gb2312', 'gb18030']:
                encoding = 'gbk'  # GBK兼容GB2312和GB18030
        
        try:
            # 尝试使用检测到的编码读取
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            logger.info(f"✅ 文件读取成功 (编码: {encoding})")
            return content
            
        except UnicodeDecodeError as e:
            logger.warning(f"⚠️ {encoding} 编码读取失败，尝试UTF-8")
            
            # 回退到UTF-8
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return content
            except Exception as e2:
                logger.error(f"❌ UTF-8读取也失败: {e2}")
                
                # 最后尝试：二进制读取并强制转换
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    return raw_data.decode('utf-8', errors='ignore')
    
    @staticmethod
    def convert_to_utf8(
        input_file: str,
        output_file: str,
        source_encoding: Optional[str] = None
    ) -> bool:
        """
        将文件转换为UTF-8编码
        
        Args:
            input_file: 输入文件
            output_file: 输出文件
            source_encoding: 源编码（如不指定则自动检测）
        
        Returns:
            bool: 是否成功
        """
        try:
            # 读取原文件
            content = EncodingDetector.read_text_file(input_file, source_encoding)
            
            # 写入UTF-8文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ 文件已转换为UTF-8: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 文件转换失败: {e}")
            return False


# 全局编码检测器实例
_encoding_detector: Optional[EncodingDetector] = None


def get_encoding_detector() -> EncodingDetector:
    """获取全局编码检测器实例（单例）"""
    global _encoding_detector
    if _encoding_detector is None:
        _encoding_detector = EncodingDetector()
    return _encoding_detector

