// 小说数据结构
export interface Novel {
  id: string;
  title: string;
  author?: string;
  summary?: string;
  tags?: string[];
  wordCount: number;
  fileSize: number;
  importDate: string;
  encoding: 'UTF-8' | 'GBK' | 'GB2312';
  
  // 系列关系
  series?: {
    relatedNovels: string[]; // 关联小说的ID数组
    order: number; // 系列序号
  };
  
  // 章节数据
  chapters: Chapter[];
  
  // 原文内容
  content: string;
}

// 章节数据结构
export interface Chapter {
  id: string;
  order: number;
  title: string;
  wordCount: number;
  startPosition: number; // 在全文中的起始位置
  endPosition: number;   // 在全文中的结束位置
}

// 搜索结果数据结构
export interface SearchResult {
  answer: string; // AI生成的回答
  references: Reference[]; // 参考段落
  timestamp: string;
}

// 参考段落数据结构
export interface Reference {
  novelId: string;
  novelTitle: string;
  chapterId: string;
  chapterTitle: string;
  paragraphIndex: number;
  excerpt: string; // 原文片段
  relevance: number; // 相关度 0-1
  highlightRanges: [number, number][]; // 高亮位置
}

// 人物关系图谱数据结构
export interface CharacterGraph {
  novelId: string;
  characters: Character[];
  relationships: Relationship[];
}

// 人物数据结构
export interface Character {
  id: string;
  name: string;
  frequency: number; // 出现次数
  importance: 'major' | 'minor'; // 主要/次要人物
  chapters: string[]; // 出现的章节ID列表
}

// 关系数据结构
export interface Relationship {
  id: string;
  from: string; // 人物ID
  to: string;
  type: 'family' | 'friend' | 'enemy' | 'mentor' | 'other';
  strength: number; // 关系强度 0-1
  chapters: string[]; // 共同出现的章节
  representativeExcerpts: string[]; // 代表性原文片段
}

// 搜索历史数据结构
export interface SearchHistory {
  id: string;
  query: string;
  result: SearchResult;
  timestamp: string;
}

