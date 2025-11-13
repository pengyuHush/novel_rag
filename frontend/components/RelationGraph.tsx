'use client';

/**
 * 角色关系图组件
 * 
 * 使用force-directed layout展示角色关系网络
 * 支持章节范围过滤、节点交互、图表导出
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Slider, Button, Space, Spin, message, Drawer, Typography, Tag, Divider } from 'antd';
import { DownloadOutlined, ReloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { apiClient } from '@/lib/api';

const { Title, Paragraph, Text } = Typography;

interface RelationGraphProps {
  novelId: number;
}

interface NodeDetails {
  id: string;
  name: string;
  type: string;
  importance: number;
  first_chapter: number;
  last_chapter?: number;
  neighbors_count: number;
  relations: Array<{
    direction: string;
    source?: string;
    target?: string;
    type: string;
    strength: number;
  }>;
}

const RelationGraph: React.FC<RelationGraphProps> = ({ novelId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [chapterRange, setChapterRange] = useState<[number, number]>([1, 100]);
  const [maxChapter, setMaxChapter] = useState(100);
  
  // 节点详情抽屉
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedNode, setSelectedNode] = useState<NodeDetails | null>(null);
  const [nodeDetailsLoading, setNodeDetailsLoading] = useState(false);

  // 加载图谱数据
  const loadGraphData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        start_chapter: chapterRange[0],
        end_chapter: chapterRange[1],
        max_nodes: 50,
        min_importance: 0.3,
      };

      const response = await apiClient.get<any>(
        `/graph/relations/${novelId}`,
        params
      );

      // 转换为ReactFlow格式
      const flowNodes: Node[] = response.nodes.map((node: any, index: number) => {
        const angle = (index / response.nodes.length) * 2 * Math.PI;
        const radius = 300;

        return {
          id: node.id,
          type: 'default',
          position: {
            x: Math.cos(angle) * radius + 400,
            y: Math.sin(angle) * radius + 300,
          },
          data: {
            label: node.name,
            importance: node.importance,
            type: node.type,
            is_protagonist: node.is_protagonist,
            is_antagonist: node.is_antagonist,
          },
          style: {
            backgroundColor: getNodeColor(node),
            border: `2px solid ${node.is_protagonist ? '#1890ff' : node.is_antagonist ? '#f5222d' : '#d9d9d9'}`,
            borderRadius: '50%',
            width: 60 + node.importance * 40,
            height: 60 + node.importance * 40,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 12,
            fontWeight: 'bold',
            padding: 10,
          },
        };
      });

      const flowEdges: Edge[] = response.edges.map((edge: any, index: number) => ({
        id: `e-${edge.source}-${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        label: edge.relation_type,
        type: 'smoothstep',
        animated: edge.strength > 0.7,
        style: {
          stroke: getEdgeColor(edge.relation_type),
          strokeWidth: 1 + edge.strength * 2,
        },
        labelStyle: {
          fontSize: 10,
          fill: '#666',
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: getEdgeColor(edge.relation_type),
        },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);

      message.success(`加载成功：${flowNodes.length} 个角色，${flowEdges.length} 个关系`);
    } catch (error: any) {
      message.error(`加载失败：${error.message || '未知错误'}`);
      console.error('Failed to load graph:', error);
    } finally {
      setLoading(false);
    }
  }, [novelId, chapterRange, setNodes, setEdges]);

  // 加载节点详情
  const loadNodeDetails = async (nodeId: string) => {
    setNodeDetailsLoading(true);
    try {
      const response = await apiClient.get<NodeDetails>(
        `/graph/relations/${novelId}/node/${encodeURIComponent(nodeId)}`
      );
      setSelectedNode(response);
    } catch (error: any) {
      message.error(`加载节点详情失败：${error.message}`);
    } finally {
      setNodeDetailsLoading(false);
    }
  };

  // 节点点击事件 (T129: 图表交互)
  const onNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      setDrawerVisible(true);
      loadNodeDetails(node.id);
    },
    [novelId]
  );

  // 导出为PNG (T130: 图表导出)
  const exportGraph = useCallback(() => {
    const svgElement = document.querySelector('.react-flow');
    if (!svgElement) {
      message.error('无法导出：图表未加载');
      return;
    }

    // 使用html2canvas或类似库导出
    message.info('导出功能需要集成html2canvas库');
    // TODO: 实现完整的导出逻辑
  }, []);

  // 初始加载
  useEffect(() => {
    loadGraphData();
  }, [loadGraphData]);

  // 获取节点颜色
  function getNodeColor(node: any): string {
    if (node.is_protagonist) return '#e6f7ff';
    if (node.is_antagonist) return '#fff1f0';
    if (node.type === 'PERSON') return '#f0f5ff';
    if (node.type === 'LOCATION') return '#f6ffed';
    return '#fafafa';
  }

  // 获取边颜色
  function getEdgeColor(relationType: string): string {
    const colorMap: { [key: string]: string } = {
      '师徒': '#1890ff',
      '朋友': '#52c41a',
      '敌对': '#f5222d',
      '情侣': '#eb2f96',
      '亲属': '#722ed1',
      '主仆': '#fa8c16',
    };
    return colorMap[relationType] || '#d9d9d9';
  }

  return (
    <div>
      {/* 控制面板 */}
      <Card className="mb-4" size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 章节范围滑块 (T128) */}
          <div>
            <Text strong>章节范围：</Text>
            <span className="ml-2 text-blue-600">
              第 {chapterRange[0]} - {chapterRange[1]} 章
            </span>
          </div>
          <Slider
            range
            min={1}
            max={maxChapter}
            value={chapterRange}
            onChange={setChapterRange}
            onAfterChange={loadGraphData}
          />

          {/* 操作按钮 */}
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadGraphData}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              icon={<DownloadOutlined />}
              onClick={exportGraph}
            >
              导出PNG
            </Button>
          </Space>
        </Space>
      </Card>

      {/* 图谱可视化 */}
      <Card
        className="relative"
        style={{ height: 600 }}
        loading={loading}
      >
        {nodes.length > 0 ? (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Background />
            <Controls />
            <MiniMap
              nodeColor={(node) => node.style?.backgroundColor || '#f0f0f0'}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
          </ReactFlow>
        ) : (
          <div className="flex items-center justify-center h-full">
            <Spin tip="加载中..." />
          </div>
        )}
      </Card>

      {/* 节点详情抽屉 */}
      <Drawer
        title={
          <Space>
            <InfoCircleOutlined />
            <span>节点详情</span>
          </Space>
        }
        placement="right"
        width={400}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {nodeDetailsLoading ? (
          <div className="text-center py-8">
            <Spin />
          </div>
        ) : selectedNode ? (
          <div>
            <Title level={4}>{selectedNode.name}</Title>
            
            <Divider />
            
            <Paragraph>
              <Text strong>类型：</Text>
              <Tag color="blue">{selectedNode.type}</Tag>
            </Paragraph>
            
            <Paragraph>
              <Text strong>重要性：</Text>
              <span className="ml-2">{(selectedNode.importance * 100).toFixed(0)}%</span>
            </Paragraph>
            
            <Paragraph>
              <Text strong>出现章节：</Text>
              <span className="ml-2">
                第 {selectedNode.first_chapter} 章
                {selectedNode.last_chapter && ` - 第 ${selectedNode.last_chapter} 章`}
              </span>
            </Paragraph>
            
            <Paragraph>
              <Text strong>关系数量：</Text>
              <span className="ml-2">{selectedNode.neighbors_count}</span>
            </Paragraph>
            
            <Divider>关系列表</Divider>
            
            {selectedNode.relations.map((rel, index) => (
              <Card key={index} size="small" className="mb-2">
                <Text type="secondary">
                  {rel.direction === 'outgoing' ? '→' : '←'}
                  {' '}
                  {rel.direction === 'outgoing' ? rel.target : rel.source}
                </Text>
                <div className="mt-1">
                  <Tag color="green">{rel.type}</Tag>
                  <span className="text-xs text-gray-500">
                    强度: {(rel.strength * 100).toFixed(0)}%
                  </span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Paragraph type="secondary">暂无数据</Paragraph>
        )}
      </Drawer>
    </div>
  );
};

export default RelationGraph;

