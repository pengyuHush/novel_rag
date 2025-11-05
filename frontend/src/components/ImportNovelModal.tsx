import React, { useState } from 'react';
import {
  Modal,
  Upload,
  Steps,
  Form,
  Input,
  Select,
  Button,
  message,
  Progress,
  List,
  Tag,
  Space,
  Checkbox
} from 'antd';
import { InboxOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { v4 as uuidv4 } from 'uuid';
import { novelAPI, apiUtils, APIError } from '../utils/api';
import { detectEncoding, readFileContent, detectChapters, cleanText } from '../utils/textProcessing';
import type { Novel, Chapter, NovelProcessingStatus } from '../types';

const { Dragger } = Upload;
const { Step } = Steps;
const { TextArea } = Input;

interface ImportNovelModalProps {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ImportNovelModal: React.FC<ImportNovelModalProps> = ({ visible, onClose, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [encoding, setEncoding] = useState<'UTF-8' | 'GBK' | 'GB2312'>('UTF-8');
  const [content, setContent] = useState('');
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  // 重置状态
  const resetState = () => {
    setCurrentStep(0);
    setFile(null);
    setEncoding('UTF-8');
    setContent('');
    setChapters([]);
    setProgress(0);
    setLoading(false);
    form.resetFields();
  };

  // 文件上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.txt',
    beforeUpload: async (file) => {
      const isTxt = file.name.toLowerCase().endsWith('.txt');
      if (!isTxt) {
        message.error('只能上传TXT文件！');
        return Upload.LIST_IGNORE;
      }

      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        message.warning('文件大小超过20MB，可能会影响性能');
      }

      setFile(file);
      
      // 自动进入下一步并解析文件
      setCurrentStep(1);
      await parseFile(file);
      
      return false; // 阻止自动上传
    },
    onDrop: (e) => {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  // 解析文件
  const parseFile = async (file: File) => {
    try {
      setLoading(true);
      
      // 检测编码
      const detectedEncoding = await detectEncoding(file);
      setEncoding(detectedEncoding);
      
      // 读取文件内容
      const fileContent = await readFileContent(file, detectedEncoding, (prog) => {
        setProgress(prog);
      });
      
      // 清理文本
      const cleaned = cleanText(fileContent);
      setContent(cleaned);
      
      // 识别章节
      const detectedChapters = detectChapters(cleaned);
      setChapters(detectedChapters);
      
      // 设置默认表单值
      form.setFieldsValue({
        title: file.name.replace('.txt', ''),
        encoding: detectedEncoding,
      });
      
      message.success('文件解析完成！');
      setProgress(100);
    } catch (error) {
      console.error('文件解析失败:', error);
      message.error('文件解析失败，请检查文件格式');
    } finally {
      setLoading(false);
    }
  };

  // 确认导入
  const handleImport = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      if (!file) {
        message.error('请选择文件');
        return;
      }

      // 上传文件（新的两步流程：先创建记录，再上传文件）
      const novelId = await novelAPI.uploadNovel(file, {
        title: values.title,
        author: values.author,
        description: values.summary, // 表单字段名是 summary
        tags: values.tags || [],
      });

      // 开始轮询处理状态
      message.info('文件上传成功，开始处理...');
      setCurrentStep(3); // 切换到处理进度步骤

      // 使用轮询监听处理状态
      await apiUtils.pollStatus(
        novelId,
        (status: NovelProcessingStatus) => {
          setProgress(status.progress);

          if (status.status === 'failed') {
            throw new Error(`处理失败: ${status.message}`);
          }
        }
      );

      // 处理完成
      message.success('小说导入成功！');
      onSuccess();
      handleClose();
    } catch (error) {
      console.error('导入失败:', error);
      if (error instanceof APIError) {
        message.error(`导入失败: ${error.message}`);
      } else {
        message.error(`导入失败: ${error.message}`);
      }
      // 发生错误时回到第一步
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  // 关闭Modal
  const handleClose = () => {
    resetState();
    onClose();
  };

  return (
    <Modal
      title="导入小说"
      open={visible}
      onCancel={handleClose}
      width={800}
      footer={null}
      destroyOnHidden
    >
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        <Step title="上传文件" />
        <Step title="解析预览" />
        <Step title="填写信息" />
        <Step title="确认导入" />
      </Steps>

      {/* 步骤1：上传文件 */}
      {currentStep === 0 && (
        <div>
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽TXT文件到此处</p>
            <p className="ant-upload-hint">
              仅支持TXT格式，建议文件大小不超过20MB
            </p>
          </Dragger>
        </div>
      )}

      {/* 步骤2：解析预览 */}
      {currentStep === 1 && (
        <div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Progress percent={Math.round(progress)} />
              <p style={{ marginTop: 16, color: '#666' }}>正在解析文件...</p>
            </div>
          ) : (
            <div>
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <div>
                  <h4>文件信息</h4>
                  <p>文件名：{file?.name}</p>
                  <p>文件大小：{apiUtils.formatFileSize(file?.size || 0)}</p>
                  <p>字数统计：{apiUtils.formatWordCount(content.length)}</p>
                  <p>检测编码：<Tag color="blue">{encoding}</Tag></p>
                </div>

                <div>
                  <h4>章节识别结果（共{chapters.length}章）</h4>
                  <List
                    size="small"
                    bordered
                    dataSource={chapters.slice(0, 10)}
                    style={{ maxHeight: 200, overflow: 'auto' }}
                    renderItem={(chapter) => (
                      <List.Item>
                        <div style={{ flex: 1 }}>
                          第{chapter.order}章：{chapter.title}
                        </div>
                        <Tag>{apiUtils.formatWordCount(chapter.wordCount)}</Tag>
                      </List.Item>
                    )}
                  />
                  {chapters.length > 10 && (
                    <p style={{ marginTop: 8, color: '#666', fontSize: '12px' }}>
                      仅显示前10章，共识别{chapters.length}章
                    </p>
                  )}
                </div>

                <div>
                  <h4>文本预览（前500字）</h4>
                  <div style={{
                    padding: 12,
                    background: '#f5f5f5',
                    borderRadius: 4,
                    maxHeight: 200,
                    overflow: 'auto',
                    fontSize: '14px',
                    lineHeight: 1.8
                  }}>
                    {content.substring(0, 500)}...
                  </div>
                </div>
              </Space>

              <div style={{ marginTop: 24, textAlign: 'right' }}>
                <Space>
                  <Button onClick={() => setCurrentStep(0)}>重新选择</Button>
                  <Button type="primary" onClick={() => setCurrentStep(2)}>
                    下一步
                  </Button>
                </Space>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 步骤3：填写信息 */}
      {currentStep === 2 && (
        <div>
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              isSeries: false,
              seriesOrder: 1,
            }}
          >
            <Form.Item
              label="书名"
              name="title"
              rules={[{ required: true, message: '请输入书名' }]}
            >
              <Input placeholder="请输入书名" />
            </Form.Item>

            <Form.Item label="作者" name="author">
              <Input placeholder="请输入作者（可选）" />
            </Form.Item>

            <Form.Item label="简介" name="summary">
              <TextArea rows={3} placeholder="请输入简介（可选）" />
            </Form.Item>

            <Form.Item label="标签" name="tags">
              <Select
                mode="tags"
                placeholder="请添加标签（可选）"
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item name="isSeries" valuePropName="checked">
              <Checkbox>这是系列小说的一部分</Checkbox>
            </Form.Item>

            <Form.Item
              noStyle
              shouldUpdate={(prevValues, currentValues) => 
                prevValues.isSeries !== currentValues.isSeries
              }
            >
              {({ getFieldValue }) =>
                getFieldValue('isSeries') ? (
                  <>
                    <Form.Item label="系列序号" name="seriesOrder">
                      <Input type="number" min={1} placeholder="第几部" />
                    </Form.Item>
                  </>
                ) : null
              }
            </Form.Item>
          </Form>

          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setCurrentStep(1)}>上一步</Button>
              <Button
                type="primary"
                loading={loading}
                onClick={handleImport}
                icon={<CheckCircleOutlined />}
              >
                开始导入
              </Button>
            </Space>
          </div>
        </div>
      )}

      {/* 步骤3：处理进度 */}
      {currentStep === 3 && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{ marginBottom: 24 }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <h4 style={{ marginTop: 16, marginBottom: 8 }}>正在处理您的小说</h4>
            <p style={{ color: '#666' }}>
              正在进行章节识别、向量化等处理，请稍候...
            </p>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Progress
              percent={progress}
              status={progress === 100 ? 'success' : 'active'}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#52c41a',
              }}
            />
            <p style={{ marginTop: 8, color: '#666', fontSize: '14px' }}>
              处理进度: {progress}%
            </p>
          </div>

          <div style={{ marginBottom: 24 }}>
            <List size="small" style={{ textAlign: 'left', maxWidth: 400, margin: '0 auto' }}>
              <List.Item>
                <span>书名：</span>
                <span style={{ fontWeight: 'bold' }}>{form.getFieldValue('title')}</span>
              </List.Item>
              {form.getFieldValue('author') && (
                <List.Item>
                  <span>作者：</span>
                  <span>{form.getFieldValue('author')}</span>
                </List.Item>
              )}
              <List.Item>
                <span>预计字数：</span>
                <span>{apiUtils.formatWordCount(content.length)}</span>
              </List.Item>
              <List.Item>
                <span>预计章节数：</span>
                <span>{chapters.length}章</span>
              </List.Item>
              <List.Item>
                <span>文件编码：</span>
                <span>{encoding}</span>
              </List.Item>
            </List>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default ImportNovelModal;

