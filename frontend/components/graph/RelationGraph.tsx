/**
 * 角色关系图谱
 * 使用Plotly.js绘制网络图
 */

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import type { RelationGraphData } from '@/types/api';

// 动态导入Plotly以避免SSR问题
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface RelationGraphProps {
  novelId: number;
}

export function RelationGraph({ novelId }: RelationGraphProps) {
  const [data, setData] = useState<RelationGraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadGraph();
  }, [novelId]);

  const loadGraph = async () => {
    try {
      setIsLoading(true);
      const graphData = await api.getRelationGraph(novelId);
      setData(graphData);
    } catch (error) {
      console.error('Failed to load relation graph:', error);
      toast.error('加载关系图谱失败');
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

  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">暂无关系图谱数据</p>
      </div>
    );
  }

  // 转换数据为Plotly格式
  const nodeTrace = {
    type: 'scatter',
    mode: 'markers+text',
    x: data.nodes.map((_, i) => Math.cos((2 * Math.PI * i) / data.nodes.length)),
    y: data.nodes.map((_, i) => Math.sin((2 * Math.PI * i) / data.nodes.length)),
    text: data.nodes.map((n) => n.name),
    textposition: 'top center',
    marker: {
      size: data.nodes.map((n) => 10 + n.importance * 30),
      color: data.nodes.map((n) => n.importance),
      colorscale: 'Viridis',
      showscale: true,
      colorbar: {
        title: '重要性',
      },
    },
    hovertemplate: '%{text}<br>重要性: %{marker.color:.2f}<extra></extra>',
  };

  const edgeTraces = data.edges.map((edge) => {
    const sourceIndex = data.nodes.findIndex((n) => n.id === edge.source);
    const targetIndex = data.nodes.findIndex((n) => n.id === edge.target);

    return {
      type: 'scatter',
      mode: 'lines',
      x: [
        Math.cos((2 * Math.PI * sourceIndex) / data.nodes.length),
        Math.cos((2 * Math.PI * targetIndex) / data.nodes.length),
      ],
      y: [
        Math.sin((2 * Math.PI * sourceIndex) / data.nodes.length),
        Math.sin((2 * Math.PI * targetIndex) / data.nodes.length),
      ],
      line: {
        width: 1,
        color: '#888',
      },
      hoverinfo: 'text',
      text: `${edge.source} → ${edge.target}<br>关系: ${edge.relationType}`,
    };
  });

  return (
    <div className="w-full h-full">
      <Plot
        data={[...edgeTraces, nodeTrace] as any}
        layout={{
          showlegend: false,
          hovermode: 'closest',
          xaxis: { visible: false },
          yaxis: { visible: false },
          margin: { t: 20, b: 20, l: 20, r: 20 },
          autosize: true,
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
        }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
}

