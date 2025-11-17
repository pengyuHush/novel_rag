/**
 * 角色关系图谱
 * 使用Plotly.js绘制网络图
 */

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import type { RelationGraphData } from '@/types/api';

// 动态导入Plotly以避免SSR问题
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface RelationGraphProps {
  novelId: number;
}

export function RelationGraph({ novelId }: RelationGraphProps) {
  const [data, setData] = useState<RelationGraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [startChapter, setStartChapter] = useState<string>('');
  const [endChapter, setEndChapter] = useState<string>('');
  const [maxNodes, setMaxNodes] = useState<string>('50');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadGraph();
  }, [novelId]);

  const loadGraph = async (filters?: {
    startChapter?: number;
    endChapter?: number;
    maxNodes?: number;
  }) => {
    try {
      setIsLoading(true);
      const graphData = await api.getRelationGraph(novelId, filters);
      setData(graphData);
    } catch (error) {
      console.error('Failed to load relation graph:', error);
      toast.error('加载关系图谱失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyFilters = () => {
    const filters: any = {};
    if (startChapter) filters.startChapter = parseInt(startChapter);
    if (endChapter) filters.endChapter = parseInt(endChapter);
    if (maxNodes) filters.maxNodes = parseInt(maxNodes);
    loadGraph(filters);
  };

  const handleResetFilters = () => {
    setStartChapter('');
    setEndChapter('');
    setMaxNodes('50');
    loadGraph();
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

          {showFilters && (
            <>
              <div className="flex items-center gap-2">
                <Label htmlFor="startChapter" className="text-sm whitespace-nowrap">
                  起始章节:
                </Label>
                <Input
                  id="startChapter"
                  type="number"
                  min="1"
                  value={startChapter}
                  onChange={(e) => setStartChapter(e.target.value)}
                  placeholder="1"
                  className="w-20 h-8"
                />
              </div>

              <div className="flex items-center gap-2">
                <Label htmlFor="endChapter" className="text-sm whitespace-nowrap">
                  结束章节:
                </Label>
                <Input
                  id="endChapter"
                  type="number"
                  min="1"
                  value={endChapter}
                  onChange={(e) => setEndChapter(e.target.value)}
                  placeholder="最后"
                  className="w-20 h-8"
                />
              </div>

              <div className="flex items-center gap-2">
                <Label htmlFor="maxNodes" className="text-sm whitespace-nowrap">
                  最大节点数:
                </Label>
                <Input
                  id="maxNodes"
                  type="number"
                  min="10"
                  max="200"
                  value={maxNodes}
                  onChange={(e) => setMaxNodes(e.target.value)}
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
            节点: {data?.metadata?.total_nodes || 0} | 边: {data?.metadata?.total_edges || 0}
          </div>
        </div>
      </Card>

      {/* 图谱可视化 */}
      <div className="flex-1 min-h-0">
      <Plot
        data={[...edgeTraces, nodeTrace] as any}
        layout={{
          showlegend: false,
          hovermode: 'closest',
          xaxis: { visible: false },
          yaxis: { visible: false },
            margin: { t: 10, b: 10, l: 10, r: 10 },
          autosize: true,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
            modeBarButtonsToRemove: ['select2d', 'lasso2d'],
        }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
      </div>
    </div>
  );
}

