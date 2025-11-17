/**
 * 预设查询按钮组
 * 提供常用查询的快速访问
 */

'use client';

import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

interface PresetQueriesProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

const presetQueries = [
  '主角在第几章获得金手指？',
  '分析主角的能力发展',
  '梳理主要角色关系',
  '时间线重建',
  '检测前后矛盾',
];

export function PresetQueries({ onSelect, disabled }: PresetQueriesProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4" />
        <span>快速查询</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {presetQueries.map((query, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSelect(query)}
            disabled={disabled}
          >
            {query}
          </Button>
        ))}
      </div>
    </div>
  );
}

