/**
 * 引用列表组件
 * 显示查询结果的原文引用
 */

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, ExternalLink, Quote } from 'lucide-react';
import type { Citation } from '@/types/api';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

interface CitationListProps {
  citations?: Citation[];
  novelId: number | null;
  className?: string;
}

export function CitationList({ citations = [], novelId, className }: CitationListProps) {
  const router = useRouter();

  const handleViewChapter = (citation: Citation) => {
    const targetNovelId = citation.novelId || novelId;
    if (targetNovelId) {
      router.push(`/reader/${targetNovelId}?chapter=${citation.chapterNum}`);
    }
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      <div className="flex-shrink-0 p-4 border-b border-border/40 bg-muted/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Quote className="h-4 w-4 text-primary stroke-[1.5]" />
          <h3 className="font-medium text-sm">原文依据</h3>
        </div>
        {citations.length > 0 && (
          <span className="text-xs text-muted-foreground bg-muted/50 px-2 py-0.5 rounded-full">
            {citations.length} 条引用
          </span>
        )}
      </div>
      
      <ScrollArea className="flex-1 min-h-0 bg-muted/10">
        <div className="p-4 space-y-3">
            {citations.length === 0 && (
              <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground/40 text-sm gap-2">
                <Quote className="h-8 w-8 stroke-[1] opacity-50" />
                <p>暂无引用内容</p>
              </div>
            )}

            {citations.map((citation, index) => (
            <div 
              key={index}
              className="group relative bg-card rounded-xl border border-border/40 p-4 transition-all hover:shadow-md hover:border-border/80"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[10px] font-normal bg-muted/30 text-muted-foreground border-border/50">
                      第{citation.chapterNum}章
                    </Badge>
                    {citation.novelTitle && (
                      <span className="text-[10px] text-muted-foreground/70">
                        {citation.novelTitle}
                      </span>
                    )}
                  </div>
                  {citation.chapterTitle && (
                    <h4 className="text-xs font-medium text-foreground/90 truncate max-w-[180px]">
                      {citation.chapterTitle}
                    </h4>
                  )}
                </div>
                
                {citation.score !== undefined && (
                  <div className="flex items-center gap-1 text-[10px] font-medium text-primary/80 bg-primary/5 px-1.5 py-0.5 rounded">
                    <span className="opacity-60">相似度</span>
                    {(citation.score * 100).toFixed(0)}%
                  </div>
                )}
              </div>

              <p className="text-xs text-muted-foreground leading-relaxed line-clamp-4 mb-3 font-serif">
                {citation.text}
              </p>

              {(citation.novelId || novelId) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleViewChapter(citation)}
                  className="w-full h-7 text-[10px] text-muted-foreground hover:text-primary hover:bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <ExternalLink className="mr-1.5 h-3 w-3" />
                  阅读原文
                </Button>
              )}
            </div>
            ))}
        </div>
      </ScrollArea>
    </div>
  );
}
