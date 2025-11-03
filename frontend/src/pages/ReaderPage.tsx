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
  message
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
  light: { background: '#fff', color: '#262626' },
  dark: { background: '#1f1f1f', color: '#e8e8e8' },
  green: { background: '#cce8cf', color: '#262626' },
  parchment: { background: '#f4f1e8', color: '#5c4a3c' }
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

  const [settings, setSettings] = useState<ReadingSettings>({
    fontSize: 16,
    fontFamily: '宋体',
    lineHeight: 1.8,
    theme: 'light',
    pageWidth: 'medium',
    autoSave: true
  });

  // 加载小说和章节
  useEffect(() => {
    if (novelId) {
      loadNovel(novelId);
    }
  }, [novelId]);

  // 根据URL参数跳转到指定章节和段落
  useEffect(() => {
    if (novel) {
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
        setHighlightParagraph(paragraphIndex);
        
        // 3秒后取消高亮
        setTimeout(() => setHighlightParagraph(null), 3000);
      }
    }
  }, [novel, searchParams]);

  // 加载章节内容
  useEffect(() => {
    if (novel && novel.chapters[currentChapterIndex]) {
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
    } finally {
      setLoading(false);
    }
  };

  const loadChapterContent = () => {
    if (!novel) return;

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
    if (novel && currentChapterIndex < novel.chapters.length - 1) {
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
  const filteredChapters = novel?.chapters.filter(chapter =>
    chapter.title.toLowerCase().includes(chapterSearchText.toLowerCase())
  ) || [];

  const currentChapter = novel?.chapters[currentChapterIndex];
  const themeStyle = THEME_STYLES[settings.theme];
  const readingProgress = novel ? ((currentChapterIndex + 1) / novel.chapters.length) * 100 : 0;

  return (
    <Layout className="page-container" style={{ minHeight: '100vh' }}>
      {/* 顶部工具栏 */}
      <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>
              返回
            </Button>
            <Button icon={<MenuOutlined />} onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
              {sidebarCollapsed ? '展开' : '收起'}目录
            </Button>
            <Text strong>{currentChapter?.title}</Text>
          </Space>

          <Space>
            <Button
              onClick={() => updateSetting('fontSize', Math.max(12, settings.fontSize - 1))}
            >
              A-
            </Button>
            <Button
              onClick={() => updateSetting('fontSize', Math.min(22, settings.fontSize + 1))}
            >
              A+
            </Button>
            <Button icon={<SettingOutlined />} onClick={() => setSettingsDrawerVisible(true)}>
              设置
            </Button>
          </Space>
        </div>
      </Header>

      <Layout>
        {/* 左侧章节目录 */}
        {!sidebarCollapsed && (
          <Sider
            width={280}
            theme="light"
            style={{
              background: '#fff',
              borderRight: '1px solid #f0f0f0',
              overflow: 'auto',
              height: 'calc(100vh - 64px)',
              position: 'sticky',
              top: 64
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
                      const index = novel?.chapters.findIndex(c => c.id === chapter.id) || 0;
                      setCurrentChapterIndex(index);
                    }
                  }))}
                />
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
                      disabled={!novel || currentChapterIndex >= novel.chapters.length - 1}
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
    </Layout>
  );
};

export default ReaderPage;

