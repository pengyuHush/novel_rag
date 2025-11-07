// Token使用统计（匹配后端API）
export interface TokenStats {
  totalTokens: number;        // 总Token消耗
  embeddingTokens: number;    // Embedding Token消耗
  chatTokens: number;         // 聊天Token消耗
  apiCalls: number;           // API调用次数
  estimatedCost: number;      // 预估费用（元）
}

// 小说数据结构（匹配后端API）
export interface Novel {
  id: string;
  title: string;
  author?: string;
  description?: string;
  tags: string[];
  seriesName?: string;     // 系列名称（可选）
  seriesOrder?: number;    // 系列顺序（可选）
  chapters?: Chapter[];    // 章节列表（可选，用于前端展示）
  wordCount: number;
  chapterCount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  importedAt: string;      // ISO 8601格式
  updatedAt: string;       // ISO 8601格式
  hasGraph: boolean;       // 是否已生成关系图谱
  // Token统计（新增）
  totalTokensUsed?: number;
  embeddingTokensUsed?: number;
  chatTokensUsed?: number;
  apiCallsCount?: number;
  estimatedCost?: number;
}

// 章节数据结构（匹配后端API）
export interface Chapter {
  id: string;
  novelId: string;
  chapterNumber: number;
  title: string;
  startPosition: number;
  endPosition: number;
  wordCount: number;
}

// 章节内容（包含段落信息）
export interface ChapterContent {
  chapter: Chapter;
  content: string;
  paragraphs: {
    index: number;
    content: string;
    startPosition: number;
  }[];
}

// 小说处理状态（匹配后端API）
export interface NovelProcessingStatus {
  novelId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;         // 0-100
  message: string;         // 当前状态描述
  stage?: 'uploading' | 'detecting_chapters' | 'vectorizing' | 'completed';
  processedWords?: number;  // 已处理字数
  totalWords?: number;      // 总字数
  estimatedTimeRemaining?: number;
  updatedAt?: string;       // ISO 8601格式
  tokenStats?: TokenStats;  // Token使用统计（新增）
}

// 搜索结果数据结构（匹配后端API）
export interface SearchResult {
  query: string;
  answer: string; // AI生成的回答
  confidence?: number; // 答案置信度 0-1
  references: Reference[]; // 参考段落
  relatedQuestions?: string[]; // 相关推荐问题
  searchTime?: number; // 搜索耗时（毫秒）
  elapsed?: number; // 搜索耗时（秒）
  tokenStats?: TokenStats; // Token消耗统计（新增）
}

// 参考段落数据结构（匹配后端API）
export interface Reference {
  novelId: string;
  novelTitle: string;
  chapterId: string;
  chapterTitle: string;
  chapterNumber: number;
  paragraphIndex: number;
  content: string; // 原文内容片段
  relevanceScore: number; // 相关度评分 0-1
  startPosition: number;
  highlightText: string; // 高亮文本
}

// 人物关系图谱数据结构（匹配后端API）
export interface CharacterGraph {
  id: string;
  novelId: string;
  characters: Character[];
  relationships: Relationship[];
  generatedAt: string; // ISO 8601格式
  version: string;
}

// 人物数据结构（匹配后端API）
export interface Character {
  id: string;
  name: string;
  aliases: string[]; // 别名/称号
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  description: string; // 人物描述
  appearances: number; // 出场次数
  importance: number; // 重要程度 0-1
  firstAppearance: { // 首次出场
    chapterId: string;
    chapterTitle: string;
  };
  attributes: Record<string, any>; // 自定义属性
}

// 关系数据结构（匹配后端API）
export interface Relationship {
  id: string;
  source: string; // 源人物ID
  target: string; // 目标人物ID
  type: 'family' | 'friend' | 'enemy' | 'master-disciple' | 'lover' | 'ally' | 'rival';
  description: string; // 关系描述
  strength: number; // 关系强度 0-10
  evidence: Array<{ // 关系证据
    chapterId: string;
    context: string;
  }>;
}

