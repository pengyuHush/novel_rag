'use client';

/**
 * 可视化分析页面
 * 
 * 显示角色关系图和时间线可视化
 */

import React, { useState } from 'react';
import { Tabs, Select, Card, Space, Typography } from 'antd';
import { ProjectOutlined, ClockCircleOutlined } from '@ant-design/icons';
import RelationGraph from '@/components/RelationGraph';
import Timeline from '@/components/Timeline';

const { Title, Paragraph } = Typography;
const { Option } = Select;

export default function GraphPage() {
  const [selectedNovelId, setSelectedNovelId] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<string>('relation');

  // TODO: 从API获取小说列表
  const novels = [
    { id: 1, title: '示例小说1' },
    { id: 2, title: '示例小说2' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <Title level={2}>📊 可视化分析</Title>
          <Paragraph type="secondary">
            探索角色关系网络和故事时间线
          </Paragraph>
        </div>

        {/* 小说选择器 */}
        <Card className="mb-4">
          <Space>
            <span>选择小说：</span>
            <Select
              value={selectedNovelId}
              onChange={setSelectedNovelId}
              style={{ width: 300 }}
            >
              {novels.map((novel) => (
                <Option key={novel.id} value={novel.id}>
                  {novel.title}
                </Option>
              ))}
            </Select>
          </Space>
        </Card>

        {/* 可视化标签页 */}
        <Card>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'relation',
                label: (
                  <span>
                    <ProjectOutlined />
                    角色关系图
                  </span>
                ),
                children: (
                  <div className="p-4">
                    <RelationGraph novelId={selectedNovelId} />
                  </div>
                ),
              },
              {
                key: 'timeline',
                label: (
                  <span>
                    <ClockCircleOutlined />
                    时间线
                  </span>
                ),
                children: (
                  <div className="p-4">
                    <Timeline novelId={selectedNovelId} />
                  </div>
                ),
              },
            ]}
          />
        </Card>
      </div>
    </div>
  );
}

