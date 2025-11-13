/**
 * 查询历史页面
 */

'use client';

import React, { useEffect, useState } from 'react';
import { Card, Select, Table, Tag, Space, Button, Pagination, Empty, Badge, Tooltip } from 'antd';
import { ArrowLeftOutlined, LikeOutlined, DislikeOutlined, ThunderboltOutlined, ClockCircleOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { NovelListItem } from '@/types/novel';
import type { ColumnsType } from 'antd/es/table';

const { Option } = Select;

interface QueryHistoryItem {
  id: number;
  novel_id: number;
  query: string;
  answer: string;
  model: string;
  total_tokens: number;
  confidence: string;
  created_at: string;
  feedback: 'positive' | 'negative' | null;
}

export default function HistoryPage() {
  const [novels, setNovels] = useState<NovelListItem[]>([]);
  const [selectedNovelId, setSelectedNovelId] = useState<number | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    loadNovels();
  }, []);

  useEffect(() => {
    loadHistory();
  }, [selectedNovelId, page, pageSize]);

  const loadNovels = async () => {
    try {
      const data = await apiClient.listNovels();
      setNovels(data);
    } catch (error) {
      console.error('加载小说列表失败:', error);
    }
  };

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getQueryHistory(
        selectedNovelId || undefined,
        page,
        pageSize
      );
      setHistory(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('加载历史失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return 'success';
      case 'medium':
        return 'warning';
      case 'low':
        return 'error';
      default:
        return 'default';
    }
  };

  const getConfidenceText = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return '未知';
    }
  };

  const columns: ColumnsType<QueryHistoryItem> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => (
        <div className="text-sm text-gray-600">
          <ClockCircleOutlined className="mr-1" />
          {new Date(text).toLocaleString('zh-CN')}
        </div>
      ),
    },
    {
      title: '问题',
      dataIndex: 'query',
      key: 'query',
      width: 300,
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <div className="font-medium text-gray-800">{text}</div>
        </Tooltip>
      ),
    },
    {
      title: '回答（摘要）',
      dataIndex: 'answer',
      key: 'answer',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <div className="text-sm text-gray-600">{text}</div>
        </Tooltip>
      ),
    },
    {
      title: '模型',
      dataIndex: 'model',
      key: 'model',
      width: 150,
      render: (text: string) => (
        <Tag icon={<ThunderboltOutlined />} color="blue">
          {text}
        </Tag>
      ),
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      align: 'center',
      render: (text: string) => (
        <Badge
          status={getConfidenceColor(text) as any}
          text={getConfidenceText(text)}
        />
      ),
    },
    {
      title: 'Token消耗',
      dataIndex: 'total_tokens',
      key: 'total_tokens',
      width: 120,
      align: 'right',
      render: (text: number) => (
        <div className="text-sm text-gray-600">
          {text.toLocaleString()}
        </div>
      ),
    },
    {
      title: '反馈',
      dataIndex: 'feedback',
      key: 'feedback',
      width: 80,
      align: 'center',
      render: (feedback: 'positive' | 'negative' | null) => {
        if (feedback === 'positive') {
          return <LikeOutlined style={{ color: '#52c41a', fontSize: '18px' }} />;
        } else if (feedback === 'negative') {
          return <DislikeOutlined style={{ color: '#ff4d4f', fontSize: '18px' }} />;
        }
        return <span className="text-gray-400">-</span>;
      },
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 头部 */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold">📜 查询历史</h1>
          <Link href="/query">
            <Button icon={<ArrowLeftOutlined />}>返回查询</Button>
          </Link>
        </div>

        {/* 筛选栏 */}
        <Card>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">筛选小说:</span>
            <Select
              value={selectedNovelId}
              onChange={(value) => {
                setSelectedNovelId(value);
                setPage(1);
              }}
              style={{ width: 300 }}
              placeholder="全部小说"
              allowClear
            >
              {novels.map((novel) => (
                <Option key={novel.id} value={novel.id}>
                  📖 {novel.title}
                  {novel.author && ` - ${novel.author}`}
                </Option>
              ))}
            </Select>
            <div className="text-sm text-gray-500">
              共 {total} 条记录
            </div>
          </div>
        </Card>
      </div>

      {/* 历史列表 */}
      {history.length === 0 && !loading ? (
        <Card>
          <Empty
            description="还没有查询历史"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Link href="/query">
              <Button type="primary">开始查询</Button>
            </Link>
          </Empty>
        </Card>
      ) : (
        <>
          <Card>
            <Table
              columns={columns}
              dataSource={history}
              rowKey="id"
              loading={loading}
              pagination={false}
              scroll={{ x: 1200 }}
            />
          </Card>

          {/* 分页 */}
          {total > 0 && (
            <div className="mt-6 flex justify-center">
              <Pagination
                current={page}
                pageSize={pageSize}
                total={total}
                onChange={(newPage, newPageSize) => {
                  setPage(newPage);
                  if (newPageSize !== pageSize) {
                    setPageSize(newPageSize);
                    setPage(1);
                  }
                }}
                showSizeChanger
                showTotal={(total) => `共 ${total} 条`}
                pageSizeOptions={['10', '20', '50', '100']}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}

