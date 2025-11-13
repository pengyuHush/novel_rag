/**
 * 矛盾卡片组件
 * 
 * 展示Self-RAG检测到的矛盾信息
 */

import React from 'react';
import { Card, Tag, Typography, Collapse, Space } from 'antd';
import { ExclamationCircleOutlined, WarningOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

export interface Contradiction {
  type: string;
  earlyDescription: string;
  earlyChapter: number;
  lateDescription: string;
  lateChapter: number;
  analysis: string;
  confidence: 'high' | 'medium' | 'low';
}

interface ContradictionCardProps {
  contradictions: Contradiction[];
  showTitle?: boolean;
}

const ContradictionCard: React.FC<ContradictionCardProps> = ({
  contradictions,
  showTitle = true
}) => {
  if (!contradictions || contradictions.length === 0) {
    return null;
  }

  // 根据置信度获取图标和颜色
  const getConfidenceIcon = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'medium':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'low':
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
      default:
        return <InfoCircleOutlined />;
    }
  };

  const getConfidenceTag = (confidence: string) => {
    const tagColors: Record<string, string> = {
      high: 'red',
      medium: 'orange',
      low: 'blue'
    };

    const tagLabels: Record<string, string> = {
      high: '高置信度',
      medium: '中置信度',
      low: '低置信度'
    };

    return (
      <Tag color={tagColors[confidence] || 'default'}>
        {tagLabels[confidence] || '未知'}
      </Tag>
    );
  };

  const getTypeTag = (type: string) => {
    const typeColors: Record<string, string> = {
      '时间线矛盾': 'magenta',
      '角色设定矛盾': 'purple',
      '情节不一致': 'cyan',
      '证据不足': 'geekblue'
    };

    return (
      <Tag color={typeColors[type] || 'default'}>
        {type}
      </Tag>
    );
  };

  return (
    <Card
      style={{ marginTop: 16 }}
      bordered={false}
      bodyStyle={{ padding: '16px 24px' }}
    >
      {showTitle && (
        <Title level={5} style={{ marginBottom: 16 }}>
          <WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />
          矛盾检测结果 ({contradictions.length})
        </Title>
      )}

      <Collapse
        bordered={false}
        defaultActiveKey={contradictions.length > 0 ? ['0'] : []}
        expandIconPosition="end"
      >
        {contradictions.map((contradiction, index) => (
          <Panel
            key={index.toString()}
            header={
              <Space>
                {getConfidenceIcon(contradiction.confidence)}
                {getTypeTag(contradiction.type)}
                <Text strong>{contradiction.analysis}</Text>
              </Space>
            }
            extra={getConfidenceTag(contradiction.confidence)}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {/* 早期描述 */}
              <div>
                <Text type="secondary" strong>
                  第 {contradiction.earlyChapter} 章：
                </Text>
                <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                  {contradiction.earlyDescription}
                </Paragraph>
              </div>

              {/* 分隔线 */}
              {contradiction.earlyChapter !== contradiction.lateChapter && (
                <>
                  <div style={{ 
                    borderTop: '1px dashed #d9d9d9', 
                    margin: '8px 0' 
                  }} />

                  {/* 后期描述 */}
                  <div>
                    <Text type="secondary" strong>
                      第 {contradiction.lateChapter} 章：
                    </Text>
                    <Paragraph style={{ marginTop: 8, marginBottom: 0 }}>
                      {contradiction.lateDescription}
                    </Paragraph>
                  </div>
                </>
              )}

              {/* 分析说明 */}
              <div style={{ 
                background: '#fafafa', 
                padding: 12, 
                borderRadius: 4,
                marginTop: 8 
              }}>
                <Text type="secondary">
                  <InfoCircleOutlined style={{ marginRight: 8 }} />
                  {contradiction.analysis}
                </Text>
              </div>
            </Space>
          </Panel>
        ))}
      </Collapse>

      {/* 底部提示 */}
      <div style={{ 
        marginTop: 16, 
        padding: 12, 
        background: '#fff7e6', 
        borderRadius: 4,
        borderLeft: '4px solid #faad14'
      }}>
        <Text type="warning">
          <InfoCircleOutlined style={{ marginRight: 8 }} />
          Self-RAG检测到以上矛盾，建议结合原文仔细判断。高置信度矛盾可能影响答案准确性。
        </Text>
      </div>
    </Card>
  );
};

export default ContradictionCard;

