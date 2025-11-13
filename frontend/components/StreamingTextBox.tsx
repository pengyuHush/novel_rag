/**
 * 流式文本展示框
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, Tooltip, message } from 'antd';
import { CopyOutlined, CheckOutlined, DownOutlined, UpOutlined } from '@ant-design/icons';

interface StreamingTextBoxProps {
  content: string;
  loading?: boolean;
  title?: string;
}

const StreamingTextBox: React.FC<StreamingTextBoxProps> = ({
  content,
  loading,
  title = '回答',
}) => {
  const contentRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (autoScroll && contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [content, autoScroll]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      message.success('已复制到剪贴板');
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      message.error('复制失败');
    }
  };

  const handleScroll = () => {
    if (contentRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setAutoScroll(isAtBottom);
    }
  };

  const scrollToBottom = () => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
      setAutoScroll(true);
    }
  };

  return (
    <Card
      title={title}
      className="streaming-text-box"
      extra={
        <Space>
          <Tooltip title={autoScroll ? '自动滚动已开启' : '自动滚动已关闭'}>
            <Button
              type="text"
              size="small"
              icon={autoScroll ? <DownOutlined /> : <UpOutlined />}
              onClick={() => setAutoScroll(!autoScroll)}
            />
          </Tooltip>
          <Tooltip title="复制">
            <Button
              type="text"
              size="small"
              icon={copied ? <CheckOutlined /> : <CopyOutlined />}
              onClick={handleCopy}
              disabled={!content}
            />
          </Tooltip>
        </Space>
      }
    >
      <div
        ref={contentRef}
        onScroll={handleScroll}
        className="streaming-content max-h-96 overflow-y-auto p-4 bg-gray-50 rounded"
        style={{ minHeight: '200px' }}
      >
        {content ? (
          <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
            {content}
            {loading && <span className="animate-pulse">▊</span>}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-12">
            {loading ? '正在生成回答...' : '等待查询'}
          </div>
        )}
      </div>

      {!autoScroll && content && (
        <div className="text-center mt-2">
          <Button
            type="link"
            size="small"
            icon={<DownOutlined />}
            onClick={scrollToBottom}
          >
            滚动到底部
          </Button>
        </div>
      )}
    </Card>
  );
};

export default StreamingTextBox;

