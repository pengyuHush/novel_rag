'use client';

/**
 * T079: 阅读器页面 (User Story 2: 在线阅读)
 * 
 * 功能:
 * - 显示小说章节列表(侧边栏)
 * - 显示章节内容(主区域)
 * - 支持章节导航(上一章/下一章)
 * - 支持全屏阅读模式
 */

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Layout, Spin, message } from 'antd';
import { FullscreenOutlined, FullscreenExitOutlined } from '@ant-design/icons';

import ChapterSidebar from '@/components/ChapterSidebar';
import ReadingArea from '@/components/ReadingArea';
import ChapterNavigation from '@/components/ChapterNavigation';

const { Header, Sider, Content } = Layout;

interface Novel {
  id: number;
  title: string;
  author?: string;
  totalChapters: number;
}

interface Chapter {
  num: number;
  title?: string;
  charCount: number;
}

interface ChapterContent {
  chapterNum: number;
  title?: string;
  content: string;
  prevChapter?: number;
  nextChapter?: number;
  totalChapters: number;
}

export default function ReaderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const novelId = searchParams.get('novelId');
  const chapterNumParam = searchParams.get('chapter');
  const currentChapter = chapterNumParam ? parseInt(chapterNumParam) : 1;
  
  const [novel, setNovel] = useState<Novel | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [chapterContent, setChapterContent] = useState<ChapterContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  
  // 验证参数
  useEffect(() => {
    if (!novelId) {
      message.error('未指定小说ID');
      router.push('/novels');
      return;
    }
  }, [novelId, router]);
  
  // 加载小说信息和章节列表
  useEffect(() => {
    if (!novelId) return;
    
    const fetchNovelAndChapters = async () => {
      try {
        setLoading(true);
        
        // 获取小说信息
        const novelResponse = await fetch(`${API_BASE_URL}/api/novels/${novelId}`);
        if (!novelResponse.ok) throw new Error('获取小说信息失败');
        const novelData = await novelResponse.json();
        setNovel({
          id: novelData.id,
          title: novelData.title,
          author: novelData.author,
          totalChapters: novelData.total_chapters
        });
        
        // 获取章节列表
        const chaptersResponse = await fetch(`${API_BASE_URL}/api/novels/${novelId}/chapters`);
        if (!chaptersResponse.ok) throw new Error('获取章节列表失败');
        const chaptersData = await chaptersResponse.json();
        
        // 映射字段名: char_count -> charCount
        const mappedChapters = chaptersData.map((ch: any) => ({
          num: ch.num,
          title: ch.title,
          charCount: ch.char_count
        }));
        setChapters(mappedChapters);
        
      } catch (error) {
        message.error(error instanceof Error ? error.message : '加载失败');
        router.push('/novels');
      } finally {
        setLoading(false);
      }
    };
    
    fetchNovelAndChapters();
  }, [novelId, router]);
  
  // 加载章节内容
  const loadChapterContent = useCallback(async (chapterNum: number) => {
    if (!novelId) return;
    
    try {
      setContentLoading(true);
      
      const response = await fetch(
        `${API_BASE_URL}/api/novels/${novelId}/chapters/${chapterNum}`
      );
      
      if (!response.ok) {
        throw new Error('获取章节内容失败');
      }
      
      const data = await response.json();
      setChapterContent({
        chapterNum: data.chapter_num,
        title: data.title,
        content: data.content,
        prevChapter: data.prev_chapter,
        nextChapter: data.next_chapter,
        totalChapters: data.total_chapters
      });
      
    } catch (error) {
      message.error(error instanceof Error ? error.message : '加载章节内容失败');
    } finally {
      setContentLoading(false);
    }
  }, [novelId]);
  
  // 当前章节变化时加载内容
  useEffect(() => {
    if (currentChapter) {
      loadChapterContent(currentChapter);
    }
  }, [currentChapter, loadChapterContent]);
  
  // 切换章节
  const handleChapterChange = (chapterNum: number) => {
    router.push(`/reader?novelId=${novelId}&chapter=${chapterNum}`);
  };
  
  // 切换全屏
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setIsFullscreen(!isFullscreen);
  };
  
  // 监听全屏状态变化
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }
  
  if (!novel) {
    return null;
  }
  
  return (
    <Layout className="h-screen">
      {/* 顶部标题栏 */}
      <Header className="bg-white border-b flex items-center justify-between px-6">
        <div>
          <h1 className="text-xl font-bold m-0">{novel.title}</h1>
          {novel.author && (
            <span className="text-sm text-gray-500">作者: {novel.author}</span>
          )}
        </div>
        <button
          onClick={toggleFullscreen}
          className="p-2 hover:bg-gray-100 rounded transition-colors"
          title={isFullscreen ? '退出全屏' : '进入全屏'}
        >
          {isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
        </button>
      </Header>
      
      <Layout>
        {/* 章节侧边栏 */}
        {!isFullscreen && (
          <Sider
            width={280}
            theme="light"
            collapsible
            collapsed={collapsed}
            onCollapse={setCollapsed}
            className="border-r"
          >
            <ChapterSidebar
              chapters={chapters}
              currentChapter={currentChapter}
              onChapterSelect={handleChapterChange}
              collapsed={collapsed}
            />
          </Sider>
        )}
        
        {/* 主阅读区域 */}
        <Layout>
          <Content className="bg-white p-6">
            {contentLoading ? (
              <div className="flex items-center justify-center h-full">
                <Spin size="large" tip="加载章节内容..." />
              </div>
            ) : chapterContent ? (
              <>
                <ReadingArea content={chapterContent} />
                <ChapterNavigation
                  currentChapter={currentChapter}
                  prevChapter={chapterContent.prevChapter}
                  nextChapter={chapterContent.nextChapter}
                  onChapterChange={handleChapterChange}
                />
              </>
            ) : (
              <div className="text-center text-gray-500 mt-20">
                请选择章节开始阅读
              </div>
            )}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

