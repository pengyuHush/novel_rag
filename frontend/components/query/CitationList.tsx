/**
 * 引用列表组件
 * 显示查询结果的原文引用
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, ExternalLink } from 'lucide-react';
import type { Citation } from '@/types/api';
import { useRouter } from 'next/navigation';

interface CitationListProps {
  citations?: Citation[];
  novelId: number | null;
  className?: string;
}

export function CitationList({ citations = [], novelId, className }: CitationListProps) {
  const router = useRouter();

  const handleViewChapter = (chapterNum: number) => {
    if (novelId) {
      router.push(`/reader/${novelId}?chapter=${chapterNum}`);
    }
  };

  return (
    <div className={`${className} flex flex-col`}>
      <div className="flex-shrink-0 p-2 border-b bg-background">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          <h3 className="text-sm font-semibold">原文引用</h3>
          {citations.length > 0 && (
            <Badge variant="secondary" className="text-xs">{citations.length}</Badge>
          )}
        </div>
      </div>
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-2 space-y-2">
            {citations.length === 0 && (
              <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">
                <p>查询完成后将显示引用内容</p>
              </div>
            )}

            {citations.map((citation, index) => (
            <Card key={index}>
              <CardHeader className="pb-2 pt-2 px-3">
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-xs flex items-center gap-1.5">
                    <Badge variant="outline" className="text-[10px] px-1.5 py-0">第{citation.chapterNum}章</Badge>
                    {citation.chapterTitle && (
                      <span className="text-[10px] text-muted-foreground truncate max-w-[120px]">
                        {citation.chapterTitle}
                      </span>
                    )}
                  </CardTitle>
                  {citation.score !== undefined && (
                    <Badge variant="secondary" className="text-[10px] px-1.5 py-0 flex-shrink-0">
                      {(citation.score * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5 pt-0 px-3 pb-2">
                <CardDescription className="text-xs leading-relaxed whitespace-pre-wrap line-clamp-4">
                  {citation.text}
                </CardDescription>
                {novelId && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleViewChapter(citation.chapterNum)}
                    className="w-full h-7 text-xs"
                  >
                    <ExternalLink className="mr-1.5 h-3 w-3" />
                    查看完整章节
                  </Button>
                )}
              </CardContent>
            </Card>
            ))}
        </div>
      </ScrollArea>
    </div>
  );
}

