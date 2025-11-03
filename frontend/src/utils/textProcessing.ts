import type { Chapter } from '../types';

// 章节标题匹配正则表达式
const CHAPTER_PATTERNS = [
  /第[零一二三四五六七八九十百千0-9]+章[：:\s]*.*/g,
  /第[零一二三四五六七八九十百千0-9]+回[：:\s]*.*/g,
  /第[零一二三四五六七八九十百千0-9]+节[：:\s]*.*/g,
  /第[零一二三四五六七八九十百千0-9]+话[：:\s]*.*/g,
  /Chapter\s+[0-9]+[：:\s]*.*/gi,
  /章节\s+[0-9]+[：:\s]*.*/g,
];

/**
 * 识别文本中的章节
 */
export function detectChapters(content: string): Chapter[] {
  const chapters: Chapter[] = [];
  const lines = content.split('\n');
  
  let chapterMatches: Array<{ title: string; position: number; lineIndex: number }> = [];
  
  // 查找所有章节标题
  let currentPosition = 0;
  lines.forEach((line, index) => {
    const trimmedLine = line.trim();
    
    // 尝试匹配章节标题
    for (const pattern of CHAPTER_PATTERNS) {
      pattern.lastIndex = 0; // 重置正则表达式
      if (pattern.test(trimmedLine) && trimmedLine.length < 50) {
        chapterMatches.push({
          title: trimmedLine,
          position: currentPosition,
          lineIndex: index
        });
        break;
      }
    }
    
    currentPosition += line.length + 1; // +1 for newline
  });
  
  // 如果没有找到章节，按固定段落数分割
  if (chapterMatches.length === 0) {
    return autoSplitChapters(content);
  }
  
  // 构建章节数据
  chapterMatches.forEach((match, index) => {
    const nextMatch = chapterMatches[index + 1];
    const startPosition = match.position;
    const endPosition = nextMatch ? nextMatch.position : content.length;
    const chapterContent = content.substring(startPosition, endPosition);
    
    chapters.push({
      id: `chapter-${index + 1}`,
      order: index + 1,
      title: match.title,
      wordCount: chapterContent.length,
      startPosition,
      endPosition
    });
  });
  
  return chapters;
}

/**
 * 自动分割章节（当没有检测到章节标题时）
 */
function autoSplitChapters(content: string): Chapter[] {
  const chapters: Chapter[] = [];
  const wordsPerChapter = 5000; // 每章约5000字
  const totalWords = content.length;
  const chapterCount = Math.ceil(totalWords / wordsPerChapter);
  
  for (let i = 0; i < chapterCount; i++) {
    const startPosition = i * wordsPerChapter;
    const endPosition = Math.min((i + 1) * wordsPerChapter, totalWords);
    
    chapters.push({
      id: `chapter-${i + 1}`,
      order: i + 1,
      title: `第${i + 1}部分`,
      wordCount: endPosition - startPosition,
      startPosition,
      endPosition
    });
  }
  
  return chapters;
}

/**
 * 检测文件编码
 */
export async function detectEncoding(file: File): Promise<'UTF-8' | 'GBK' | 'GB2312'> {
  try {
    // 读取文件前1000字节来检测编码
    const blob = file.slice(0, 1000);
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    
    // 简单的编码检测逻辑
    // 检查BOM
    if (bytes[0] === 0xEF && bytes[1] === 0xBB && bytes[2] === 0xBF) {
      return 'UTF-8';
    }
    
    // 尝试UTF-8解码
    const decoder = new TextDecoder('utf-8', { fatal: true });
    try {
      decoder.decode(bytes);
      return 'UTF-8';
    } catch (e) {
      // UTF-8解码失败，可能是GBK或GB2312
      return 'GBK';
    }
  } catch (error) {
    console.error('编码检测失败:', error);
    return 'UTF-8'; // 默认返回UTF-8
  }
}

/**
 * 读取文件内容
 */
export async function readFileContent(
  file: File,
  encoding: 'UTF-8' | 'GBK' | 'GB2312' = 'UTF-8',
  onProgress?: (progress: number) => void
): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = (event.loaded / event.total) * 100;
        onProgress(progress);
      }
    };
    
    reader.onload = (event) => {
      try {
        const result = event.target?.result;
        if (typeof result === 'string') {
          resolve(result);
        } else {
          reject(new Error('读取文件失败'));
        }
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error('文件读取错误'));
    };
    
    // 根据编码读取文件
    if (encoding === 'UTF-8') {
      reader.readAsText(file, 'UTF-8');
    } else {
      reader.readAsText(file, 'GBK');
    }
  });
}

/**
 * 清理文本（删除多余空行和空格）
 */
export function cleanText(text: string): string {
  return text
    .replace(/\r\n/g, '\n') // 统一换行符
    .replace(/\n{3,}/g, '\n\n') // 最多保留两个连续换行
    .replace(/[ \t]+/g, ' ') // 多个空格替换为单个
    .trim();
}

/**
 * 提取文本片段
 */
export function extractExcerpt(
  content: string,
  startPos: number,
  endPos: number,
  maxLength: number = 500
): string {
  let excerpt = content.substring(startPos, endPos);
  if (excerpt.length > maxLength) {
    excerpt = excerpt.substring(0, maxLength) + '...';
  }
  return excerpt;
}

/**
 * 获取段落上下文
 */
export function getParagraphContext(
  content: string,
  paragraphIndex: number,
  contextLines: number = 2
): string {
  const paragraphs = content.split('\n\n');
  const start = Math.max(0, paragraphIndex - contextLines);
  const end = Math.min(paragraphs.length, paragraphIndex + contextLines + 1);
  return paragraphs.slice(start, end).join('\n\n');
}

