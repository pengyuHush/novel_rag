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
  // 智谱AI
  ZHIPU_GLM_4_5_FLASH = "zhipu/GLM-4.5-Flash",
  ZHIPU_GLM_4_5 = "zhipu/GLM-4.5",
  ZHIPU_GLM_4_6 = "zhipu/GLM-4.6",
  ZHIPU_GLM_4_5_AIR = "zhipu/GLM-4.5-Air",
  ZHIPU_GLM_4_PLUS = "zhipu/GLM-4-Plus",
  ZHIPU_GLM_4_LONG = "zhipu/GLM-4-Long",
  
  // OpenAI
  OPENAI_GPT_4O = "openai/gpt-4o",
  OPENAI_GPT_4O_MINI = "openai/gpt-4o-mini",
  OPENAI_GPT_4_TURBO = "openai/gpt-4-turbo",
  OPENAI_GPT_3_5_TURBO = "openai/gpt-3.5-turbo",
  
  // DeepSeek
  DEEPSEEK_CHAT = "deepseek/deepseek-chat",
  DEEPSEEK_REASONER = "deepseek/deepseek-reasoner",
  
  // Gemini
  GEMINI_1_5_PRO = "gemini/gemini-1.5-pro",
  GEMINI_1_5_FLASH = "gemini/gemini-1.5-flash",
  GEMINI_2_0_FLASH_EXP = "gemini/gemini-2.0-flash-exp",
  GEMINI_3_PRO_PREVIEW = "gemini/gemini-3-pro-preview",
  
  // 阿里通义千问
  ALI_QWEN_MAX = "ali/qwen-max",
  ALI_QWEN_PLUS = "ali/qwen-plus",
  ALI_QWEN_TURBO = "ali/qwen-turbo",
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
  use_rewritten_in_prompt: boolean; // 是否在Prompt中使用改写后的查询
  recency_bias_weight: number;
}

export interface Citation {
  novelId: number;           // 来源小说ID
  novelTitle?: string;       // 来源小说标题
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
  firstChapter?: number;
  lastChapter?: number;
  degree?: number;
  communityId?: number;
  x?: number;
  y?: number;
  isProtagonist?: boolean;
  isAntagonist?: boolean;
  attributes?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationType: string;
  strength: number;
  startChapter: number;
  endChapter?: number;
  isPublic?: boolean;
  revealChapter?: number;
  evolution?: Array<{
    chapter: number;
    type: string;
  }>;
}

export interface RelationGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    totalNodes: number;
    totalEdges: number;
    chapterFilter?: [number, number] | null;
    relationTypes: string[];
    communities?: number;
    layoutAlgorithm?: string;
    [key: string]: any;
  };
}

export interface GraphStatistics {
  total_nodes: number;
  total_edges: number;
  density: number;
  average_degree: number;
  max_degree: number;
  chapter_range: [number, number];
  node_types: Record<string, number>;
  relation_types: Record<string, number>;
  num_communities: number;
  top_nodes: Array<{
    name: string;
    degree: number;
    importance: number;
    type: string;
  }>;
  relation_summary: Array<{
    type: string;
    count: number;
    avgStrength: number;
  }>;
}

export interface TimelineEvent {
  chapterNum: number;
  narrativeOrder: number;
  description: string;
  eventType: 'entity_appear' | 'relation_start' | 'relation_evolve' | string;
  importance: number;
  entity?: string;
  source?: string;
  target?: string;
  relationType?: string;
}

export interface TimelineData {
  events: TimelineEvent[];
  metadata: {
    total_events: number;
    entity_filter?: string;
    event_types_filter?: string;
    min_importance?: number;
    chapter_range: [number, number];
    available_event_types?: string[];
    [key: string]: any;
  };
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

