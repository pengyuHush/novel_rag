/**
 * 思考内容和答案展示面板
 * 支持Markdown渲染和流式输出
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Brain, CheckCircle, Maximize2 } from 'lucide-react';
import { FeedbackButtons } from './FeedbackButtons';

interface ThinkingPanelProps {
  thinking?: string;
  answer?: string;
  isGenerating: boolean;
  queryId?: number | null;
  className?: string;
}

export function ThinkingPanel({
  thinking,
  answer,
  isGenerating,
  queryId,
  className,
}: ThinkingPanelProps) {
  const answerScrollRef = useRef<HTMLDivElement>(null);
  const thinkingScrollRef = useRef<HTMLDivElement>(null);
  const [isThinkingCollapsed, setIsThinkingCollapsed] = useState(false); // 默认展开
  const [isAnswerModalOpen, setIsAnswerModalOpen] = useState(false);
  const hasAnswerStarted = useRef(false);
  const hasThinkingStarted = useRef(false);
  const prevThinkingLength = useRef(0);
  const prevAnswerLength = useRef(0);

  // 监听查询状态：新查询开始时重置
  useEffect(() => {
    if (isGenerating && !thinking && !answer) {
      // 新查询刚开始，重置状态
      console.log('🆕 新查询开始，重置状态，思考框展开');
      setIsThinkingCollapsed(false); // 查询开始时展开思考框，准备显示思考内容
      hasAnswerStarted.current = false;
      hasThinkingStarted.current = false;
      prevThinkingLength.current = 0;
      prevAnswerLength.current = 0;
    }
  }, [isGenerating, thinking, answer]);

  // 【阶段1：思考阶段】当思考内容开始或更新时，保持展开
  useEffect(() => {
    if (thinking && thinking.length > 0) {
      // 思考内容开始
      if (!hasThinkingStarted.current) {
        console.log('💭 【阶段1】思考内容开始，展开思考框');
        hasThinkingStarted.current = true;
        setIsThinkingCollapsed(false);
      }
      
      // 思考内容在增长 - 保持展开状态
      if (thinking.length > prevThinkingLength.current) {
        console.log(`💭 思考内容增长: ${prevThinkingLength.current} -> ${thinking.length}`);
        prevThinkingLength.current = thinking.length;
        
        // 只要思考内容在增长，确保不会被折叠
        if (isThinkingCollapsed && !hasAnswerStarted.current) {
          console.log('💭 思考还在进行，重新展开');
          setIsThinkingCollapsed(false);
        }
        
        // 自动滚动思考内容到底部
        setTimeout(() => {
          if (thinkingScrollRef.current && !isThinkingCollapsed) {
            const scrollElement = thinkingScrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollElement) {
              scrollElement.scrollTop = scrollElement.scrollHeight;
            }
          }
        }, 50);
      }
    }
  }, [thinking, isThinkingCollapsed]);

  // 【阶段2：答案阶段】只有当答案开始增长且思考已停止时，才折叠
  useEffect(() => {
    const thinkingLength = thinking?.length || 0;
    const answerLength = answer?.length || 0;
    
    // 只有同时满足以下条件才折叠：
    // 1. 答案有内容且在增长
    // 2. 答案还没开始过（避免重复触发）
    // 3. 思考长度不再变化（已停止）
    if (answerLength > 0 && 
        answerLength > prevAnswerLength.current && 
        !hasAnswerStarted.current) {
      
      // 检查思考是否真的停止了（长度不再变化）
      if (thinkingLength > 0 && thinkingLength === prevThinkingLength.current) {
        console.log('✨ 【阶段2】思考完成，答案开始输出，自动折叠思考框');
        console.log(`   思考长度: ${thinkingLength}, 答案长度: ${answerLength}`);
        setIsThinkingCollapsed(true);
        hasAnswerStarted.current = true;
      } else {
        console.log(`⏳ 答案开始但思考还在更新，暂不折叠 (思考: ${thinkingLength}, 答案: ${answerLength})`);
      }
    }
  }, [thinking, answer]);

  // 答案内容自动滚动到底部（只在答案内容更新时）
  useEffect(() => {
    if (answer && answer.length > prevAnswerLength.current) {
      prevAnswerLength.current = answer.length;
      
      // 自动滚动答案到底部
      setTimeout(() => {
        if (answerScrollRef.current) {
          const scrollElement = answerScrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
          if (scrollElement) {
            scrollElement.scrollTop = scrollElement.scrollHeight;
          }
        }
      }, 50);
    }
  }, [answer]);

  return (
    <div className={`${className} h-full flex flex-col gap-1.5 p-2`}>
      {/* 思考内容区域 - 始终显示，可折叠 */}
      <Card className="border-muted flex-shrink-0">
        <CardHeader 
          className="pb-1.5 pt-2 px-3 cursor-pointer hover:bg-muted/50 transition-colors"
          onClick={() => setIsThinkingCollapsed(!isThinkingCollapsed)}
        >
          <CardTitle className="text-sm flex items-center gap-2 text-muted-foreground">
            <Brain className="h-3.5 w-3.5" />
            思考过程
            {isGenerating && thinking && !hasAnswerStarted.current && (
              <div className="animate-pulse ml-2 h-2 w-2 rounded-full bg-primary"></div>
            )}
            <span className="text-xs ml-auto">
              {isThinkingCollapsed ? '展开' : '收起'}
            </span>
          </CardTitle>
        </CardHeader>
        {!isThinkingCollapsed && (
          <CardContent className="pb-2 px-3 pt-0">
            <ScrollArea className="h-[180px]" ref={thinkingScrollRef}>
              {thinking ? (
                <div className="prose prose-sm max-w-none dark:prose-invert pr-3">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {thinking}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[180px] text-muted-foreground text-sm">
                  等待思考内容...
                </div>
              )}
            </ScrollArea>
          </CardContent>
        )}
      </Card>

      {/* 最终答案区域 - 始终显示 */}
      <Card className="border-primary flex-1 flex flex-col min-h-0">
        <CardHeader className="pb-1.5 pt-2 px-3 bg-primary/5 flex-shrink-0">
          <CardTitle className="text-base flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            最终答案
            {answer && (
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-6 px-2"
                onClick={() => setIsAnswerModalOpen(true)}
              >
                <Maximize2 className="h-3.5 w-3.5" />
              </Button>
            )}
            {isGenerating && hasAnswerStarted.current && (
              <div className="animate-pulse ml-auto h-2 w-2 rounded-full bg-primary"></div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2 pb-2 px-3 flex-1 min-h-0 flex flex-col overflow-hidden">
          <div className="flex-1 min-h-0">
            <ScrollArea className="h-full" ref={answerScrollRef}>
              {answer ? (
                <div className="prose prose-sm max-w-none dark:prose-invert pr-3">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {answer}
                  </ReactMarkdown>
                  {isGenerating && (
                    <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse">▋</span>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  <div className="text-center">
                    <Brain className="h-10 w-10 mx-auto mb-3 opacity-20" />
                    <p className="text-sm">
                      {isGenerating ? '正在生成答案...' : '选择小说并输入问题开始查询'}
                    </p>
                  </div>
                </div>
              )}
            </ScrollArea>
          </div>
          {/* 反馈按钮 - 只在查询完成且有答案时显示 */}
          {!isGenerating && answer && queryId && (
            <div className="flex-shrink-0 mt-2">
              <FeedbackButtons queryId={queryId} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 答案全屏展示弹窗 */}
      <Dialog open={isAnswerModalOpen} onOpenChange={setIsAnswerModalOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              最终答案
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="max-h-[calc(90vh-100px)] mt-4">
            <div className="prose prose-sm max-w-none dark:prose-invert p-6">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {answer || ''}
              </ReactMarkdown>
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}

