import React, { useEffect, useState } from 'react';
import {
  Layout,
  Menu,
  Typography,
  Button,
  Space,
  Input,
  Drawer,
  Slider,
  Radio,
  Switch,
  Progress,
  message,
  FloatButton
} from 'antd';
import {
  ArrowLeftOutlined,
  MenuOutlined,
  SettingOutlined,
  FullscreenOutlined,
  LeftOutlined,
  RightOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { dbUtils } from '../utils/db';
import type { Novel, Chapter } from '../types';

const { Header, Content, Sider } = Layout;
const { Title, Paragraph, Text } = Typography;

interface ReadingSettings {
  fontSize: number;
  fontFamily: string;
  lineHeight: number;
  theme: 'light' | 'dark' | 'green' | 'parchment';
  pageWidth: 'narrow' | 'medium' | 'wide';
  autoSave: boolean;
}

const THEME_STYLES = {
  light: { background: '#FFFEF9', color: '#3D3D3D' },
  dark: { background: '#2C2416', color: '#E8DCC0' },
  green: { background: '#E8F5E0', color: '#2D4A2B' },
  parchment: { background: '#FAF8F3', color: '#5C4A3C' }
};

const PAGE_WIDTH = {
  narrow: 600,
  medium: 800,
  wide: 1000
};

const ReaderPage: React.FC = () => {
  const { novelId } = useParams<{ novelId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { novels } = useStore();

  const [novel, setNovel] = useState<Novel | null>(null);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [chapterContent, setChapterContent] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [settingsDrawerVisible, setSettingsDrawerVisible] = useState(false);
  const [searchDrawerVisible, setSearchDrawerVisible] = useState(false);
  const [chapterSearchText, setChapterSearchText] = useState('');
  const [highlightParagraph, setHighlightParagraph] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [chapterDrawerVisible, setChapterDrawerVisible] = useState(false);

  const [settings, setSettings] = useState<ReadingSettings>({
    fontSize: 16,
    fontFamily: '宋体',
    lineHeight: 1.8,
    theme: 'light',
    pageWidth: 'medium',
    autoSave: true
  });

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
    if (novel && currentChapter) {
      document.title = `${currentChapter.title} - ${novel.title} - 小说RAG分析系统`;
    } else if (novel) {
      document.title = `${novel.title} - 阅读 - 小说RAG分析系统`;
    } else {
      document.title = '阅读 - 小说RAG分析系统';
    }
  }, [novel, currentChapter]);

  // 加载小说和章节
  useEffect(() => {
    if (novelId) {
      loadNovel(novelId);
    }
  }, [novelId]);

  // 根据URL参数跳转到指定章节和段落
  useEffect(() => {
    if (novel && novel.chapters && novel.chapters.length > 0) {
      const chapterParam = searchParams.get('chapter');
      const paragraphParam = searchParams.get('paragraph');

      if (chapterParam) {
        const chapterIndex = novel.chapters.findIndex(c => c.id === chapterParam);
        if (chapterIndex >= 0) {
          setCurrentChapterIndex(chapterIndex);
        }
      }

      if (paragraphParam) {
        const paragraphIndex = parseInt(paragraphParam);
        if (!isNaN(paragraphIndex)) {
          setHighlightParagraph(paragraphIndex);
          
          // 3秒后取消高亮
          setTimeout(() => setHighlightParagraph(null), 3000);
        }
      }
    }
  }, [novel, searchParams]);

  // 加载章节内容
  useEffect(() => {
    if (novel && novel.chapters && novel.chapters[currentChapterIndex]) {
      loadChapterContent();
    }
  }, [novel, currentChapterIndex]);

  const loadNovel = async (id: string) => {
    try {
      setLoading(true);
      const loadedNovel = await dbUtils.getNovelById(id);
      
      if (!loadedNovel) {
        message.error('小说未找到');
        navigate('/');
        return;
      }

      setNovel(loadedNovel);
    } catch (error) {
      console.error('加载小说失败:', error);
      message.error('加载小说失败');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const loadChapterContent = () => {
    if (!novel || !novel.chapters || !novel.content) return;

    const chapter = novel.chapters[currentChapterIndex];
    if (!chapter) return;

    // 提取章节内容
    const content = novel.content.substring(chapter.startPosition, chapter.endPosition);
    setChapterContent(content);

    // 自动滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // 上一章
  const handlePreviousChapter = () => {
    if (currentChapterIndex > 0) {
      setCurrentChapterIndex(currentChapterIndex - 1);
    } else {
      message.info('已经是第一章了');
    }
  };

  // 下一章
  const handleNextChapter = () => {
    if (novel && novel.chapters && currentChapterIndex < novel.chapters.length - 1) {
      setCurrentChapterIndex(currentChapterIndex + 1);
    } else {
      message.info('已经是最后一章了');
    }
  };

  // 更新设置
  const updateSetting = <K extends keyof ReadingSettings>(
    key: K,
    value: ReadingSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  // 筛选章节
  const filteredChapters = React.useMemo(() => {
    if (!novel?.chapters) return [];
    return novel.chapters.filter(chapter =>
      chapter.title.toLowerCase().includes(chapterSearchText.toLowerCase())
    );
  }, [novel, chapterSearchText]);

  const currentChapter = novel?.chapters?.[currentChapterIndex];
  const themeStyle = THEME_STYLES[settings.theme];
  const readingProgress = (novel && novel.chapters && novel.chapters.length > 0) 
    ? ((currentChapterIndex + 1) / novel.chapters.length) * 100 
    : 0;

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
              {!isMobile && '返回'}
            </Button>
            {!isMobile && (
              <Button 
                icon={<MenuOutlined style={{ fontSize: '16px' }} />} 
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                size="large"
                style={{ fontWeight: 500 }}
              >
                {sidebarCollapsed ? '展开' : '收起'}目录
              </Button>
            )}
            <Text 
              strong 
              style={{ 
                fontSize: isMobile ? '14px' : '16px', 
                color: '#8B6914',
                maxWidth: isMobile ? '120px' : 'none',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {currentChapter?.title}
            </Text>
          </Space>

          <Space size={isMobile ? 'small' : 'middle'}>
            <Button
              onClick={() => updateSetting('fontSize', Math.max(12, settings.fontSize - 1))}
              size={isMobile ? 'small' : 'large'}
              style={{ fontWeight: 600, fontSize: isMobile ? '14px' : '16px' }}
            >
              A-
            </Button>
            <Button
              onClick={() => updateSetting('fontSize', Math.min(22, settings.fontSize + 1))}
              size={isMobile ? 'small' : 'large'}
              style={{ fontWeight: 600, fontSize: isMobile ? '16px' : '18px' }}
            >
              A+
            </Button>
            <Button 
              icon={<SettingOutlined style={{ fontSize: isMobile ? '14px' : '16px' }} />} 
              onClick={() => setSettingsDrawerVisible(true)}
              size={isMobile ? 'middle' : 'large'}
              style={{ fontWeight: 500 }}
            >
              {!isMobile && '设置'}
            </Button>
          </Space>
        </div>
      </Header>

      <Layout>
        {/* 左侧章节目录 - 仅桌面端显示 */}
        {!isMobile && !sidebarCollapsed && (
          <Sider
            width={280}
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
            <div style={{ padding: '16px' }}>
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <div>
                  <Title level={5} style={{ margin: 0 }}>{novel?.title}</Title>
                  <Progress
                    percent={Math.round(readingProgress)}
                    size="small"
                    showInfo={false}
                  />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    已阅读 {currentChapterIndex + 1} / {novel?.chapters.length || 0} 章
                  </Text>
                </div>

                <Input.Search
                  placeholder="搜索章节"
                  value={chapterSearchText}
                  onChange={(e) => setChapterSearchText(e.target.value)}
                  allowClear
                />

                {filteredChapters.length > 0 ? (
                  <Menu
                    mode="inline"
                    selectedKeys={[currentChapter?.id || '']}
                    style={{ borderRight: 0 }}
                    items={filteredChapters.map(chapter => ({
                      key: chapter.id,
                      label: (
                        <div>
                          <div>{chapter.title}</div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            约{Math.round(chapter.wordCount / 1000)}千字
                          </Text>
                        </div>
                      ),
                      onClick: () => {
                        if (novel?.chapters) {
                          const index = novel.chapters.findIndex(c => c.id === chapter.id);
                          if (index !== undefined && index >= 0) {
                            setCurrentChapterIndex(index);
                          }
                        }
                      }
                    }))}
                  />
                ) : (
                  <div style={{ padding: '20px', textAlign: 'center' }}>
                    <Text type="secondary">暂无章节</Text>
                  </div>
                )}
              </Space>
            </div>
          </Sider>
        )}

        {/* 阅读内容区 */}
        <Content
          style={{
            ...themeStyle,
            padding: '40px',
            minHeight: 'calc(100vh - 64px)'
          }}
        >
          <div
            style={{
              maxWidth: PAGE_WIDTH[settings.pageWidth],
              margin: '0 auto'
            }}
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Text>加载中...</Text>
              </div>
            ) : !novel ? (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Text>小说未找到</Text>
              </div>
            ) : !currentChapter ? (
              <div style={{ textAlign: 'center', padding: '100px 0' }}>
                <Text>章节未找到</Text>
              </div>
            ) : (
              <>
                {/* 章节标题 */}
                <Title
                  level={2}
                  style={{
                    textAlign: 'center',
                    marginBottom: 40,
                    color: themeStyle.color
                  }}
                >
                  {currentChapter?.title}
                </Title>

                {/* 章节内容 */}
                <div
                  style={{
                    fontSize: settings.fontSize,
                    fontFamily: settings.fontFamily,
                    lineHeight: settings.lineHeight,
                    color: themeStyle.color,
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {chapterContent.split('\n\n').map((paragraph, index) => (
                    <Paragraph
                      key={index}
                      style={{
                        textIndent: '2em',
                        marginBottom: '1em',
                        backgroundColor: highlightParagraph === index ? 'rgba(255, 235, 59, 0.3)' : 'transparent',
                        padding: highlightParagraph === index ? '8px' : 0,
                        transition: 'all 0.3s ease',
                        color: themeStyle.color
                      }}
                    >
                      {paragraph}
                    </Paragraph>
                  ))}
                </div>

                {/* 章节导航 */}
                <div style={{ marginTop: 60, textAlign: 'center' }}>
                  <Space size="large">
                    <Button
                      size="large"
                      icon={<LeftOutlined />}
                      onClick={handlePreviousChapter}
                      disabled={currentChapterIndex === 0}
                    >
                      上一章
                    </Button>
                    <Text style={{ color: themeStyle.color }}>
                      {currentChapterIndex + 1} / {novel?.chapters.length || 0}
                    </Text>
                    <Button
                      size="large"
                      onClick={handleNextChapter}
                      disabled={!novel || !novel.chapters || currentChapterIndex >= novel.chapters.length - 1}
                    >
                      下一章
                      <RightOutlined />
                    </Button>
                  </Space>
                </div>
              </>
            )}
          </div>
        </Content>
      </Layout>

      {/* 阅读设置抽屉 */}
      <Drawer
        title="阅读设置"
        placement="right"
        width={360}
        onClose={() => setSettingsDrawerVisible(false)}
        open={settingsDrawerVisible}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 字体大小 */}
          <div>
            <Text strong>字体大小：{settings.fontSize}px</Text>
            <Slider
              min={12}
              max={22}
              value={settings.fontSize}
              onChange={(value) => updateSetting('fontSize', value)}
            />
          </div>

          {/* 字体类型 */}
          <div>
            <Text strong>字体类型</Text>
            <Radio.Group
              value={settings.fontFamily}
              onChange={(e) => updateSetting('fontFamily', e.target.value)}
              style={{ marginTop: 8 }}
            >
              <Space direction="vertical">
                <Radio value="宋体">宋体</Radio>
                <Radio value="黑体">黑体</Radio>
                <Radio value="楷体">楷体</Radio>
                <Radio value="微软雅黑">微软雅黑</Radio>
              </Space>
            </Radio.Group>
          </div>

          {/* 行高 */}
          <div>
            <Text strong>行高：{settings.lineHeight}</Text>
            <Slider
              min={1.4}
              max={2.0}
              step={0.1}
              value={settings.lineHeight}
              onChange={(value) => updateSetting('lineHeight', value)}
            />
          </div>

          {/* 主题 */}
          <div>
            <Text strong>阅读主题</Text>
            <Radio.Group
              value={settings.theme}
              onChange={(e) => updateSetting('theme', e.target.value)}
              style={{ marginTop: 8 }}
            >
              <Space direction="vertical">
                <Radio value="light">白天模式</Radio>
                <Radio value="dark">夜间模式</Radio>
                <Radio value="green">护眼模式</Radio>
                <Radio value="parchment">羊皮纸模式</Radio>
              </Space>
            </Radio.Group>
          </div>

          {/* 页面宽度 */}
          <div>
            <Text strong>页面宽度</Text>
            <Radio.Group
              value={settings.pageWidth}
              onChange={(e) => updateSetting('pageWidth', e.target.value)}
              style={{ marginTop: 8 }}
            >
              <Space direction="vertical">
                <Radio value="narrow">窄</Radio>
                <Radio value="medium">中</Radio>
                <Radio value="wide">宽</Radio>
              </Space>
            </Radio.Group>
          </div>

          {/* 自动保存进度 */}
          <div>
            <Text strong>自动保存阅读进度</Text>
            <div style={{ marginTop: 8 }}>
              <Switch
                checked={settings.autoSave}
                onChange={(checked) => updateSetting('autoSave', checked)}
              />
            </div>
          </div>
        </Space>
      </Drawer>

      {/* 移动端章节列表Drawer */}
      {isMobile && (
        <>
          <Drawer
            title="章节目录"
            placement="bottom"
            height="70%"
            onClose={() => setChapterDrawerVisible(false)}
            open={chapterDrawerVisible}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              {/* 阅读进度 */}
              <div>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  已阅读 {currentChapterIndex + 1} / {novel?.chapters.length || 0} 章
                </Text>
                <Progress
                  percent={Math.round(readingProgress)}
                  size="small"
                  strokeColor="#8B6914"
                  style={{ marginTop: 4 }}
                />
              </div>

              {/* 搜索章节 */}
              <Input
                placeholder="搜索章节..."
                value={chapterSearchText}
                onChange={(e) => setChapterSearchText(e.target.value)}
                prefix={<SearchOutlined />}
                allowClear
              />

              {/* 章节列表 */}
              {filteredChapters.length > 0 ? (
                <Menu
                  mode="inline"
                  selectedKeys={[currentChapter?.id || '']}
                  style={{ 
                    borderRight: 0,
                    background: 'transparent',
                    maxHeight: 'calc(70vh - 200px)',
                    overflowY: 'auto'
                  }}
                  items={filteredChapters.map(chapter => ({
                    key: chapter.id,
                    label: (
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: 500 }}>{chapter.title}</div>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          约{Math.round(chapter.wordCount / 1000)}千字
                        </Text>
                      </div>
                    ),
                    onClick: () => {
                      if (novel?.chapters) {
                        const index = novel.chapters.findIndex(c => c.id === chapter.id);
                        if (index !== undefined && index >= 0) {
                          setCurrentChapterIndex(index);
                          setChapterDrawerVisible(false);
                        }
                      }
                    }
                  }))}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                  <Text type="secondary">暂无章节</Text>
                </div>
              )}
            </Space>
          </Drawer>

          {/* 移动端浮动按钮 */}
          <FloatButton.Group shape="circle" style={{ right: 24, bottom: 24 }}>
            <FloatButton
              icon={<MenuOutlined />}
              onClick={() => setChapterDrawerVisible(true)}
              tooltip="章节目录"
            />
            <FloatButton
              icon={<SettingOutlined />}
              onClick={() => setSettingsDrawerVisible(true)}
              tooltip="阅读设置"
            />
            <FloatButton.BackTop visibilityHeight={200} />
          </FloatButton.Group>
        </>
      )}
    </Layout>
  );
};

export default ReaderPage;

