/**
 * 追加章节弹窗
 * 用于向已索引的小说追加新章节
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { useNovelStore } from '@/store/novelStore';
import { toast } from 'sonner';
import type { NovelListItem } from '@/types/api';

interface AppendChaptersModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  novel: NovelListItem | null;
}

export function AppendChaptersModal({ open, onOpenChange, novel }: AppendChaptersModalProps) {
  const [step, setStep] = useState<'select' | 'uploading' | 'processing' | 'completed'>('select');
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [processingDetail, setProcessingDetail] = useState<any>(null);
  const [completedStats, setCompletedStats] = useState<any>(null);

  const { updateNovel } = useNovelStore();

  // 清理轮询定时器
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // 自动滚动到当前处理的步骤
  useEffect(() => {
    if (step === 'processing' && processingDetail?.steps) {
      const processingIdx = processingDetail.steps.findIndex((s: any) => s.status === 'processing');
      if (processingIdx >= 0) {
        const element = document.getElementById(`append-step-${processingIdx}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    }
  }, [step, processingDetail]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleAppend = async () => {
    if (!file || !novel) {
      toast.error('请选择文件');
      return;
    }

    try {
      setStep('uploading');
      setProgress(0);
      setProgressMessage('正在上传文件...');

      // 上传文件
      const response = await api.appendChapters(novel.id, file);
      
      // 更新小说状态
      updateNovel(novel.id, {
        index_status: response.index_status,
        index_progress: response.index_progress,
      });

      setStep('processing');
      setProgress(0);
      setProgressMessage('开始处理新章节...');
      
      toast.success('文件上传成功，开始处理新章节...');

      // 清理之前的轮询
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }

      // 轮询获取处理进度
      pollIntervalRef.current = setInterval(async () => {
        try {
          const progressData = await api.getNovelProgress(novel.id);
          setProgress(progressData.progress);
          setProgressMessage(`${progressData.message} (${(progressData.progress * 100).toFixed(0)}%)`);
          
          // 更新详细信息
          if (progressData.detail) {
            setProcessingDetail(progressData.detail);
          }
          
          // 更新store中的小说状态
          updateNovel(novel.id, {
            index_status: progressData.status,
            index_progress: progressData.progress,
            total_chapters: progressData.total_chapters || novel.total_chapters,
            total_chars: progressData.total_chars || novel.total_chars,
          });
          
          // 检查是否完成
          if (progressData.status === 'completed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            
            // 获取统计信息
            setCompletedStats({
              newChapters: progressData.total_chapters - novel.total_chapters,
              totalChapters: progressData.total_chapters,
              tokenStats: progressData.detail?.token_stats,
              failedChapters: progressData.detail?.failed_chapters || [],
              warnings: progressData.detail?.warnings || []
            });
            
            setStep('completed');
            setProgress(1);
            setProgressMessage('追加章节完成！');
            toast.success('追加章节完成');
          } else if (progressData.status === 'failed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            
            toast.error('追加章节失败');
            setStep('select');
          }
        } catch (error) {
          console.error('Failed to fetch progress:', error);
        }
      }, 1500);

    } catch (error: any) {
      console.error('Append failed:', error);
      const errorMsg = error.response?.data?.detail || '追加章节失败，请重试';
      toast.error(errorMsg);
      setStep('select');
    }
  };

  const handleClose = () => {
    if (step !== 'processing') {
      onOpenChange(false);
      // 重置状态
      setTimeout(() => {
        setStep('select');
        setFile(null);
        setProgress(0);
        setProgressMessage('');
        setProcessingDetail(null);
        setCompletedStats(null);
      }, 300);
    }
  };

  if (!novel) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>追加章节 - {novel.title}</DialogTitle>
          <DialogDescription>
            上传包含所有章节（旧+新）的完整文件，系统会自动跳过已索引的章节
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 提示信息 */}
          {step === 'select' && (
            <div className="flex items-start gap-2 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm space-y-1">
                <p className="font-medium text-blue-900">注意事项：</p>
                <ul className="text-blue-700 space-y-1 ml-4 list-disc">
                  <li>上传的文件必须包含所有章节（已有的+新增的）</li>
                  <li>文件格式必须与原文件一致（{novel.file_format.toUpperCase()}）</li>
                  <li>系统会自动识别并只处理新章节</li>
                  <li>当前小说有 {novel.total_chapters} 章</li>
                </ul>
              </div>
            </div>
          )}

          {/* 文件选择 */}
          {step === 'select' && (
            <>
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors">
                <label htmlFor="append-file-upload" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    点击选择或拖拽 {novel.file_format.toUpperCase()} 文件到此处
                  </p>
                  {file && (
                    <div className="mt-4 flex items-center justify-center gap-2 text-sm">
                      <FileText className="h-4 w-4" />
                      <span>{file.name}</span>
                    </div>
                  )}
                </label>
                <input
                  id="append-file-upload"
                  type="file"
                  accept={novel.file_format === 'txt' ? '.txt' : '.epub'}
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              <Button
                onClick={handleAppend}
                disabled={!file}
                className="w-full"
                size="lg"
              >
                开始追加章节
              </Button>
            </>
          )}

          {/* 上传进度 */}
          {step === 'uploading' && (
            <div className="space-y-4">
              <Progress value={progress * 100} className="h-2" />
              <p className="text-sm text-center text-muted-foreground">
                {progressMessage}
              </p>
            </div>
          )}

          {/* 处理进度 */}
          {step === 'processing' && (
            <div className="space-y-4">
              {/* 总体进度 */}
              <div className="space-y-2">
                <Progress value={progress * 100} className="h-2" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{progressMessage}</span>
                  <span>{(progress * 100).toFixed(0)}%</span>
                </div>
              </div>

              {/* 详细步骤 */}
              {processingDetail?.steps && processingDetail.steps.length > 0 && (
                <div className="space-y-2 p-4 bg-muted/30 rounded-lg max-h-48 overflow-y-auto">
                  <h4 className="text-sm font-semibold mb-2">处理步骤</h4>
                  {processingDetail.steps.map((step: any, idx: number) => (
                    <div 
                      key={idx} 
                      id={`append-step-${idx}`}
                      className="flex items-center gap-3 text-sm"
                    >
                      {/* 状态图标 */}
                      {step.status === 'completed' && (
                        <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                      )}
                      {step.status === 'processing' && (
                        <div className="h-4 w-4 flex-shrink-0">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent"></div>
                        </div>
                      )}
                      {step.status === 'failed' && (
                        <XCircle className="h-4 w-4 text-destructive flex-shrink-0" />
                      )}
                      {step.status === 'pending' && (
                        <div className="h-4 w-4 rounded-full border-2 border-muted-foreground flex-shrink-0"></div>
                      )}
                      
                      {/* 步骤信息 */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`font-medium ${
                            step.status === 'processing' ? 'text-primary' : 
                            step.status === 'completed' ? 'text-green-600' :
                            step.status === 'failed' ? 'text-destructive' :
                            'text-muted-foreground'
                          }`}>
                            {step.name}
                          </span>
                          {step.status === 'processing' && step.progress > 0 && (
                            <span className="text-xs text-muted-foreground">
                              {(step.progress * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground truncate">
                          {step.message}
                        </p>
                        {step.error && (
                          <p className="text-xs text-destructive mt-1">{step.error}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <p className="text-xs text-center text-yellow-600">
                处理中，请勿关闭此窗口
              </p>
            </div>
          )}

          {/* 完成 */}
          {step === 'completed' && (
            <div className="space-y-4">
              <div className="text-center space-y-3">
                <CheckCircle className="mx-auto h-16 w-16 text-green-600" />
                <p className="text-lg font-medium">追加章节完成！</p>
                <p className="text-sm text-muted-foreground">
                  新增 {completedStats?.newChapters || 0} 章，
                  总计 {completedStats?.totalChapters || 0} 章
                </p>
              </div>
              
              {/* Token统计 */}
              {completedStats?.tokenStats && (
                <div className="space-y-2 p-4 bg-muted/30 rounded-lg">
                  <h4 className="font-semibold text-sm">Token消耗统计</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 bg-background rounded">
                      <div className="text-muted-foreground">总Token</div>
                      <div className="font-semibold text-primary">
                        {completedStats.tokenStats.totalTokens?.toLocaleString() || 0}
                      </div>
                    </div>
                    <div className="p-2 bg-background rounded">
                      <div className="text-muted-foreground">预估成本</div>
                      <div className="font-semibold text-green-600">
                        ¥{completedStats.tokenStats.embeddingTokens ? 
                          (completedStats.tokenStats.embeddingTokens * 0.0001 / 1000).toFixed(4) : '0.0000'}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* 失败章节 */}
              {completedStats?.failedChapters && completedStats.failedChapters.length > 0 && (
                <div className="space-y-2 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                  <h4 className="font-semibold text-sm text-destructive">
                    处理失败的章节 ({completedStats.failedChapters.length})
                  </h4>
                  <div className="space-y-1 max-h-24 overflow-y-auto">
                    {completedStats.failedChapters.map((chapter: any, idx: number) => (
                      <div key={idx} className="text-xs">
                        <span className="font-medium">第{chapter.chapter_num}章</span>
                        {chapter.chapter_title && <span> - {chapter.chapter_title}</span>}
                        <p className="text-destructive ml-4">{chapter.error}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* 警告信息 */}
              {completedStats?.warnings && completedStats.warnings.length > 0 && (
                <div className="space-y-2 p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                  <h4 className="font-semibold text-sm text-yellow-700">
                    警告 ({completedStats.warnings.length})
                  </h4>
                  <div className="space-y-1 max-h-24 overflow-y-auto">
                    {completedStats.warnings.map((warning: string, idx: number) => (
                      <p key={idx} className="text-xs text-yellow-700">{warning}</p>
                    ))}
                  </div>
                </div>
              )}
              
              <Button onClick={handleClose} className="w-full" size="lg">
                关闭
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

