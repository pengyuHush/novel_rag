/**
 * 小说上传弹窗
 * 支持文件拖拽上传和实时进度展示
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { createProgressWebSocket, ProgressWebSocket } from '@/lib/websocket';
import { useNovelStore } from '@/store/novelStore';
import { toast } from 'sonner';

interface UploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function UploadModal({ open, onOpenChange }: UploadModalProps) {
  const [step, setStep] = useState<'select' | 'uploading' | 'indexing' | 'completed'>('select');
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [novelId, setNovelId] = useState<number | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [indexingDetail, setIndexingDetail] = useState<any>(null); // 索引详情
  const [completedStats, setCompletedStats] = useState<any>(null); // 完成后的统计

  const { addNovel, updateNovel } = useNovelStore();

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
    if (step === 'indexing' && indexingDetail?.steps) {
      const processingIdx = indexingDetail.steps.findIndex((s: any) => s.status === 'processing');
      if (processingIdx >= 0) {
        const element = document.getElementById(`step-${processingIdx}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    }
  }, [step, indexingDetail]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // 从文件名提取书名
      const fileName = selectedFile.name.replace(/\.(txt|epub)$/i, '');
      setTitle(fileName);
    }
  };

  const handleUpload = async () => {
    if (!file || !title) {
      toast.error('请选择文件并填写书名');
      return;
    }

    try {
      setStep('uploading');
      setProgress(0);
      setProgressMessage('正在上传文件...');

      // 上传文件
      const response = await api.uploadNovel(file, title, author || undefined);
      setNovelId(response.id);
      
      // 添加到小说列表（初始数据可能不完整，后续轮询会更新）
      addNovel({
        id: response.id,
        title: response.title,
        author: response.author,
        total_chars: response.total_chars || 0,
        total_chapters: response.total_chapters || 0,
        index_status: response.index_status,
        index_progress: response.index_progress,
        file_format: response.file_format,
        upload_date: response.upload_date,
      });

      setStep('indexing');
      setProgress(0);
      setProgressMessage('开始索引...');
      
      toast.success('文件上传成功，开始索引...');

      // 清理之前的轮询（如果有）
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }

      // 使用轮询获取索引进度（避免WebSocket事件循环冲突）
      pollIntervalRef.current = setInterval(async () => {
        try {
          const progressData = await api.getNovelProgress(response.id);
          setProgress(progressData.progress);
          setProgressMessage(`${progressData.message} (${(progressData.progress * 100).toFixed(0)}%)`);
          
          // 更新详细信息（如果有）
          if (progressData.detail) {
            setIndexingDetail(progressData.detail);
          }
          
          // 更新store中的小说状态（包含章节数等信息）
          updateNovel(response.id, {
            index_status: progressData.status,
            index_progress: progressData.progress,
            total_chapters: progressData.total_chapters || 0,
            total_chars: progressData.total_chars || 0,
          });
          
          // 检查是否完成
          if (progressData.status === 'completed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            
            // 获取Token统计
            try {
              const tokenStats = await api.getTokenStats({ period: 'all' });
              setCompletedStats({
                totalChapters: progressData.total_chapters,
                tokenStats: progressData.detail?.token_stats || tokenStats,
                failedChapters: progressData.detail?.failed_chapters || [],
                warnings: progressData.detail?.warnings || []
              });
            } catch (e) {
              console.error('Failed to get token stats:', e);
            }
            
          setStep('completed');
          setProgress(1);
          setProgressMessage('索引完成！');
          toast.success('小说索引完成');
          } else if (progressData.status === 'failed') {
            if (pollIntervalRef.current) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
            }
            
            // 保存失败信息
            if (progressData.detail) {
              setCompletedStats({
                failed: true,
                error: progressData.message,
                failedChapters: progressData.detail.failed_chapters || []
              });
            }
            
            toast.error('索引失败');
          setStep('select');
          }
        } catch (error) {
          console.error('Failed to fetch progress:', error);
        }
      }, 1500); // 每1.5秒轮询一次

    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('上传失败，请重试');
      setStep('select');
    }
  };

  const handleClose = () => {
    if (step !== 'indexing') {
      onOpenChange(false);
      // 重置状态
      setTimeout(() => {
        setStep('select');
        setFile(null);
        setTitle('');
        setAuthor('');
        setProgress(0);
        setProgressMessage('');
        setNovelId(null);
      }, 300);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>上传小说</DialogTitle>
          <DialogDescription>
            支持TXT和EPUB格式，单本最大1000万字
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 文件选择 */}
          {step === 'select' && (
            <>
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    点击选择或拖拽文件到此处
                  </p>
                  {file && (
                    <div className="mt-4 flex items-center justify-center gap-2 text-sm">
                      <FileText className="h-4 w-4" />
                      <span>{file.name}</span>
                    </div>
                  )}
                </label>
                <input
                  id="file-upload"
                  type="file"
                  accept=".txt,.epub"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">书名 *</label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="请输入小说名称"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">作者</label>
                <Input
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  placeholder="请输入作者名称（可选）"
                />
              </div>

              <Button
                onClick={handleUpload}
                disabled={!file || !title}
                className="w-full"
                size="lg"
              >
                开始上传
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
              <p className="text-xs text-center text-muted-foreground">
                {(progress * 100).toFixed(0)}%
              </p>
            </div>
          )}

          {/* 索引进度 - 显示详细步骤 */}
              {step === 'indexing' && (
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
              {indexingDetail?.steps && indexingDetail.steps.length > 0 && (
                <div className="space-y-2 p-4 bg-muted/30 rounded-lg max-h-48 overflow-y-auto" id="steps-container">
                  <h4 className="text-sm font-semibold mb-2">处理步骤</h4>
                  {indexingDetail.steps.map((step, idx) => (
                    <div 
                      key={idx} 
                      id={`step-${idx}`}
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
                  索引中，请勿关闭此窗口
                </p>
            </div>
          )}

          {/* 完成 */}
          {step === 'completed' && (
            <div className="space-y-4">
              <div className="text-center space-y-3">
              <CheckCircle className="mx-auto h-16 w-16 text-green-600" />
              <p className="text-lg font-medium">上传完成！</p>
              <p className="text-sm text-muted-foreground">
                小说已成功索引，现在可以开始查询
              </p>
              </div>
              
              {/* Token统计 */}
              {completedStats?.tokenStats && (
                <div className="space-y-3 p-4 bg-muted/30 rounded-lg">
                  <h4 className="font-semibold text-sm">Token消耗统计</h4>
                  
                  {/* 总计 */}
                  <div className="grid grid-cols-3 gap-2 text-xs p-2 bg-background rounded border">
                    <div>
                      <div className="text-muted-foreground">输入Token</div>
                      <div className="font-semibold">{completedStats.tokenStats.total?.input_tokens?.toLocaleString() || 0}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">总Token</div>
                      <div className="font-semibold text-primary">{completedStats.tokenStats.total?.total_tokens?.toLocaleString() || 0}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">预估成本</div>
                      <div className="font-semibold text-green-600">¥{completedStats.tokenStats.total?.estimated_cost?.toFixed(4) || '0.0000'}</div>
                    </div>
                  </div>
                  
                  {/* 分步骤详情 */}
                  {completedStats.tokenStats.steps && completedStats.tokenStats.steps.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-xs font-medium text-muted-foreground">分步骤详情：</div>
                      <div className="max-h-32 overflow-y-auto space-y-1">
                        {completedStats.tokenStats.steps.map((step: any, idx: number) => (
                          <div key={idx} className="text-xs p-2 bg-background rounded flex justify-between items-center">
                            <div className="flex-1">
                              <span className="font-medium">{step.step}</span>
                              <span className="text-muted-foreground ml-2">({step.model})</span>
                            </div>
                            <div className="flex gap-3 text-right">
                              <span className="text-muted-foreground">{step.total_tokens.toLocaleString()} tokens</span>
                              <span className="text-green-600">¥{step.cost.toFixed(4)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="text-xs text-muted-foreground">
                    总章节：{completedStats.totalChapters || 0}
                  </div>
                </div>
              )}
              
              {/* 失败章节 */}
              {completedStats?.failedChapters && completedStats.failedChapters.length > 0 && (
                <div className="space-y-2 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                  <h4 className="font-semibold text-sm text-destructive">处理失败的章节 ({completedStats.failedChapters.length})</h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {completedStats.failedChapters.map((chapter: any, idx: number) => (
                      <div key={idx} className="text-xs">
                        <span className="font-medium">第{chapter.chapter_num}章</span>
                        {chapter.chapter_title && <span className="text-muted-foreground"> - {chapter.chapter_title}</span>}
                        <p className="text-destructive ml-4">{chapter.error}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* 警告信息 */}
              {completedStats?.warnings && completedStats.warnings.length > 0 && (
                <div className="space-y-2 p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                  <h4 className="font-semibold text-sm text-yellow-700">警告 ({completedStats.warnings.length})</h4>
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

