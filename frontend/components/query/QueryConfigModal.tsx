/**
 * 查询配置弹窗
 * 允许用户配置查询参数：top_k_retrieval、top_k_rerank、max_context_chunks
 */

'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useQueryStore } from '@/store/queryStore';
import { QueryConfig } from '@/types/api';

interface QueryConfigModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

// 预设配置
const PRESET_CONFIGS = {
  normal: {
    label: '常规',
    description: '平衡速度和精度的标准配置',
    config: {
      top_k_retrieval: 30,
      top_k_rerank: 10,
      max_context_chunks: 10,
    },
  },
  highPrecision: {
    label: '高精度',
    description: '最大精度配置，查询时间较长',
    config: {
      top_k_retrieval: 100,
      top_k_rerank: 30,
      max_context_chunks: 20,
    },
  },
};

export function QueryConfigModal({ open, onOpenChange }: QueryConfigModalProps) {
  const { queryConfig, setQueryConfig, resetQueryConfig } = useQueryStore();
  
  // 本地状态
  const [localConfig, setLocalConfig] = useState<QueryConfig>(queryConfig);
  const [preset, setPreset] = useState<'normal' | 'highPrecision' | 'custom'>('normal');

  // 同步store配置到本地状态
  useEffect(() => {
    if (open) {
      setLocalConfig(queryConfig);
      // 检测当前配置匹配哪个预设
      detectPreset(queryConfig);
    }
  }, [open, queryConfig]);

  // 检测当前配置是否匹配预设
  const detectPreset = (config: QueryConfig) => {
    if (
      config.top_k_retrieval === PRESET_CONFIGS.normal.config.top_k_retrieval &&
      config.top_k_rerank === PRESET_CONFIGS.normal.config.top_k_rerank &&
      config.max_context_chunks === PRESET_CONFIGS.normal.config.max_context_chunks
    ) {
      setPreset('normal');
    } else if (
      config.top_k_retrieval === PRESET_CONFIGS.highPrecision.config.top_k_retrieval &&
      config.top_k_rerank === PRESET_CONFIGS.highPrecision.config.top_k_rerank &&
      config.max_context_chunks === PRESET_CONFIGS.highPrecision.config.max_context_chunks
    ) {
      setPreset('highPrecision');
    } else {
      setPreset('custom');
    }
  };

  // 处理预设选择
  const handlePresetChange = (value: string) => {
    if (value === 'normal' || value === 'highPrecision') {
      setPreset(value);
      setLocalConfig(PRESET_CONFIGS[value].config);
    }
  };

  // 处理参数调整
  const handleParamChange = (param: keyof QueryConfig, value: number) => {
    const newConfig = { ...localConfig, [param]: value };
    setLocalConfig(newConfig);
    detectPreset(newConfig);
  };

  // 保存配置
  const handleSave = () => {
    setQueryConfig(localConfig);
    onOpenChange(false);
  };

  // 重置配置
  const handleReset = () => {
    resetQueryConfig();
    setLocalConfig(PRESET_CONFIGS.normal.config);
    setPreset('normal');
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>查询参数配置</DialogTitle>
          <DialogDescription>
            调整查询参数以优化检索和生成效果。配置将自动保存，刷新页面后仍然有效。
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* 预设选择 */}
          <div className="space-y-3">
            <Label>预设配置</Label>
            <RadioGroup value={preset} onValueChange={handlePresetChange}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="normal" id="normal" />
                <Label htmlFor="normal" className="font-normal cursor-pointer">
                  <div>
                    <div className="font-medium">{PRESET_CONFIGS.normal.label}</div>
                    <div className="text-sm text-muted-foreground">
                      {PRESET_CONFIGS.normal.description}
                    </div>
                  </div>
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="highPrecision" id="highPrecision" />
                <Label htmlFor="highPrecision" className="font-normal cursor-pointer">
                  <div>
                    <div className="font-medium">{PRESET_CONFIGS.highPrecision.label}</div>
                    <div className="text-sm text-muted-foreground">
                      {PRESET_CONFIGS.highPrecision.description}
                    </div>
                  </div>
                </Label>
              </div>
              {preset === 'custom' && (
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="custom" id="custom" disabled />
                  <Label htmlFor="custom" className="font-normal text-muted-foreground">
                    自定义配置
                  </Label>
                </div>
              )}
            </RadioGroup>
          </div>

          {/* 参数滑块 */}
          <div className="space-y-6 pt-4 border-t">
            {/* top_k_retrieval */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="top_k_retrieval">初始检索数量 (Top-K Retrieval)</Label>
                <span className="text-sm font-medium">{localConfig.top_k_retrieval}</span>
              </div>
              <Slider
                id="top_k_retrieval"
                min={10}
                max={100}
                step={10}
                value={[localConfig.top_k_retrieval]}
                onValueChange={(value) => handleParamChange('top_k_retrieval', value[0])}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                向量检索返回的候选文档数量。数值越大召回率越高，但计算量增加。
              </p>
            </div>

            {/* top_k_rerank */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="top_k_rerank">重排序后保留数量 (Top-K Rerank)</Label>
                <span className="text-sm font-medium">{localConfig.top_k_rerank}</span>
              </div>
              <Slider
                id="top_k_rerank"
                min={5}
                max={30}
                step={5}
                value={[localConfig.top_k_rerank]}
                onValueChange={(value) => handleParamChange('top_k_rerank', value[0])}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                重排序后发送给LLM的文档数量。数值越大上下文越丰富，但Token成本增加。
              </p>
            </div>

            {/* max_context_chunks */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="max_context_chunks">最大上下文块数</Label>
                <span className="text-sm font-medium">{localConfig.max_context_chunks}</span>
              </div>
              <Slider
                id="max_context_chunks"
                min={5}
                max={20}
                step={5}
                value={[localConfig.max_context_chunks]}
                onValueChange={(value) => handleParamChange('max_context_chunks', value[0])}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                构建Prompt时使用的最大文本块数量。数值越大答案越全面，但可能引入噪音。
              </p>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleReset}>
            重置为默认
          </Button>
          <Button onClick={handleSave}>
            保存配置
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

