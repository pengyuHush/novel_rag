/**
 * 在线阅读器页面
 * 显示小说章节列表和内容
 */

'use client';

import { use, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { ChevronLeft, ChevronRight, ArrowLeft, Search } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import type { ChapterListItem, ChapterContent } from '@/types/api';

interface ReaderPageProps {
  params: Promise<{ novelId: string }>;
}

export default function ReaderPage({ params }: ReaderPageProps) {
  const resolvedParams = use(params);
  const novelId = parseInt(resolvedParams.novelId);
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [chapters, setChapters] = useState<ChapterListItem[]>([]);
  const [currentChapter, setCurrentChapter] = useState<ChapterContent | null>(null);
  const [currentChapterNum, setCurrentChapterNum] = useState<number>(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!novelId || isNaN(novelId)) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">无效的小说ID</p>
      </div>
    );
  }

  // 加载章节列表
  useEffect(() => {
    console.log('Loading chapters for novel:', novelId);
    loadChapters();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [novelId]);

  // 从URL参数读取章节号
  useEffect(() => {
    const chapterParam = searchParams?.get('chapter');
    if (chapterParam) {
      setCurrentChapterNum(parseInt(chapterParam));
    }
  }, [searchParams]);

  // 加载章节内容
  useEffect(() => {
    if (currentChapterNum > 0) {
      loadChapter(currentChapterNum);
    }
  }, [currentChapterNum, novelId]);

  const loadChapters = async () => {
    try {
      console.log('Fetching chapters for novel:', novelId);
      const chapterList = await api.getChapters(novelId);
      console.log('Chapter list response:', chapterList);
      
      // 处理不同的返回格式
      let chapters = [];
      if (Array.isArray(chapterList)) {
        chapters = chapterList;
      } else if (chapterList && Array.isArray(chapterList.items)) {
        chapters = chapterList.items;
      }
      
      console.log('Processed chapters:', chapters);
      setChapters(chapters);
      
      if (chapters.length > 0) {
        toast.success(`加载了 ${chapters.length} 个章节`);
      }
    } catch (error) {
      console.error('Failed to load chapters:', error);
      toast.error('加载章节列表失败');
      setChapters([]);
    }
  };

  const loadChapter = async (chapterNum: number) => {
    try {
      setIsLoading(true);
      const chapter = await api.getChapterContent(novelId, chapterNum);
      setCurrentChapter(chapter);
      // 更新URL
      router.replace(`/reader/${novelId}?chapter=${chapterNum}`, { scroll: false });
    } catch (error) {
      console.error('Failed to load chapter:', error);
      toast.error(`加载第${chapterNum}章失败`);
      setCurrentChapter(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrevChapter = () => {
    if (currentChapter?.prev_chapter) {
      setCurrentChapterNum(currentChapter.prev_chapter);
    }
  };

  const handleNextChapter = () => {
    if (currentChapter?.next_chapter) {
      setCurrentChapterNum(currentChapter.next_chapter);
    }
  };

  const filteredChapters = (chapters || []).filter(
    (chapter) =>
      chapter.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      chapter.num.toString().includes(searchTerm)
  );

  return (
    <div className="flex h-full">
      {/* 左侧：章节列表 */}
      <aside className="w-64 border-r flex flex-col h-full">
        <div className="p-4 border-b space-y-3 flex-shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/')}
            className="w-full justify-start"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回主页
          </Button>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="搜索章节..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-2">
              {filteredChapters.map((chapter) => (
                <Button
                  key={chapter.num}
                  variant={currentChapterNum === chapter.num ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setCurrentChapterNum(chapter.num)}
                  className="w-full justify-start mb-1 h-auto py-2"
                >
                  <div className="text-left">
                    <div className="font-medium">第{chapter.num}章</div>
                    {chapter.title && (
                      <div className="text-xs text-muted-foreground truncate">
                        {chapter.title}
                      </div>
                    )}
                  </div>
                </Button>
              ))}
            </div>
          </ScrollArea>
        </div>
      </aside>

      {/* 右侧：阅读区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 章节标题 */}
        {currentChapter && (
          <div className="p-4 border-b flex-shrink-0">
            <h2 className="text-xl font-bold">
              第{currentChapter.chapter_num}章
              {currentChapter.title && ` ${currentChapter.title}`}
            </h2>
          </div>
        )}

        {/* 章节内容 */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-8">
            {isLoading ? (
              <div className="text-center text-muted-foreground py-20">
                加载中...
              </div>
            ) : currentChapter ? (
              <div className="prose prose-lg max-w-none dark:prose-invert">
                <pre className="whitespace-pre-wrap font-sans leading-relaxed">
                  {currentChapter.content}
                </pre>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-20">
                请选择章节
              </div>
            )}
          </div>
        </div>

        {/* 底部导航 */}
        {currentChapter && (
          <div className="p-4 border-t flex-shrink-0">
            <div className="flex justify-between items-center max-w-4xl mx-auto">
              <Button
                onClick={handlePrevChapter}
                disabled={!currentChapter.prev_chapter}
                size="lg"
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                上一章
              </Button>

              <span className="text-sm text-muted-foreground">
                第 {currentChapter.chapter_num} / {currentChapter.total_chapters} 章
              </span>

              <Button
                onClick={handleNextChapter}
                disabled={!currentChapter.next_chapter}
                size="lg"
              >
                下一章
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

