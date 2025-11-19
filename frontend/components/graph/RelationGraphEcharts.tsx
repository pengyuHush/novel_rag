/**
 * 关系图谱组件（ECharts版本）
 * 使用力导向布局展示角色关系网络
 */

'use client';

import { useEffect, useState, useMemo } from 'react';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { GraphChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import type { RelationGraphData, GraphNode, GraphEdge } from '@/types/api';
import { RELATION_STYLES, NODE_STYLES } from '@/types/visualization';
import { calculateLayout } from '@/lib/graphLayout';

// 注册必要的 ECharts 组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GraphChart,
  CanvasRenderer,
]);

interface RelationGraphProps {
  novelId: number;
}

export function RelationGraphEcharts({ novelId }: RelationGraphProps) {
  const [data, setData] = useState<RelationGraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [startChapter, setStartChapter] = useState<string>('');
  const [endChapter, setEndChapter] = useState<string>('');
  const [maxNodes, setMaxNodes] = useState<string>('50');
  const [minImportance, setMinImportance] = useState<string>('0.3');
  const [showFilters, setShowFilters] = useState(false);
  const [layoutAlgorithm, setLayoutAlgorithm] = useState<string>('force');

  useEffect(() => {
    loadGraph();
  }, [novelId]);

  const loadGraph = async (filters?: {
    startChapter?: number;
    endChapter?: number;
    maxNodes?: number;
    minImportance?: number;
  }) => {
    try {
      setIsLoading(true);
      const graphData = await api.getRelationGraph(novelId, {
        ...filters,
        includeLayout: false, // 前端计算布局
        layoutAlgorithm: layoutAlgorithm,
      });
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
    if (minImportance) filters.minImportance = parseFloat(minImportance);
    loadGraph(filters);
  };

  const handleResetFilters = () => {
    setStartChapter('');
    setEndChapter('');
    setMaxNodes('50');
    setMinImportance('0.3');
    loadGraph();
  };

  // 计算布局并生成 ECharts 配置
  const chartOption = useMemo(() => {
    if (!data || !data.nodes || data.nodes.length === 0) {
      return null;
    }

    // 使用前端布局计算
    const layoutResult = calculateLayout(
      data.nodes,
      data.edges,
      layoutAlgorithm as any,
      {
        width: 1000,
        height: 800,
        config: {
          iterations: 300,
          repulsion: 300,
          attraction: 0.1,
        },
      }
    );

    // 转换节点数据
    const nodes = layoutResult.nodes.map((node) => {
      const nodeStyle = NODE_STYLES[node.type || 'unknown'] || NODE_STYLES.unknown;
      return {
        id: node.id,
        name: node.name,
        x: node.x,
        y: node.y,
        value: node.importance,
        symbolSize: 15 + node.importance * 35,
        itemStyle: {
          color: nodeStyle.color,
        },
        label: {
          show: true,
          fontSize: 11 + node.importance * 3,
          fontWeight: node.importance > 0.7 ? 'bold' : 'normal',
        },
        // 存储原始数据用于tooltip
        originalData: node,
      };
    });

    // 转换边数据
    const links = data.edges.map((edge) => {
      const relationStyle =
        RELATION_STYLES[edge.relationType] || RELATION_STYLES['未知'];
      return {
        source: edge.source,
        target: edge.target,
        value: edge.strength,
        lineStyle: {
          color: relationStyle.color,
          width: relationStyle.width,
          type: relationStyle.type,
          curveness: 0.1,
        },
        label: {
          show: false,
          formatter: edge.relationType,
        },
        // 存储原始数据
        originalData: edge,
      };
    });

    // 生成图例数据（关系类型）
    const legendData = Array.from(
      new Set(data.edges.map((e) => e.relationType))
    ).map((type) => ({
      name: type,
      itemStyle: {
        color: RELATION_STYLES[type]?.color || '#9CA3AF',
      },
    }));

    return {
      title: {
        text: '角色关系图谱',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const node = params.data.originalData;
            return `
              <div style="padding: 8px;">
                <div style="font-weight: bold; margin-bottom: 4px;">${node.name}</div>
                <div>类型: ${node.type || '未知'}</div>
                <div>重要性: ${node.importance.toFixed(2)}</div>
                <div>出场章节: ${node.firstChapter || '?'} ${node.lastChapter ? '- ' + node.lastChapter : ''}</div>
                <div>关系数: ${node.degree || 0}</div>
              </div>
            `;
          } else if (params.dataType === 'edge') {
            const edge = params.data.originalData;
            return `
              <div style="padding: 8px;">
                <div style="font-weight: bold; margin-bottom: 4px;">${edge.source} → ${edge.target}</div>
                <div>关系: ${edge.relationType}</div>
                <div>强度: ${edge.strength.toFixed(2)}</div>
                <div>章节: ${edge.startChapter} ${edge.endChapter ? '- ' + edge.endChapter : ''}</div>
              </div>
            `;
          }
          return '';
        },
      },
      legend: {
        data: legendData,
        orient: 'vertical',
        right: 10,
        top: 50,
        textStyle: {
          fontSize: 11,
        },
      },
      series: [
        {
          type: 'graph',
          layout: 'none',
          data: nodes,
          links: links,
          roam: true,
          zoom: 1,
          scaleLimit: {
            min: 0.3,
            max: 3,
          },
          focusNodeAdjacency: true,
          lineStyle: {
            opacity: 0.6,
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 3,
              opacity: 1,
            },
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2,
            },
          },
          blur: {
            itemStyle: {
              opacity: 0.3,
            },
            lineStyle: {
              opacity: 0.1,
            },
          },
        },
      ],
    };
  }, [data, layoutAlgorithm]);

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

  if (!chartOption) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">无法生成图谱</p>
      </div>
    );
  }

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

              <div className="flex items-center gap-2">
                <Label htmlFor="layout" className="text-sm whitespace-nowrap">
                  布局:
                </Label>
                <select
                  id="layout"
                  value={layoutAlgorithm}
                  onChange={(e) => setLayoutAlgorithm(e.target.value)}
                  className="h-8 px-2 border rounded text-sm"
                >
                  <option value="force">力导向</option>
                  <option value="circular">圆形</option>
                  <option value="hierarchical">分层</option>
                  <option value="grid">网格</option>
                </select>
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
            节点: {data?.metadata?.totalNodes || 0} | 边: {data?.metadata?.totalEdges || 0}
          </div>
        </div>
      </Card>

      {/* 图谱可视化 */}
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

