import React, { useState, useEffect } from 'react';
import {
  Layout,
  Input,
  Button,
  Card,
  Tabs,
  List,
  Tag,
  Space,
  Checkbox,
  Drawer,
  Typography,
  message,
  Empty,
  Spin,
  Statistic,
  Row,
  Col,
  Popconfirm,
  Divider,
  FloatButton,
  Modal
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  CopyOutlined,
  ReloadOutlined,
  DeleteOutlined,
  ExpandAltOutlined,
  ReadOutlined,
  PlusOutlined,
  TeamOutlined,
  EditOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FileTextOutlined,
  BookFilled,
  CloudUploadOutlined,
  QuestionCircleOutlined,
  AppstoreOutlined,
  ThunderboltOutlined,
  ApiOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { novelAPI, searchAPI, apiUtils, APIError } from '../utils/api';
import { EXAMPLE_QUERIES } from '../utils/mockData';
import ImportNovelModal from '../components/ImportNovelModal';
import EditNovelModal from '../components/EditNovelModal';
import type { SearchResult, Novel } from '../types';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// 配置 dayjs
dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Header, Content, Sider } = Layout;
const { Title, Paragraph, Text } = Typography;

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const {
    novels,
    setNovels,
    removeNovel,
    recentQueries,
    addRecentQuery,
    currentSearchResult,
    setCurrentSearchResult,
    loading,
    setLoading,
    searching,
    setSearching,
    storageInfo,
    setStorageInfo
  } = useStore();
  
  const [query, setQuery] = useState('');
  const [selectedNovelIds, setSelectedNovelIds] = useState<string[]>([]);
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('semantic');
  const [expandedContexts, setExpandedContexts] = useState<Set<number>>(new Set());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);
  const [novelsLoading, setNovelsLoading] = useState(true);
  const [autoSearch, setAutoSearch] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [novelDrawerVisible, setNovelDrawerVisible] = useState(false);
  const [helpModalVisible, setHelpModalVisible] = useState(false);

  // 检测移动端
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 设置页面标题
  useEffect(() => {
    document.title = '搜索与问答 - Novel Rag';
  }, []);

  // 加载小说列表
  const loadNovels = async () => {
    try {
      setLoading(true);
      setNovelsLoading(true);
      console.log('🔄 开始加载小说列表...');
      
      const allNovels = await novelAPI.getAllNovels();
      console.log('✅ 加载小说成功，共', allNovels.length, '部小说');
      setNovels(allNovels);

      const info = await apiUtils.getStorageInfo();
      console.log('📊 存储信息:', info);
      setStorageInfo(info);
    } catch (error) {
      console.error('❌ 加载小说列表失败:', error);
      if (error instanceof APIError) {
        message.error(`加载小说列表失败: ${error.message}`);
      } else {
        message.error('加载小说列表失败');
      }
    } finally {
      setLoading(false);
      setNovelsLoading(false);
      console.log('✅ 小说列表加载完成');
    }
  };

  // 执行搜索
  const handleSearch = React.useCallback(async () => {
    if (!query.trim()) {
      message.warning('请输入问题或关键词');
      return;
    }

    if (selectedNovelIds.length === 0) {
      message.warning('请在左侧选择要搜索的小说');
      return;
    }

    try {
      setSearching(true);

      // 调用API进行搜索（使用POST + JSON Body）
      const result = await searchAPI.search({
        query,
        novelIds: selectedNovelIds,
        searchMode,
        topK: 5,
        includeReferences: true,
        saveHistory: true
      });

      setCurrentSearchResult(result);

      // 添加到最近查询
      addRecentQuery(query);

      message.success(`搜索完成，找到${result.references.length}处相关内容`);
    } catch (error) {
      console.error('搜索失败:', error);
      if (error instanceof APIError) {
        message.error(`搜索失败: ${error.message}`);
      } else {
        message.error('搜索失败，请重试');
      }
    } finally {
      setSearching(false);
    }
  }, [query, selectedNovelIds, searchMode, setCurrentSearchResult, addRecentQuery]);

  // 从location state中获取预选的小说和查询
  useEffect(() => {
    const state = location.state as { selectedNovelIds?: string[]; query?: string };
    if (state?.selectedNovelIds) {
      setSelectedNovelIds(state.selectedNovelIds);
    }
    if (state?.query) {
      setQuery(state.query);
      // 如果有预设查询且有选中的小说，标记需要自动搜索
      if (state.selectedNovelIds && state.selectedNovelIds.length > 0) {
        setAutoSearch(true);
      }
    }
  }, [location]);

  // 自动执行搜索
  useEffect(() => {
    if (autoSearch && query && selectedNovelIds.length > 0) {
      const timer = setTimeout(() => {
        handleSearch();
        setAutoSearch(false);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [autoSearch, query, selectedNovelIds, handleSearch]);

  // 加载小说列表
  useEffect(() => {
    loadNovels();
  }, []);

  // 删除小说
  const handleDelete = async (id: string, title: string) => {
    try {
      await novelAPI.deleteNovel(id);
      removeNovel(id);

      // 从选中列表中移除
      setSelectedNovelIds(prev => prev.filter(novelId => novelId !== id));

      message.success(`已删除《${title}》`);

      // 更新存储信息
      const info = await apiUtils.getStorageInfo();
      setStorageInfo(info);
    } catch (error) {
      console.error('删除失败:', error);
      if (error instanceof APIError) {
        message.error(`删除失败: ${error.message}`);
      } else {
        message.error('删除失败');
      }
    }
  };

  // 编辑小说
  const handleEdit = (novel: Novel) => {
    setSelectedNovel(novel);
    setEditModalVisible(true);
  };

  // 复制文本
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  // 点击示例问题
  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  
  // 跳转到章节阅读
  const handleJumpToReader = (novelId: string, chapterId: string, paragraphIndex: number) => {
    navigate(`/reader/${novelId}?chapter=${chapterId}&paragraph=${paragraphIndex}`);
  };

  // 展开/收起上下文
  const toggleContext = (index: number) => {
    const newSet = new Set(expandedContexts);
    if (newSet.has(index)) {
      newSet.delete(index);
    } else {
      newSet.add(index);
    }
    setExpandedContexts(newSet);
  };

  // 高亮关键词
  // 高亮文本函数（基于highlightText字段）
  const highlightContent = (content: string, highlightText: string) => {
    if (!highlightText || !content.includes(highlightText)) {
      return content;
    }
    
    const parts = content.split(highlightText);
    return (
      <>
        {parts.map((part, i) => (
          <React.Fragment key={i}>
            {part}
            {i < parts.length - 1 && (
              <span className="highlight-text">{highlightText}</span>
            )}
          </React.Fragment>
        ))}
      </>
    );
  };

  // 切换小说选择
  const toggleNovelSelection = (novelId: string) => {
    setSelectedNovelIds(prev => {
      if (prev.includes(novelId)) {
        return prev.filter(id => id !== novelId);
      } else {
        return [...prev, novelId];
      }
    });
  };

  // 全选/全不选
  const handleSelectAll = () => {
    if (selectedNovelIds.length === novels.length) {
      setSelectedNovelIds([]);
    } else {
      setSelectedNovelIds(novels.map(n => n.id));
    }
  };

  return (
    <Layout className="page-container" style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #FFFEF9 0%, #FAF8F3 100%)', 
        padding: isMobile ? '0 16px' : '0 32px', 
        boxShadow: '0 2px 12px rgba(139, 105, 20, 0.08)',
        borderBottom: '1px solid #E8E3D6'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? '8px' : '16px' }}>
            {!isMobile && (
              <Button
                type="text"
                size="large"
                icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                style={{ 
                  color: '#8B6914',
                  fontSize: '18px'
                }}
              />
            )}
            <BookFilled style={{ fontSize: isMobile ? '24px' : '28px', color: '#8B6914' }} />
            <h1 style={{ 
              margin: 0, 
              fontSize: isMobile ? '16px' : '22px', 
              fontWeight: 600,
              color: '#3D3D3D',
              letterSpacing: '0.5px'
            }}>
              {isMobile ? '小说RAG' : 'Novel Rag'}
            </h1>
          </div>
          <Space size={isMobile ? 'small' : 'large'}>
                        {!isMobile && (
              <Button 
                type="text"
                size="large"
                icon={<QuestionCircleOutlined style={{ fontSize: '16px' }} />}
                onClick={() => setHelpModalVisible(true)}
                style={{ 
                  color: '#8B7355',
                  fontWeight: 500
                }}
              >
                帮助
              </Button>
            )}
          </Space>
        </div>
      </Header>

      <Layout>
        {/* 左侧小说管理侧边栏 - 仅桌面端显示 */}
        {!isMobile && !sidebarCollapsed && (
          <Sider
            width={300}
            theme="light"
            style={{
              background: 'linear-gradient(180deg, #FFFEF9 0%, #FAF8F3 100%)',
              borderRight: '1px solid #E8E3D6',
              overflow: 'auto',
              height: 'calc(100vh - 64px)',
              position: 'sticky',
              top: 64,
              boxShadow: '2px 0 8px rgba(139, 105, 20, 0.05)'
            }}
          >
            <div style={{ padding: '20px 16px' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                {/* 统计信息 */}
                <Card 
                  size="small" 
                  style={{ 
                    background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF4D6 100%)',
                    border: '1px solid #E8DCC0',
                    borderRadius: 12
                  }}
                >
                  <Row gutter={[8, 8]}>
                    <Col span={24}>
                      <Statistic
                        title={<span style={{ color: '#8B7355', fontWeight: 500 }}>已导入小说</span>}
                        value={storageInfo.novelCount}
                        suffix="部"
                        valueStyle={{ fontSize: '24px', color: '#8B6914', fontWeight: 600 }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title={<span style={{ color: '#8B7355', fontSize: '12px' }}>总字数</span>}
                        value={Math.round(storageInfo.totalWords / 10000)}
                        suffix="万字"
                        valueStyle={{ fontSize: '16px', color: '#8B6914' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title={<span style={{ color: '#8B7355', fontSize: '12px' }}>存储</span>}
                        value={storageInfo.formattedSize}
                        valueStyle={{ fontSize: '16px', color: '#8B6914' }}
                      />
                    </Col>
                  </Row>
                  <Button
                    type="primary"
                    block
                    size="large"
                    icon={<CloudUploadOutlined style={{ fontSize: '16px' }} />}
                    onClick={() => setImportModalVisible(true)}
                    style={{ 
                      marginTop: 16,
                      height: 44,
                      fontWeight: 500,
                      fontSize: '15px',
                      boxShadow: '0 2px 8px rgba(139, 105, 20, 0.2)'
                    }}
                  >
                    导入新小说
                  </Button>
                </Card>

                <Divider style={{ margin: '8px 0' }} />

                {/* 小说列表 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <Text strong>小说列表</Text>
                    <Button
                      type="link"
                      size="small"
                      onClick={handleSelectAll}
                    >
                      {selectedNovelIds.length === novels.length ? '取消全选' : '全选'}
                    </Button>
                  </div>

                  {novelsLoading ? (
                    <div style={{ textAlign: 'center', padding: '20px 0' }}>
                      <Spin />
                    </div>
                  ) : novels.length === 0 ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description="还没有导入小说"
                      style={{ padding: '20px 0' }}
                    >
                      <Button type="link" onClick={() => setImportModalVisible(true)}>
                        立即导入
                      </Button>
                    </Empty>
                  ) : (
                    <List
                      size="small"
                      dataSource={novels}
                      renderItem={(novel) => (
                        <List.Item
                          style={{
                            padding: '8px 12px',
                            cursor: 'pointer',
                            background: selectedNovelIds.includes(novel.id) ? '#e6f7ff' : 'transparent',
                            borderRadius: 4,
                            marginBottom: 4
                          }}
                          onClick={() => toggleNovelSelection(novel.id)}
                        >
                          <List.Item.Meta
                            avatar={
                              <Checkbox
                                checked={selectedNovelIds.includes(novel.id)}
                                onChange={(e) => {
                                  e.stopPropagation();
                                  toggleNovelSelection(novel.id);
                                }}
                                onClick={(e) => e.stopPropagation()}
                              />
                            }
                            title={
                              <div>
                                <Text strong style={{ fontSize: '14px' }}>{novel.title}</Text>
                              </div>
                            }
                            description={
                              <Space direction="vertical" size={0} style={{ width: '100%' }}>
                                {novel.author && (
                                  <Text type="secondary" style={{ fontSize: '12px' }}>
                                    {novel.author}
                                  </Text>
                                )}
                                <Space size={4} wrap>
                                  <Tag color="blue" style={{ fontSize: '11px' }}>
                                    {apiUtils.formatWordCount(novel.wordCount)}
                                  </Tag>
                                  <Tag color="green" style={{ fontSize: '11px' }}>
                                    {novel.chapterCount}章
                                  </Tag>
                                </Space>
                              </Space>
                            }
                          />
                          <Space direction="vertical" size={4} style={{ alignItems: 'flex-end' }}>
                            <Button
                              type="text"
                              size="small"
                              icon={<TeamOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/graph/${novel.id}`);
                              }}
                              style={{ 
                                width: '70px',
                                justifyContent: 'flex-start',
                                padding: '2px 8px'
                              }}
                            >
                              关系图
                            </Button>
                            <Button
                              type="text"
                              size="small"
                              icon={<ReadOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/reader/${novel.id}`);
                              }}
                              style={{ 
                                width: '70px',
                                justifyContent: 'flex-start',
                                padding: '2px 8px'
                              }}
                            >
                              阅读
                            </Button>
                            <Button
                              type="text"
                              size="small"
                              icon={<EditOutlined />}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEdit(novel);
                              }}
                              style={{ 
                                width: '70px',
                                justifyContent: 'flex-start',
                                padding: '2px 8px'
                              }}
                            >
                              编辑
                            </Button>
                            <Popconfirm
                              title="确定删除？"
                              description={`确定要删除《${novel.title}》吗？`}
                              onConfirm={(e) => {
                                e?.stopPropagation();
                                handleDelete(novel.id, novel.title);
                              }}
                              okText="确定"
                              cancelText="取消"
                              okButtonProps={{ danger: true }}
                            >
                              <Button
                                type="text"
                                size="small"
                                danger
                                icon={<DeleteOutlined />}
                                onClick={(e) => e.stopPropagation()}
                                style={{ 
                                  width: '70px',
                                  justifyContent: 'flex-start',
                                  padding: '2px 8px'
                                }}
                              >
                                删除
                              </Button>
                            </Popconfirm>
                          </Space>
                        </List.Item>
                      )}
                    />
                  )}
                </div>
              </Space>
            </div>
          </Sider>
        )}

        {/* 主搜索区域 */}
        <Content className="content-wrapper" style={{ maxWidth: sidebarCollapsed ? '1200px' : '900px' }}>
          {/* 搜索区域 */}
          <Card 
            style={{ 
              marginBottom: 24,
              borderRadius: 16,
              boxShadow: '0 4px 16px rgba(139, 105, 20, 0.08)',
              border: '1px solid #E8E3D6'
            }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 搜索框 */}
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  size="large"
                  placeholder="输入问题或关键词，如：XX角色第一次出现在哪里？"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onPressEnter={handleSearch}
                  style={{ flex: 1 }}
                />
                <Button 
                  type="primary" 
                  size="large"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                >
                  搜索
                </Button>
              </Space.Compact>

              {/* 搜索选项 */}
              <div>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>已选择：</Text>
                    <Text style={{ marginLeft: 8 }}>
                      {selectedNovelIds.length > 0 
                        ? `${selectedNovelIds.length}部小说`
                        : '未选择小说'}
                    </Text>
                    {selectedNovelIds.length === 0 && (
                      <Button
                        type="link"
                        size="small"
                        onClick={() => setSidebarCollapsed(false)}
                      >
                        点击左侧选择小说
                      </Button>
                    )}
                  </div>

                  <div>
                    <Text strong>搜索模式：</Text>
                    <Tabs
                      size="small"
                      activeKey={searchMode}
                      onChange={(key) => setSearchMode(key as typeof searchMode)}
                      style={{ marginLeft: 16, display: 'inline-block' }}
                      items={[
                        { key: 'semantic', label: '语义问答' },
                        { key: 'keyword', label: '关键词搜索' }
                      ]}
                    />
                  </div>
                </Space>
              </div>
            </Space>
          </Card>

          {/* 搜索结果或默认状态 */}
          {loading || searching ? (
            <Card>
              <div style={{ textAlign: 'center', padding: '60px 0' }}>
                <Spin size="large" />
                <p style={{ marginTop: 16, color: '#666' }}>
                  正在分析问题... → 正在检索相关内容... → 正在生成回答...
                </p>
              </div>
            </Card>
          ) : currentSearchResult ? (
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* Token消耗统计卡片 - 新增 */}
              {currentSearchResult.tokenStats && (
                <Card
                  title={
                    <span>
                      <ThunderboltOutlined style={{ color: '#1890ff', marginRight: 8 }} />
                      Token消耗统计
                    </span>
                  }
                  size="small"
                  style={{ 
                    background: 'linear-gradient(135deg, #E6F7FF 0%, #D6F0FF 100%)',
                    border: '1px solid #91CAFF',
                    borderRadius: 12
                  }}
                >
                  <Row gutter={16}>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="总Token"
                        value={currentSearchResult.tokenStats.totalTokens}
                        prefix={<ApiOutlined />}
                        valueStyle={{ color: '#1890ff', fontSize: 18 }}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="Embedding"
                        value={currentSearchResult.tokenStats.embeddingTokens}
                        valueStyle={{ color: '#52c41a', fontSize: 18 }}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="Chat"
                        value={currentSearchResult.tokenStats.chatTokens}
                        valueStyle={{ color: '#faad14', fontSize: 18 }}
                      />
                    </Col>
                    <Col xs={12} sm={6}>
                      <Statistic
                        title="预估费用"
                        value={currentSearchResult.tokenStats.estimatedCost}
                        precision={4}
                        prefix="¥"
                        valueStyle={{ color: '#f5222d', fontSize: 18 }}
                      />
                    </Col>
                  </Row>
                  <Divider style={{ margin: '12px 0' }} />
                  <Space>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      <ApiOutlined /> API调用: {currentSearchResult.tokenStats.apiCalls}次
                    </Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      <ClockCircleOutlined /> 耗时: {currentSearchResult.elapsed?.toFixed(2)}秒
                    </Text>
                  </Space>
                </Card>
              )}

              {/* 回答区域 */}
              <Card
                title="AI 回答"
                extra={
                  <Space>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      基于 {currentSearchResult.references.length} 处原文生成
                    </Text>
                    <Button size="small" icon={<CopyOutlined />} onClick={() => handleCopy(currentSearchResult.answer)}>
                      复制
                    </Button>
                    <Button size="small" icon={<ReloadOutlined />} onClick={handleSearch}>
                      重新生成
                    </Button>
                  </Space>
                }
                style={{ background: '#fafafa' }}
              >
                <div className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {currentSearchResult.answer}
                  </ReactMarkdown>
                </div>
              </Card>

              {/* 参考段落列表 */}
              <div>
                <Title level={4}>相关原文引用</Title>
                <List
                  dataSource={currentSearchResult.references}
                  renderItem={(ref, index) => (
                    <Card
                      key={index}
                      style={{ marginBottom: 16 }}
                      className="hover-card"
                    >
                      {/* 卡片头部 */}
                      <div style={{ marginBottom: 12 }}>
                        <Space>
                          <Tag color="blue">{ref.novelTitle}</Tag>
                          <Text strong>{ref.chapterTitle}</Text>
                          <Text type="secondary">第{ref.paragraphIndex}段</Text>
                          <Tag color="green">相关度: {Math.round(ref.relevanceScore * 100)}%</Tag>
                        </Space>
                      </div>

                      {/* 原文内容 */}
                      <Paragraph style={{ fontSize: '14px', lineHeight: 1.8 }}>
                        {highlightContent(ref.content, ref.highlightText)}
                      </Paragraph>

                      {/* 操作按钮 */}
                      <Space>
                        <Button
                          size="small"
                          icon={<ExpandAltOutlined />}
                          onClick={() => toggleContext(index)}
                        >
                          {expandedContexts.has(index) ? '收起' : '展开'}上下文
                        </Button>
                        <Button
                          size="small"
                          icon={<ReadOutlined />}
                          onClick={() => handleJumpToReader(ref.novelId, ref.chapterId, ref.paragraphIndex)}
                        >
                          跳转阅读
                        </Button>
                        <Button
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() => handleCopy(ref.content)}
                        >
                          复制原文
                        </Button>
                      </Space>

                      {/* 展开的上下文 */}
                      {expandedContexts.has(index) && (
                        <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                          <Text type="secondary">
                            [上文] 这里是展开的上下文内容，实际应用中会显示该段落前后的文字...
                          </Text>
                        </div>
                      )}
                    </Card>
                  )}
                />
              </div>
            </Space>
          ) : (
            <Card>
              <div className="empty-state">
                <SearchOutlined className="empty-state-icon" />
                <p className="empty-state-text">开始搜索，探索小说世界</p>
                
                {/* 示例问题 */}
                <div style={{ marginTop: 32 }}>
                  <Text strong>试试这些问题：</Text>
                  <div style={{ marginTop: 16 }}>
                    <Space wrap>
                      {EXAMPLE_QUERIES.map((example, index) => (
                        <Button
                          key={index}
                          onClick={() => handleExampleClick(example)}
                        >
                          {example}
                        </Button>
                      ))}
                    </Space>
                  </div>
                </div>

                {/* 最近查询 */}
                {recentQueries.length > 0 && (
                  <div style={{ marginTop: 32, maxWidth: 600, margin: '32px auto 0' }}>
                    <Text strong>最近的查询：</Text>
                    <List
                      size="small"
                      dataSource={recentQueries.slice(0, 5)}
                      renderItem={(query) => (
                        <List.Item
                          style={{ cursor: 'pointer' }}
                          onClick={() => {
                            setQuery(query);
                          }}
                        >
                          <Text>{query}</Text>
                        </List.Item>
                      )}
                    />
                  </div>
                )}
              </div>
            </Card>
          )}
        </Content>
      </Layout>

      {/* 移动端小说管理Drawer */}
      {isMobile && (
        <>
          <Drawer
            title={
              <Space>
                <BookFilled style={{ color: '#8B6914' }} />
                <span>小说管理</span>
              </Space>
            }
            placement="bottom"
            height="75%"
            onClose={() => setNovelDrawerVisible(false)}
            open={novelDrawerVisible}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {/* 统计信息 */}
              <Card 
                size="small" 
                style={{ 
                  background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF4D6 100%)',
                  border: '1px solid #E8DCC0',
                  borderRadius: 12
                }}
              >
                <Row gutter={[8, 8]}>
                  <Col span={24}>
                    <Statistic
                      title={<span style={{ color: '#8B7355', fontWeight: 500 }}>已导入小说</span>}
                      value={storageInfo.novelCount}
                      suffix="部"
                      valueStyle={{ fontSize: '24px', color: '#8B6914', fontWeight: 600 }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title={<span style={{ color: '#8B7355', fontSize: '12px' }}>总字数</span>}
                      value={Math.round(storageInfo.totalWords / 10000)}
                      suffix="万字"
                      valueStyle={{ fontSize: '16px', color: '#8B6914' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title={<span style={{ color: '#8B7355', fontSize: '12px' }}>存储</span>}
                      value={storageInfo.formattedSize}
                      valueStyle={{ fontSize: '16px', color: '#8B6914' }}
                    />
                  </Col>
                </Row>
                <Button
                  type="primary"
                  block
                  size="large"
                  icon={<CloudUploadOutlined style={{ fontSize: '16px' }} />}
                  onClick={() => {
                    setNovelDrawerVisible(false);
                    setImportModalVisible(true);
                  }}
                  style={{ 
                    marginTop: 16,
                    height: 44,
                    fontWeight: 500,
                    fontSize: '15px',
                    boxShadow: '0 2px 8px rgba(139, 105, 20, 0.2)'
                  }}
                >
                  导入新小说
                </Button>
              </Card>

              <Divider style={{ margin: '8px 0' }} />

              {/* 小说列表 */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <Text strong>小说列表</Text>
                  <Button
                    type="link"
                    size="small"
                    onClick={handleSelectAll}
                  >
                    {selectedNovelIds.length === novels.length ? '取消全选' : '全选'}
                  </Button>
                </div>

                {novelsLoading ? (
                  <div style={{ textAlign: 'center', padding: '20px 0' }}>
                    <Spin />
                  </div>
                ) : novels.length === 0 ? (
                  <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description="还没有导入小说"
                    style={{ padding: '20px 0' }}
                  >
                    <Button type="link" onClick={() => {
                      setNovelDrawerVisible(false);
                      setImportModalVisible(true);
                    }}>
                      立即导入
                    </Button>
                  </Empty>
                ) : (
                  <List
                    size="small"
                    dataSource={novels}
                    renderItem={(novel) => (
                      <List.Item
                        style={{
                          padding: '12px',
                          cursor: 'pointer',
                          background: selectedNovelIds.includes(novel.id) ? '#e6f7ff' : 'transparent',
                          borderRadius: 8,
                          marginBottom: 8,
                          border: '1px solid #E8E3D6'
                        }}
                        onClick={() => toggleNovelSelection(novel.id)}
                      >
                        <List.Item.Meta
                          avatar={
                            <Checkbox
                              checked={selectedNovelIds.includes(novel.id)}
                              onChange={(e) => {
                                e.stopPropagation();
                                toggleNovelSelection(novel.id);
                              }}
                              onClick={(e) => e.stopPropagation()}
                            />
                          }
                          title={
                            <div>
                              <Text strong style={{ fontSize: '15px' }}>{novel.title}</Text>
                            </div>
                          }
                          description={
                            <Space direction="vertical" size={4} style={{ width: '100%', marginTop: 4 }}>
                              {novel.author && (
                                <Text type="secondary" style={{ fontSize: '13px' }}>
                                  {novel.author}
                                </Text>
                              )}
                              <Space size={4} wrap>
                                <Tag color="blue" style={{ fontSize: '12px' }}>
                                  {apiUtils.formatWordCount(novel.wordCount)}
                                </Tag>
                                <Tag color="green" style={{ fontSize: '12px' }}>
                                  {novel.chapterCount}章
                                </Tag>
                              </Space>
                              <Space size={4} wrap style={{ marginTop: 4 }}>
                                <Button
                                  type="link"
                                  size="small"
                                  icon={<TeamOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setNovelDrawerVisible(false);
                                    navigate(`/graph/${novel.id}`);
                                  }}
                                  style={{ padding: '0 4px', height: 'auto' }}
                                >
                                  关系图
                                </Button>
                                <Button
                                  type="link"
                                  size="small"
                                  icon={<ReadOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setNovelDrawerVisible(false);
                                    navigate(`/reader/${novel.id}`);
                                  }}
                                  style={{ padding: '0 4px', height: 'auto' }}
                                >
                                  阅读
                                </Button>
                                <Button
                                  type="link"
                                  size="small"
                                  icon={<EditOutlined />}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setNovelDrawerVisible(false);
                                    handleEdit(novel);
                                  }}
                                  style={{ padding: '0 4px', height: 'auto' }}
                                >
                                  编辑
                                </Button>
                                <Popconfirm
                                  title="确定删除？"
                                  description={`确定要删除《${novel.title}》吗？`}
                                  onConfirm={(e) => {
                                    e?.stopPropagation();
                                    setNovelDrawerVisible(false);
                                    handleDelete(novel.id, novel.title);
                                  }}
                                  okText="确定"
                                  cancelText="取消"
                                  okButtonProps={{ danger: true }}
                                >
                                  <Button
                                    type="link"
                                    size="small"
                                    danger
                                    icon={<DeleteOutlined />}
                                    onClick={(e) => e.stopPropagation()}
                                    style={{ padding: '0 4px', height: 'auto' }}
                                  >
                                    删除
                                  </Button>
                                </Popconfirm>
                              </Space>
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                )}
              </div>
            </Space>
          </Drawer>

          {/* 移动端浮动按钮 */}
          <FloatButton
            icon={<AppstoreOutlined />}
            type="primary"
            style={{ 
              right: 24,
              bottom: 24,
              width: 56,
              height: 56
            }}
            onClick={() => setNovelDrawerVisible(true)}
            tooltip="小说管理"
          />
        </>
      )}

      
      {/* 导入小说Modal */}
      <ImportNovelModal
        visible={importModalVisible}
        onClose={() => setImportModalVisible(false)}
        onSuccess={loadNovels}
      />

      {/* 编辑小说Modal */}
      {selectedNovel && (
        <EditNovelModal
          visible={editModalVisible}
          novel={selectedNovel}
          onClose={() => {
            setEditModalVisible(false);
            setSelectedNovel(null);
          }}
          onSuccess={loadNovels}
        />
      )}

      {/* 帮助Modal */}
      <Modal
        title={<span><QuestionCircleOutlined /> 使用帮助</span>}
        open={helpModalVisible}
        onCancel={() => setHelpModalVisible(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setHelpModalVisible(false)}>
            知道了
          </Button>
        ]}
        width={700}
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto', padding: '8px 0' }}>
          <Title level={4}>📚 小说管理</Title>
          <Paragraph>
            <ul>
              <li><strong>导入小说</strong>：点击"导入小说"按钮，上传 TXT 格式的中文小说文件</li>
              <li><strong>选择小说</strong>：勾选左侧列表中的小说，可以选择多部进行搜索</li>
              <li><strong>编辑信息</strong>：点击"编辑"按钮修改小说的标题、作者、简介等信息</li>
              <li><strong>删除小说</strong>：点击"删除"按钮移除不需要的小说</li>
            </ul>
          </Paragraph>

          <Divider />

          <Title level={4}>🔍 智能搜索</Title>
          <Paragraph>
            <ul>
              <li><strong>提问</strong>：在搜索框输入你的问题，系统会基于选中的小说内容生成答案</li>
              <li><strong>示例问题</strong>：
                <ul>
                  <li>"张三是谁？"</li>
                  <li>"总结第5章的内容"</li>
                  <li>"张三和李四的关系是什么？"</li>
                </ul>
              </li>
              <li><strong>查看引用</strong>：答案下方会显示相关段落的原文引用和位置</li>
              <li><strong>跳转阅读</strong>：点击引用可以直接跳转到对应章节阅读</li>
            </ul>
          </Paragraph>

          <Divider />

          <Title level={4}>👥 人物关系图谱</Title>
          <Paragraph>
            <ul>
              <li><strong>查看图谱</strong>：点击小说列表中的"关系图"按钮</li>
              <li><strong>生成图谱</strong>：首次使用需要点击"生成关系图"按钮</li>
              <li><strong>交互操作</strong>：
                <ul>
                  <li>拖拽节点调整位置</li>
                  <li>点击节点查看人物详情</li>
                  <li>筛选关系类型（朋友、家人、师徒等）</li>
                  <li>搜索特定人物</li>
                </ul>
              </li>
            </ul>
          </Paragraph>

          <Divider />

          <Title level={4}>📖 章节阅读</Title>
          <Paragraph>
            <ul>
              <li><strong>打开阅读器</strong>：点击小说列表中的"阅读"按钮</li>
              <li><strong>章节导航</strong>：左侧显示完整章节列表，点击切换章节</li>
              <li><strong>阅读设置</strong>：调整字体大小、行距、主题等</li>
              <li><strong>进度保存</strong>：系统会自动记录你的阅读进度</li>
            </ul>
          </Paragraph>

          <Divider />

          <Title level={4}>💡 使用技巧</Title>
          <Paragraph>
            <ul>
              <li>支持多部小说联合搜索，获取跨作品的分析结果</li>
              <li>搜索历史会自动保存，方便回顾之前的提问</li>
              <li>在移动端使用时，点击浮动按钮访问侧边栏功能</li>
              <li>目前支持 UTF-8、GBK、GB2312 编码的 TXT 文件</li>
            </ul>
          </Paragraph>

          <Divider />

          <Title level={4}>⚙️ 当前模式</Title>
          <Paragraph>
            <Tag color="blue" style={{ fontSize: '14px' }}>
              {import.meta.env.VITE_USE_MOCK_API === 'true' ? '🎭 Mock 演示模式' : '🌐 在线模式'}
            </Tag>
            {import.meta.env.VITE_USE_MOCK_API === 'true' && (
              <div style={{ marginTop: 8, color: '#666' }}>
                当前使用模拟数据进行功能演示，刷新页面后数据会重置。
              </div>
            )}
          </Paragraph>
        </div>
      </Modal>
    </Layout>
  );
};

export default SearchPage;
