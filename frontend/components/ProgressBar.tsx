/**
 * 进度条组件
 * 显示索引进度，带实时更新和状态提示
 */

'use client';

import React, { useEffect, useState } from 'react';
import { Progress, Card, Space, Typography, Tag, Alert } from 'antd';
import {
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useIndexingProgress, ProgressData } from '@/hooks/useIndexingProgress';

const { Text, Paragraph } = Typography;

export interface ProgressBarProps {
  novelId: number;
  title?: string;
  showDetails?: boolean;
  onComplete?: (data: ProgressData) => void;
  onError?: (error: string) => void;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  novelId,
  title = '索引进度',
  showDetails = true,
  onComplete,
  onError,
}) => {
  const { progressData, isConnected, error, disconnect } = useIndexingProgress({
    novelId,
    enabled: true,
    onComplete,
    onError,
  });

  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // 计算已用时间
  useEffect(() => {
    if (!progressData || progressData.status !== 'processing') {
      return;
    }

    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [progressData, startTime]);

  // 格式化时间
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // 获取状态图标和颜色
  const getStatusInfo = () => {
    if (!progressData) {
      return {
        icon: <ClockCircleOutlined />,
        color: 'default',
        text: '等待中',
      };
    }

    switch (progressData.status) {
      case 'pending':
        return {
          icon: <ClockCircleOutlined />,
          color: 'default',
          text: '等待索引',
        };
      case 'processing':
        return {
          icon: <LoadingOutlined spin />,
          color: 'processing',
          text: '索引中',
        };
      case 'completed':
        return {
          icon: <CheckCircleOutlined />,
          color: 'success',
          text: '已完成',
        };
      case 'failed':
        return {
          icon: <CloseCircleOutlined />,
          color: 'error',
          text: '索引失败',
        };
      default:
        return {
          icon: <ClockCircleOutlined />,
          color: 'default',
          text: '未知状态',
        };
    }
  };

  const statusInfo = getStatusInfo();
  const percent = progressData ? Math.round(progressData.progress * 100) : 0;

  return (
    <Card title={title} size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 连接状态提示 */}
        {!isConnected && progressData?.status === 'processing' && (
          <Alert message="正在重新连接..." type="warning" showIcon banner />
        )}

        {/* 错误提示 */}
        {error && <Alert message={error} type="error" showIcon closable />}

        {/* 状态标签 */}
        <div>
          <Tag icon={statusInfo.icon} color={statusInfo.color}>
            {statusInfo.text}
          </Tag>
          {progressData?.status === 'processing' && (
            <Text type="secondary"> 已用时: {formatTime(elapsedTime)}</Text>
          )}
        </div>

        {/* 进度条 */}
        <Progress
          percent={percent}
          status={
            progressData?.status === 'completed'
              ? 'success'
              : progressData?.status === 'failed'
              ? 'exception'
              : progressData?.status === 'processing'
              ? 'active'
              : 'normal'
          }
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
        />

        {/* 进度消息 */}
        {progressData?.message && (
          <Paragraph style={{ margin: 0 }}>
            <Text>{progressData.message}</Text>
          </Paragraph>
        )}

        {/* 详细信息 */}
        {showDetails && progressData && (
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            {progressData.totalChapters !== undefined && (
              <Text type="secondary">
                章节进度: {progressData.completedChapters || 0} /{' '}
                {progressData.totalChapters}
              </Text>
            )}
            {progressData.totalChunks !== undefined && progressData.totalChunks > 0 && (
              <Text type="secondary">已生成块数: {progressData.totalChunks}</Text>
            )}
          </Space>
        )}

        {/* 预计剩余时间 */}
        {progressData?.status === 'processing' &&
          progressData.progress > 0 &&
          progressData.progress < 1 && (
            <Text type="secondary">
              预计剩余时间:{' '}
              {formatTime(
                Math.round((elapsedTime / progressData.progress) * (1 - progressData.progress))
              )}
            </Text>
          )}
      </Space>
    </Card>
  );
};

export default ProgressBar;

