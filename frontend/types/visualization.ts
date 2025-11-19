/**
 * 可视化相关类型定义
 */

// 布局算法类型
export type LayoutAlgorithm = 'spring' | 'force_atlas2' | 'circular' | 'hierarchical';

// 时间线布局类型
export type TimelineLayout = 'swimlane' | 'bubble';

// 关系类型样式配置
export interface RelationStyle {
  color: string;
  width: number;
  type: 'solid' | 'dashed' | 'dotted';
}

// 节点类型样式配置
export interface NodeStyle {
  color: string;
  shape: 'circle' | 'rect' | 'diamond' | 'triangle';
  icon?: string;
}

// 事件类型样式配置
export interface EventStyle {
  color: string;
  symbol: 'circle' | 'rect' | 'diamond' | 'triangle' | 'pin' | 'arrow';
  size: number;
  icon?: string;
}

// 图谱筛选选项
export interface GraphFilters {
  startChapter?: number;
  endChapter?: number;
  maxNodes?: number;
  minImportance?: number;
  relationTypes?: string[];
  nodeTypes?: string[];
  searchQuery?: string;
}

// 时间线筛选选项
export interface TimelineFilters {
  entityFilter?: string[];
  eventTypes?: string[];
  minImportance?: number;
  chapterRange?: [number, number];
}

// 图表导出选项
export interface ExportOptions {
  format: 'png' | 'svg';
  filename?: string;
  backgroundColor?: string;
  pixelRatio?: number;
}

// 节点详情
export interface NodeDetails {
  id: string;
  name: string;
  type: string;
  importance: number;
  first_chapter: number;
  last_chapter?: number;
  neighbors_count: number;
  relations: Array<{
    direction: 'incoming' | 'outgoing';
    source?: string;
    target?: string;
    type: string;
    strength: number;
    start_chapter: number;
    end_chapter?: number;
  }>;
  attributes: Record<string, any>;
}

// 关系类型配置映射
export const RELATION_STYLES: Record<string, RelationStyle> = {
  '师徒': { color: '#10B981', width: 3, type: 'solid' },
  '敌对': { color: '#EF4444', width: 2, type: 'dashed' },
  '盟友': { color: '#3B82F6', width: 2, type: 'solid' },
  '恋人': { color: '#EC4899', width: 3, type: 'solid' },
  '亲属': { color: '#F59E0B', width: 2, type: 'solid' },
  '朋友': { color: '#14B8A6', width: 2, type: 'solid' },
  '复杂': { color: '#6B7280', width: 1, type: 'dotted' },
  '未知': { color: '#9CA3AF', width: 1, type: 'dotted' },
};

// 节点类型配置映射
export const NODE_STYLES: Record<string, NodeStyle> = {
  'character': { color: '#8B5CF6', shape: 'circle' },
  'location': { color: '#3B82F6', shape: 'rect' },
  'item': { color: '#10B981', shape: 'diamond' },
  'organization': { color: '#F59E0B', shape: 'rect' },
  'unknown': { color: '#6B7280', shape: 'circle' },
};

// 事件类型配置映射
export const EVENT_STYLES: Record<string, EventStyle> = {
  'entity_appear': { color: '#8B5CF6', symbol: 'circle', size: 12, icon: '👤' },
  'relation_start': { color: '#3B82F6', symbol: 'diamond', size: 14, icon: '🤝' },
  'relation_evolve': { color: '#F59E0B', symbol: 'triangle', size: 13, icon: '⚡' },
};

// 图表配置
export interface ChartConfig {
  width?: number;
  height?: number;
  theme?: 'light' | 'dark';
  animation?: boolean;
  animationDuration?: number;
}

// 力导向布局配置
export interface ForceLayoutConfig {
  iterations?: number;
  repulsion?: number;
  attraction?: number;
  gravity?: number;
  friction?: number;
}

