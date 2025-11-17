/**
 * 查询阶段状态指示器
 * 显示5个查询处理阶段的进度
 */

'use client';

import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Search, Database, Brain, CheckCircle2, Package } from 'lucide-react';
import { QueryStage } from '@/types/api';
import { cn } from '@/lib/utils';

interface QueryStagesProps {
  currentStage: QueryStage | null;
  progress: number; // 0-1
}

const stages = [
  {
    key: QueryStage.UNDERSTANDING,
    label: '查询理解',
    icon: Search,
  },
  {
    key: QueryStage.RETRIEVING,
    label: '检索内容',
    icon: Database,
  },
  {
    key: QueryStage.GENERATING,
    label: '生成答案',
    icon: Brain,
  },
  {
    key: QueryStage.VALIDATING,
    label: 'Self-RAG验证',
    icon: CheckCircle2,
  },
  {
    key: QueryStage.FINALIZING,
    label: '完成汇总',
    icon: Package,
  },
];

export function QueryStages({ currentStage, progress }: QueryStagesProps) {
  if (!currentStage) return null;

  const currentIndex = stages.findIndex((s) => s.key === currentStage);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = index === currentIndex;
          const isCompleted = index < currentIndex;

          return (
            <div
              key={stage.key}
              className={cn(
                'flex flex-col items-center flex-1',
                index < stages.length - 1 && 'relative'
              )}
            >
              {/* 图标和状态 */}
              <div
                className={cn(
                  'flex items-center justify-center w-7 h-7 rounded-full border-2 transition-colors',
                  isActive && 'border-primary bg-primary text-primary-foreground',
                  isCompleted && 'border-green-500 bg-green-500 text-white',
                  !isActive && !isCompleted && 'border-muted-foreground/30 bg-background'
                )}
              >
                <Icon className="h-3.5 w-3.5" />
              </div>

              {/* 标签 */}
              <div className="mt-1 text-[10px] text-center">
                {isActive ? (
                  <Badge variant="default" className="text-[10px] px-1.5 py-0">
                    {stage.label}
                  </Badge>
                ) : (
                  <span
                    className={cn(
                      'font-medium',
                      isCompleted ? 'text-green-600' : 'text-muted-foreground'
                    )}
                  >
                    {stage.label}
                  </span>
                )}
              </div>

              {/* 连接线 */}
              {index < stages.length - 1 && (
                <div
                  className={cn(
                    'absolute top-3.5 left-1/2 w-full h-0.5',
                    isCompleted ? 'bg-green-500' : 'bg-muted-foreground/30'
                  )}
                  style={{ transform: 'translateY(-50%)' }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* 进度条 */}
      <div className="flex items-center gap-2">
        <Progress value={progress * 100} className="h-1.5 flex-1" />
        <span className="text-[10px] text-muted-foreground tabular-nums min-w-[32px] text-right">
          {(progress * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

