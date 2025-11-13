/**
 * 查询阶段进度组件
 */

'use client';

import React from 'react';
import { Steps, Progress } from 'antd';
import { QueryStage } from '@/types/query';
import {
  BulbOutlined,
  SearchOutlined,
  EditOutlined,
  CheckCircleOutlined,
  RocketOutlined,
} from '@ant-design/icons';

interface StageProgressProps {
  stage: QueryStage | string;
  progress: number;
}

const stageInfo = {
  [QueryStage.UNDERSTANDING]: {
    title: '理解问题',
    icon: <BulbOutlined />,
    description: '正在分析您的问题...',
  },
  [QueryStage.RETRIEVING]: {
    title: '检索内容',
    icon: <SearchOutlined />,
    description: '正在搜索相关章节...',
  },
  [QueryStage.GENERATING]: {
    title: '生成答案',
    icon: <EditOutlined />,
    description: '正在生成回答...',
  },
  [QueryStage.VALIDATING]: {
    title: '验证答案',
    icon: <CheckCircleOutlined />,
    description: '正在检查答案...',
  },
  [QueryStage.FINALIZING]: {
    title: '完成',
    icon: <RocketOutlined />,
    description: '整理结果...',
  },
};

const stageOrder = [
  QueryStage.UNDERSTANDING,
  QueryStage.RETRIEVING,
  QueryStage.GENERATING,
  QueryStage.FINALIZING,
];

const StageProgress: React.FC<StageProgressProps> = ({ stage, progress }) => {
  const currentIndex = stageOrder.indexOf(stage as QueryStage);
  
  return (
    <div className="stage-progress py-4">
      <Steps
        current={currentIndex}
        size="small"
        items={stageOrder.map((s) => ({
          title: stageInfo[s].title,
          icon: stageInfo[s].icon,
        }))}
      />
      
      <div className="mt-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">
            {stageInfo[stage as QueryStage]?.description || '处理中...'}
          </span>
          <span className="font-medium">
            {(progress * 100).toFixed(0)}%
          </span>
        </div>
        <Progress
          percent={progress * 100}
          status="active"
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          showInfo={false}
        />
      </div>
    </div>
  );
};

export default StageProgress;

