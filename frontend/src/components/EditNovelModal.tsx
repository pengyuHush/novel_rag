import React, { useEffect } from 'react';
import { Modal, Form, Input, Select, Checkbox, Button, message } from 'antd';
import { dbUtils } from '../utils/db';
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
        summary: novel.summary,
        tags: novel.tags || [],
        isSeries: !!novel.series,
        seriesOrder: novel.series?.order || 1,
        relatedNovels: novel.series?.relatedNovels || [],
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
        summary: values.summary,
        tags: values.tags || [],
      };

      if (values.isSeries) {
        updates.series = {
          relatedNovels: values.relatedNovels || [],
          order: values.seriesOrder || 1,
        };
      } else {
        updates.series = undefined;
      }

      await dbUtils.updateNovel(novel.id, updates);
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
      destroyOnClose
    >
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
          <Input placeholder="请输入作者" />
        </Form.Item>

        <Form.Item label="简介" name="summary">
          <TextArea rows={3} placeholder="请输入简介" />
        </Form.Item>

        <Form.Item label="标签" name="tags">
          <Select
            mode="tags"
            placeholder="请添加标签"
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
              <Form.Item label="系列序号" name="seriesOrder">
                <Input type="number" min={1} placeholder="第几部" />
              </Form.Item>
            ) : null
          }
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditNovelModal;

