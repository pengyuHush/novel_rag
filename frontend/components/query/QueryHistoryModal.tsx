/**
 * 查询历史弹窗
 * 显示历史查询记录，支持翻页和查看详情
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
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { ThumbsUp, ThumbsDown, Clock, MessageSquare, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface QueryHistoryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  novelId?: number | null;
}

interface HistoryItem {
  id: number;
  novel_id: number;
  query: string;
  answer: string;
  model: string;
  total_tokens: number;
  confidence: string;
  created_at: string;
  feedback: 'positive' | 'negative' | null;
}

export function QueryHistoryModal({ open, onOpenChange, novelId }: QueryHistoryModalProps) {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const response = await api.getQueryHistory({
        novelId: novelId || undefined,
        page,
        pageSize,
      });
      setHistoryItems(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to fetch query history:', error);
      toast.error('获取查询历史失败');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchHistory();
    }
  }, [open, page, novelId]);

  const getConfidenceBadge = (confidence: string) => {
    const config = {
      high: { label: '高', variant: 'default' as const },
      medium: { label: '中', variant: 'secondary' as const },
      low: { label: '低', variant: 'outline' as const },
    };
    const conf = config[confidence as keyof typeof config] || config.medium;
    return <Badge variant={conf.variant}>{conf.label}</Badge>;
  };

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'yyyy-MM-dd HH:mm', { locale: zhCN });
    } catch {
      return dateStr;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            查询历史
            {novelId && <span className="text-sm text-muted-foreground">（当前小说）</span>}
          </DialogTitle>
          <DialogDescription>
            共 {total} 条查询记录
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="max-h-[calc(90vh-180px)] mt-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="text-muted-foreground">加载中...</div>
            </div>
          ) : historyItems.length === 0 ? (
            <div className="flex items-center justify-center h-32 text-muted-foreground">
              <div className="text-center">
                <MessageSquare className="h-10 w-10 mx-auto mb-2 opacity-20" />
                <p>暂无查询历史</p>
              </div>
            </div>
          ) : (
            <div className="space-y-3 pr-4">
              {historyItems.map((item) => (
                <Card key={item.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        {/* 问题 */}
                        <div className="flex items-center gap-2 mb-2">
                          <MessageSquare className="h-4 w-4 text-primary flex-shrink-0" />
                          <p className="font-medium text-sm">{item.query}</p>
                        </div>

                        {/* 答案摘要 */}
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                          {item.answer}
                        </p>

                        {/* 元信息 */}
                        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {formatDate(item.created_at)}
                          </span>
                          <span>模型: {item.model}</span>
                          <span>Token: {item.total_tokens}</span>
                          <span>置信度: {getConfidenceBadge(item.confidence)}</span>
                          {item.feedback && (
                            <span className="flex items-center gap-1">
                              {item.feedback === 'positive' ? (
                                <>
                                  <ThumbsUp className="h-3 w-3 text-green-600" />
                                  <span className="text-green-600">准确</span>
                                </>
                              ) : (
                                <>
                                  <ThumbsDown className="h-3 w-3 text-red-600" />
                                  <span className="text-red-600">不准确</span>
                                </>
                              )}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* 操作按钮 */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // TODO: 实现查看详情功能
                          toast.info('查看详情功能即将上线');
                        }}
                      >
                        查看详情
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* 分页控制 */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-muted-foreground">
              第 {page} 页，共 {totalPages} 页
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={page === 1 || isLoading}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                上一页
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages || isLoading}
              >
                下一页
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

