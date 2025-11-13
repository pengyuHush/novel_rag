'use client';

/**
 * 模型配置组件
 * 
 * 允许用户设置默认模型
 */

import React, { useState, useEffect } from 'react';
import { Card, Space, Button, message, Typography, Divider } from 'antd';
import { SettingOutlined, SaveOutlined } from '@ant-design/icons';
import ModelSelector from './ModelSelector';
import { ModelType } from '@/types/query';
import { saveDefaultModel, getDefaultModel } from '@/store/userPreferences';

const { Text, Paragraph } = Typography;

const ModelConfig: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<ModelType>(ModelType.GLM_4_5_AIR);
  const [hasChanges, setHasChanges] = useState(false);

  // 加载当前设置
  useEffect(() => {
    const current = getDefaultModel();
    setSelectedModel(current);
  }, []);

  // 处理模型变化
  const handleModelChange = (model: ModelType) => {
    setSelectedModel(model);
    setHasChanges(true);
  };

  // 保存设置
  const handleSave = () => {
    saveDefaultModel(selectedModel);
    setHasChanges(false);
    message.success('默认模型已保存');
  };

  return (
    <Card
      title={
        <Space>
          <SettingOutlined />
          <span>默认模型设置</span>
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 说明 */}
        <div>
          <Paragraph>
            选择您在查询时默认使用的智谱AI模型。您可以根据查询复杂度和成本需求选择不同的模型。
          </Paragraph>
          <Paragraph type="secondary">
            <Text strong>推荐：</Text>
            <ul className="mt-2 ml-4">
              <li><Text code>GLM-4.5-Flash</Text> - 免费模型，适合日常查询</li>
              <li><Text code>GLM-4.5-Air</Text> - 高性价比，推荐使用</li>
              <li><Text code>GLM-4-Plus</Text> - 高性能，适合复杂分析</li>
            </ul>
          </Paragraph>
        </div>

        <Divider />

        {/* 模型选择 */}
        <div>
          <Text strong>默认模型:</Text>
          <div className="mt-2">
            <ModelSelector
              value={selectedModel}
              onChange={handleModelChange}
              size="large"
              style={{ width: '100%' }}
            />
          </div>
        </div>

        {/* 保存按钮 */}
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          disabled={!hasChanges}
          size="large"
        >
          保存设置
        </Button>

        {/* 提示 */}
        {hasChanges && (
          <Text type="warning">
            您有未保存的更改，请点击"保存设置"按钮。
          </Text>
        )}
      </Space>
    </Card>
  );
};

export default ModelConfig;

