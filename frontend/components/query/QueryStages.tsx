/**
 * 查询阶段状态指示器
 * 显示5个查询处理阶段的进度
 */

'use client';

import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Search, Database, Brain, CheckCircle2, Package, Check } from 'lucide-react';
import { QueryStage } from '@/types/api';
import { cn } from '@/lib/utils';

interface QueryStagesProps {
  currentStage: QueryStage | null;
  progress: number; // 0-1
}

const stages = [
  { key: QueryStage.UNDERSTANDING, label: '理解', icon: Search },
  { key: QueryStage.RETRIEVING, label: '检索', icon: Database },
  { key: QueryStage.GENERATING, label: '思考', icon: Brain },
  { key: QueryStage.VALIDATING, label: '验证', icon: CheckCircle2 },
  { key: QueryStage.FINALIZING, label: '汇总', icon: Package },
];

export function QueryStages({ currentStage, progress }: QueryStagesProps) {
  if (!currentStage) return null;

  const currentIndex = stages.findIndex((s) => s.key === currentStage);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between relative">
        {/* 进度背景线 */}
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-muted -z-10 -translate-y-1/2" />
        
        {/* 进度填充线 (近似计算) */}
        <div 
          className="absolute top-1/2 left-0 h-0.5 bg-primary/20 -z-10 -translate-y-1/2 transition-all duration-500"
          style={{ width: `${((currentIndex) / (stages.length - 1)) * 100}%` }}
        />

        {stages.map((stage, index) => {
          const isActive = index === currentIndex;
          const isCompleted = index < currentIndex;
          const Icon = stage.icon;

          return (
            <div key={stage.key} className="flex flex-col items-center gap-1.5 relative z-10 group">
              <div
                className={cn(
                  "flex items-center justify-center w-6 h-6 rounded-full border-2 transition-all duration-300 bg-background",
                  isActive 
                    ? "border-primary text-primary scale-110 ring-2 ring-primary/20" 
                    : isCompleted 
                      ? "border-primary/40 text-primary/40" 
                      : "border-muted text-muted-foreground/30"
                )}
              >
                {isCompleted ? (
                  <Check className="h-3 w-3 stroke-[3]" />
                ) : (
                  <Icon className={cn("h-3 w-3", isActive ? "stroke-[2]" : "stroke-[1.5]")} />
                )}
              </div>
              
              <span className={cn(
                "text-[10px] font-medium transition-colors",
                isActive ? "text-foreground" : "text-muted-foreground/50"
              )}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* 总体进度 */}
      <div className="flex items-center gap-3 bg-muted/30 rounded-full px-3 py-1">
        <Progress value={progress * 100} className="h-1 flex-1" />
        <span className="text-[10px] font-mono text-muted-foreground tabular-nums w-8 text-right">
          {(progress * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  );
}
