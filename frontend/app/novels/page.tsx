/**
 * 小说列表页面
 */

'use client';

import React, { useEffect, useState } from 'react';
import { Button, Empty, Spin, message, Space, Input, Select } from 'antd';
import { PlusOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import NovelCard from '@/components/NovelCard';
import UploadModal from '@/components/UploadModal';
import { apiClient } from '@/lib/api';
import { NovelListItem, IndexStatus } from '@/types/novel';

const { Search } = Input;
const { Option } = Select;

export default function NovelsPage() {
  const [novels, setNovels] = useState<NovelListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<IndexStatus | 'all'>('all');
  const [searchText, setSearchText] = useState('');

  const loadNovels = async () => {
    try {
      setLoading(true);
      const data = await apiClient.listNovels();
      setNovels(data);
    } catch (error: any) {
      message.error(error.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNovels();
  }, []);

  // 单独的定时器effect，只在有处理中的小说时刷新
  useEffect(() => {
    const hasProcessing = novels.some(
      (n) => n.index_status === IndexStatus.PROCESSING
    );
    
    if (!hasProcessing) {
      return; // 没有处理中的小说，不需要定时刷新
    }

    const interval = setInterval(() => {
      loadNovels();
    }, 5000); // 每5秒刷新一次

    return () => clearInterval(interval);
  }, [novels]);

  const handleDelete = async (id: number) => {
    try {
      await apiClient.deleteNovel(id);
      message.success('删除成功');
      loadNovels();
    } catch (error: any) {
      message.error(error.message || '删除失败');
    }
  };

  const filteredNovels = novels
    .filter((novel) => {
      if (statusFilter !== 'all' && novel.index_status !== statusFilter) {
        return false;
      }
      if (searchText && !novel.title.toLowerCase().includes(searchText.toLowerCase())) {
        return false;
      }
      return true;
    });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold">我的小说</h1>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadNovels}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setUploadModalOpen(true)}
            >
              上传小说
            </Button>
          </Space>
        </div>

        <Space className="w-full" size="middle">
          <Search
            placeholder="搜索小说标题"
            allowClear
            prefix={<SearchOutlined />}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 300 }}
          />
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 150 }}
          >
            <Option value="all">全部状态</Option>
            <Option value={IndexStatus.COMPLETED}>索引完成</Option>
            <Option value={IndexStatus.PROCESSING}>索引中</Option>
            <Option value={IndexStatus.PENDING}>等待索引</Option>
            <Option value={IndexStatus.FAILED}>索引失败</Option>
          </Select>
        </Space>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Spin size="large" tip="加载中..." />
        </div>
      ) : filteredNovels.length === 0 ? (
        <Empty
          description={
            novels.length === 0
              ? "还没有上传小说"
              : "没有符合条件的小说"
          }
        >
          {novels.length === 0 && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setUploadModalOpen(true)}
            >
              立即上传
            </Button>
          )}
        </Empty>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNovels.map((novel) => (
            <NovelCard
              key={novel.id}
              novel={novel}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      <UploadModal
        open={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onSuccess={loadNovels}
      />
    </div>
  );
}

