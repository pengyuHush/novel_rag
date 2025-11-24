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
import { Brain, Sparkles, Maximize2, Copy, ChevronDown, ChevronUp, Loader2, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import { FeedbackButtons } from './FeedbackButtons';
import { cn } from '@/lib/utils';

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
  const [isThinkingCollapsed, setIsThinkingCollapsed] = useState(false);
  const [isAnswerModalOpen, setIsAnswerModalOpen] = useState(false);
  const [thinkingKey, setThinkingKey] = useState(0);
  const hasAnswerStarted = useRef(false);
  const hasThinkingStarted = useRef(false);
  const prevThinkingLength = useRef(0);
  const prevAnswerLength = useRef(0);

  const handleCopy = async () => {
    if (!answer) return;
    try {
      await navigator.clipboard.writeText(answer);
      toast.success('答案已复制');
    } catch (err) {
      console.error('复制失败:', err);
      toast.error('复制失败');
    }
  };

  // 监听查询状态：新查询开始时重置
  useEffect(() => {
    if (isGenerating && !thinking && !answer) {
      setIsThinkingCollapsed(false);
      hasAnswerStarted.current = false;
      hasThinkingStarted.current = false;
      prevThinkingLength.current = 0;
      prevAnswerLength.current = 0;
    }
  }, [isGenerating, thinking, answer]);

  // 思考框展开/折叠时重新渲染 ScrollArea
  useEffect(() => {
    if (!isThinkingCollapsed) {
      // 等待 transition 动画完成后更新 key
      const timer = setTimeout(() => {
        setThinkingKey(prev => prev + 1);
      }, 350);
      return () => clearTimeout(timer);
    }
  }, [isThinkingCollapsed]);

  // 思考阶段逻辑
  useEffect(() => {
    if (thinking && thinking.length > 0) {
      if (!hasThinkingStarted.current) {
        hasThinkingStarted.current = true;
        setIsThinkingCollapsed(false);
      }
      
      if (thinking.length > prevThinkingLength.current) {
        prevThinkingLength.current = thinking.length;
        
        if (isThinkingCollapsed && !hasAnswerStarted.current) {
          setIsThinkingCollapsed(false);
        }
        
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

  // 答案阶段逻辑
  useEffect(() => {
    const thinkingLength = thinking?.length || 0;
    const answerLength = answer?.length || 0;
    
    if (answerLength > 0 && 
        answerLength > prevAnswerLength.current && 
        !hasAnswerStarted.current) {
      
      if (thinkingLength > 0 && thinkingLength === prevThinkingLength.current) {
        setIsThinkingCollapsed(true);
        hasAnswerStarted.current = true;
      }
    }
  }, [thinking, answer]);

  // 答案自动滚动
  useEffect(() => {
    if (answer && answer.length > prevAnswerLength.current) {
      prevAnswerLength.current = answer.length;
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
    <div className={cn("flex flex-col h-full bg-background/50", className)}>
      {/* 思考过程区域 - 可折叠 */}
      <div className={cn(
        "border-b border-border/40 transition-all duration-300 ease-in-out flex flex-col",
        isThinkingCollapsed ? "bg-muted/10 flex-none" : "bg-muted/30 flex-[0.4] max-h-[40vh]"
      )}>
        <div 
          className="flex items-center justify-between px-6 py-3 cursor-pointer hover:bg-muted/40 transition-colors flex-none"
          onClick={() => setIsThinkingCollapsed(!isThinkingCollapsed)}
        >
          <div className="flex items-center gap-2.5 text-sm font-medium text-muted-foreground">
            <Brain className="h-4 w-4 stroke-[1.5]" />
            <span>深度思考</span>
            {isGenerating && thinking && !hasAnswerStarted.current && (
              <Loader2 className="h-3 w-3 animate-spin ml-1" />
            )}
          </div>
          <Button variant="ghost" size="icon" className="h-6 w-6 text-muted-foreground/50">
            {isThinkingCollapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
          </Button>
        </div>

        {!isThinkingCollapsed && (
          <div className="flex-1 px-6 pb-4 min-h-0 overflow-hidden">
            <ScrollArea key={thinkingKey} className="h-full pr-4" ref={thinkingScrollRef}>
              {thinking ? (
                <div className="prose prose-sm max-w-none dark:prose-invert text-muted-foreground/80 leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {thinking}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="flex items-center justify-center min-h-[200px] text-muted-foreground/40 text-sm">
                  等待思考开始...
                </div>
              )}
            </ScrollArea>
          </div>
        )}
      </div>

      {/* 最终答案区域 */}
      <div className="flex-1 flex flex-col min-h-0 relative bg-card">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border/20">
          <div className="flex items-center gap-2.5">
            <Sparkles className="h-4 w-4 text-primary stroke-[1.5]" />
            <h3 className="font-medium">智能回答</h3>
          </div>
          
          {answer && (
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                onClick={handleCopy}
                title="复制"
              >
                <Copy className="h-4 w-4 stroke-[1.5]" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-foreground"
                onClick={() => setIsAnswerModalOpen(true)}
                title="全屏"
              >
                <Maximize2 className="h-4 w-4 stroke-[1.5]" />
              </Button>
            </div>
          )}
        </div>

        <div className="flex-1 overflow-hidden px-6 py-2">
          <ScrollArea className="h-full pr-4" ref={answerScrollRef}>
            {answer ? (
              <div className="prose max-w-none dark:prose-invert py-4 leading-loose text-foreground/90">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {answer}
                </ReactMarkdown>
                {isGenerating && (
                  <span className="inline-block w-1.5 h-4 ml-1 bg-primary/50 animate-pulse rounded-full align-middle"></span>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground/30 gap-4">
                <MessageSquare className="h-12 w-12 stroke-[1]" />
                <p className="text-sm font-light">准备就绪，请开始提问</p>
              </div>
            )}
          </ScrollArea>
        </div>

        {/* 底部反馈栏 */}
        {!isGenerating && answer && queryId && (
          <div className="px-6 py-3 border-t border-border/20 bg-muted/5">
            <FeedbackButtons queryId={queryId} />
          </div>
        )}
      </div>

      {/* 全屏弹窗 */}
      <Dialog open={isAnswerModalOpen} onOpenChange={setIsAnswerModalOpen}>
        <DialogContent className="max-w-5xl h-[90vh] flex flex-col p-0 gap-0 bg-card">
          <DialogHeader className="px-8 py-4 border-b border-border/40">
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              完整回答
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="flex-1 p-8">
            <div className="prose max-w-4xl mx-auto dark:prose-invert">
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
