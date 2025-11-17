/**
 * 查询输入组件
 * 包含输入框、模型选择器、查询按钮
 */

'use client';

import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Loader2, Settings } from 'lucide-react';
import { ModelType } from '@/types/api';
import { QueryConfigModal } from './QueryConfigModal';

interface QueryInputProps {
  value?: string;
  onChange?: (value: string) => void;
  onQuery: (query: string, model: ModelType) => void;
  isQuerying: boolean;
  disabled?: boolean;
}

export function QueryInput({ value, onChange, onQuery, isQuerying, disabled }: QueryInputProps) {
  const [internalQuery, setInternalQuery] = useState('');
  const [model, setModel] = useState<ModelType>(ModelType.GLM_4_5_AIR);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  
  const query = value !== undefined ? value : internalQuery;
  const setQuery = onChange || setInternalQuery;

  const handleSubmit = () => {
    if (!query.trim()) return;
    onQuery(query, model);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-3">
      {/* 输入框 */}
      <Textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="请输入您的问题，例如：萧炎和药老是什么时候相遇的？（Ctrl+Enter 提交）"
        className="min-h-[100px] resize-none"
        disabled={disabled || isQuerying}
      />

      {/* 底部控制栏 */}
      <div className="flex items-center justify-between gap-3">
        {/* 模型选择器 */}
        <div className="flex items-center gap-2 flex-1">
          <label className="text-sm font-medium whitespace-nowrap">模型：</label>
          <Select
            value={model}
            onValueChange={(value) => setModel(value as ModelType)}
            disabled={disabled || isQuerying}
          >
            <SelectTrigger className="w-[220px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ModelType.GLM_4_5_FLASH}>GLM-4.5-Flash（免费）</SelectItem>
              <SelectItem value={ModelType.GLM_4_FLASH}>GLM-4-Flash（免费，128K）</SelectItem>
              <SelectItem value={ModelType.GLM_4_5_AIR}>GLM-4.5-Air（推荐）</SelectItem>
              <SelectItem value={ModelType.GLM_4_5_AIRX}>GLM-4.5-AirX（增强）</SelectItem>
              <SelectItem value={ModelType.GLM_4_5_X}>GLM-4.5-X（极速）</SelectItem>
              <SelectItem value={ModelType.GLM_4_5}>GLM-4.5（高性能）</SelectItem>
              <SelectItem value={ModelType.GLM_4_PLUS}>GLM-4-Plus（顶级）</SelectItem>
              <SelectItem value={ModelType.GLM_4_6}>GLM-4.6（旗舰）</SelectItem>
              <SelectItem value={ModelType.GLM_4_LONG}>GLM-4-Long（百万上下文）</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* 查询按钮组 */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="lg"
            onClick={() => setConfigModalOpen(true)}
            disabled={disabled || isQuerying}
            title="查询参数配置"
          >
            <Settings className="h-4 w-4" />
          </Button>
        <Button
          onClick={handleSubmit}
          disabled={!query.trim() || disabled || isQuerying}
          size="lg"
        >
          {isQuerying ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              查询中...
            </>
          ) : (
            <>
              <Search className="mr-2 h-4 w-4" />
              查询
            </>
          )}
        </Button>
      </div>
      </div>

      {/* 配置弹窗 */}
      <QueryConfigModal
        open={configModalOpen}
        onOpenChange={setConfigModalOpen}
      />
    </div>
  );
}

