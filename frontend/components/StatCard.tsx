'use client';

/**
 * 统计卡片组件
 * 
 * 用于展示关键统计指标
 */

import React from 'react';
import { Card, Statistic, Space } from 'antd';
import {
  ThunderboltOutlined,
  DollarOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';

interface StatCardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: string;
  precision?: number;
  valueStyle?: React.CSSProperties;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  loading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  prefix,
  suffix,
  precision = 0,
  valueStyle,
  icon,
  trend,
  loading = false,
}) => {
  return (
    <Card loading={loading} className="shadow-sm hover:shadow-md transition-shadow">
      <Statistic
        title={
          <Space>
            {icon}
            <span>{title}</span>
          </Space>
        }
        value={value}
        prefix={prefix}
        suffix={suffix}
        precision={precision}
        valueStyle={valueStyle || { color: '#1890ff' }}
      />
      {trend && (
        <div className="mt-2 text-sm">
          <span className={trend.isPositive ? 'text-red-500' : 'text-green-500'}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value).toFixed(1)}%
          </span>
          <span className="text-gray-500 ml-2">vs 上周</span>
        </div>
      )}
    </Card>
  );
};

// 预定义的统计卡片类型
export const TokenStatCard: React.FC<{ value: number; loading?: boolean }> = ({
  value,
  loading,
}) => (
  <StatCard
    title="总Token消耗"
    value={value}
    suffix="tokens"
    icon={<ThunderboltOutlined />}
    valueStyle={{ color: '#1890ff' }}
    loading={loading}
  />
);

export const CostStatCard: React.FC<{ value: number; loading?: boolean }> = ({
  value,
  loading,
}) => (
  <StatCard
    title="总成本"
    value={value}
    prefix="¥"
    precision={4}
    icon={<DollarOutlined />}
    valueStyle={{ color: '#52c41a' }}
    loading={loading}
  />
);

export const QueryCountStatCard: React.FC<{ value: number; loading?: boolean }> = ({
  value,
  loading,
}) => (
  <StatCard
    title="查询次数"
    value={value}
    suffix="次"
    icon={<FileTextOutlined />}
    valueStyle={{ color: '#faad14' }}
    loading={loading}
  />
);

export const IndexCountStatCard: React.FC<{ value: number; loading?: boolean }> = ({
  value,
  loading,
}) => (
  <StatCard
    title="索引次数"
    value={value}
    suffix="次"
    icon={<ClockCircleOutlined />}
    valueStyle={{ color: '#722ed1' }}
    loading={loading}
  />
);

export default StatCard;

