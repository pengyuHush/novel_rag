'use client';

/**
 * Token统计图表组件
 * 
 * 使用Chart.js展示Token使用趋势
 */

import React, { useEffect, useState } from 'react';
import { Card, Select, Empty, Spin } from 'antd';
import { BarChartOutlined } from '@ant-design/icons';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { apiClient } from '@/lib/api';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const { Option } = Select;

interface TrendData {
  period: string;
  total_tokens: number;
  total_cost: number;
}

const TokenChart: React.FC = () => {
  const [period, setPeriod] = useState<'day' | 'week' | 'month'>('day');
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTrendData();
  }, [period]);

  const loadTrendData = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<{
        period: string;
        data: TrendData[];
      }>(`/stats/tokens/trend`, {
        period,
        limit: period === 'day' ? 30 : period === 'week' ? 12 : 12,
      });

      setTrendData(response.data);
    } catch (error) {
      console.error('Failed to load trend data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: trendData.map((item) => item.period),
    datasets: [
      {
        label: 'Token消耗',
        data: trendData.map((item) => item.total_tokens),
        backgroundColor: 'rgba(24, 144, 255, 0.6)',
        borderColor: 'rgba(24, 144, 255, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.parsed.y;
            const index = context.dataIndex;
            const cost = trendData[index]?.total_cost || 0;
            return [
              `Token: ${value.toLocaleString()}`,
              `成本: ¥${cost.toFixed(4)}`,
            ];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return value.toLocaleString();
          },
        },
      },
    },
  };

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <span>
            <BarChartOutlined className="mr-2" />
            Token使用趋势
          </span>
          <Select value={period} onChange={setPeriod} style={{ width: 120 }}>
            <Option value="day">按天</Option>
            <Option value="week">按周</Option>
            <Option value="month">按月</Option>
          </Select>
        </div>
      }
      className="shadow-sm"
    >
      {loading ? (
        <div className="flex justify-center items-center h-80">
          <Spin />
        </div>
      ) : trendData.length > 0 ? (
        <div style={{ height: '320px' }}>
          <Bar data={chartData} options={chartOptions} />
        </div>
      ) : (
        <Empty description="暂无数据" />
      )}
    </Card>
  );
};

export default TokenChart;

