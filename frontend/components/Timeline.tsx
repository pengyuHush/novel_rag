'use client';

/**
 * 时间线组件
 * 
 * 展示小说事件的时间线可视化
 * 支持实体过滤和非线性叙事标注
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Select, Button, Space, Spin, message, Empty, Timeline as AntTimeline, Tag } from 'antd';
import { ReloadOutlined, ClockCircleOutlined, DownloadOutlined } from '@ant-design/icons';
import { apiClient } from '@/lib/api';

const { Option } = Select;

interface TimelineProps {
  novelId: number;
}

interface TimelineEvent {
  chapter: number;
  type: string;
  entity?: string;
  source?: string;
  target?: string;
  relation_type?: string;
  description: string;
  importance: number;
  entity_type?: string;
}

interface TimelineData {
  events: TimelineEvent[];
  metadata: {
    total_events: number;
    entity_filter: string | null;
    chapter_range: [number, number];
  };
}

const Timeline: React.FC<TimelineProps> = ({ novelId }) => {
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(false);
  const [entityFilter, setEntityFilter] = useState<string | null>(null);
  const [entities, setEntities] = useState<string[]>([]);

  // 加载时间线数据
  const loadTimeline = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = {
        max_events: 100,
      };
      
      if (entityFilter) {
        params.entity_filter = entityFilter;
      }

      const response = await apiClient.get<TimelineData>(
        `/graph/timeline/${novelId}`,
        params
      );

      setTimelineData(response);

      // 提取所有实体用于过滤器
      const uniqueEntities = new Set<string>();
      response.events.forEach((event) => {
        if (event.entity) uniqueEntities.add(event.entity);
        if (event.source) uniqueEntities.add(event.source);
        if (event.target) uniqueEntities.add(event.target);
      });
      setEntities(Array.from(uniqueEntities).sort());

      message.success(`加载成功：${response.events.length} 个事件`);
    } catch (error: any) {
      message.error(`加载失败：${error.message || '未知错误'}`);
      console.error('Failed to load timeline:', error);
    } finally {
      setLoading(false);
    }
  }, [novelId, entityFilter]);

  // 导出时间线
  const exportTimeline = useCallback(() => {
    if (!timelineData) {
      message.error('无数据可导出');
      return;
    }

    // 生成CSV格式
    const csvContent = [
      ['章节', '类型', '描述', '重要性'].join(','),
      ...timelineData.events.map((event) =>
        [
          event.chapter,
          event.type,
          `"${event.description.replace(/"/g, '""')}"`,
          event.importance,
        ].join(',')
      ),
    ].join('\n');

    // 下载文件
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `timeline_novel_${novelId}.csv`;
    link.click();

    message.success('导出成功');
  }, [timelineData, novelId]);

  // 初始加载
  useEffect(() => {
    loadTimeline();
  }, [loadTimeline]);

  // 获取事件颜色
  const getEventColor = (eventType: string): string => {
    const colorMap: { [key: string]: string } = {
      'entity_appear': 'blue',
      'relation_start': 'green',
      'relation_evolve': 'orange',
      'conflict': 'red',
      'plot_twist': 'purple',
    };
    return colorMap[eventType] || 'gray';
  };

  // 获取事件图标
  const getEventDot = (event: TimelineEvent) => {
    const color = getEventColor(event.type);
    return <ClockCircleOutlined style={{ color, fontSize: 16 }} />;
  };

  // 按章节分组事件
  const groupEventsByChapter = (events: TimelineEvent[]) => {
    const grouped: { [chapter: number]: TimelineEvent[] } = {};
    events.forEach((event) => {
      if (!grouped[event.chapter]) {
        grouped[event.chapter] = [];
      }
      grouped[event.chapter].push(event);
    });
    return grouped;
  };

  return (
    <div>
      {/* 控制面板 */}
      <Card className="mb-4" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 实体过滤器 */}
          <div>
            <span className="mr-2">过滤实体：</span>
            <Select
              value={entityFilter}
              onChange={setEntityFilter}
              style={{ width: 200 }}
              placeholder="选择实体"
              allowClear
            >
              {entities.map((entity) => (
                <Option key={entity} value={entity}>
                  {entity}
                </Option>
              ))}
            </Select>
          </div>

          {/* 操作按钮 */}
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadTimeline}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={exportTimeline}
              disabled={!timelineData}
            >
              导出CSV
            </Button>
          </Space>

          {/* 元数据 */}
          {timelineData && (
            <div className="text-sm text-gray-600">
              <Space split={<span>|</span>}>
                <span>共 {timelineData.metadata.total_events} 个事件</span>
                <span>
                  章节范围: {timelineData.metadata.chapter_range[0]} -{' '}
                  {timelineData.metadata.chapter_range[1]}
                </span>
                {timelineData.metadata.entity_filter && (
                  <span>
                    <Tag color="blue">{timelineData.metadata.entity_filter}</Tag>
                    相关事件
                  </span>
                )}
              </Space>
            </div>
          )}
        </Space>
      </Card>

      {/* 时间线可视化 */}
      <Card loading={loading} style={{ maxHeight: 800, overflow: 'auto' }}>
        {timelineData && timelineData.events.length > 0 ? (
          <AntTimeline mode="left">
            {Object.entries(groupEventsByChapter(timelineData.events)).map(
              ([chapter, events]) => (
                <AntTimeline.Item
                  key={chapter}
                  label={
                    <div className="font-bold text-blue-600">第 {chapter} 章</div>
                  }
                  dot={<ClockCircleOutlined style={{ fontSize: 16 }} />}
                >
                  <Space direction="vertical" size="small" style={{ width: '100%' }}>
                    {events.map((event, index) => (
                      <Card
                        key={`${chapter}-${index}`}
                        size="small"
                        className="shadow-sm"
                        style={{ borderLeft: `3px solid ${getEventColor(event.type)}` }}
                      >
                        <Space direction="vertical" size={0}>
                          <div>
                            <Tag color={getEventColor(event.type)}>
                              {event.type.replace(/_/g, ' ')}
                            </Tag>
                            {event.entity_type && (
                              <Tag>{event.entity_type}</Tag>
                            )}
                            {event.relation_type && (
                              <Tag color="green">{event.relation_type}</Tag>
                            )}
                          </div>
                          <div className="text-sm">{event.description}</div>
                          <div className="text-xs text-gray-500">
                            重要性: {(event.importance * 100).toFixed(0)}%
                          </div>
                        </Space>
                      </Card>
                    ))}
                  </Space>
                </AntTimeline.Item>
              )
            )}
          </AntTimeline>
        ) : (
          <Empty
            description="暂无时间线数据"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Card>
    </div>
  );
};

export default Timeline;

