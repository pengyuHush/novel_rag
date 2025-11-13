'use client';

/**
 * API Key配置组件
 * 
 * 允许用户配置和测试智谱AI API Key
 */

import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Space, Alert, message, Typography } from 'antd';
import { KeyOutlined, CheckCircleOutlined, CloseCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { apiClient } from '@/lib/api';
import { saveApiKey, getApiKey } from '@/store/userPreferences';

const { Paragraph, Text } = Typography;

const ApiKeyConfig: React.FC = () => {
  const [apiKey, setApiKey] = useState<string>('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  // 加载已保存的API Key
  useEffect(() => {
    const saved = getApiKey();
    if (saved) {
      setApiKey(saved);
    }
  }, []);

  // 测试连接
  const testConnection = async () => {
    if (!apiKey || apiKey.trim().length === 0) {
      message.error('请输入API Key');
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await apiClient.post<{
        success: boolean;
        message: string;
        model_tested: string;
      }>('/config/test-connection', {
        api_key: apiKey.trim(),
      });

      setTestResult({
        success: response.success,
        message: response.message,
      });

      if (response.success) {
        message.success('连接测试成功！');
        // 保存API Key
        saveApiKey(apiKey.trim());
      } else {
        message.error('连接测试失败');
      }
    } catch (error: any) {
      setTestResult({
        success: false,
        message: error.message || '连接测试失败',
      });
      message.error('连接测试失败');
    } finally {
      setTesting(false);
    }
  };

  // 保存API Key
  const handleSave = () => {
    if (!apiKey || apiKey.trim().length === 0) {
      message.error('请输入API Key');
      return;
    }

    saveApiKey(apiKey.trim());
    message.success('API Key已保存');
  };

  return (
    <Card
      title={
        <Space>
          <KeyOutlined />
          <span>智谱AI API Key 配置</span>
        </Space>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 说明文字 */}
        <Alert
          message="如何获取API Key"
          description={
            <div>
              <Paragraph>
                1. 访问{' '}
                <a href="https://open.bigmodel.cn/" target="_blank" rel="noopener noreferrer">
                  智谱AI开放平台
                </a>
              </Paragraph>
              <Paragraph>2. 注册并登录账号</Paragraph>
              <Paragraph>3. 进入"API管理"页面，创建新的API Key</Paragraph>
              <Paragraph>4. 复制API Key并粘贴到下方输入框</Paragraph>
            </div>
          }
          type="info"
          showIcon
        />

        {/* API Key输入 */}
        <div>
          <Text strong>API Key:</Text>
          <Input.Password
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="请输入您的智谱AI API Key"
            size="large"
            prefix={<KeyOutlined />}
            style={{ marginTop: 8 }}
          />
        </div>

        {/* 操作按钮 */}
        <Space>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={testConnection}
            loading={testing}
            disabled={!apiKey || apiKey.trim().length === 0}
          >
            测试连接
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleSave}
            disabled={!apiKey || apiKey.trim().length === 0}
          >
            保存
          </Button>
        </Space>

        {/* 测试结果 */}
        {testResult && (
          <Alert
            message={testResult.success ? '连接成功' : '连接失败'}
            description={testResult.message}
            type={testResult.success ? 'success' : 'error'}
            showIcon
            icon={testResult.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          />
        )}

        {/* 安全提示 */}
        <Alert
          message="安全提示"
          description="API Key存储在浏览器本地，不会上传到服务器。请妥善保管您的API Key，不要分享给他人。"
          type="warning"
          showIcon
        />
      </Space>
    </Card>
  );
};

export default ApiKeyConfig;

