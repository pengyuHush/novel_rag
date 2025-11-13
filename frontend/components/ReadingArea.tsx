'use client';

/**
 * T081: 阅读区域组件 (User Story 2: 在线阅读)
 * 
 * 功能:
 * - 显示章节内容
 * - 优化排版和阅读体验
 * - 支持10万字超长章节流畅显示
 */

import { Typography } from 'antd';
import { useMemo } from 'react';

const { Title, Paragraph } = Typography;

interface ChapterContent {
  chapterNum: number;
  title?: string;
  content: string;
  prevChapter?: number;
  nextChapter?: number;
  totalChapters: number;
}

interface ReadingAreaProps {
  content: ChapterContent;
}

export default function ReadingArea({ content }: ReadingAreaProps) {
  // 将内容分段显示(优化性能)
  const paragraphs = useMemo(() => {
    return content.content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
  }, [content.content]);
  
  return (
    <div className="max-w-4xl mx-auto">
      {/* 章节标题 */}
      <div className="mb-8 border-b pb-4">
        <Title level={2} className="mb-2">
          第{content.chapterNum}章
          {content.title && ` ${content.title}`}
        </Title>
        <div className="text-sm text-gray-500">
          <span>{formatNumber(content.content.length)} 字</span>
          <span className="mx-2">·</span>
          <span>第 {content.chapterNum} / {content.totalChapters} 章</span>
        </div>
      </div>
      
      {/* 章节内容 */}
      <div className="chapter-content">
        {paragraphs.map((para, index) => (
          <Paragraph
            key={index}
            className="text-base leading-relaxed mb-4"
            style={{
              textIndent: '2em',
              fontSize: '18px',
              lineHeight: '2.0',
              color: '#333'
            }}
          >
            {para}
          </Paragraph>
        ))}
      </div>
      
      {/* 章节结束标记 */}
      <div className="text-center text-gray-400 mt-12 mb-8 text-sm">
        — 本章完 —
      </div>
    </div>
  );
}

// 格式化数字显示
function formatNumber(num: number): string {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`;
  }
  return num.toString();
}

