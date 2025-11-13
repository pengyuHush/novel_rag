'use client';

/**
 * T083: 章节导航组件 (User Story 2: 在线阅读)
 * 
 * 功能:
 * - 上一章/下一章按钮
 * - 快速跳转到第一章/最新章
 * - 显示当前进度
 * - 键盘快捷键支持
 */

import { Button, Space, InputNumber } from 'antd';
import { LeftOutlined, RightOutlined, VerticalAlignTopOutlined, VerticalAlignBottomOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';

interface ChapterNavigationProps {
  currentChapter: number;
  prevChapter?: number;
  nextChapter?: number;
  onChapterChange: (chapterNum: number) => void;
}

export default function ChapterNavigation({
  currentChapter,
  prevChapter,
  nextChapter,
  onChapterChange
}: ChapterNavigationProps) {
  const [jumpChapter, setJumpChapter] = useState<number>(currentChapter);
  
  // 同步跳转输入框
  useEffect(() => {
    setJumpChapter(currentChapter);
  }, [currentChapter]);
  
  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 左箭头: 上一章
      if (e.key === 'ArrowLeft' && prevChapter) {
        e.preventDefault();
        onChapterChange(prevChapter);
      }
      // 右箭头: 下一章
      else if (e.key === 'ArrowRight' && nextChapter) {
        e.preventDefault();
        onChapterChange(nextChapter);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [prevChapter, nextChapter, onChapterChange]);
  
  // 跳转到指定章节
  const handleJump = () => {
    if (jumpChapter && jumpChapter !== currentChapter) {
      onChapterChange(jumpChapter);
    }
  };
  
  return (
    <div className="sticky bottom-0 bg-white border-t shadow-lg py-4 px-6 mt-8">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        {/* 上一章 */}
        <Button
          type="default"
          icon={<LeftOutlined />}
          disabled={!prevChapter}
          onClick={() => prevChapter && onChapterChange(prevChapter)}
          size="large"
        >
          上一章
        </Button>
        
        {/* 中间操作区 */}
        <Space size="middle">
          {/* 回到第一章 */}
          <Button
            type="text"
            icon={<VerticalAlignTopOutlined />}
            onClick={() => onChapterChange(1)}
            disabled={currentChapter === 1}
            title="回到第一章"
          />
          
          {/* 跳转到指定章节 */}
          <Space.Compact>
            <InputNumber
              value={jumpChapter}
              onChange={(value) => setJumpChapter(value || currentChapter)}
              onPressEnter={handleJump}
              min={1}
              style={{ width: '100px' }}
              placeholder="章节号"
            />
            <Button type="primary" onClick={handleJump}>
              跳转
            </Button>
          </Space.Compact>
          
          {/* 滚动到顶部 */}
          <Button
            type="text"
            icon={<VerticalAlignBottomOutlined className="rotate-180" />}
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            title="回到顶部"
          />
        </Space>
        
        {/* 下一章 */}
        <Button
          type="primary"
          icon={<RightOutlined />}
          iconPosition="end"
          disabled={!nextChapter}
          onClick={() => nextChapter && onChapterChange(nextChapter)}
          size="large"
        >
          下一章
        </Button>
      </div>
      
      {/* 快捷键提示 */}
      <div className="text-center text-xs text-gray-400 mt-2">
        提示: 使用 ← → 方向键快速翻页
      </div>
    </div>
  );
}

