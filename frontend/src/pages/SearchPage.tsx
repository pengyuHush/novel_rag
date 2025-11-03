import React, { useState, useEffect } from 'react';
import {
  Layout,
  Input,
  Button,
  Card,
  Select,
  Tabs,
  List,
  Tag,
  Space,
  Checkbox,
  Collapse,
  Drawer,
  Typography,
  message,
  Empty,
  Spin
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  CopyOutlined,
  ReloadOutlined,
  HistoryOutlined,
  DeleteOutlined,
  ExpandAltOutlined,
  ReadOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { dbUtils } from '../utils/db';
import { generateMockSearchResult, EXAMPLE_QUERIES } from '../utils/mockData';
import type { SearchResult, SearchHistory } from '../types';
import { v4 as uuidv4 } from 'uuid';
import dayjs from 'dayjs';

const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { novels, searchHistory, setSearchHistory, addSearchHistory } = useStore();
  
  const [query, setQuery] = useState('');
  const [selectedNovelIds, setSelectedNovelIds] = useState<string[]>([]);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('semantic');
  const [historyDrawerVisible, setHistoryDrawerVisible] = useState(false);
  const [expandedContexts, setExpandedContexts] = useState<Set<number>>(new Set());

  // 从location state中获取预选的小说
  useEffect(() => {
    const state = location.state as { selectedNovelIds?: string[] };
    if (state?.selectedNovelIds) {
      setSelectedNovelIds(state.selectedNovelIds);
    }
  }, [location]);

  // 加载搜索历史
  useEffect(() => {
    loadSearchHistory();
  }, []);

  const loadSearchHistory = async () => {
    try {
      const history = await dbUtils.getSearchHistory(20);
      setSearchHistory(history);
    } catch (error) {
      console.error('加载搜索历史失败:', error);
    }
  };

  // 执行搜索
  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入问题或关键词');
      return;
    }

    if (selectedNovelIds.length === 0) {
      message.warning('请选择要搜索的小说');
      return;
    }

    try {
      setLoading(true);
      
      // 模拟搜索延迟
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // 生成模拟搜索结果
      const result = generateMockSearchResult(query, selectedNovelIds);
      setSearchResult(result);

      // 保存到搜索历史
      const historyItem: SearchHistory = {
        id: uuidv4(),
        query,
        result,
        timestamp: new Date().toISOString()
      };
      
      await dbUtils.addSearchHistory(historyItem);
      addSearchHistory(historyItem);
      
      message.success('搜索完成');
    } catch (error) {
      console.error('搜索失败:', error);
      message.error('搜索失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 复制文本
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  // 点击示例问题
  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
    if (selectedNovelIds.length > 0) {
      setQuery(exampleQuery);
    }
  };

  // 查看历史记录
  const handleViewHistory = (item: SearchHistory) => {
    setQuery(item.query);
    setSearchResult(item.result);
    setHistoryDrawerVisible(false);
  };

  // 清空历史
  const handleClearHistory = async () => {
    try {
      await dbUtils.clearSearchHistory();
      setSearchHistory([]);
      message.success('历史记录已清空');
    } catch (error) {
      message.error('清空失败');
    }
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
  const highlightText = (text: string, ranges: [number, number][]) => {
    if (!ranges || ranges.length === 0) return text;
    
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    
    ranges.forEach(([start, end], i) => {
      if (start > lastIndex) {
        parts.push(text.substring(lastIndex, start));
      }
      parts.push(
        <span key={i} className="highlight-text">
          {text.substring(start, end)}
        </span>
      );
      lastIndex = end;
    });
    
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }
    
    return parts;
  };

  return (
    <Layout className="page-container" style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <BookOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold' }}>小说RAG分析系统</h1>
          </div>
          <Space size="middle">
            <Button type="link" onClick={() => navigate('/')}>首页</Button>
            <Button type="link" onClick={() => navigate('/search')}>搜索</Button>
            <Button type="link" icon={<HistoryOutlined />} onClick={() => setHistoryDrawerVisible(true)}>
              历史
            </Button>
          </Space>
        </div>
      </Header>

      <Content className="content-wrapper" style={{ maxWidth: '1200px' }}>
        {/* 搜索区域 */}
        <Card style={{ marginBottom: 24 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 搜索框 */}
            <Input.Search
              size="large"
              placeholder="输入问题或关键词，如：XX角色第一次出现在哪里？"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onSearch={handleSearch}
              loading={loading}
              enterButton={
                <Button type="primary" icon={<SearchOutlined />}>
                  搜索
                </Button>
              }
            />

            {/* 搜索选项 */}
            <div>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>搜索范围：</Text>
                  <Checkbox.Group
                    style={{ marginLeft: 16 }}
                    value={selectedNovelIds}
                    onChange={(values) => setSelectedNovelIds(values as string[])}
                  >
                    <Space wrap>
                      {novels.map(novel => (
                        <Checkbox key={novel.id} value={novel.id}>
                          {novel.title}
                        </Checkbox>
                      ))}
                    </Space>
                  </Checkbox.Group>
                  {novels.length === 0 && (
                    <Text type="secondary" style={{ marginLeft: 16 }}>
                      还没有导入小说，请先<Button type="link" onClick={() => navigate('/')}>导入小说</Button>
                    </Text>
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
        {loading ? (
          <Card>
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <Spin size="large" />
              <p style={{ marginTop: 16, color: '#666' }}>
                正在分析问题... → 正在检索相关内容... → 正在生成回答...
              </p>
            </div>
          </Card>
        ) : searchResult ? (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 回答区域 */}
            <Card
              title="AI 回答"
              extra={
                <Space>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    基于 {searchResult.references.length} 处原文生成
                  </Text>
                  <Button size="small" icon={<CopyOutlined />} onClick={() => handleCopy(searchResult.answer)}>
                    复制
                  </Button>
                  <Button size="small" icon={<ReloadOutlined />} onClick={handleSearch}>
                    重新生成
                  </Button>
                </Space>
              }
              style={{ background: '#fafafa' }}
            >
              <Paragraph style={{ fontSize: '16px', lineHeight: 1.8, margin: 0 }}>
                {searchResult.answer}
              </Paragraph>
            </Card>

            {/* 参考段落列表 */}
            <div>
              <Title level={4}>相关原文引用</Title>
              <List
                dataSource={searchResult.references}
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
                        <Tag color="green">相关度: {Math.round(ref.relevance * 100)}%</Tag>
                      </Space>
                    </div>

                    {/* 原文内容 */}
                    <Paragraph style={{ fontSize: '14px', lineHeight: 1.8 }}>
                      {highlightText(ref.excerpt, ref.highlightRanges)}
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
                        onClick={() => handleCopy(ref.excerpt)}
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

              {/* 最近搜索 */}
              {searchHistory.length > 0 && (
                <div style={{ marginTop: 32, maxWidth: 600, margin: '32px auto 0' }}>
                  <Text strong>最近的搜索：</Text>
                  <List
                    size="small"
                    dataSource={searchHistory.slice(0, 5)}
                    renderItem={(item) => (
                      <List.Item
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleViewHistory(item)}
                      >
                        <Text>{item.query}</Text>
                        <Text type="secondary">{dayjs(item.timestamp).fromNow()}</Text>
                      </List.Item>
                    )}
                  />
                </div>
              )}
            </div>
          </Card>
        )}
      </Content>

      {/* 搜索历史侧边栏 */}
      <Drawer
        title="搜索历史"
        placement="right"
        onClose={() => setHistoryDrawerVisible(false)}
        open={historyDrawerVisible}
        extra={
          <Button
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={handleClearHistory}
          >
            清空历史
          </Button>
        }
      >
        {searchHistory.length === 0 ? (
          <Empty description="暂无搜索历史" />
        ) : (
          <List
            dataSource={searchHistory}
            renderItem={(item) => (
              <Card
                size="small"
                style={{ marginBottom: 12, cursor: 'pointer' }}
                onClick={() => handleViewHistory(item)}
                hoverable
              >
                <div>
                  <Text strong>{item.query}</Text>
                </div>
                <div style={{ marginTop: 4 }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {dayjs(item.timestamp).format('YYYY-MM-DD HH:mm')}
                  </Text>
                </div>
              </Card>
            )}
          />
        )}
      </Drawer>
    </Layout>
  );
};

export default SearchPage;

