/**
 * 查询输入组件
 * 包含输入框、模型选择器、查询按钮
 */

'use client';

import { useState, useEffect } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from '@/components/ui/select';
import { Search, Loader2, Settings, Sparkles } from 'lucide-react';
import { ModelType } from '@/types/api';
import { QueryConfigModal } from './QueryConfigModal';
import { useQueryStore } from '@/store/queryStore';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface QueryInputProps {
  value?: string;
  onChange?: (value: string) => void;
  onQuery: (query: string, model: ModelType) => void;
  isQuerying: boolean;
  disabled?: boolean;
}

export function QueryInput({ value, onChange, onQuery, isQuerying, disabled }: QueryInputProps) {
  const [internalQuery, setInternalQuery] = useState('');
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [providersStatus, setProvidersStatus] = useState<Record<string, boolean>>({});
  const [isFocused, setIsFocused] = useState(false);
  
  // 使用持久化的selectedModel
  const selectedModel = useQueryStore((state) => state.selectedModel);
  const setSelectedModel = useQueryStore((state) => state.setSelectedModel);
  
  const query = value !== undefined ? value : internalQuery;
  const setQuery = onChange || setInternalQuery;

  // 在组件挂载时获取提供商状态
  useEffect(() => {
    const fetchProvidersStatus = async () => {
      try {
        const status = await api.getProvidersStatus();
        setProvidersStatus(status);
      } catch (error) {
        console.error('获取提供商状态失败:', error);
      }
    };
    
    fetchProvidersStatus();
  }, []);

  const handleSubmit = () => {
    if (!query.trim()) return;
    onQuery(query, selectedModel);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative max-w-3xl mx-auto w-full">
      <div 
        className={cn(
          "relative rounded-2xl bg-card transition-all duration-300 ease-out border border-transparent",
          isFocused ? "shadow-xl ring-1 ring-primary/10 translate-y-[-2px]" : "shadow-lg hover:shadow-xl"
        )}
      >
        <div className="p-4 pb-2">
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="问点什么... (例如: 萧炎什么时候遇见药老的?)"
            className="min-h-[80px] resize-none border-0 bg-transparent p-2 text-lg placeholder:text-muted-foreground/50 focus-visible:ring-0 shadow-none"
            disabled={disabled || isQuerying}
          />
        </div>

        {/* 底部控制栏 */}
        <div className="flex items-center justify-between px-4 pb-3 pt-1 border-t border-border/20 mx-2 mt-1">
          {/* 模型选择器 - 极简风格 */}
          <div className="flex items-center">
            <Select
              value={selectedModel}
              onValueChange={(value) => setSelectedModel(value as ModelType)}
              disabled={disabled || isQuerying}
            >
              <SelectTrigger className="h-8 border-0 bg-transparent focus:ring-0 hover:bg-muted/50 rounded-lg px-2.5 text-xs font-medium text-muted-foreground gap-2 w-auto shadow-none">
                <Sparkles className="h-3.5 w-3.5" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {/* 智谱AI */}
                {providersStatus.zhipu && (
                  <SelectGroup>
                    <SelectLabel className="text-xs">智谱AI</SelectLabel>
                    <SelectItem value={ModelType.ZHIPU_GLM_4_5_FLASH}>GLM-4.5-Flash</SelectItem>
                    <SelectItem value={ModelType.ZHIPU_GLM_4_5}>GLM-4.5</SelectItem>
                    <SelectItem value={ModelType.ZHIPU_GLM_4_6}>GLM-4.6</SelectItem>
                    <SelectItem value={ModelType.ZHIPU_GLM_4_5_AIR}>GLM-4.5-Air</SelectItem>
                    <SelectItem value={ModelType.ZHIPU_GLM_4_PLUS}>GLM-4-Plus</SelectItem>
                  </SelectGroup>
                )}
                
                {/* OpenAI */}
                {providersStatus.openai && (
                  <SelectGroup>
                    <SelectLabel className="text-xs">OpenAI</SelectLabel>
                    <SelectItem value={ModelType.OPENAI_GPT_4O}>GPT-4o</SelectItem>
                    <SelectItem value={ModelType.OPENAI_GPT_4O_MINI}>GPT-4o-mini</SelectItem>
                    <SelectItem value={ModelType.OPENAI_GPT_4_TURBO}>GPT-4-Turbo</SelectItem>
                    <SelectItem value={ModelType.OPENAI_GPT_3_5_TURBO}>GPT-3.5-Turbo</SelectItem>
                  </SelectGroup>
                )}
                
                {/* DeepSeek */}
                {providersStatus.deepseek && (
                  <SelectGroup>
                    <SelectLabel className="text-xs">DeepSeek</SelectLabel>
                    <SelectItem value={ModelType.DEEPSEEK_CHAT}>DeepSeek-Chat</SelectItem>
                    <SelectItem value={ModelType.DEEPSEEK_REASONER}>DeepSeek-Reasoner</SelectItem>
                  </SelectGroup>
                )}
                
                {/* Gemini */}
                {providersStatus.gemini && (
                  <SelectGroup>
                    <SelectLabel className="text-xs">Gemini</SelectLabel>
                    <SelectItem value={ModelType.GEMINI_1_5_PRO}>Gemini-1.5-Pro</SelectItem>
                    <SelectItem value={ModelType.GEMINI_1_5_FLASH}>Gemini-1.5-Flash</SelectItem>
                    <SelectItem value={ModelType.GEMINI_2_0_FLASH_EXP}>Gemini-2.0-Flash</SelectItem>
                    <SelectItem value={ModelType.GEMINI_3_PRO_PREVIEW}>Gemini-3-Pro</SelectItem>
                  </SelectGroup>
                )}
                
                {/* 阿里通义千问 */}
                {providersStatus.ali && (
                  <SelectGroup>
                    <SelectLabel className="text-xs">阿里通义千问</SelectLabel>
                    <SelectItem value={ModelType.ALI_QWEN_MAX}>Qwen-Max</SelectItem>
                    <SelectItem value={ModelType.ALI_QWEN_PLUS}>Qwen-Plus</SelectItem>
                    <SelectItem value={ModelType.ALI_QWEN_TURBO}>Qwen-Turbo</SelectItem>
                  </SelectGroup>
                )}
              </SelectContent>
            </Select>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setConfigModalOpen(true)}
              disabled={disabled || isQuerying}
              className="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50"
            >
              <Settings className="h-4 w-4 stroke-[1.5]" />
            </Button>
          </div>

          {/* 查询按钮 */}
          <Button
            onClick={handleSubmit}
            disabled={!query.trim() || disabled || isQuerying}
            size="sm"
            className={cn(
              "h-9 px-4 rounded-xl transition-all duration-300 shadow-sm",
              isQuerying ? "w-32" : "w-24",
              !query.trim() ? "opacity-50 cursor-not-allowed" : "hover:shadow-md hover:translate-y-[-1px]"
            )}
          >
            {isQuerying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                <span className="text-xs font-medium">思考中...</span>
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4 stroke-[2]" />
                <span className="text-xs font-medium">查询</span>
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
