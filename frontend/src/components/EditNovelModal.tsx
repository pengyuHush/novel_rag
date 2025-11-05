import React, { useEffect } from 'react';
import { Modal, Form, Input, Select, Button, message } from 'antd';
import { novelAPI } from '../utils/api';
import type { Novel } from '../types';
import { useStore } from '../store/useStore';

const { TextArea } = Input;

interface EditNovelModalProps {
  visible: boolean;
  novel: Novel;
  onClose: () => void;
  onSuccess: () => void;
}

const EditNovelModal: React.FC<EditNovelModalProps> = ({ visible, novel, onClose, onSuccess }) => {
  const [form] = Form.useForm();
  const { updateNovel } = useStore();
  const [loading, setLoading] = React.useState(false);

  useEffect(() => {
    if (visible && novel) {
      form.setFieldsValue({
        title: novel.title,
        author: novel.author,
        description: novel.description,
        tags: novel.tags || [],
        seriesName: novel.seriesName,
        seriesOrder: novel.seriesOrder,
      });
    }
  }, [visible, novel, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const updates: Partial<Novel> = {
        title: values.title,
        author: values.author,
        description: values.description,
        tags: values.tags || [],
        seriesName: values.seriesName || undefined,
        seriesOrder: values.seriesOrder || undefined,
      };

      await novelAPI.updateNovel(novel.id, updates);
      updateNovel(novel.id, updates);
      
      message.success('小说信息已更新');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('更新失败:', error);
      message.error('更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="编辑小说信息"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          保存
        </Button>,
      ]}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          label="书名"
          name="title"
          rules={[{ required: true, message: '请输入书名' }]}
        >
          <Input placeholder="请输入书名" />
        </Form.Item>

        <Form.Item label="作者" name="author">
          <Input placeholder="请输入作者" />
        </Form.Item>

        <Form.Item label="简介" name="description">
          <TextArea rows={3} placeholder="请输入简介" />
        </Form.Item>

        <Form.Item label="标签" name="tags">
          <Select
            mode="tags"
            placeholder="请添加标签"
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item label="系列名称" name="seriesName">
          <Input placeholder="如果是系列小说，请输入系列名称（可选）" />
        </Form.Item>

        <Form.Item label="系列序号" name="seriesOrder">
          <Input type="number" min={1} placeholder="该小说在系列中的序号（可选）" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditNovelModal;

