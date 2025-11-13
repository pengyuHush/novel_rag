'use client';

/**
 * Token统计展示组件
 * 
 * 用于在查询结果中展示Token消耗
 */

import React from 'react';
import { Collapse, Descriptions, Tag, Typography } from 'antd';
import { ThunderboltOutlined, DollarOutlined } from '@ant-design/icons';

const { Panel } = Collapse;
const { Text } = Typography;

interface TokenStatsProps {
  totalTokens: number;
  inputTokens?: number;
  outputTokens?: number;
  embeddingTokens?: number;
  cost?: number;
  model?: string;
}

const TokenStats: React.FC<TokenStatsProps> = ({
  totalTokens,
  inputTokens = 0,
  outputTokens = 0,
  embeddingTokens = 0,
  cost = 0,
  model = '未知',
}) => {
  return (
    <Collapse
      ghost
      expandIconPosition="end"
      className="bg-gray-50 rounded-lg mt-4"
    >
      <Panel
        header={
          <div className="flex items-center justify-between pr-4">
            <span className="font-medium">
              <ThunderboltOutlined className="mr-2" />
              Token消耗统计
            </span>
            <div className="flex items-center gap-4">
              <Tag color="blue">{totalTokens} tokens</Tag>
              {cost > 0 && (
                <Tag color="green">
                  <DollarOutlined /> ¥{cost.toFixed(6)}
                </Tag>
              )}
            </div>
          </div>
        }
        key="1"
      >
        <Descriptions size="small" column={2}>
          <Descriptions.Item label="总Token数">
            <Text strong>{totalTokens.toLocaleString()}</Text>
          </Descriptions.Item>
          
          <Descriptions.Item label="使用模型">
            <Tag color="blue">{model}</Tag>
          </Descriptions.Item>
          
          {inputTokens > 0 && (
            <Descriptions.Item label="输入Tokens">
              {inputTokens.toLocaleString()}
            </Descriptions.Item>
          )}
          
          {outputTokens > 0 && (
            <Descriptions.Item label="输出Tokens">
              {outputTokens.toLocaleString()}
            </Descriptions.Item>
          )}
          
          {embeddingTokens > 0 && (
            <Descriptions.Item label="向量化Tokens">
              {embeddingTokens.toLocaleString()}
            </Descriptions.Item>
          )}
          
          {cost > 0 && (
            <Descriptions.Item label="消耗成本">
              <Text type="success" strong>
                ¥{cost.toFixed(6)}
              </Text>
            </Descriptions.Item>
          )}
        </Descriptions>
        
        {/* Token组成饼图（简化文字版） */}
        <div className="mt-4 p-3 bg-white rounded border">
          <Text type="secondary" className="text-xs">Token组成：</Text>
          <div className="mt-2 space-y-1">
            {inputTokens > 0 && (
              <div className="flex justify-between text-sm">
                <span>输入 ({((inputTokens / totalTokens) * 100).toFixed(1)}%)</span>
                <div className="flex-1 mx-2 bg-gray-200 rounded h-4 overflow-hidden">
                  <div
                    className="bg-blue-500 h-full"
                    style={{ width: `${(inputTokens / totalTokens) * 100}%` }}
                  />
                </div>
                <span className="text-gray-600">{inputTokens}</span>
              </div>
            )}
            
            {outputTokens > 0 && (
              <div className="flex justify-between text-sm">
                <span>输出 ({((outputTokens / totalTokens) * 100).toFixed(1)}%)</span>
                <div className="flex-1 mx-2 bg-gray-200 rounded h-4 overflow-hidden">
                  <div
                    className="bg-green-500 h-full"
                    style={{ width: `${(outputTokens / totalTokens) * 100}%` }}
                  />
                </div>
                <span className="text-gray-600">{outputTokens}</span>
              </div>
            )}
            
            {embeddingTokens > 0 && (
              <div className="flex justify-between text-sm">
                <span>向量化 ({((embeddingTokens / totalTokens) * 100).toFixed(1)}%)</span>
                <div className="flex-1 mx-2 bg-gray-200 rounded h-4 overflow-hidden">
                  <div
                    className="bg-purple-500 h-full"
                    style={{ width: `${(embeddingTokens / totalTokens) * 100}%` }}
                  />
                </div>
                <span className="text-gray-600">{embeddingTokens}</span>
              </div>
            )}
          </div>
        </div>
      </Panel>
    </Collapse>
  );
};

export default TokenStats;

