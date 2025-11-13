'use client';

/**
 * 模型选择器组件
 * 
 * 允许用户选择智谱AI模型
 */

import React, { useState, useEffect } from 'react';
import { Select, Tag, Tooltip, Spin } from 'antd';
import { InfoCircleOutlined, ThunderboltOutlined, DollarOutlined } from '@ant-design/icons';
import { apiClient } from '@/lib/api';
import { ModelType } from '@/types/query';

const { Option } = Select;

interface ModelInfo {
  name: string;
  category: string;
  max_tokens: number;
  price_input: number;
  price_output: number;
  description: string;
  is_default: boolean;
}

interface ModelSelectorProps {
  value?: ModelType;
  onChange?: (model: ModelType) => void;
  size?: 'small' | 'middle' | 'large';
  style?: React.CSSProperties;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  value,
  onChange,
  size = 'middle',
  style,
}) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载模型列表
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<{
        models: ModelInfo[];
        default_model: string;
      }>('/config/models');
      
      setModels(response.models);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取分类颜色
  const getCategoryColor = (category: string): string => {
    const colorMap: { [key: string]: string } = {
      '免费': 'green',
      '高性价比': 'blue',
      '极速': 'orange',
      '高性能': 'red',
      '超长上下文': 'purple',
    };
    return colorMap[category] || 'default';
  };

  // 获取分类图标
  const getCategoryIcon = (category: string) => {
    if (category === '免费' || category === '高性价比') {
      return <DollarOutlined />;
    }
    if (category === '极速') {
      return <ThunderboltOutlined />;
    }
    return null;
  };

  // 渲染选项
  const renderOption = (model: ModelInfo) => (
    <div className="flex items-center justify-between w-full">
      <div className="flex items-center gap-2">
        <span className="font-medium">{model.name}</span>
        <Tag color={getCategoryColor(model.category)} icon={getCategoryIcon(model.category)}>
          {model.category}
        </Tag>
        {model.is_default && (
          <Tag color="cyan">默认</Tag>
        )}
      </div>
      <div className="text-xs text-gray-500">
        {model.price_input === 0 ? (
          <span className="text-green-600 font-medium">免费</span>
        ) : (
          <span>¥{model.price_input}/1K tokens</span>
        )}
      </div>
    </div>
  );

  return (
    <Select
      value={value}
      onChange={onChange}
      size={size}
      style={{ minWidth: 200, ...style }}
      loading={loading}
      placeholder="选择模型"
      optionLabelProp="label"
      suffixIcon={loading ? <Spin size="small" /> : undefined}
    >
      {models.map((model) => (
        <Option
          key={model.name}
          value={model.name}
          label={
            <div className="flex items-center gap-2">
              <span>{model.name}</span>
              {model.is_default && <Tag color="cyan" style={{ margin: 0 }}>默认</Tag>}
            </div>
          }
        >
          <div className="py-1">
            {renderOption(model)}
            <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <InfoCircleOutlined />
              {model.description}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              最大 tokens: {model.max_tokens.toLocaleString()}
            </div>
          </div>
        </Option>
      ))}
    </Select>
  );
};

export default ModelSelector;

