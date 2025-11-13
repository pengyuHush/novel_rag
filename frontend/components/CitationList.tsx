/**
 * 引用列表组件
 */

'use client';

import React from 'react';
import { Card, List, Tag, Empty } from 'antd';
import { BookOutlined } from '@ant-design/icons';
import { Citation } from '@/types/query';

interface CitationListProps {
  citations: Citation[];
}

const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  if (citations.length === 0) {
    return (
      <Card title="📚 引用来源" className="citation-list">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无引用"
        />
      </Card>
    );
  }

  return (
    <Card title="📚 引用来源" className="citation-list">
      <List
        dataSource={citations}
        renderItem={(citation) => (
          <List.Item>
            <div className="w-full">
              <div className="flex items-center gap-2 mb-2">
                <Tag color="blue" icon={<BookOutlined />}>
                  第 {citation.chapter_num} 章
                </Tag>
                {citation.chapter_title && (
                  <span className="text-sm font-medium text-gray-700">
                    {citation.chapter_title}
                  </span>
                )}
                {citation.score !== undefined && (
                  <Tag color="green">
                    相关度: {(citation.score * 100).toFixed(1)}%
                  </Tag>
                )}
              </div>
              <div className="text-sm text-gray-600 pl-4 border-l-2 border-gray-200">
                {citation.text}
              </div>
            </div>
          </List.Item>
        )}
      />
    </Card>
  );
};

export default CitationList;

