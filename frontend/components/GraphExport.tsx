'use client';

/**
 * 图表导出组件
 * 
 * 提供图表导出为PNG/SVG/PDF的功能
 */

import React, { useState } from 'react';
import { Button, Dropdown, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';

interface GraphExportProps {
  graphType: 'relation' | 'timeline';
  novelId: number;
  graphData?: any;
}

const GraphExport: React.FC<GraphExportProps> = ({
  graphType,
  novelId,
  graphData,
}) => {
  const [exporting, setExporting] = useState(false);

  // 导出为PNG
  const exportAsPNG = async () => {
    setExporting(true);
    try {
      // 使用html2canvas导出
      const { default: html2canvas } = await import('html2canvas');
      
      const targetElement = document.querySelector(
        graphType === 'relation' ? '.react-flow' : '.ant-timeline'
      );

      if (!targetElement) {
        message.error('无法找到图表元素');
        return;
      }

      const canvas = await html2canvas(targetElement as HTMLElement, {
        backgroundColor: '#ffffff',
        scale: 2, // 高清
      });

      const link = document.createElement('a');
      link.download = `${graphType}_novel_${novelId}_${Date.now()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();

      message.success('导出PNG成功');
    } catch (error: any) {
      message.error(`导出失败: ${error.message}`);
      console.error('Export error:', error);
    } finally {
      setExporting(false);
    }
  };

  // 导出为SVG
  const exportAsSVG = async () => {
    message.info('SVG导出功能开发中');
    // TODO: 实现SVG导出
  };

  // 导出为PDF
  const exportAsPDF = async () => {
    message.info('PDF导出功能开发中');
    // TODO: 实现PDF导出（可以使用jsPDF）
  };

  // 导出为JSON
  const exportAsJSON = () => {
    if (!graphData) {
      message.error('无数据可导出');
      return;
    }

    const jsonStr = JSON.stringify(graphData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${graphType}_novel_${novelId}_${Date.now()}.json`;
    link.click();

    message.success('导出JSON成功');
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'png',
      label: '导出为PNG',
      onClick: exportAsPNG,
    },
    {
      key: 'svg',
      label: '导出为SVG',
      onClick: exportAsSVG,
      disabled: true, // 暂未实现
    },
    {
      key: 'pdf',
      label: '导出为PDF',
      onClick: exportAsPDF,
      disabled: true, // 暂未实现
    },
    {
      type: 'divider',
    },
    {
      key: 'json',
      label: '导出为JSON',
      onClick: exportAsJSON,
    },
  ];

  return (
    <Dropdown menu={{ items: menuItems }} placement="bottomRight">
      <Button icon={<DownloadOutlined />} loading={exporting}>
        导出
      </Button>
    </Dropdown>
  );
};

export default GraphExport;

