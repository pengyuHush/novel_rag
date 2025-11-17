/**
 * 左侧小说列表侧边栏
 * 显示小说总览和小说列表，支持勾选、阅读、查看图谱等操作
 */

'use client';

import { useEffect, useState } from 'react';
import { Upload, BookOpen, Network, Trash2, Plus, Library } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useNovelStore } from '@/store/novelStore';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import type { NovelListItem, IndexStatus } from '@/types/api';

interface NovelSidebarProps {
  onUploadClick?: () => void;
  onViewGraphClick?: (novelId: number) => void;
}

function formatNumber(num: number): string {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`;
  }
  return num.toLocaleString();
}

function getStatusBadge(status: IndexStatus) {
  const variants: Record<IndexStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
    pending: { label: '待处理', variant: 'secondary' },
    processing: { label: '处理中', variant: 'default' },
    completed: { label: '已完成', variant: 'outline' },
    failed: { label: '失败', variant: 'destructive' },
  };
  
  const { label, variant } = variants[status];
  return <Badge variant={variant}>{label}</Badge>;
}

export function NovelSidebar({ onUploadClick, onViewGraphClick }: NovelSidebarProps) {
  const router = useRouter();
  const { novels = [], selectedNovelId, setNovels, setSelectedNovel, removeNovel, setLoading } = useNovelStore();
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 加载小说列表
  useEffect(() => {
    loadNovels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadNovels = async () => {
    try {
      setIsRefreshing(true);
      setLoading(true);
      const novelList = await api.getNovels();
      console.log('Loaded novels:', novelList);
      setNovels(novelList);
      if (novelList && novelList.length > 0) {
        toast.success(`加载了 ${novelList.length} 本小说`);
      }
    } catch (error) {
      console.error('Failed to load novels:', error);
      toast.error('加载小说列表失败');
    } finally {
      setIsRefreshing(false);
      setLoading(false);
    }
  };

  const handleSelectNovel = (novelId: number, checked: boolean) => {
    if (checked) {
      setSelectedNovel(novelId);
    } else if (selectedNovelId === novelId) {
      setSelectedNovel(null);
    }
  };

  const handleDelete = async (novelId: number) => {
    if (!confirm('确定要删除这本小说吗？此操作不可恢复。')) {
      return;
    }

    try {
      await api.deleteNovel(novelId);
      removeNovel(novelId);
      toast.success('小说已删除');
    } catch (error) {
      console.error('Failed to delete novel:', error);
      toast.error('删除失败');
    }
  };

  const handleRead = (novelId: number) => {
    router.push(`/reader/${novelId}`);
  };

  // 计算统计信息
  const totalNovels = novels.length;
  const totalChapters = novels.reduce((sum, novel) => sum + (novel.total_chapters || 0), 0);
  const totalWords = novels.reduce((sum, novel) => sum + (novel.total_chars || 0), 0);
  const indexedNovels = novels.filter(n => n.index_status === 'completed').length;

  return (
    <aside className="w-80 border-r bg-background flex flex-col">
      {/* 顶部：上传按钮 */}
      <div className="p-4 border-b">
        <Button onClick={onUploadClick} className="w-full" size="lg">
          <Upload className="mr-2 h-4 w-4" />
          上传小说
        </Button>
      </div>

      {/* 小说总览 */}
      <div className="px-4 py-3 border-b bg-muted/30">
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Library className="h-4 w-4" />
          小说总览
        </h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex flex-col">
            <span className="text-muted-foreground">小说数量</span>
            <span className="font-semibold text-base">{totalNovels}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground">已索引</span>
            <span className="font-semibold text-base text-green-600">{indexedNovels}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground">总章节</span>
            <span className="font-semibold text-base">{totalChapters.toLocaleString()}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-muted-foreground">总字数</span>
            <span className="font-semibold text-base">{(totalWords / 10000).toFixed(1)}万</span>
          </div>
        </div>
      </div>

      {/* 小说列表 */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {novels.length === 0 && !isRefreshing && (
            <div className="text-center text-muted-foreground py-8">
              <p>暂无小说</p>
              <p className="text-sm mt-2">点击上方按钮上传小说</p>
            </div>
          )}

          {novels.map((novel) => (
            <Card 
              key={novel.id} 
              className={`cursor-pointer transition-all ${selectedNovelId === novel.id ? 'border-primary bg-primary/5' : 'hover:border-primary/50'}`}
              onClick={() => handleSelectNovel(novel.id, selectedNovelId !== novel.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <Checkbox
                      checked={selectedNovelId === novel.id}
                      onCheckedChange={(checked) => handleSelectNovel(novel.id, checked as boolean)}
                      className="mt-1 h-5 w-5"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div className="flex-1">
                      <CardTitle className="text-base leading-tight">{novel.title}</CardTitle>
                      {novel.author && (
                        <CardDescription className="text-sm">{novel.author}</CardDescription>
                      )}
                    </div>
                  </div>
                  {getStatusBadge(novel.index_status)}
                </div>
              </CardHeader>

              <CardContent className="pb-3 space-y-2">
                <div className="text-sm text-muted-foreground space-y-1">
                  <div>字数：{formatNumber(novel.total_chars)}</div>
                  <div>章节：{novel.total_chapters}</div>
                </div>

                {novel.index_status === 'processing' && (
                  <div>
                    <Progress value={novel.index_progress * 100} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-1">
                      索引进度: {(novel.index_progress * 100).toFixed(0)}%
                    </p>
                  </div>
                )}
              </CardContent>

              <CardFooter className="pt-0 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRead(novel.id);
                  }}
                  disabled={novel.index_status !== 'completed'}
                >
                  <BookOpen className="mr-1 h-3 w-3" />
                  阅读
                </Button>

                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onViewGraphClick?.(novel.id);
                      }}
                      disabled={novel.index_status !== 'completed'}
                  title="查看图谱"
                    >
                  <Network className="h-4 w-4" />
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(novel.id);
                      }}
                  className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                  title="删除"
                    >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}

