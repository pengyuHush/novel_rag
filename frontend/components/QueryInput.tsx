/**
 * 查询输入组件
 */

'use client';

import React, { useState } from 'react';
import { Input, Button, Select, Space } from 'antd';
import { SendOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { ModelType } from '@/types/query';

const { TextArea } = Input;
const { Option } = Select;

interface QueryInputProps {
  onSubmit: (query: string, model: ModelType) => void;
  loading?: boolean;
  disabled?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, loading, disabled }) => {
  const [query, setQuery] = useState('');
  const [model, setModel] = useState<ModelType>(ModelType.GLM_4_5_FLASH);

  const handleSubmit = () => {
    if (query.trim()) {
      onSubmit(query.trim(), model);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  const quickQuestions = [
    '主角叫什么名字？',
    '故事发生在哪里？',
    '主角的性格特点是什么？',
    '主要配角有哪些？',
  ];

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <Space direction="vertical" size="middle" className="w-full">
        <div className="flex items-start gap-3">
          <TextArea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题... (Ctrl+Enter 发送)"
            autoSize={{ minRows: 3, maxRows: 6 }}
            disabled={disabled}
            className="flex-1"
          />
        </div>

        <div className="flex justify-between items-center">
          <Space>
            <Select
              value={model}
              onChange={setModel}
              disabled={disabled}
              style={{ width: 200 }}
              suffixIcon={<ThunderboltOutlined />}
              placeholder="选择模型"
            >
              <Option value={ModelType.GLM_4_5_FLASH}>
                GLM-4.5-Flash 🆓 (免费推荐)
              </Option>
              <Option value={ModelType.GLM_4_5_AIR}>
                GLM-4.5-Air ⚡ (高性价比)
              </Option>
              <Option value={ModelType.GLM_4_5_AIRX}>
                GLM-4.5-AirX 🚀 (极速性价比)
              </Option>
              <Option value={ModelType.GLM_4_5_X}>
                GLM-4.5-X (超强极速)
              </Option>
              <Option value={ModelType.GLM_4_5}>
                GLM-4.5 (超强性能)
              </Option>
              <Option value={ModelType.GLM_4_6}>
                GLM-4.6 🏆 (旗舰200K)
              </Option>
              <Option value={ModelType.GLM_4_PLUS}>
                GLM-4-Plus (性能优秀)
              </Option>
              <Option value={ModelType.GLM_4_LONG}>
                GLM-4-Long (1M上下文)
              </Option>
              <Option value={ModelType.GLM_4_FLASH}>
                GLM-4-Flash 🆓 (免费)
              </Option>
              <Option value={ModelType.GLM_4_5V}>
                GLM-4.5V 👁️ (视觉旗舰)
              </Option>
            </Select>
            
            <span className="text-xs text-gray-500">
              已输入 {query.length} 字
            </span>
          </Space>

          <Button
            type="primary"
            size="large"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            loading={loading}
            disabled={disabled || !query.trim()}
          >
            发送提问
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-500">快速提问:</span>
          {quickQuestions.map((q, idx) => (
            <Button
              key={idx}
              size="small"
              type="text"
              onClick={() => setQuery(q)}
              disabled={disabled}
              className="text-xs"
            >
              {q}
            </Button>
          ))}
        </div>
      </Space>
    </div>
  );
};

export default QueryInput;

