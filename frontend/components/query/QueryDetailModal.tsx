/**
 * 查询详情弹窗
 * 显示单个查询的完整详情，包括答案、引用、Token统计等
 */

'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Clock, 
  Cpu, 
  AlertTriangle, 
  CheckCircle,
  TrendingUp,
  Copy 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import type { QueryResponse, Confidence } from '@/types/api';
import { TokenStats } from './TokenStats';

interface QueryDetailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  queryId: number | null;
  novelId?: number | null;
}

export function QueryDetailModal({ 
  open, 
  onOpenChange, 
  queryId,
  novelId 
}: QueryDetailModalProps) {
  const [detail, setDetail] = useState<QueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDetail = async () => {
    if (!queryId) return;

    try {
      setIsLoading(true);
      const response = await api.getQueryDetail(queryId);
      setDetail(response);
    } catch (error) {
      console.error('Failed to fetch query detail:', error);
      toast.error('获取查询详情失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (open && queryId) {
      fetchDetail();
    }
  }, [open, queryId]);

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'yyyy-MM-dd HH:mm:ss', { locale: zhCN });
    } catch {
      return dateStr;
    }
  };

  const getConfidenceBadge = (confidence: Confidence) => {
    const config = {
      high: { label: '高置信度', variant: 'default' as const, className: 'bg-green-500' },
      medium: { label: '中等置信度', variant: 'secondary' as const, className: '' },
      low: { label: '低置信度', variant: 'outline' as const, className: 'border-yellow-500 text-yellow-600' },
    };
    const conf = config[confidence] || config.medium;
    return (
      <Badge variant={conf.variant} className={conf.className}>
        {conf.label}
      </Badge>
    );
  };

  const formatResponseTime = (time: number) => {
    if (time < 1) {
      return `${(time * 1000).toFixed(0)}ms`;
    }
    return `${time.toFixed(2)}s`;
  };

  const handleCopy = async () => {
    if (!detail?.answer) return;
    try {
      await navigator.clipboard.writeText(detail.answer);
      toast.success('答案已复制到剪贴板');
    } catch (err) {
      console.error('复制失败:', err);
      toast.error('复制失败，请重试');
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl h-[90vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            查询详情
          </DialogTitle>
          <DialogDescription>
            查询ID: {queryId}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">加载中...</div>
          </div>
        ) : !detail ? (
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            无法加载查询详情
          </div>
        ) : (
          <div className="flex-1 min-h-0 flex flex-col">
            {/* 元信息卡片 */}
            <Card className="mb-4 flex-shrink-0">
              <CardContent className="p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">查询时间</div>
                      <div className="text-sm font-medium">
                        {formatDate(detail.timestamp)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">使用模型</div>
                      <div className="text-sm font-medium">{detail.model}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">响应时间</div>
                      <div className="text-sm font-medium">
                        {formatResponseTime(detail.response_time)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="text-xs text-muted-foreground">置信度</div>
                      <div className="text-sm font-medium">
                        {getConfidenceBadge(detail.confidence)}
                      </div>
                    </div>
                  </div>
                </div>

                {detail.rewritten_query && (
                  <div className="mt-3 pt-3 border-t">
                    <div className="text-xs text-muted-foreground mb-1">查询优化</div>
                    <div className="text-sm bg-muted/50 px-3 py-2 rounded border border-dashed">
                      {detail.rewritten_query}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 主要内容区域 - 使用标签页 */}
            <Tabs defaultValue="answer" className="flex-1 min-h-0 flex flex-col">
              <TabsList className="flex-shrink-0">
                <TabsTrigger value="answer">
                  <CheckCircle className="h-4 w-4 mr-1.5" />
                  完整答案
                </TabsTrigger>
                <TabsTrigger value="stats">
                  <TrendingUp className="h-4 w-4 mr-1.5" />
                  统计信息
                </TabsTrigger>
                {detail.contradictions.length > 0 && (
                  <TabsTrigger value="contradictions">
                    <AlertTriangle className="h-4 w-4 mr-1.5" />
                    矛盾检测
                    <Badge variant="destructive" className="ml-1.5 text-xs">
                      {detail.contradictions.length}
                    </Badge>
                  </TabsTrigger>
                )}
              </TabsList>

              {/* 答案标签页 */}
              <TabsContent value="answer" className="flex-1 min-h-0 mt-4 data-[state=active]:flex data-[state=active]:flex-col">
                <div className="flex justify-end mb-2 px-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs gap-1"
                    onClick={handleCopy}
                  >
                    <Copy className="h-3.5 w-3.5" />
                    复制答案
                  </Button>
                </div>
                <ScrollArea className="flex-1 min-h-0">
                  <div className="prose prose-sm max-w-none dark:prose-invert pr-4 pb-4">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {detail.answer}
                    </ReactMarkdown>
                  </div>
                </ScrollArea>
              </TabsContent>

              {/* 统计信息标签页 */}
              <TabsContent value="stats" className="flex-1 min-h-0 mt-4 data-[state=active]:flex data-[state=active]:flex-col">
                <ScrollArea className="flex-1 min-h-0">
                  <div className="space-y-4 pr-4 pb-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Token消耗统计</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <TokenStats stats={detail.token_stats} />
                      </CardContent>
                    </Card>

                    {detail.graph_info && Object.keys(detail.graph_info).length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">图谱信息</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <pre className="text-xs bg-muted p-3 rounded overflow-auto">
                            {JSON.stringify(detail.graph_info, null, 2)}
                          </pre>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>

              {/* 矛盾检测标签页 */}
              {detail.contradictions.length > 0 && (
                <TabsContent value="contradictions" className="flex-1 min-h-0 mt-4 data-[state=active]:flex data-[state=active]:flex-col">
                  <ScrollArea className="flex-1 min-h-0">
                    <div className="space-y-3 pr-4 pb-4">
                      {detail.contradictions.map((contradiction, index) => (
                        <Card key={index} className="border-yellow-500/50">
                          <CardHeader>
                            <div className="flex items-center gap-2">
                              <AlertTriangle className="h-4 w-4 text-yellow-600" />
                              <CardTitle className="text-sm">
                                {contradiction.type}
                              </CardTitle>
                              <Badge 
                                variant="outline" 
                                className="ml-auto border-yellow-500 text-yellow-600"
                              >
                                {contradiction.confidence}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">
                                早期描述（第{contradiction.earlyChapter}章）
                              </div>
                              <div className="text-sm bg-muted/30 p-2 rounded">
                                {contradiction.earlyDescription}
                              </div>
                            </div>
                            <div>
                              <div className="text-xs text-muted-foreground mb-1">
                                后期描述（第{contradiction.lateChapter}章）
                              </div>
                              <div className="text-sm bg-muted/30 p-2 rounded">
                                {contradiction.lateDescription}
                              </div>
                            </div>
                            {contradiction.analysis && (
                              <div>
                                <div className="text-xs text-muted-foreground mb-1">分析</div>
                                <div className="text-sm">{contradiction.analysis}</div>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </TabsContent>
              )}
            </Tabs>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

