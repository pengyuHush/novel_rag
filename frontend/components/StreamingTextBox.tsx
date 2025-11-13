/**
 * 流式文本展示框
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, Tooltip, message } from 'antd';
import { CopyOutlined, CheckOutlined, DownOutlined, UpOutlined, LikeOutlined, DislikeOutlined, LikeFilled, DislikeFilled } from '@ant-design/icons';

interface StreamingTextBoxProps {
  content: string;
  loading?: boolean;
  title?: string;
  queryId?: number;  // 查询ID，用于提交反馈
  onFeedback?: (queryId: number, isPositive: boolean) => void;  // 反馈回调
}

const StreamingTextBox: React.FC<StreamingTextBoxProps> = ({
  content,
  loading,
  title = '回答',
  queryId,
  onFeedback,
}) => {
  const contentRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);

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

  const handleFeedback = (isPositive: boolean) => {
    if (!queryId || !onFeedback) return;
    
    const newFeedback = isPositive ? 'positive' : 'negative';
    
    // 如果点击相同的反馈，则取消
    if (feedback === newFeedback) {
      setFeedback(null);
      message.info('已取消反馈');
      return;
    }
    
    setFeedback(newFeedback);
    onFeedback(queryId, isPositive);
    message.success(isPositive ? '感谢您的肯定 👍' : '感谢您的反馈 👎');
  };

  return (
    <Card
      title={title}
      className="streaming-text-box"
      extra={
        <Space>
          {/* 反馈按钮 */}
          {queryId && !loading && content && (
            <>
              <Tooltip title="好评">
                <Button
                  type="text"
                  size="small"
                  icon={feedback === 'positive' ? <LikeFilled /> : <LikeOutlined />}
                  onClick={() => handleFeedback(true)}
                  style={{ color: feedback === 'positive' ? '#52c41a' : undefined }}
                />
              </Tooltip>
              <Tooltip title="差评">
                <Button
                  type="text"
                  size="small"
                  icon={feedback === 'negative' ? <DislikeFilled /> : <DislikeOutlined />}
                  onClick={() => handleFeedback(false)}
                  style={{ color: feedback === 'negative' ? '#ff4d4f' : undefined }}
                />
              </Tooltip>
            </>
          )}
          
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

