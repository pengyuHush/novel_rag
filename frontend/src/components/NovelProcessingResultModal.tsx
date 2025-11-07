import React from 'react';
import { Modal, Result, Descriptions, Tag, Space, Statistic, Row, Col } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  DollarOutlined,
  ApiOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import type { Novel, TokenStats } from '../types';

interface NovelProcessingResultModalProps {
  visible: boolean;
  novel: Partial<Novel> | null;
  success: boolean;
  errorMessage?: string;
  onClose: () => void;
}

const NovelProcessingResultModal: React.FC<NovelProcessingResultModalProps> = ({
  visible,
  novel,
  success,
  errorMessage,
  onClose,
}) => {
  // 格式化数字
  const formatNumber = (num: number) => {
    return num.toLocaleString('zh-CN');
  };

  // 格式化费用
  const formatCost = (cost: number) => {
    return `¥${cost.toFixed(4)}`;
  };

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      onOk={onClose}
      width={700}
      footer={null}
      centered
    >
      {success ? (
        // 成功界面
        <Result
          status="success"
          title="小说导入成功！"
          subTitle="您的小说已成功导入并完成向量化处理"
          icon={<CheckCircleOutlined />}
        >
          {novel && (
            <div style={{ textAlign: 'left' }}>
              <Descriptions
                title="小说信息"
                bordered
                column={2}
                size="small"
                style={{ marginBottom: 24 }}
              >
                <Descriptions.Item label="书名" span={2}>
                  <strong style={{ fontSize: 16 }}>{novel.title}</strong>
                </Descriptions.Item>
                {novel.author && (
                  <Descriptions.Item label="作者" span={2}>
                    {novel.author}
                  </Descriptions.Item>
                )}
                <Descriptions.Item label="字数">
                  <Tag color="blue" icon={<FileTextOutlined />}>
                    {formatNumber(novel.wordCount || 0)}字
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="章节">
                  <Tag color="green">
                    {novel.chapterCount || 0}章
                  </Tag>
                </Descriptions.Item>
                {novel.tags && novel.tags.length > 0 && (
                  <Descriptions.Item label="标签" span={2}>
                    <Space>
                      {novel.tags.map((tag, index) => (
                        <Tag key={index}>{tag}</Tag>
                      ))}
                    </Space>
                  </Descriptions.Item>
                )}
              </Descriptions>

              {/* Token消耗统计 */}
              {(novel.totalTokensUsed || 0) > 0 && (
                <div>
                  <h4 style={{ marginBottom: 16 }}>
                    <ThunderboltOutlined style={{ marginRight: 8 }} />
                    Token消耗统计
                  </h4>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic
                        title="总Token消耗"
                        value={novel.totalTokensUsed || 0}
                        prefix={<ApiOutlined />}
                        suffix="tokens"
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="API调用次数"
                        value={novel.apiCallsCount || 0}
                        prefix={<ApiOutlined />}
                        suffix="次"
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={12} style={{ marginTop: 16 }}>
                      <Statistic
                        title="Embedding Token"
                        value={novel.embeddingTokensUsed || 0}
                        suffix="tokens"
                        valueStyle={{ fontSize: 16 }}
                      />
                    </Col>
                    <Col span={12} style={{ marginTop: 16 }}>
                      <Statistic
                        title="预估费用"
                        value={novel.estimatedCost || 0}
                        precision={4}
                        prefix={<DollarOutlined />}
                        suffix="元"
                        valueStyle={{ color: '#faad14', fontSize: 16 }}
                      />
                    </Col>
                  </Row>

                  <div style={{ 
                    marginTop: 16, 
                    padding: 12, 
                    background: '#f0f5ff',
                    borderRadius: 4,
                    fontSize: 12,
                    color: '#666'
                  }}>
                    💡 费用基于智谱AI Embedding-3官方价格（0.5元/百万tokens）计算
                  </div>
                </div>
              )}
            </div>
          )}
        </Result>
      ) : (
        // 失败界面
        <Result
          status="error"
          title="小说导入失败"
          subTitle="处理过程中遇到错误，请检查后重试"
          icon={<CloseCircleOutlined />}
        >
          {errorMessage && (
            <div style={{ 
              padding: 16,
              background: '#fff2f0',
              border: '1px solid #ffccc7',
              borderRadius: 4,
              marginTop: 16,
              textAlign: 'left'
            }}>
              <h4 style={{ color: '#cf1322', marginBottom: 8 }}>错误信息：</h4>
              <p style={{ color: '#595959', margin: 0, wordBreak: 'break-word' }}>
                {errorMessage}
              </p>
            </div>
          )}

          <div style={{ marginTop: 24, textAlign: 'left' }}>
            <h4>常见问题排查：</h4>
            <ul style={{ color: '#595959' }}>
              <li>检查文件格式是否为TXT纯文本</li>
              <li>确认文件编码（支持UTF-8、GBK、GB2312）</li>
              <li>验证文件大小不超过50MB</li>
              <li>确保文件包含足够的中文内容（至少60%）</li>
              <li>检查网络连接是否正常</li>
            </ul>
          </div>
        </Result>
      )}
    </Modal>
  );
};

export default NovelProcessingResultModal;

