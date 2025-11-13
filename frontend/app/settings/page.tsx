'use client';

/**
 * 设置页面
 * 
 * 提供API Key配置、模型管理等设置功能
 */

import React, { useState, useEffect } from 'react';
import { Tabs, Typography, Space, Row, Col, Card, Spin } from 'antd';
import { SettingOutlined, KeyOutlined, ThunderboltOutlined, InfoCircleOutlined, BarChartOutlined } from '@ant-design/icons';
import ApiKeyConfig from '@/components/ApiKeyConfig';
import ModelConfig from '@/components/ModelConfig';
import { TokenStatCard, CostStatCard, QueryCountStatCard, IndexCountStatCard } from '@/components/StatCard';
import TokenChart from '@/components/TokenChart';
import { apiClient } from '@/lib/api';

const { Title, Paragraph } = Typography;

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<string>('api');
  const [statsLoading, setStatsLoading] = useState(false);
  const [tokenStats, setTokenStats] = useState<any>(null);

  // 加载统计数据
  useEffect(() => {
    if (activeTab === 'stats') {
      loadStats();
    }
  }, [activeTab]);

  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const [stats, summary] = await Promise.all([
        apiClient.get('/stats/tokens', { period: 'all' }),
        apiClient.get('/stats/tokens/summary'),
      ]);
      setTokenStats({ ...stats, summary });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <Space>
            <SettingOutlined style={{ fontSize: 32, color: '#1890ff' }} />
            <Title level={2} style={{ margin: 0 }}>系统设置</Title>
          </Space>
          <Paragraph type="secondary" className="mt-2">
            配置API Key、选择默认模型，优化您的使用体验
          </Paragraph>
        </div>

        {/* 设置标签页 */}
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'api',
              label: (
                <span>
                  <KeyOutlined />
                  API配置
                </span>
              ),
              children: (
                <div className="p-4">
                  <ApiKeyConfig />
                </div>
              ),
            },
            {
              key: 'model',
              label: (
                <span>
                  <ThunderboltOutlined />
                  模型管理
                </span>
              ),
              children: (
                <div className="p-4">
                  <ModelConfig />
                </div>
              ),
            },
            {
              key: 'stats',
              label: (
                <span>
                  <BarChartOutlined />
                  Token统计
                </span>
              ),
              children: (
                <div className="p-4">
                  {statsLoading ? (
                    <div className="text-center py-12">
                      <Spin size="large" />
                    </div>
                  ) : tokenStats ? (
                    <Space direction="vertical" size="large" style={{ width: '100%' }}>
                      {/* 统计卡片 */}
                      <Row gutter={[16, 16]}>
                        <Col xs={24} sm={12} lg={6}>
                          <TokenStatCard
                            value={tokenStats.summary?.all_time?.total_tokens || 0}
                          />
                        </Col>
                        <Col xs={24} sm={12} lg={6}>
                          <CostStatCard
                            value={tokenStats.summary?.all_time?.total_cost || 0}
                          />
                        </Col>
                        <Col xs={24} sm={12} lg={6}>
                          <QueryCountStatCard
                            value={tokenStats.by_operation?.query?.operation_count || 0}
                          />
                        </Col>
                        <Col xs={24} sm={12} lg={6}>
                          <IndexCountStatCard
                            value={tokenStats.by_operation?.index?.operation_count || 0}
                          />
                        </Col>
                      </Row>

                      {/* 趋势图 */}
                      <TokenChart />

                      {/* 按模型分类统计 */}
                      <Card title="按模型分类统计" className="shadow-sm">
                        <div className="space-y-3">
                          {Object.entries(tokenStats.by_model || {}).map(
                            ([model, data]: [string, any]) => (
                              <div
                                key={model}
                                className="flex justify-between items-center p-3 bg-gray-50 rounded"
                              >
                                <div>
                                  <div className="font-medium">{model}</div>
                                  <div className="text-sm text-gray-500">
                                    使用 {data.usage_count} 次
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="text-lg font-bold text-blue-600">
                                    {data.total_tokens.toLocaleString()} tokens
                                  </div>
                                  <div className="text-sm text-green-600">
                                    ¥{data.total_cost.toFixed(4)}
                                  </div>
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      </Card>

                      {/* 按操作类型统计 */}
                      <Card title="按操作类型统计" className="shadow-sm">
                        <Row gutter={16}>
                          {Object.entries(tokenStats.by_operation || {}).map(
                            ([type, data]: [string, any]) => (
                              <Col key={type} xs={24} sm={12}>
                                <div className="p-4 bg-gray-50 rounded">
                                  <div className="text-gray-600 mb-2">
                                    {type === 'index' ? '索引操作' : '查询操作'}
                                  </div>
                                  <div className="text-2xl font-bold text-blue-600 mb-1">
                                    {data.total_tokens.toLocaleString()} tokens
                                  </div>
                                  <div className="text-sm text-green-600">
                                    ¥{data.total_cost.toFixed(4)} / {data.operation_count} 次
                                  </div>
                                </div>
                              </Col>
                            )
                          )}
                        </Row>
                      </Card>
                    </Space>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      暂无统计数据
                    </div>
                  )}
                </div>
              ),
            },
            {
              key: 'about',
              label: (
                <span>
                  <InfoCircleOutlined />
                  关于
                </span>
              ),
              children: (
                <div className="p-4">
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <Title level={3}>关于本系统</Title>
                    <Paragraph>
                      <Text strong>网络小说智能问答系统</Text> v0.1.0
                    </Paragraph>
                    <Paragraph>
                      基于RAG（Retrieval-Augmented Generation）架构的网络小说智能问答系统，
                      支持小说上传、智能问答、知识图谱、可视化分析等功能。
                    </Paragraph>
                    
                    <Title level={4} className="mt-6">核心功能</Title>
                    <ul className="list-disc ml-6 space-y-2">
                      <li>📚 小说管理：支持TXT/EPUB格式上传</li>
                      <li>🤖 智能问答：基于GraphRAG和Self-RAG</li>
                      <li>📖 在线阅读：分章节浏览</li>
                      <li>🕸️ 知识图谱：角色关系自动提取</li>
                      <li>📊 可视化：关系图和时间线</li>
                      <li>⚙️ 模型管理：多模型切换</li>
                    </ul>
                    
                    <Title level={4} className="mt-6">技术栈</Title>
                    <Paragraph>
                      <Text strong>前端：</Text> Next.js 14 + React + TypeScript + Ant Design<br />
                      <Text strong>后端：</Text> FastAPI + Python 3.12<br />
                      <Text strong>AI：</Text> 智谱AI (GLM-4系列 + Embedding-3)<br />
                      <Text strong>数据库：</Text> SQLite + ChromaDB + NetworkX
                    </Paragraph>
                    
                    <Paragraph className="mt-6 text-gray-500">
                      © 2025 网络小说智能问答系统. All rights reserved.
                    </Paragraph>
                  </div>
                </div>
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}

