/**
 * 查询相关类型定义
 */

/**
 * 智谱AI模型类型 - 基于官方文档
 * 参考: https://docs.bigmodel.cn/cn/guide/start/model-overview
 */
export enum ModelType {
  // 免费模型
  GLM_4_5_FLASH = 'GLM-4.5-Flash',
  GLM_4_FLASH = 'GLM-4-Flash-250414',
  
  // 高性价比模型
  GLM_4_5_AIR = 'GLM-4.5-Air',
  GLM_4_5_AIRX = 'GLM-4.5-AirX',
  GLM_4_AIR = 'GLM-4-Air-250414',
  
  // 极速模型
  GLM_4_5_X = 'GLM-4.5-X',
  GLM_4_AIRX = 'GLM-4-AirX',
  GLM_4_FLASHX = 'GLM-4-FlashX-250414',
  
  // 高性能模型
  GLM_4_5 = 'GLM-4.5',
  GLM_4_PLUS = 'GLM-4-Plus',
  GLM_4_6 = 'GLM-4.6',
  
  // 超长上下文
  GLM_4_LONG = 'GLM-4-Long',
  
  // 视觉模型
  GLM_4_5V = 'GLM-4.5V',
  GLM_4V = 'GLM-4V',
}

export enum Confidence {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum QueryStage {
  UNDERSTANDING = 'understanding',
  RETRIEVING = 'retrieving',
  GENERATING = 'generating',
  VALIDATING = 'validating',
  FINALIZING = 'finalizing',
}

export interface Citation {
  chapter_num: number;
  chapter_title?: string;
  text: string;
  score?: number;
}

export interface TokenStats {
  total_tokens: number;
  embedding_tokens?: number;
  prompt_tokens?: number;
  completion_tokens?: number;
}

export interface QueryRequest {
  novel_id: number;
  query: string;
  model?: ModelType;
}

export interface QueryResponse {
  query_id: number;
  answer: string;
  citations: Citation[];
  token_stats: TokenStats;
  response_time: number;
  confidence: Confidence;
  model: string;
  timestamp: string;
}

export interface StreamMessage {
  stage: QueryStage;
  content: string;
  progress: number;
  metadata?: Record<string, any>;
  is_delta?: boolean;
  done?: boolean;
  citations?: Citation[];
  error?: string;
}

