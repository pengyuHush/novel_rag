import React, { useEffect, useState, useRef } from 'react';
import {
  Layout,
  Card,
  Button,
  Space,
  Slider,
  Radio,
  Input,
  List,
  Drawer,
  Tag,
  Typography,
  message,
  Spin,
  Modal,
  FloatButton
} from 'antd';
import {
  ArrowLeftOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
  ExpandOutlined,
  DownloadOutlined,
  FullscreenOutlined,
  TeamOutlined,
  BookOutlined,
  FilterOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { graphAPI, APIError } from '../utils/api';
import { generateMockCharacterGraph } from '../utils/mockData';
import type { CharacterGraph, Character, Relationship } from '../types';
import ForceGraph2D from 'react-force-graph-2d';

const { Header, Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;

interface GraphNode {
  id: string;
  name: string;
  val: number;
  color: string;
  character: Character;
}

interface GraphLink {
  source: string;
  target: string;
  color: string;
  label: string;
  relationship: Relationship;
}

// 关系类型颜色映射
const RELATIONSHIP_COLORS: Record<string, string> = {
  family: '#ff4d4f',
  friend: '#1890ff',
  enemy: '#8c8c8c',
  mentor: '#52c41a',
  other: '#faad14'
};

// 关系类型中文名称
const RELATIONSHIP_LABELS: Record<string, string> = {
  family: '亲属',
  friend: '朋友',
  enemy: '敌对',
  mentor: '师徒',
  other: '其他'
};

const GraphPage: React.FC = () => {
  const { novelId } = useParams<{ novelId: string }>();
  const navigate = useNavigate();
  const { novels } = useStore();
  const graphRef = useRef<any>();

  const [loading, setLoading] = useState(true);
  const [graph, setGraph] = useState<CharacterGraph | null>(null);
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: []
  });
  const [filterMode, setFilterMode] = useState<'all' | 'major' | 'minor'>('all');
  const [minFrequency, setMinFrequency] = useState(0);
  const [searchText, setSearchText] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<GraphLink | null>(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [highlightNodes, setHighlightNodes] = useState<Set<string>>(new Set());
  const [highlightLinks, setHighlightLinks] = useState<Set<string>>(new Set());
  const [isMobile, setIsMobile] = useState(false);
  const [filterDrawerVisible, setFilterDrawerVisible] = useState(false);

  const novel = novels.find(n => n.id === novelId);

  // 检测移动端
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 设置页面标题
  useEffect(() => {
    if (novel) {
      document.title = `${novel.title} - 人物关系图谱 - Novel Rag`;
    } else {
      document.title = '人物关系图谱 - Novel Rag';
    }
  }, [novel]);

  // 加载人物关系图谱
  useEffect(() => {
    if (novelId) {
      loadGraph(novelId);
    }
  }, [novelId]);

  // 根据筛选条件更新图谱数据
  useEffect(() => {
    if (graph) {
      updateGraphData();
    }
  }, [graph, filterMode, minFrequency, searchText]);

  const loadGraph = async (id: string) => {
    try {
      setLoading(true);

      // 尝试从API加载
      let characterGraph = await graphAPI.getGraph(id);

      if (!characterGraph) {
        // 如果没有图谱，生成新的
        message.info('正在分析人物关系，请稍候...');

        const result = await graphAPI.generateGraph(id);
        // 注意：这里可能需要等待一段时间，然后重新获取
        message.success('人物关系图谱生成任务已提交');

        // 重新获取生成的图谱
        await new Promise(resolve => setTimeout(resolve, 2000));
        characterGraph = await graphAPI.getGraph(id);
      }

      setGraph(characterGraph);
      message.success('人物关系图谱加载完成');
    } catch (error) {
      console.error('加载图谱失败:', error);
      if (error instanceof APIError) {
        message.error(`加载图谱失败: ${error.message}`);
      } else {
        message.error('加载图谱失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateGraphData = () => {
    if (!graph) return;

    // 筛选人物
    let filteredCharacters = graph.characters;
    
    if (filterMode !== 'all') {
      filteredCharacters = filteredCharacters.filter(c => c.importance === filterMode);
    }
    
    if (minFrequency > 0) {
      filteredCharacters = filteredCharacters.filter(c => c.frequency >= minFrequency);
    }
    
    if (searchText) {
      filteredCharacters = filteredCharacters.filter(c => 
        c.name.toLowerCase().includes(searchText.toLowerCase())
      );
    }

    const characterIds = new Set(filteredCharacters.map(c => c.id));

    // 构建节点
    const nodes: GraphNode[] = filteredCharacters.map(char => ({
      id: char.id,
      name: char.name,
      val: char.appearances / 10, // 节点大小
      color: char.role === 'protagonist' || char.role === 'antagonist' ? '#1890ff' : '#95de64',
      character: char
    }));

    // 筛选关系（只保留两端都在筛选后的人物中的关系）
    const filteredRelationships = graph.relationships.filter(rel =>
      characterIds.has(rel.source) && characterIds.has(rel.target)
    );

    // 构建边
    const links: GraphLink[] = filteredRelationships.map(rel => ({
      source: rel.source,
      target: rel.target,
      color: RELATIONSHIP_COLORS[rel.type],
      label: RELATIONSHIP_LABELS[rel.type],
      relationship: rel
    }));

    setGraphData({ nodes, links });
  };

  // 点击节点
  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    setSelectedLink(null);
    setDetailDrawerVisible(true);

    // 高亮该节点的所有关系
    const connectedLinks = graphData.links.filter(
      link => link.source === node.id || link.target === node.id
    );
    const connectedNodeIds = new Set<string>();
    connectedLinks.forEach(link => {
      connectedNodeIds.add(typeof link.source === 'object' ? link.source.id : link.source);
      connectedNodeIds.add(typeof link.target === 'object' ? link.target.id : link.target);
    });

    setHighlightNodes(connectedNodeIds);
    setHighlightLinks(new Set(connectedLinks.map(l => `${l.source}-${l.target}`)));
  };

  // 点击关系线
  const handleLinkClick = (link: GraphLink) => {
    setSelectedLink(link);
    setSelectedNode(null);
    setDetailDrawerVisible(true);
  };

  // 导出图谱
  const handleExport = (format: 'json' | 'csv') => {
    if (!graph) return;

    try {
      let content: string;
      let filename: string;
      let mimeType: string;

      if (format === 'json') {
        // 导出为JSON格式
        content = JSON.stringify(graph, null, 2);
        filename = `${novel?.title || 'novel'}_character_graph.json`;
        mimeType = 'application/json';
      } else {
        // 导出为CSV格式（简单列表）
        const csvLines = [
          '角色名,角色类型,出现次数,重要程度',
          ...graph.characters.map(c => 
            `"${c.name}","${c.role}",${c.appearances},${c.importance}`
          ),
          '',
          '角色1,角色2,关系类型,关系强度',
          ...graph.relationships.map(r => {
            const source = graph.characters.find(c => c.id === r.source);
            const target = graph.characters.find(c => c.id === r.target);
            return `"${source?.name}","${target?.name}","${r.type}",${r.strength}`;
          })
        ];
        content = csvLines.join('\n');
        filename = `${novel?.title || 'novel'}_character_graph.csv`;
        mimeType = 'text/csv;charset=utf-8;';
      }

      // 创建下载链接
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      message.success(`导出为${format.toUpperCase()}格式成功`);
      setExportModalVisible(false);
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请重试');
    }
  };

  // 缩放控制
  const handleZoom = (delta: number) => {
    if (graphRef.current) {
      const currentZoom = graphRef.current.zoom();
      graphRef.current.zoom(currentZoom + delta, 400);
    }
  };

  // 适应屏幕
  const handleFitToScreen = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400);
    }
  };

  return (
    <Layout className="page-container" style={{ minHeight: '100vh' }}>
      {/* 顶部工具栏 */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #FFFEF9 0%, #FAF8F3 100%)', 
        padding: isMobile ? '0 16px' : '0 32px', 
        boxShadow: '0 2px 12px rgba(139, 105, 20, 0.08)',
        borderBottom: '1px solid #E8E3D6'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
          <Space size={isMobile ? 'small' : 'middle'}>
            <Button 
              icon={<ArrowLeftOutlined style={{ fontSize: isMobile ? '14px' : '16px' }} />} 
              onClick={() => navigate('/')}
              size={isMobile ? 'middle' : 'large'}
              style={{ fontWeight: 500 }}
            >
              {!isMobile && '返回首页'}
            </Button>
            <TeamOutlined style={{ fontSize: isMobile ? '18px' : '20px', color: '#8B6914' }} />
            <Text 
              strong 
              style={{ 
                fontSize: isMobile ? '14px' : '16px', 
                color: '#3D3D3D',
                maxWidth: isMobile ? '100px' : 'none',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {novel?.title || '小说'}{!isMobile && ' - 人物关系图谱'}
            </Text>
          </Space>
          
          {!isMobile && (
            <Space size="middle">
              <Button 
                icon={<ZoomOutOutlined style={{ fontSize: '16px' }} />} 
                onClick={() => handleZoom(-0.2)}
                size="large"
              >
                缩小
              </Button>
              <Button 
                icon={<ZoomInOutlined style={{ fontSize: '16px' }} />} 
                onClick={() => handleZoom(0.2)}
                size="large"
              >
                放大
              </Button>
              <Button 
                icon={<ExpandOutlined style={{ fontSize: '16px' }} />} 
                onClick={handleFitToScreen}
                size="large"
              >
                适应屏幕
              </Button>
              <Button 
                icon={<DownloadOutlined style={{ fontSize: '16px' }} />} 
                onClick={() => setExportModalVisible(true)}
                type="primary"
                size="large"
              >
                导出
              </Button>
            </Space>
          )}
        </div>
      </Header>

      <Layout>
        {/* 左侧筛选面板 - 仅桌面端显示 */}
        {!isMobile && (
          <Sider 
            width={280} 
            theme="light" 
            style={{ 
              background: 'linear-gradient(180deg, #FFFEF9 0%, #FAF8F3 100%)', 
              padding: '24px',
              borderRight: '1px solid #E8E3D6',
              boxShadow: '2px 0 8px rgba(139, 105, 20, 0.05)'
            }}
          >
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 人物筛选 */}
            <div>
              <Title level={5}>人物筛选</Title>
              <Radio.Group
                value={filterMode}
                onChange={(e) => setFilterMode(e.target.value)}
                style={{ width: '100%' }}
              >
                <Space direction="vertical">
                  <Radio value="all">全部人物</Radio>
                  <Radio value="major">主要人物</Radio>
                  <Radio value="minor">次要人物</Radio>
                </Space>
              </Radio.Group>
            </div>

            {/* 出现次数筛选 */}
            <div>
              <Text>最少出现次数：{minFrequency}</Text>
              <Slider
                min={0}
                max={100}
                value={minFrequency}
                onChange={setMinFrequency}
              />
            </div>

            {/* 搜索人物 */}
            <div>
              <Input.Search
                placeholder="搜索人物名"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
              />
            </div>

            {/* 人物列表 */}
            <div>
              <Title level={5}>人物列表</Title>
              <List
                size="small"
                dataSource={graphData.nodes.sort((a, b) => b.character.appearances - a.character.appearances)}
                style={{ maxHeight: 400, overflow: 'auto' }}
                renderItem={(node) => (
                  <List.Item
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleNodeClick(node)}
                  >
                    <Text>{node.name}</Text>
                    <Tag color={node.character.role === 'protagonist' || node.character.role === 'antagonist' ? 'blue' : 'green'}>
                      {node.character.appearances}次
                    </Tag>
                  </List.Item>
                )}
              />
            </div>

            {/* 图例 */}
            <div>
              <Title level={5}>图例</Title>
              <Space direction="vertical">
                <Text strong>节点大小：出现频率</Text>
                <div>
                  <Tag color="blue">主要人物</Tag>
                  <Tag color="green">次要人物</Tag>
                </div>
                <Text strong>关系类型：</Text>
                {Object.entries(RELATIONSHIP_LABELS).map(([type, label]) => (
                  <div key={type}>
                    <span
                      style={{
                        display: 'inline-block',
                        width: 20,
                        height: 3,
                        backgroundColor: RELATIONSHIP_COLORS[type],
                        marginRight: 8
                      }}
                    />
                    {label}
                  </div>
                ))}
              </Space>
            </div>
          </Space>
        </Sider>
        )}

        {/* 主图谱区域 */}
        <Content style={{ background: '#fff', position: 'relative' }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Spin size="large" tip="正在加载人物关系图谱..." />
            </div>
          ) : (
            <ForceGraph2D
              ref={graphRef}
              graphData={graphData}
              nodeLabel="name"
              nodeColor={(node: any) => node.color}
              nodeVal={(node: any) => node.val}
              linkColor={(link: any) => link.color}
              linkWidth={2}
              linkDirectionalArrowLength={6}
              linkDirectionalArrowRelPos={1}
              onNodeClick={(node: any) => handleNodeClick(node)}
              onLinkClick={(link: any) => handleLinkClick(link)}
              nodeCanvasObject={(node: any, ctx, globalScale) => {
                const label = node.name;
                const fontSize = 12 / globalScale;
                ctx.font = `${fontSize}px Sans-Serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                // 如果节点被高亮
                if (highlightNodes.size > 0) {
                  ctx.globalAlpha = highlightNodes.has(node.id) ? 1 : 0.2;
                }
                
                // 绘制节点
                ctx.fillStyle = node.color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI);
                ctx.fill();
                
                // 绘制文字
                ctx.fillStyle = '#000';
                ctx.fillText(label, node.x, node.y + node.val + fontSize);
                
                ctx.globalAlpha = 1;
              }}
              onBackgroundClick={() => {
                setHighlightNodes(new Set());
                setHighlightLinks(new Set());
              }}
            />
          )}
        </Content>
      </Layout>

      {/* 详情抽屉 */}
      <Drawer
        title={selectedNode ? '人物详情' : '关系详情'}
        placement="right"
        width={400}
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
      >
        {selectedNode && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Title level={4}>{selectedNode.name}</Title>
              <Space>
                <Tag color={selectedNode.character.importance >= 0.7 ? 'blue' : 'green'}>
                  {selectedNode.character.importance >= 0.7 ? '主要人物' : '次要人物'}
                </Tag>
                {selectedNode.character.aliases.length > 0 && (
                  <Tag>别名：{selectedNode.character.aliases.join('、')}</Tag>
                )}
              </Space>
            </div>

            <div>
              <Text strong>基础信息</Text>
              <div style={{ marginTop: 8 }}>
                <p>出现次数：{selectedNode.character.appearances}次</p>
                <p>重要程度：{Math.round(selectedNode.character.importance * 100)}%</p>
                <p>角色类型：{
                  selectedNode.character.role === 'protagonist' ? '主角' :
                  selectedNode.character.role === 'antagonist' ? '反派' :
                  selectedNode.character.role === 'supporting' ? '配角' : '次要角色'
                }</p>
                <p>人物描述：{selectedNode.character.description}</p>
              </div>
            </div>

            <div>
              <Text strong>关系列表</Text>
              <List
                size="small"
                dataSource={graphData.links.filter(
                  l => l.source === selectedNode.id || l.target === selectedNode.id
                )}
                renderItem={(link) => {
                  const otherCharId = link.source === selectedNode.id ? link.target : link.source;
                  const otherChar = graphData.nodes.find(n => n.id === otherCharId);
                  return (
                    <List.Item>
                      <Space>
                        <Text>{otherChar?.name}</Text>
                        <Tag color={link.color}>{link.label}</Tag>
                      </Space>
                    </List.Item>
                  );
                }}
              />
            </div>

            <div>
              <Text strong>首次出场</Text>
              <div style={{ marginTop: 8 }}>
                <p>{selectedNode.character.firstAppearance.chapterTitle}</p>
                <Button 
                  type="link" 
                  onClick={() => navigate(`/reader/${novelId}?chapter=${selectedNode.character.firstAppearance.chapterId}`)}
                >
                  跳转阅读
                </Button>
              </div>
            </div>

            <Button
              type="primary"
              block
              onClick={() => navigate('/', { state: { query: selectedNode.name, selectedNovelIds: [novelId] } })}
            >
              查看所有相关内容
            </Button>
          </Space>
        )}

        {selectedLink && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <Title level={4}>
                {graphData.nodes.find(n => n.id === selectedLink.source)?.name}
                {' ↔ '}
                {graphData.nodes.find(n => n.id === selectedLink.target)?.name}
              </Title>
              <Tag color={selectedLink.color}>{selectedLink.label}关系</Tag>
            </div>

            <div>
              <Text strong>共同出现章节</Text>
              <p>共在{selectedLink.relationship.chapters.length}个章节中同时出现</p>
            </div>

            <div>
              <Text strong>代表性原文片段</Text>
              {selectedLink.relationship.representativeExcerpts.map((excerpt, index) => (
                <Card key={index} size="small" style={{ marginTop: 8 }}>
                  <Paragraph>{excerpt}</Paragraph>
                </Card>
              ))}
            </div>
          </Space>
        )}
      </Drawer>

      {/* 导出Modal */}
      <Modal
        title="导出人物关系图谱"
        open={exportModalVisible}
        onCancel={() => setExportModalVisible(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button block onClick={() => handleExport('json')}>导出为JSON（完整数据）</Button>
          <Button block onClick={() => handleExport('csv')}>导出为CSV（表格格式）</Button>
        </Space>
      </Modal>

      {/* 移动端筛选Drawer */}
      {isMobile && (
        <>
          <Drawer
            title="筛选与控制"
            placement="bottom"
            height="70%"
            onClose={() => setFilterDrawerVisible(false)}
            open={filterDrawerVisible}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 缩放控制 */}
              <div>
                <Title level={5}>图谱控制</Title>
                <Space wrap>
                  <Button icon={<ZoomOutOutlined />} onClick={() => handleZoom(-0.2)}>缩小</Button>
                  <Button icon={<ZoomInOutlined />} onClick={() => handleZoom(0.2)}>放大</Button>
                  <Button icon={<ExpandOutlined />} onClick={handleFitToScreen}>适应</Button>
                  <Button icon={<DownloadOutlined />} onClick={() => {
                    setFilterDrawerVisible(false);
                    setExportModalVisible(true);
                  }}>导出</Button>
                </Space>
              </div>

              {/* 人物筛选 */}
              <div>
                <Title level={5}>人物筛选</Title>
                <Radio.Group
                  value={filterMode}
                  onChange={(e) => setFilterMode(e.target.value)}
                  style={{ width: '100%' }}
                >
                  <Space direction="vertical">
                    <Radio value="all">全部人物</Radio>
                    <Radio value="major">主要人物</Radio>
                    <Radio value="minor">次要人物</Radio>
                  </Space>
                </Radio.Group>
              </div>

              {/* 出场频次筛选 */}
              <div>
                <Title level={5}>出场频次（最小值：{minFrequency}）</Title>
                <Slider
                  min={0}
                  max={100}
                  value={minFrequency}
                  onChange={setMinFrequency}
                />
              </div>

              {/* 搜索人物 */}
              <div>
                <Title level={5}>搜索人物</Title>
                <Input
                  placeholder="输入人物名字..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                />
              </div>
            </Space>
          </Drawer>

          {/* 移动端浮动按钮 */}
          <FloatButton.Group shape="circle" style={{ right: 24, bottom: 24 }}>
            <FloatButton
              icon={<FilterOutlined />}
              onClick={() => setFilterDrawerVisible(true)}
              tooltip="筛选与控制"
              type="primary"
            />
            <FloatButton.BackTop visibilityHeight={200} />
          </FloatButton.Group>
        </>
      )}
    </Layout>
  );
};

export default GraphPage;

