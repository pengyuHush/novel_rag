/**
 * Token统计面板
 * 显示实时Token消耗统计
 */

'use client';

import type { TokenStats as TokenStatsType } from '@/types/api';
import { Cpu, ArrowDown, ArrowUp } from 'lucide-react';

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
      <div className="text-xs text-muted-foreground/40 text-center py-1">
        暂无数据
      </div>
    );
  }

  const totalTokens = stats.totalTokens || stats.total_tokens || 0;
  const inputTokens = stats.inputTokens || stats.input_tokens || 0;
  const outputTokens = stats.outputTokens || stats.output_tokens || 0;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Cpu className="h-4 w-4 stroke-[1.5]" />
          <span>算力消耗</span>
        </div>
        <span className="text-sm font-mono font-semibold text-primary">
          {formatNumber(totalTokens)}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="flex flex-col items-center p-2 rounded-lg bg-muted/20 border border-border/20">
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-0.5">
            <ArrowUp className="h-3 w-3 text-blue-500" />
            输入
          </div>
          <span className="text-xs font-mono">{formatNumber(inputTokens)}</span>
        </div>
        
        <div className="flex flex-col items-center p-2 rounded-lg bg-muted/20 border border-border/20">
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-0.5">
            <ArrowDown className="h-3 w-3 text-green-500" />
            输出
          </div>
          <span className="text-xs font-mono">{formatNumber(outputTokens)}</span>
        </div>
      </div>
    </div>
  );
}
