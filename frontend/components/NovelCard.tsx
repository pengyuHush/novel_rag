/**
 * 小说卡片组件
 */

'use client';

import React from 'react';
import { Card, Tag, Progress, Button, Popconfirm, Space, Tooltip } from 'antd';
import { DeleteOutlined, EyeOutlined, FileTextOutlined, CheckCircleOutlined, ClockCircleOutlined, SyncOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { NovelListItem, IndexStatus } from '@/types/novel';
import Link from 'next/link';

interface NovelCardProps {
  novel: NovelListItem;
  onDelete: (id: number) => void;
}

const NovelCard: React.FC<NovelCardProps> = ({ novel, onDelete }) => {
  const getStatusTag = (status: IndexStatus) => {
    switch (status) {
      case IndexStatus.COMPLETED:
        return <Tag icon={<CheckCircleOutlined />} color="success">索引完成</Tag>;
      case IndexStatus.PROCESSING:
        return <Tag icon={<SyncOutlined spin />} color="processing">索引中</Tag>;
      case IndexStatus.PENDING:
        return <Tag icon={<ClockCircleOutlined />} color="default">等待索引</Tag>;
      case IndexStatus.FAILED:
        return <Tag icon={<CloseCircleOutlined />} color="error">索引失败</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`;
    }
    return num.toString();
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN');
  };

  return (
    <Card
      hoverable
      className="novel-card"
      actions={[
        <Link key="view" href={`/novels/${novel.id}`}>
          <Button type="text" icon={<EyeOutlined />}>
            查看
          </Button>
        </Link>,
        <Link key="query" href={`/query?novel_id=${novel.id}`}>
          <Button type="text" icon={<FileTextOutlined />}>
            问答
          </Button>
        </Link>,
        <Popconfirm
          key="delete"
          title="确定要删除这本小说吗？"
          description="此操作将删除所有相关数据，无法恢复。"
          onConfirm={() => onDelete(novel.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="text" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>,
      ]}
    >
      <Card.Meta
        title={
          <Space>
            <span className="text-lg font-bold">{novel.title}</span>
            {getStatusTag(novel.index_status)}
          </Space>
        }
        description={
          <div className="space-y-2">
            {novel.author && (
              <div className="text-sm text-gray-600">
                作者：{novel.author}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <Tooltip title="总字数">
                <div>📖 {formatNumber(novel.total_chars)} 字</div>
              </Tooltip>
              <Tooltip title="章节数">
                <div>📚 {novel.total_chapters} 章</div>
              </Tooltip>
              <Tooltip title="文件格式">
                <div>📄 {novel.file_format.toUpperCase()}</div>
              </Tooltip>
              <Tooltip title="上传日期">
                <div>📅 {formatDate(novel.upload_date)}</div>
              </Tooltip>
            </div>

            {novel.index_status === IndexStatus.PROCESSING && (
              <div className="mt-3">
                <div className="text-xs text-gray-500 mb-1">
                  索引进度: {(novel.index_progress * 100).toFixed(1)}%
                </div>
                <Progress
                  percent={novel.index_progress * 100}
                  status="active"
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
              </div>
            )}
          </div>
        }
      />
    </Card>
  );
};

export default NovelCard;

