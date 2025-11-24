/**
 * 左侧小说列表侧边栏
 * 显示小说总览和小说列表，支持勾选、阅读、查看图谱等操作
 */

'use client';

import { useEffect, useState } from 'react';
import { Upload, BookOpen, Network, Trash2, Plus, Library, History, FilePlus, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useNovelStore } from '@/store/novelStore';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import type { NovelListItem, IndexStatus } from '@/types/api';
import { cn } from '@/lib/utils';

interface NovelSidebarProps {
  onUploadClick?: () => void;
  onViewGraphClick?: (novelId: number) => void;
  onHistoryClick?: () => void;
  onAppendClick?: (novel: NovelListItem) => void;
}

function formatNumber(num: number): string {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`;
  }
  return num.toLocaleString();
}

function getStatusBadge(status: IndexStatus) {
  const variants: Record<IndexStatus, { label: string; className: string }> = {
    pending: { label: '待处理', className: 'bg-secondary text-secondary-foreground' },
    processing: { label: '处理中', className: 'bg-primary text-primary-foreground' },
    completed: { label: '已完成', className: 'bg-green-50 text-green-700 border-green-200' },
    failed: { label: '失败', className: 'bg-destructive/10 text-destructive' },
  };
  
  const { label, className } = variants[status];
  return <span className={cn("text-[10px] px-2 py-0.5 rounded-full font-medium", className)}>{label}</span>;
}

export function NovelSidebar({ onUploadClick, onViewGraphClick, onHistoryClick, onAppendClick }: NovelSidebarProps) {
  const router = useRouter();
  const { novels = [], selectedNovelIds, setNovels, toggleNovelSelection, removeNovel, setLoading } = useNovelStore();
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
      setNovels(novelList);
    } catch (error) {
      console.error('Failed to load novels:', error);
      toast.error('加载小说列表失败');
    } finally {
      setIsRefreshing(false);
      setLoading(false);
    }
  };

  const handleSelectNovel = (novelId: number, checked: boolean) => {
    toggleNovelSelection(novelId);
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
  const totalWords = novels.reduce((sum, novel) => sum + (novel.total_chars || 0), 0);

  return (
    <aside className="w-80 border-r border-border/40 bg-sidebar flex flex-col h-full overflow-hidden">
      {/* 顶部：操作按钮 */}
      <div className="p-6 space-y-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium tracking-wide">我的书架</h2>
          <span className="text-xs text-muted-foreground">{totalNovels} 本书</span>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <Button onClick={onUploadClick} className="w-full shadow-sm hover:shadow transition-all" size="default">
            <Upload className="mr-2 h-4 w-4 stroke-[1.5]" />
            上传
          </Button>
          {onHistoryClick && (
            <Button onClick={onHistoryClick} variant="outline" className="w-full border-border/60 shadow-sm hover:shadow transition-all">
              <History className="mr-2 h-4 w-4 stroke-[1.5]" />
              历史
            </Button>
          )}
        </div>
      </div>

      {/* 小说列表 */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="px-6 pb-6 space-y-4">
          {novels.length === 0 && !isRefreshing && (
            <div className="text-center text-muted-foreground py-12 bg-muted/30 rounded-xl border border-border/40 border-dashed">
              <Library className="h-8 w-8 mx-auto mb-3 opacity-20 stroke-[1.5]" />
              <p className="text-sm">暂无小说</p>
              <p className="text-xs mt-1 opacity-60">点击上方上传按钮开始</p>
            </div>
          )}

          {novels.map((novel) => {
            const isSelected = selectedNovelIds.includes(novel.id);
            return (
              <div 
                key={novel.id} 
                className={cn(
                  "group relative rounded-xl border p-4 transition-all duration-200 cursor-pointer hover:shadow-md",
                  isSelected 
                    ? "bg-card border-primary/20 shadow-sm ring-1 ring-primary/10" 
                    : "bg-card border-border/40 hover:border-border/80"
                )}
                onClick={() => handleSelectNovel(novel.id, !isSelected)}
              >
                {/* 选中标记 */}
                <div className={cn(
                  "absolute top-4 right-4 h-5 w-5 rounded-full border flex items-center justify-center transition-colors",
                  isSelected ? "bg-primary border-primary text-primary-foreground" : "border-muted-foreground/30"
                )}>
                  {isSelected && <Check className="h-3 w-3 stroke-[2.5]" />}
                </div>

                <div className="pr-8">
                  <h3 className={cn("font-medium leading-tight transition-colors", isSelected ? "text-foreground" : "text-foreground/80")}>
                    {novel.title}
                  </h3>
                  {novel.author && (
                    <p className="text-sm text-muted-foreground mt-1">{novel.author}</p>
                  )}
                </div>

                <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground/80">
                  <span>{formatNumber(novel.total_chars)}字</span>
                  <span>{novel.total_chapters}章</span>
                  {getStatusBadge(novel.index_status)}
                </div>

                {novel.index_status === 'processing' && (
                  <div className="mt-3">
                    <Progress value={novel.index_progress * 100} className="h-1" />
                  </div>
                )}

                {/* 操作栏 - 悬停显示或选中显示 */}
                <div className={cn(
                  "mt-4 pt-3 border-t border-border/40 flex items-center gap-1 transition-opacity",
                  isSelected || "group-hover:opacity-100 opacity-50"
                )}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 flex-1 text-muted-foreground hover:text-primary hover:bg-primary/5"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRead(novel.id);
                    }}
                    disabled={novel.index_status !== 'completed'}
                  >
                    <BookOpen className="mr-1.5 h-3.5 w-3.5 stroke-[1.5]" />
                    阅读
                  </Button>

                  <Button 
                    variant="ghost" 
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/5"
                    onClick={(e) => {
                      e.stopPropagation();
                      onViewGraphClick?.(novel.id);
                    }}
                    disabled={novel.index_status !== 'completed'}
                    title="查看图谱"
                  >
                    <Network className="h-3.5 w-3.5 stroke-[1.5]" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-primary hover:bg-primary/5"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAppendClick?.(novel);
                    }}
                    disabled={novel.index_status !== 'completed'}
                    title="追加章节"
                  >
                    <FilePlus className="h-3.5 w-3.5 stroke-[1.5]" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(novel.id);
                    }}
                    className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10 ml-auto"
                    title="删除"
                  >
                    <Trash2 className="h-3.5 w-3.5 stroke-[1.5]" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </aside>
  );
}
