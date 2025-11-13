'use client';

/**
 * T080: 章节侧边栏组件 (User Story 2: 在线阅读)
 * T082: 实现章节搜索功能
 * 
 * 功能:
 * - 显示所有章节列表
 * - 高亮当前章节
 * - 支持章节搜索
 * - 支持快速跳转
 */

import { useState, useMemo } from 'react';
import { Input, List, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface Chapter {
  num: number;
  title?: string;
  charCount: number;
}

interface ChapterSidebarProps {
  chapters: Chapter[];
  currentChapter: number;
  onChapterSelect: (chapterNum: number) => void;
  collapsed: boolean;
}

export default function ChapterSidebar({
  chapters,
  currentChapter,
  onChapterSelect,
  collapsed
}: ChapterSidebarProps) {
  const [searchText, setSearchText] = useState('');
  
  // 过滤章节
  const filteredChapters = useMemo(() => {
    if (!searchText.trim()) {
      return chapters;
    }
    
    const searchLower = searchText.toLowerCase();
    return chapters.filter(chapter => 
      chapter.num.toString().includes(searchText) ||
      chapter.title?.toLowerCase().includes(searchLower)
    );
  }, [chapters, searchText]);
  
  // 滚动到当前章节
  const scrollToCurrentChapter = () => {
    const element = document.getElementById(`chapter-${currentChapter}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };
  
  // 当侧边栏展开时滚动到当前章节
  useMemo(() => {
    if (!collapsed && currentChapter) {
      setTimeout(scrollToCurrentChapter, 100);
    }
  }, [collapsed, currentChapter]);
  
  if (collapsed) {
    return null;
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* 搜索框 */}
      <div className="p-4 border-b">
        <Input
          placeholder="搜索章节..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
        />
      </div>
      
      {/* 章节列表 */}
      <div className="flex-1 overflow-y-auto">
        <List
          dataSource={filteredChapters}
          renderItem={(chapter) => (
            <List.Item
              id={`chapter-${chapter.num}`}
              onClick={() => onChapterSelect(chapter.num)}
              className={`
                cursor-pointer px-4 hover:bg-gray-50 transition-colors
                ${chapter.num === currentChapter ? 'bg-blue-50 border-l-4 border-blue-500' : ''}
              `}
              style={{ padding: '12px 16px' }}
            >
              <div className="w-full">
                <div className="flex items-center justify-between mb-1">
                  <Text
                    strong={chapter.num === currentChapter}
                    className="text-sm"
                  >
                    第{chapter.num}章
                  </Text>
                  <Text type="secondary" className="text-xs">
                    {formatCharCount(chapter.charCount)}
                  </Text>
                </div>
                {chapter.title && (
                  <Text
                    className={`text-xs ${chapter.num === currentChapter ? 'text-blue-600' : 'text-gray-600'}`}
                    ellipsis={{ tooltip: chapter.title }}
                  >
                    {chapter.title}
                  </Text>
                )}
              </div>
            </List.Item>
          )}
          locale={{ emptyText: '未找到匹配的章节' }}
        />
      </div>
      
      {/* 底部统计信息 */}
      <div className="p-4 border-t bg-gray-50">
        <Text type="secondary" className="text-xs">
          共 {chapters.length} 章 {filteredChapters.length !== chapters.length && `(显示 ${filteredChapters.length} 章)`}
        </Text>
      </div>
    </div>
  );
}

// 格式化字数显示
function formatCharCount(count: number): string {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万字`;
  }
  return `${count}字`;
}

