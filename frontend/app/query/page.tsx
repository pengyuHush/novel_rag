/**
 * 智能问答页面
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, Select, Alert, Spin, Empty, Button, Space } from 'antd';
import { ArrowLeftOutlined, ThunderboltOutlined } from '@ant-design/icons';
import Link from 'next/link';
import QueryInput from '@/components/QueryInput';
import StageProgress from '@/components/StageProgress';
import StreamingTextBox from '@/components/StreamingTextBox';
import CitationList from '@/components/CitationList';
import ContradictionCard from '@/components/ContradictionCard';
import { useQueryStream } from '@/hooks/useQueryStream';
import { apiClient } from '@/lib/api';
import { NovelListItem, IndexStatus } from '@/types/novel';
import { ModelType, Contradiction } from '@/types/query';

const { Option } = Select;

export default function QueryPage() {
  const searchParams = useSearchParams();
  const initialNovelId = searchParams.get('novel_id');

  const [novels, setNovels] = useState<NovelListItem[]>([]);
  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(
    initialNovelId ? parseInt(initialNovelId) : null
  );
  const [loading, setLoading] = useState(true);

  const {
    answer,
    stage,
    progress,
    citations,
    contradictions,
    isLoading,
    error,
    sendQuery,
  } = useQueryStream();

  useEffect(() => {
    loadNovels();
  }, []);

  const loadNovels = async () => {
    try {
      const data = await apiClient.listNovels();
      // 只显示已索引完成的小说
      const completedNovels = data.filter(
        (n) => n.index_status === IndexStatus.COMPLETED
      );
      setNovels(completedNovels);

      // 如果没有选中的小说，自动选择第一个
      if (!selectedNovelId && completedNovels.length > 0) {
        setSelectedNovelId(completedNovels[0].id);
      }
    } catch (error) {
      console.error('加载失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = (query: string, model: ModelType) => {
    if (selectedNovelId) {
      sendQuery(selectedNovelId, query, model);
    }
  };

  const selectedNovel = novels.find((n) => n.id === selectedNovelId);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (novels.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Empty
          description="还没有已索引完成的小说"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Link href="/novels">
            <Button type="primary" icon={<ArrowLeftOutlined />}>
              去上传小说
            </Button>
          </Link>
        </Empty>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 头部 */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold">💬 智能问答</h1>
          <Link href="/novels">
            <Button icon={<ArrowLeftOutlined />}>返回小说列表</Button>
          </Link>
        </div>

        <Card>
          <div className="flex items-center gap-3">
            <span className="text-gray-600">选择小说:</span>
            <Select
              value={selectedNovelId}
              onChange={setSelectedNovelId}
              style={{ width: 300 }}
              suffixIcon={<ThunderboltOutlined />}
            >
              {novels.map((novel) => (
                <Option key={novel.id} value={novel.id}>
                  📖 {novel.title}
                  {novel.author && ` - ${novel.author}`}
                </Option>
              ))}
            </Select>
            {selectedNovel && (
              <div className="text-sm text-gray-500">
                {selectedNovel.total_chapters} 章 ·{' '}
                {(selectedNovel.total_chars / 10000).toFixed(1)} 万字
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* 错误提示 */}
      {error && (
        <Alert
          message="查询出错"
          description={error}
          type="error"
          closable
          className="mb-4"
        />
      )}

      {/* 查询输入 */}
      <div className="mb-6">
        <QueryInput
          onSubmit={handleQuery}
          loading={isLoading}
          disabled={!selectedNovelId}
        />
      </div>

      {/* 进度展示 */}
      {isLoading && stage && (
        <div className="mb-6">
          <Card>
            <StageProgress stage={stage} progress={progress} />
          </Card>
        </div>
      )}

      {/* 回答和引用 */}
      {(answer || isLoading) && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <StreamingTextBox
                content={answer}
                loading={isLoading}
                title="💡 AI 回答"
              />
              
              {/* Self-RAG矛盾检测结果 */}
              {contradictions && contradictions.length > 0 && !isLoading && (
                <ContradictionCard contradictions={contradictions} />
              )}
            </div>
            <div>
              <CitationList citations={citations} />
            </div>
          </div>
        </>
      )}

      {/* 使用提示 */}
      {!answer && !isLoading && (
        <Card className="bg-blue-50 border-blue-200">
          <div className="space-y-3">
            <div className="font-medium text-lg">💡 使用提示</div>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• 选择一本已索引完成的小说</li>
              <li>• 输入您的问题，支持人物、情节、关系等多种查询</li>
              <li>• 使用 Ctrl+Enter 快速发送</li>
              <li>• 查看引用来源，了解答案依据</li>
            </ul>
            
            <div className="mt-4 p-3 bg-white rounded border border-blue-200">
              <div className="text-xs text-gray-600 mb-2">示例问题:</div>
              <div className="flex flex-wrap gap-2">
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">主角叫什么名字？</code>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">故事发生在哪里？</code>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">主角的武功有哪些？</code>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

