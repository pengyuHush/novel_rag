/**
 * Token统计面板
 * 显示实时Token消耗统计
 */

'use client';

import type { TokenStats as TokenStatsType } from '@/types/api';

interface TokenStatsProps {
  stats: TokenStatsType | null;
}

function formatNumber(num?: number): string {
  if (num === undefined || num === null) return '0';
  return num.toLocaleString();
}

export function TokenStats({ stats }: TokenStatsProps) {
  if (!stats) {
    return (
      <div className="text-xs text-muted-foreground text-center py-2">
        暂无消耗数据
      </div>
    );
  }

  // 安全地获取数值，兼容不同命名方式
  const totalTokens = stats.totalTokens || stats.total_tokens || 0;
  const inputTokens = stats.inputTokens || stats.input_tokens || 0;
  const outputTokens = stats.outputTokens || stats.output_tokens || 0;
  const byStage = stats.byStage || stats.by_stage || [];

  // 阶段名称映射
  const stageNameMap: Record<string, string> = {
    'understanding': '查询理解',
    'retrieving': '检索',
    'generating': '生成',
    'validating': '验证',
    'finalizing': '完成'
  };

  return (
    <div className="space-y-2">
      {/* 标题和总计 */}
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold flex items-center gap-1">
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Token消耗
        </span>
        <span className="text-sm font-bold text-primary">{formatNumber(totalTokens)}</span>
      </div>

      {/* 输入输出 */}
      <div className="flex justify-between text-[10px] text-muted-foreground px-1">
        <span>输入: {formatNumber(inputTokens)}</span>
        <span>输出: {formatNumber(outputTokens)}</span>
      </div>

      {/* 按阶段统计（紧凑显示） */}
      {byStage.length > 0 && (
        <div className="space-y-1 pt-1">
          {byStage.map((stageStats, index) => {
            const stageName = stageNameMap[stageStats.stage] || stageStats.stage;
            return (
              <div key={index} className="text-[10px] p-1.5 rounded bg-muted/30">
                <div className="flex justify-between items-center mb-0.5">
                  <span className="font-medium">{stageName}</span>
                  <span className="font-semibold">{formatNumber(stageStats.totalTokens)}</span>
                </div>
                <div className="flex justify-between text-muted-foreground">
                  <span className="truncate max-w-[120px]">{stageStats.model}</span>
                  <span>↑{formatNumber(stageStats.inputTokens)} ↓{formatNumber(stageStats.outputTokens)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

