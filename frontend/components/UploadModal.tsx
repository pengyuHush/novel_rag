/**
 * 上传小说Modal组件
 */

'use client';

import React, { useState } from 'react';
import { Modal, Form, Input, Upload, Button, message, Steps } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { apiClient } from '@/lib/api';

const { Dragger } = Upload;

interface UploadModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ open, onClose, onSuccess }) => {
  const [form] = Form.useForm();
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { title: '选择文件', description: '选择要上传的小说文件' },
    { title: '填写信息', description: '填写小说标题和作者' },
    { title: '开始上传', description: '确认并开始上传' },
  ];

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.error('请先选择文件');
      return;
    }

    try {
      const values = await form.validateFields();
      setUploading(true);

      await apiClient.uploadNovel({
        file: fileList[0] as any,
        title: values.title,
        author: values.author,
      });

      message.success('上传成功！后台正在索引中...');
      form.resetFields();
      setFileList([]);
      setCurrentStep(0);
      onSuccess();
      onClose();
    } catch (error: any) {
      message.error(error.message || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    accept: '.txt,.epub',
    beforeUpload: (file) => {
      const isTxtOrEpub = file.name.endsWith('.txt') || file.name.endsWith('.epub');
      if (!isTxtOrEpub) {
        message.error('只支持 TXT 和 EPUB 格式！');
        return false;
      }

      const isLt100M = file.size / 1024 / 1024 < 100;
      if (!isLt100M) {
        message.error('文件大小不能超过 100MB！');
        return false;
      }

      setFileList([file]);
      
      // 自动从文件名提取标题
      const filename = file.name.replace(/\.(txt|epub)$/i, '');
      form.setFieldValue('title', filename);
      
      setCurrentStep(1);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setFileList([]);
      setCurrentStep(0);
    },
  };

  const handleNext = () => {
    if (currentStep === 1) {
      form.validateFields().then(() => {
        setCurrentStep(2);
      });
    }
  };

  const handlePrev = () => {
    setCurrentStep(Math.max(0, currentStep - 1));
  };

  return (
    <Modal
      title="上传小说"
      open={open}
      onCancel={onClose}
      width={700}
      footer={[
        <Button key="cancel" onClick={onClose} disabled={uploading}>
          取消
        </Button>,
        currentStep > 0 && currentStep < 2 && (
          <Button key="prev" onClick={handlePrev} disabled={uploading}>
            上一步
          </Button>
        ),
        currentStep === 1 && (
          <Button key="next" type="primary" onClick={handleNext}>
            下一步
          </Button>
        ),
        currentStep === 2 && (
          <Button
            key="upload"
            type="primary"
            loading={uploading}
            onClick={handleUpload}
          >
            开始上传
          </Button>
        ),
      ]}
    >
      <Steps current={currentStep} className="mb-6">
        {steps.map((step) => (
          <Steps.Step key={step.title} title={step.title} description={step.description} />
        ))}
      </Steps>

      <div className="upload-content">
        {currentStep === 0 && (
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持 TXT 和 EPUB 格式，文件大小不超过 100MB
            </p>
          </Dragger>
        )}

        {currentStep >= 1 && (
          <Form
            form={form}
            layout="vertical"
            initialValues={{ title: '', author: '' }}
          >
            {fileList.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded">
                <div className="text-sm text-gray-600">选择的文件:</div>
                <div className="font-medium">{fileList[0].name}</div>
                <div className="text-xs text-gray-500">
                  大小: {(fileList[0].size! / 1024 / 1024).toFixed(2)} MB
                </div>
              </div>
            )}

            <Form.Item
              label="小说标题"
              name="title"
              rules={[{ required: true, message: '请输入小说标题' }]}
            >
              <Input placeholder="请输入小说标题" maxLength={200} />
            </Form.Item>

            <Form.Item
              label="作者"
              name="author"
            >
              <Input placeholder="请输入作者名称（可选）" maxLength={100} />
            </Form.Item>

            {currentStep === 2 && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <div className="text-sm">
                  <div className="font-medium mb-2">📝 准备上传</div>
                  <div className="space-y-1 text-gray-700">
                    <div>• 上传后将自动开始索引</div>
                    <div>• 索引时间取决于文件大小（约1-30分钟）</div>
                    <div>• 您可以在小说列表中查看索引进度</div>
                    <div>• 索引完成后即可开始问答</div>
                  </div>
                </div>
              </div>
            )}
          </Form>
        )}
      </div>
    </Modal>
  );
};

export default UploadModal;

