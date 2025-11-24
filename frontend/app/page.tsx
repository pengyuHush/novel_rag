/**
 * 智能问答主界面
 * 包含左侧小说列表、中间查询区域、右侧引用列表
 */

'use client';

import { useState } from 'react';
import { NovelSidebar } from '@/components/layout/NovelSidebar';
import { Header } from '@/components/layout/Header';
import { QueryInput } from '@/components/query/QueryInput';
import { PresetQueries } from '@/components/query/PresetQueries';
import { QueryStages } from '@/components/query/QueryStages';
import { TokenStats } from '@/components/query/TokenStats';
import { ThinkingPanel } from '@/components/query/ThinkingPanel';
import { CitationList } from '@/components/query/CitationList';
import { QueryHistoryModal } from '@/components/query/QueryHistoryModal';
import { UploadModal } from '@/components/novel/UploadModal';
import { AppendChaptersModal } from '@/components/novel/AppendChaptersModal';
import { GraphModal } from '@/components/graph/GraphModal';
import { useQueryStore } from '@/store/queryStore';
import { useNovelStore } from '@/store/novelStore';
import { toast } from 'sonner';
import type { ModelType, NovelListItem } from '@/types/api';
import { useQueryWebSocket } from '@/hooks/useQuery';

export default function HomePage() {
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [appendModalOpen, setAppendModalOpen] = useState(false);
  const [graphModalOpen, setGraphModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedGraphNovelId, setSelectedGraphNovelId] = useState<number | null>(null);
  const [selectedAppendNovel, setSelectedAppendNovel] = useState<NovelListItem | null>(null);
  const [queryText, setQueryText] = useState('');

  const { novels, selectedNovelIds } = useNovelStore();
  const {
    isQuerying,
    currentStage,
    stageProgress,
    thinking = '',
    answer = '',
    citations = [],
    tokenStats,
    queryId,
    rewrittenQuery,
  } = useQueryStore();

  const { executeQuery } = useQueryWebSocket();

  const handleQuery = (query: string, model: ModelType) => {
    if (selectedNovelIds.length === 0) {
      toast.error('请先选择至少一本小说');
      return;
    }

    const completedNovels = novels.filter(
      (n) => selectedNovelIds.includes(n.id) && n.index_status === 'completed'
    );

    if (completedNovels.length === 0) {
      toast.error('选中的小说均未完成索引，请等待索引完成后再查询');
      return;
    }

    const completedIds = completedNovels.map((n) => n.id);
    
    if (completedIds.length < selectedNovelIds.length) {
      toast.info(`已自动过滤 ${selectedNovelIds.length - completedIds.length} 本未完成索引的小说`);
    }

    setQueryText(query);
    executeQuery(completedIds, query, model);
  };

  const handlePresetSelect = (query: string) => {
    setQueryText(query);
  };

  const handleViewGraph = (novelId: number) => {
    setSelectedGraphNovelId(novelId);
    setGraphModalOpen(true);
  };

  const handleAppendChapters = (novel: NovelListItem) => {
    setSelectedAppendNovel(novel);
    setAppendModalOpen(true);
  };

  return (
    <div className="flex h-full bg-background">
      {/* 左侧：小说列表 */}
      <NovelSidebar
        onUploadClick={() => setUploadModalOpen(true)}
        onViewGraphClick={handleViewGraph}
        onHistoryClick={() => setHistoryModalOpen(true)}
        onAppendClick={handleAppendChapters}
      />

      {/* 中间：主界面 */}
      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-background to-background pointer-events-none" />
        
        <div className="relative z-10 flex flex-col h-full max-w-[1600px] mx-auto w-full">
          {/* 上半部分：查询区 (自动收缩) */}
          <div className="flex-shrink-0 px-8 pt-8 pb-4 space-y-6">
            <div className="max-w-3xl mx-auto w-full space-y-6">
              <QueryInput
                value={queryText}
                onChange={setQueryText}
                onQuery={handleQuery}
                isQuerying={isQuerying}
                disabled={selectedNovelIds.length === 0}
              />
              
              {!isQuerying && !answer && (
                <div className="pt-2">
                  <PresetQueries
                    onSelect={handlePresetSelect}
                    disabled={isQuerying || selectedNovelIds.length === 0}
                  />
                </div>
              )}
            </div>

            {/* 查询状态条 - 仅在查询时或有结果时显示 */}
            {(isQuerying || currentStage) && (
              <div className="max-w-3xl mx-auto w-full bg-card/50 backdrop-blur-sm rounded-xl p-4 border border-border/50 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <QueryStages currentStage={currentStage} progress={stageProgress} />
                {rewrittenQuery && (
                  <div className="mt-3 bg-primary/5 rounded-lg border border-primary/10 overflow-hidden">
                    <div className="flex items-start gap-3 px-3 py-2.5 max-h-28 overflow-y-auto">
                      <span className="font-medium text-primary text-xs flex-shrink-0 pt-0.5">优化查询</span>
                      <span className="text-xs text-muted-foreground flex-1 leading-relaxed pr-2">{rewrittenQuery}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 下半部分：结果展示 (Flex Grow) */}
          <div className="flex-1 min-h-0 px-8 pb-8 flex gap-6 overflow-hidden">
            {/* 思考与答案区 */}
            <div className="flex-1 flex flex-col min-w-0 bg-card rounded-2xl shadow-sm border border-border/50 overflow-hidden">
              <ThinkingPanel
                thinking={thinking}
                answer={answer}
                isGenerating={isQuerying && currentStage === 'generating'}
                queryId={queryId}
                className="flex-1 min-h-0"
              />
            </div>

            {/* 右侧边栏：统计与引用 */}
            {(citations.length > 0 || tokenStats) && (
              <div className="w-80 flex-shrink-0 flex flex-col gap-6 animate-in fade-in slide-in-from-right-4 duration-500">
                {/* Token统计 */}
                <div className="bg-card rounded-2xl shadow-sm border border-border/50 p-4 flex-shrink-0">
                  <TokenStats stats={tokenStats} />
                </div>
                
                {/* 引用列表 */}
                <div className="flex-1 min-h-0 bg-card rounded-2xl shadow-sm border border-border/50 overflow-hidden flex flex-col">
                  <CitationList
                    citations={citations}
                    novelId={selectedNovelIds.length > 0 ? selectedNovelIds[0] : null}
                    className="flex-1 min-h-0"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* 弹窗 */}
      <UploadModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
      />
      <AppendChaptersModal
        open={appendModalOpen}
        onOpenChange={setAppendModalOpen}
        novel={selectedAppendNovel}
      />
      <GraphModal
        open={graphModalOpen}
        onOpenChange={setGraphModalOpen}
        novelId={selectedGraphNovelId}
      />
      <QueryHistoryModal
        open={historyModalOpen}
        onOpenChange={setHistoryModalOpen}
        novelId={selectedNovelIds.length > 0 ? selectedNovelIds[0] : null}
      />
    </div>
  );
}
