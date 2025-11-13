'use client';

/**
 * 加载骨架屏组件
 * 
 * 提供各种场景的加载占位符，提升用户体验
 */

import React from 'react';
import { Skeleton, Card } from 'antd';

/**
 * 通用骨架屏
 */
export const LoadingSkeleton: React.FC<{
  active?: boolean;
  rows?: number;
  avatar?: boolean;
}> = ({ active = true, rows = 4, avatar = false }) => (
  <Skeleton active={active} paragraph={{ rows }} avatar={avatar} />
);

/**
 * 卡片骨架屏
 */
export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 1 }) => (
  <>
    {Array.from({ length: count }).map((_, index) => (
      <Card key={index} className="mb-4">
        <Skeleton active paragraph={{ rows: 3 }} />
      </Card>
    ))}
  </>
);

/**
 * 列表骨架屏
 */
export const ListSkeleton: React.FC<{ count?: number }> = ({ count = 5 }) => (
  <div className="space-y-4">
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="flex items-center space-x-4 p-4 bg-white rounded">
        <Skeleton.Avatar active size="large" />
        <div className="flex-1">
          <Skeleton active paragraph={{ rows: 2 }} />
        </div>
      </div>
    ))}
  </div>
);

/**
 * 表格骨架屏
 */
export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 10 }) => (
  <div className="space-y-2">
    {/* 表头 */}
    <div className="flex space-x-2 p-4 bg-gray-100 rounded">
      <Skeleton.Button active size="small" style={{ width: 100 }} />
      <Skeleton.Button active size="small" style={{ width: 150 }} />
      <Skeleton.Button active size="small" style={{ width: 120 }} />
      <Skeleton.Button active size="small" style={{ width: 80 }} />
    </div>
    
    {/* 表格行 */}
    {Array.from({ length: rows }).map((_, index) => (
      <div key={index} className="flex space-x-2 p-4 bg-white rounded">
        <Skeleton.Button active size="small" style={{ width: 100 }} />
        <Skeleton.Button active size="small" style={{ width: 150 }} />
        <Skeleton.Button active size="small" style={{ width: 120 }} />
        <Skeleton.Button active size="small" style={{ width: 80 }} />
      </div>
    ))}
  </div>
);

/**
 * 统计卡片骨架屏
 */
export const StatCardSkeleton: React.FC = () => (
  <Card className="shadow-sm">
    <Skeleton active paragraph={{ rows: 1 }} />
    <div className="mt-4">
      <Skeleton.Button active size="large" block style={{ height: 40 }} />
    </div>
  </Card>
);

/**
 * 图表骨架屏
 */
export const ChartSkeleton: React.FC = () => (
  <Card className="shadow-sm">
    <Skeleton.Input active style={{ width: 200, marginBottom: 16 }} />
    <Skeleton.Image active style={{ width: '100%', height: 300 }} />
  </Card>
);

/**
 * 小说卡片骨架屏
 */
export const NovelCardSkeleton: React.FC<{ count?: number }> = ({ count = 4 }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {Array.from({ length: count }).map((_, index) => (
      <Card key={index} className="shadow-sm">
        <Skeleton.Image active style={{ width: '100%', height: 200 }} />
        <div className="mt-4">
          <Skeleton active paragraph={{ rows: 2 }} />
        </div>
      </Card>
    ))}
  </div>
);

/**
 * 查询结果骨架屏
 */
export const QueryResultSkeleton: React.FC = () => (
  <div className="space-y-4">
    <Skeleton.Input active style={{ width: '100%', height: 40 }} />
    <div className="space-y-2">
      <Skeleton active paragraph={{ rows: 6 }} />
    </div>
    <div className="space-y-2">
      <Skeleton.Button active size="small" />
      <Skeleton.Button active size="small" />
      <Skeleton.Button active size="small" />
    </div>
  </div>
);

/**
 * 关系图骨架屏
 */
export const GraphSkeleton: React.FC = () => (
  <div className="relative" style={{ height: 600 }}>
    <Skeleton.Node active style={{ width: '100%', height: '100%' }}>
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <div className="text-4xl mb-4">📊</div>
          <div>正在加载图表...</div>
        </div>
      </div>
    </Skeleton.Node>
  </div>
);

export default LoadingSkeleton;

