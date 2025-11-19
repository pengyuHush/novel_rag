/**
 * 导出按钮组件
 * 提供图表导出功能（PNG/SVG）
 */

'use client';

import { useState } from 'react';
import { Download, Copy, Printer } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { exportChart, copyChartToClipboard, printChart } from '@/lib/chartExport';
import type { EChartsType } from 'echarts/core';

interface ExportButtonProps {
  chartInstance: EChartsType | null;
  filename?: string;
}

export function ExportButton({ chartInstance, filename }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (format: 'png' | 'svg') => {
    if (!chartInstance) {
      toast.error('图表未加载');
      return;
    }

    try {
      setIsExporting(true);
      exportChart(chartInstance, {
        format,
        filename: filename || `chart_${Date.now()}.${format}`,
        backgroundColor: '#ffffff',
        pixelRatio: 2,
      });
      toast.success(`已导出为 ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('导出失败');
      console.error(error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopy = async () => {
    if (!chartInstance) {
      toast.error('图表未加载');
      return;
    }

    try {
      setIsExporting(true);
      await copyChartToClipboard(chartInstance);
      toast.success('已复制到剪贴板');
    } catch (error) {
      toast.error('复制失败');
      console.error(error);
    } finally {
      setIsExporting(false);
    }
  };

  const handlePrint = () => {
    if (!chartInstance) {
      toast.error('图表未加载');
      return;
    }

    try {
      printChart(chartInstance);
    } catch (error) {
      toast.error('打印失败');
      console.error(error);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={!chartInstance || isExporting}
        >
          <Download className="w-4 h-4 mr-1" />
          导出
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleExport('png')}>
          <Download className="w-4 h-4 mr-2" />
          导出为 PNG
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('svg')}>
          <Download className="w-4 h-4 mr-2" />
          导出为 SVG
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleCopy}>
          <Copy className="w-4 h-4 mr-2" />
          复制到剪贴板
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handlePrint}>
          <Printer className="w-4 h-4 mr-2" />
          打印
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

