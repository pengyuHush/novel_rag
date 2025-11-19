/**
 * 时间线组件（ECharts版本）
 * 支持泳道式和气泡式两种布局
 */

'use client';

import { useEffect, useState, useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { ScatterChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import type { TimelineData, TimelineEvent } from '@/types/api';
import { EVENT_STYLES } from '@/types/visualization';

// 注册必要的 ECharts 组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ScatterChart,
  LineChart,
  CanvasRenderer,
]);

interface TimelineProps {
  novelId: number;
}

type TimelineLayout = 'swimlane' | 'bubble';

export function TimelineEcharts({ novelId }: TimelineProps) {
  const [data, setData] = useState<TimelineData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [layout, setLayout] = useState<TimelineLayout>('swimlane');
  const [showFilters, setShowFilters] = useState(false);
  const [minImportance, setMinImportance] = useState<string>('0');
  const [eventTypesFilter, setEventTypesFilter] = useState<string[]>([]);

  useEffect(() => {
    loadTimeline();
  }, [novelId]);

  const loadTimeline = async (filters?: {
    eventTypes?: string;
    minImportance?: number;
  }) => {
    try {
      setIsLoading(true);
      const timelineData = await api.getTimeline(novelId, filters);
      setData(timelineData);
    } catch (error) {
      console.error('Failed to load timeline:', error);
      toast.error('加载时间线失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilters = () => {
    const filters: any = {};
    if (eventTypesFilter.length > 0) {
      filters.eventTypes = eventTypesFilter.join(',');
    }
    if (minImportance) {
      filters.minImportance = parseFloat(minImportance);
    }
    loadTimeline(filters);
  };

  const handleResetFilters = () => {
    setMinImportance('0');
    setEventTypesFilter([]);
    loadTimeline();
  };

  const toggleEventType = (type: string) => {
    setEventTypesFilter((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  // 生成泳道式布局
  const generateSwimlaneOption = (events: TimelineEvent[]) => {
    // 按事件类型分组
    const eventLanes: Record<string, { y: number; name: string; color: string; events: TimelineEvent[] }> = {
      entity_appear: { y: 1, name: '角色出现', color: EVENT_STYLES.entity_appear.color, events: [] },
      relation_start: { y: 2, name: '关系建立', color: EVENT_STYLES.relation_start.color, events: [] },
      relation_evolve: { y: 3, name: '关系演变', color: EVENT_STYLES.relation_evolve.color, events: [] },
    };

    events.forEach((event) => {
      const lane = eventLanes[event.eventType];
      if (lane) {
        lane.events.push(event);
      }
    });

    // 为每个泳道创建系列
    const series = Object.entries(eventLanes).map(([type, lane]) => ({
      name: lane.name,
      type: 'scatter',
      data: lane.events.map((e) => ({
        value: [e.chapterNum, lane.y, e.importance],
        event: e,
      })),
      symbolSize: (val: number[]) => 8 + val[2] * 20,
      itemStyle: {
        color: lane.color,
      },
      label: {
        show: false,
      },
      emphasis: {
        label: {
          show: true,
          formatter: (params: any) => params.data.event.description.substring(0, 20),
          position: 'top',
        },
      },
    }));

    return {
      title: {
        text: '事件时间线（泳道式）',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const event = params.data.event;
          return `
            <div style="padding: 8px; max-width: 300px;">
              <div style="font-weight: bold; margin-bottom: 4px;">第 ${event.chapterNum} 章</div>
              <div style="margin-bottom: 4px;">${event.description}</div>
              <div>类型: ${eventLanes[event.eventType]?.name || event.eventType}</div>
              <div>重要性: ${event.importance.toFixed(2)}</div>
            </div>
          `;
        },
      },
      legend: {
        data: Object.values(eventLanes).map((lane) => lane.name),
        top: 40,
      },
      grid: {
        left: 60,
        right: 40,
        top: 80,
        bottom: 80,
      },
      xAxis: {
        name: '章节号',
        type: 'value',
        nameLocation: 'middle',
        nameGap: 30,
      },
      yAxis: {
        type: 'value',
        min: 0.5,
        max: 3.5,
        interval: 1,
        axisLabel: {
          formatter: (value: number) => {
            const lane = Object.values(eventLanes).find((l) => l.y === value);
            return lane ? lane.name : '';
          },
        },
      },
      dataZoom: [
        {
          type: 'slider',
          xAxisIndex: 0,
          start: 0,
          end: 100,
          bottom: 20,
        },
        {
          type: 'inside',
          xAxisIndex: 0,
        },
      ],
      series: series,
    };
  };

  // 生成气泡式布局
  const generateBubbleOption = (events: TimelineEvent[]) => {
    // 计算每个章节的事件数，用于分散布局
    const chapterCounts: Record<number, number> = {};
    events.forEach((e) => {
      chapterCounts[e.chapterNum] = (chapterCounts[e.chapterNum] || 0) + 1;
    });

    // 为每个事件计算Y坐标（避免重叠）
    const chapterCounters: Record<number, number> = {};
    const eventsWithY = events.map((event) => {
      const chapter = event.chapterNum;
      const counter = chapterCounters[chapter] || 0;
      chapterCounters[chapter] = counter + 1;
      
      const totalInChapter = chapterCounts[chapter];
      const y = counter - totalInChapter / 2 + 0.5;
      
      return {
        ...event,
        y: y * 5, // 缩放Y轴以增加间距
      };
    });

    // 按事件类型分组
    const eventTypes = ['entity_appear', 'relation_start', 'relation_evolve'];
    const series = eventTypes.map((type) => {
      const typeEvents = eventsWithY.filter((e) => e.eventType === type);
      const style = EVENT_STYLES[type] || EVENT_STYLES.entity_appear;

      return {
        name: style.icon + ' ' + (
          type === 'entity_appear' ? '角色出现' :
          type === 'relation_start' ? '关系建立' : '关系演变'
        ),
        type: 'scatter',
        data: typeEvents.map((e) => ({
          value: [e.chapterNum, e.y, e.importance],
          event: e,
        })),
        symbolSize: (val: number[]) => 10 + val[2] * 25,
        itemStyle: {
          color: style.color,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            formatter: (params: any) => params.data.event.description.substring(0, 20),
            position: 'top',
          },
        },
      };
    });

    return {
      title: {
        text: '事件时间线（气泡式）',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const event = params.data.event;
          return `
            <div style="padding: 8px; max-width: 300px;">
              <div style="font-weight: bold; margin-bottom: 4px;">第 ${event.chapterNum} 章</div>
              <div style="margin-bottom: 4px;">${event.description}</div>
              <div>重要性: ${event.importance.toFixed(2)}</div>
              ${event.entity ? `<div>实体: ${event.entity}</div>` : ''}
              ${event.source && event.target ? `<div>关系: ${event.source} → ${event.target}</div>` : ''}
            </div>
          `;
        },
      },
      legend: {
        data: series.map((s) => s.name),
        top: 40,
      },
      grid: {
        left: 60,
        right: 40,
        top: 80,
        bottom: 80,
      },
      xAxis: {
        name: '章节号',
        type: 'value',
        nameLocation: 'middle',
        nameGap: 30,
      },
      yAxis: {
        type: 'value',
        name: '事件分布',
        nameLocation: 'middle',
        nameGap: 40,
        axisLabel: {
          show: false,
        },
      },
      dataZoom: [
        {
          type: 'slider',
          xAxisIndex: 0,
          start: 0,
          end: 100,
          bottom: 20,
        },
        {
          type: 'inside',
          xAxisIndex: 0,
        },
      ],
      series: series,
    };
  };

  const chartOption = useMemo(() => {
    if (!data || !data.events || data.events.length === 0) {
      return null;
    }

    if (layout === 'swimlane') {
      return generateSwimlaneOption(data.events);
    } else {
      return generateBubbleOption(data.events);
    }
  }, [data, layout]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">加载中...</p>
      </div>
    );
  }

  if (!data || !data.events || data.events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">暂无时间线数据</p>
      </div>
    );
  }

  if (!chartOption) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">无法生成时间线</p>
      </div>
    );
  }

  const availableEventTypes = data.metadata?.available_event_types || [
    'entity_appear',
    'relation_start',
    'relation_evolve',
  ];

  return (
    <div className="flex flex-col h-full gap-3">
      {/* 筛选控制栏 */}
      <Card className="p-3">
        <div className="flex items-center gap-4 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? '隐藏筛选' : '显示筛选'}
          </Button>

          <div className="flex items-center gap-2">
            <Label className="text-sm whitespace-nowrap">布局:</Label>
            <select
              value={layout}
              onChange={(e) => setLayout(e.target.value as TimelineLayout)}
              className="h-8 px-2 border rounded text-sm"
            >
              <option value="swimlane">泳道式</option>
              <option value="bubble">气泡式</option>
            </select>
          </div>

          {showFilters && (
            <>
              <div className="flex items-center gap-2">
                <Label className="text-sm whitespace-nowrap">事件类型:</Label>
                <div className="flex gap-2">
                  {availableEventTypes.map((type) => {
                    const typeName =
                      type === 'entity_appear'
                        ? '角色'
                        : type === 'relation_start'
                        ? '建立'
                        : '演变';
                    return (
                      <Button
                        key={type}
                        size="sm"
                        variant={eventTypesFilter.includes(type) ? 'default' : 'outline'}
                        onClick={() => toggleEventType(type)}
                      >
                        {typeName}
                      </Button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Label htmlFor="minImportance" className="text-sm whitespace-nowrap">
                  最小重要性:
                </Label>
                <Input
                  id="minImportance"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={minImportance}
                  onChange={(e) => setMinImportance(e.target.value)}
                  className="w-20 h-8"
                />
              </div>

              <Button size="sm" onClick={handleApplyFilters}>
                应用
              </Button>
              <Button size="sm" variant="outline" onClick={handleResetFilters}>
                重置
              </Button>
            </>
          )}

          <div className="ml-auto text-sm text-muted-foreground">
            事件数: {data?.metadata?.total_events || 0}
          </div>
        </div>
      </Card>

      {/* 时间线可视化 */}
      <div className="flex-1 min-h-0">
        <ReactEChartsCore
          echarts={echarts}
          option={chartOption}
          style={{ height: '100%', width: '100%' }}
          notMerge={true}
          lazyUpdate={true}
        />
      </div>
    </div>
  );
}

