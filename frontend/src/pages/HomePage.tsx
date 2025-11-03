import React, { useEffect, useState } from 'react';
import {
  Layout,
  Card,
  Button,
  Row,
  Col,
  Statistic,
  Tag,
  Space,
  Modal,
  message,
  Empty,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  TeamOutlined,
  ReadOutlined,
  EditOutlined,
  DeleteOutlined,
  BookOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { db, dbUtils, formatWordCount } from '../utils/db';
import ImportNovelModal from '../components/ImportNovelModal';
import EditNovelModal from '../components/EditNovelModal';
import type { Novel } from '../types';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.locale('zh-cn');
dayjs.extend(relativeTime);

const { Header, Content } = Layout;

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { novels, setNovels, removeNovel, storageInfo, setStorageInfo } = useStore();
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);
  const [loading, setLoading] = useState(true);

  // 加载小说列表
  useEffect(() => {
    loadNovels();
  }, []);

  const loadNovels = async () => {
    try {
      setLoading(true);
      const allNovels = await dbUtils.getAllNovels();
      setNovels(allNovels);
      
      const info = await dbUtils.getStorageInfo();
      setStorageInfo(info);
    } catch (error) {
      console.error('加载小说列表失败:', error);
      message.error('加载小说列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除小说
  const handleDelete = async (id: string, title: string) => {
    try {
      await dbUtils.deleteNovel(id);
      removeNovel(id);
      message.success(`已删除《${title}》`);
      
      // 更新存储信息
      const info = await dbUtils.getStorageInfo();
      setStorageInfo(info);
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  // 编辑小说
  const handleEdit = (novel: Novel) => {
    setSelectedNovel(novel);
    setEditModalVisible(true);
  };

  // 跳转到搜索页
  const handleAnalyze = (novelId: string) => {
    navigate('/search', { state: { selectedNovelIds: [novelId] } });
  };

  return (
    <Layout className="page-container">
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
            <Button type="link">帮助</Button>
          </Space>
        </div>
      </Header>

      {/* 主内容区 */}
      <Content className="content-wrapper">
        {/* 统计卡片 */}
        <Card
          style={{ marginBottom: 24 }}
          bodyStyle={{ padding: '24px' }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Statistic
                title="已导入小说"
                value={storageInfo.novelCount}
                suffix="部"
                prefix={<BookOutlined />}
              />
            </Col>
            <Col xs={24} sm={8}>
              <Statistic
                title="总字数"
                value={Math.round(storageInfo.totalWords / 10000)}
                suffix="万字"
                prefix={<ReadOutlined />}
              />
            </Col>
            <Col xs={24} sm={8}>
              <Statistic
                title="存储空间"
                value={storageInfo.formattedSize}
                prefix={<TeamOutlined />}
              />
            </Col>
          </Row>
          <div style={{ marginTop: 24 }}>
            <Button
              type="primary"
              size="large"
              icon={<PlusOutlined />}
              onClick={() => setImportModalVisible(true)}
            >
              导入新小说
            </Button>
          </div>
        </Card>

        {/* 小说列表 */}
        {loading ? (
          <Card loading={true} />
        ) : novels.length === 0 ? (
          <Card>
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="还没有导入任何小说"
            >
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setImportModalVisible(true)}>
                立即导入
              </Button>
            </Empty>
          </Card>
        ) : (
          <Row gutter={[16, 16]}>
            {novels.map((novel) => (
              <Col xs={24} sm={12} lg={8} key={novel.id}>
                <Card
                  className="hover-card"
                  style={{ height: '100%' }}
                  actions={[
                    <Button
                      type="link"
                      icon={<SearchOutlined />}
                      onClick={() => handleAnalyze(novel.id)}
                    >
                      分析
                    </Button>,
                    <Button
                      type="link"
                      icon={<TeamOutlined />}
                      onClick={() => navigate(`/graph/${novel.id}`)}
                    >
                      关系图
                    </Button>,
                    <Button
                      type="link"
                      icon={<ReadOutlined />}
                      onClick={() => navigate(`/reader/${novel.id}`)}
                    >
                      阅读
                    </Button>,
                  ]}
                >
                  <div style={{ marginBottom: 12 }}>
                    <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
                      {novel.title}
                    </h3>
                    {novel.author && (
                      <p style={{ margin: '4px 0', color: '#666', fontSize: '14px' }}>
                        作者：{novel.author}
                      </p>
                    )}
                  </div>

                  <Space direction="vertical" style={{ width: '100%' }} size="small">
                    <div>
                      <Tag color="blue">{formatWordCount(novel.wordCount)}</Tag>
                      <Tag color="green">{novel.chapters.length} 章节</Tag>
                    </div>

                    {novel.series && (
                      <Tag color="purple">系列第{novel.series.order}部</Tag>
                    )}

                    {novel.tags && novel.tags.length > 0 && (
                      <div>
                        {novel.tags.map((tag, index) => (
                          <Tag key={index}>{tag}</Tag>
                        ))}
                      </div>
                    )}

                    <div style={{ color: '#999', fontSize: '12px' }}>
                      导入于 {dayjs(novel.importDate).fromNow()}
                    </div>
                  </Space>

                  <div style={{ marginTop: 12, display: 'flex', gap: '8px' }}>
                    <Button
                      size="small"
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(novel)}
                    >
                      编辑
                    </Button>
                    <Popconfirm
                      title="确定要删除这部小说吗？"
                      description="此操作不可撤销，所有相关数据将被删除。"
                      onConfirm={() => handleDelete(novel.id, novel.title)}
                      okText="确定删除"
                      cancelText="取消"
                      okButtonProps={{ danger: true }}
                    >
                      <Button
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Content>

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
    </Layout>
  );
};

export default HomePage;

