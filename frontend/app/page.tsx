/**
 * 智能问答主界面
 * 包含左侧小说列表、中间查询区域、右侧引用列表
 */

'use client';

import { useState } from 'react';
import { NovelSidebar } from '@/components/layout/NovelSidebar';
import { QueryInput } from '@/components/query/QueryInput';
import { PresetQueries } from '@/components/query/PresetQueries';
import { QueryStages } from '@/components/query/QueryStages';
import { TokenStats } from '@/components/query/TokenStats';
import { ThinkingPanel } from '@/components/query/ThinkingPanel';
import { CitationList } from '@/components/query/CitationList';
import { Separator } from '@/components/ui/separator';
import { UploadModal } from '@/components/novel/UploadModal';
import { GraphModal } from '@/components/graph/GraphModal';
import { useQueryStore } from '@/store/queryStore';
import { useNovelStore } from '@/store/novelStore';
import { toast } from 'sonner';
import type { ModelType } from '@/types/api';
import { useQueryWebSocket } from '@/hooks/useQuery';

export default function HomePage() {
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [selectedGraphNovelId, setSelectedGraphNovelId] = useState<number | null>(null);
  const [queryText, setQueryText] = useState('');

  const { selectedNovelId } = useNovelStore();
  const {
    isQuerying,
    currentStage,
    stageProgress,
    thinking = '',
    answer = '',
    citations = [],
    tokenStats,
  } = useQueryStore();

  const { executeQuery } = useQueryWebSocket();

  const handleQuery = (query: string, model: ModelType) => {
    if (!selectedNovelId) {
      toast.error('请先选择一本小说');
      return;
    }

    setQueryText(query);
    executeQuery(selectedNovelId, query, model);
  };

  const handlePresetSelect = (query: string) => {
    setQueryText(query);
  };

  const handleViewGraph = (novelId: number) => {
    setSelectedGraphNovelId(novelId);
    setGraphModalOpen(true);
  };

  return (
    <div className="flex h-full">
      {/* 左侧：小说列表 */}
      <NovelSidebar
        onUploadClick={() => setUploadModalOpen(true)}
        onViewGraphClick={handleViewGraph}
      />

      {/* 中间：主界面 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* 查询输入区 */}
        <div className="p-3 border-b space-y-3">
          <QueryInput
            value={queryText}
            onChange={setQueryText}
            onQuery={handleQuery}
            isQuerying={isQuerying}
            disabled={!selectedNovelId}
          />
          <PresetQueries
            onSelect={handlePresetSelect}
            disabled={isQuerying || !selectedNovelId}
          />
        </div>

        {/* 查询阶段（压缩高度） */}
        <div className="flex-shrink-0 px-3 py-2 border-b bg-muted/30">
          <QueryStages currentStage={currentStage} progress={stageProgress} />
        </div>

        {/* 思考内容 + 引用列表（固定高度，可独立滚动） */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          <ThinkingPanel
            thinking={thinking}
            answer={answer}
            isGenerating={isQuerying && currentStage === 'generating'}
            className="flex-1"
          />
          <Separator orientation="vertical" />
          <div className="w-80 flex flex-col min-h-0">
            {/* Token消耗统计 - 使用新组件 */}
            <div className="flex-shrink-0 border-b p-2">
              <TokenStats stats={tokenStats} />
            </div>
            
            {/* 引用列表 - 独立固定高度 */}
            <CitationList
              citations={citations}
              novelId={selectedNovelId}
              className="flex-1 min-h-0"
            />
          </div>
        </div>
      </main>

      {/* 弹窗 */}
      <UploadModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
      />
      <GraphModal
        open={graphModalOpen}
        onOpenChange={setGraphModalOpen}
        novelId={selectedGraphNovelId}
      />
    </div>
  );
}
