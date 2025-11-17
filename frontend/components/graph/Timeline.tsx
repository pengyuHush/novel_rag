/**
 * 时间线可视化
 * 显示事件按时间顺序排列
 */

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import type { TimelineData } from '@/types/api';

// 动态导入Plotly以避免SSR问题
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface TimelineProps {
  novelId: number;
}

export function Timeline({ novelId }: TimelineProps) {
  const [data, setData] = useState<TimelineData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadTimeline();
  }, [novelId]);

  const loadTimeline = async () => {
    try {
      setIsLoading(true);
      const timelineData = await api.getTimeline(novelId);
      setData(timelineData);
    } catch (error) {
      console.error('Failed to load timeline:', error);
      toast.error('加载时间线失败');
    } finally {
      setIsLoading(false);
    }
  };

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

  // 转换数据为Plotly格式
  const trace = {
    type: 'scatter',
    mode: 'markers+lines',
    x: data.events.map((e) => e.chapterNum),
    y: data.events.map((e) => e.narrativeOrder),
    marker: {
      size: 12,
      color: data.events.map((e) => e.chapterNum),
      colorscale: 'Viridis',
      showscale: true,
      colorbar: {
        title: '章节',
        thickness: 15,
        len: 0.7,
      },
      line: {
        color: 'white',
        width: 1,
      },
    },
    line: {
      color: 'rgba(100, 100, 100, 0.3)',
      width: 1,
    },
    hovertemplate: 
      '<b>第 %{x} 章</b><br>' +
      '事件序号: %{y}<br>' +
      '%{customdata}' +
      '<extra></extra>',
    customdata: data.events.map((e) => e.description),
  };

  return (
    <div className="w-full h-full">
      <Plot
        data={[trace] as any}
        layout={{
          title: {
            text: '小说事件时间线',
            font: { size: 18 },
          },
          xaxis: {
            title: '章节号',
            gridcolor: 'rgba(200, 200, 200, 0.2)',
            zeroline: false,
          },
          yaxis: {
            title: '事件序号（叙述顺序）',
            gridcolor: 'rgba(200, 200, 200, 0.2)',
            zeroline: false,
          },
          hovermode: 'closest',
          margin: { t: 60, b: 60, l: 80, r: 40 },
          autosize: true,
          plot_bgcolor: 'rgba(0,0,0,0)',
          paper_bgcolor: 'rgba(0,0,0,0)',
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
}

