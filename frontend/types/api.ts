/**
 * API类型定义
 * 对应后端 app/models/schemas.py
 */

// ========================================
// 枚举类型
// ========================================

export enum IndexStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum FileFormat {
  TXT = "txt",
  EPUB = "epub",
}

export enum ModelType {
  // 免费模型
  GLM_4_5_FLASH = "GLM-4.5-Flash",
  GLM_4_FLASH = "GLM-4-Flash-250414",
  
  // 高性价比模型
  GLM_4_5_AIR = "GLM-4.5-Air",
  GLM_4_5_AIRX = "GLM-4.5-AirX",
  GLM_4_AIR = "GLM-4-Air-250414",
  
  // 极速模型
  GLM_4_5_X = "GLM-4.5-X",
  GLM_4_AIRX = "GLM-4-AirX",
  GLM_4_FLASHX = "GLM-4-FlashX-250414",
  
  // 高性能模型
  GLM_4_5 = "GLM-4.5",
  GLM_4_PLUS = "GLM-4-Plus",
  GLM_4_6 = "GLM-4.6",
  
  // 超长上下文
  GLM_4_LONG = "GLM-4-Long",
}

export enum Confidence {
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
}

export enum QueryStage {
  UNDERSTANDING = "understanding",
  RETRIEVING = "retrieving",
  GENERATING = "generating",
  VALIDATING = "validating",
  FINALIZING = "finalizing",
}

// ========================================
// 小说相关类型
// ========================================

export interface NovelCreate {
  title: string;
  author?: string;
}

export interface NovelResponse {
  id: number;
  title: string;
  author?: string;
  total_chars: number;
  total_chapters: number;
  index_status: IndexStatus;
  index_progress: number; // 0-1
  file_format: FileFormat;
  
  // 索引统计
  total_chunks: number;
  total_entities: number;
  total_relations: number;
  embedding_tokens: number;
  
  upload_date: string;
  indexed_date?: string;
  created_at: string;
  updated_at: string;
}

export interface NovelListItem {
  id: number;
  title: string;
  author?: string;
  total_chars: number;
  total_chapters: number;
  index_status: IndexStatus;
  index_progress: number;
  file_format: FileFormat;
  upload_date: string;
}

export interface IndexingStep {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface FailedChapter {
  chapter_num: number;
  chapter_title?: string;
  error: string;
}

export interface TokenUsageStep {
  step: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
}

export interface TokenStatsDetail {
  steps: TokenUsageStep[];
  total: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    estimated_cost: number;
  };
}

export interface IndexingDetail {
  steps: IndexingStep[];
  failed_chapters: FailedChapter[];
  token_stats?: TokenStatsDetail;
  warnings: string[];
}

export interface NovelProgressResponse {
  novel_id: number;
  status: IndexStatus;
  progress: number; // 0-1
  current_chapter?: number;
  total_chapters: number;
  message: string;
  detail?: IndexingDetail;  // 详细信息
}

// ========================================
// 章节相关类型
// ========================================

export interface ChapterListItem {
  num: number;
  title?: string;
  char_count: number;
}

export interface ChapterContent {
  chapter_num: number;
  title?: string;
  content: string;
  prev_chapter?: number;
  next_chapter?: number;
  total_chapters: number;
}

// ========================================
// 查询相关类型
// ========================================

export interface QueryRequest {
  novel_id: number;
  query: string;
  model: ModelType;
  enable_query_rewrite?: boolean;
  recency_bias_weight?: number;
}

export interface QueryConfig {
  top_k_retrieval: number;
  top_k_rerank: number;
  max_context_chunks: number;
  enable_query_rewrite: boolean;
  recency_bias_weight: number;
}

export interface Citation {
  chapterNum: number;
  chapterTitle?: string;
  text: string;
  score?: number;
}

export interface Contradiction {
  type: string;
  earlyDescription: string;
  earlyChapter: number;
  lateDescription: string;
  lateChapter: number;
  analysis: string;
  confidence: Confidence;
}

// 阶段级别的Token统计
export interface StageTokenStats {
  stage: string; // 阶段名称：understanding, retrieving, generating, validating
  model: string; // 使用的模型名称
  inputTokens: number; // 输入token数
  outputTokens: number; // 输出token数
  totalTokens: number; // 该阶段总token数
}

export interface TokenStats {
  totalTokens?: number;
  total_tokens?: number;
  embeddingTokens?: number;
  embedding_tokens?: number;
  promptTokens?: number;
  prompt_tokens?: number;
  inputTokens?: number;
  input_tokens?: number;
  completionTokens?: number;
  completion_tokens?: number;
  outputTokens?: number;
  output_tokens?: number;
  cachedTokens?: number;
  cached_tokens?: number;
  selfRagTokens?: number;
  self_rag_tokens?: number;
  byModel?: Record<string, Record<string, number>>;
  by_model?: Record<string, Record<string, number>>;
  // 新增：按阶段统计
  byStage?: StageTokenStats[];
  by_stage?: StageTokenStats[];
}

export interface QueryResponse {
  query_id: number;
  answer: string;
  citations: Citation[];
  graph_info?: Record<string, any>;
  contradictions: Contradiction[];
  token_stats: TokenStats;
  response_time: number;
  retrieve_time?: number;
  generate_time?: number;
  confidence: Confidence;
  model: string;
  timestamp: string;
  rewritten_query?: string;
}

// ========================================
// WebSocket流式消息
// ========================================

export interface StreamMessage {
  stage: QueryStage;
  content: string;
  thinking?: string; // 思考过程内容（thinking模式）
  progress: number; // 0-1
  is_delta: boolean; // 是否为增量消息
  done: boolean; // 是否完成
  citations?: Citation[]; // 引用来源
  contradictions?: Contradiction[]; // 矛盾检测结果
  query_id?: number; // 查询ID
  error?: string; // 错误信息
  metadata?: Record<string, any>;
}

export interface IndexingProgressMessage {
  novel_id: number;
  status: IndexStatus;
  progress: number;
  current_chapter: number;
  total_chapters: number;
  message: string;
  timestamp: string;
  token_stats?: Record<string, any>;
}

// ========================================
// 统计相关类型
// ========================================

export interface TokenStatsQuery {
  period?: 'day' | 'week' | 'month';
  start_date?: string;
  end_date?: string;
  model?: string;
}

export interface TokenStatsResponse {
  total_tokens: number;
  total_cost: number;
  by_model: Record<string, Record<string, any>>;
  by_operation: Record<string, Record<string, any>>;
  period: string;
}

// ========================================
// 图谱相关类型
// ========================================

export interface GraphNode {
  id: string;
  name: string;
  importance: number;
  type?: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationType: string;
  startChapter: number;
  endChapter?: number;
}

export interface RelationGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: Record<string, any>;
}

export interface TimelineEvent {
  chapterNum: number;
  narrativeOrder: number;
  description: string;
  eventType?: string;
  importance?: number;
  entity?: string;
  source?: string;
  target?: string;
  relationType?: string;
}

export interface TimelineData {
  events: TimelineEvent[];
  metadata: Record<string, any>;
}

// ========================================
// 配置相关类型
// ========================================

export interface AppConfig {
  defaultModel: ModelType;
  topK: number;
  chunkSize: number;
  chunkOverlap: number;
  enableSelfRAG: boolean;
  enableSmartRouting: boolean;
}

export interface TestConnectionRequest {
  apiKey: string;
}

export interface TestConnectionResponse {
  success: boolean;
  message: string;
}

