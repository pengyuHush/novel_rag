/**
 * 查询反馈按钮组件
 * 允许用户对答案的准确性进行反馈
 */

'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { api } from '@/lib/api';

interface FeedbackButtonsProps {
  queryId: number;
  disabled?: boolean;
}

export function FeedbackButtons({ queryId, disabled }: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);
  const [showNoteDialog, setShowNoteDialog] = useState(false);
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePositiveFeedback = async () => {
    try {
      setIsSubmitting(true);
      await api.submitFeedback(queryId, 'positive', undefined);
      setFeedback('positive');
      toast.success('感谢您的反馈！');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('提交反馈失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNegativeFeedback = () => {
    setShowNoteDialog(true);
  };

  const handleSubmitNote = async () => {
    try {
      setIsSubmitting(true);
      await api.submitFeedback(queryId, 'negative', note || undefined);
      setFeedback('negative');
      setShowNoteDialog(false);
      setNote('');
      toast.success('感谢您的反馈！');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('提交反馈失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="flex items-center gap-3 pt-4 border-t">
        <span className="text-sm text-muted-foreground">这个答案准确吗？</span>
        <div className="flex gap-2">
          <Button
            variant={feedback === 'positive' ? 'default' : 'outline'}
            size="sm"
            onClick={handlePositiveFeedback}
            disabled={disabled || isSubmitting || feedback !== null}
            className="gap-1"
          >
            <ThumbsUp className="h-4 w-4" />
            准确
          </Button>
          <Button
            variant={feedback === 'negative' ? 'destructive' : 'outline'}
            size="sm"
            onClick={handleNegativeFeedback}
            disabled={disabled || isSubmitting || feedback !== null}
            className="gap-1"
          >
            <ThumbsDown className="h-4 w-4" />
            不准确
          </Button>
        </div>
        {feedback && (
          <span className="text-sm text-green-600">
            ✓ 已提交反馈
          </span>
        )}
      </div>

      <Dialog open={showNoteDialog} onOpenChange={setShowNoteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>反馈详情</DialogTitle>
            <DialogDescription>
              请告诉我们答案哪里不准确，以便我们改进（可选）
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder="例如：答案中的时间信息有误、缺少关键情节等..."
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={4}
            maxLength={500}
          />
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowNoteDialog(false)}
              disabled={isSubmitting}
            >
              取消
            </Button>
            <Button
              onClick={handleSubmitNote}
              disabled={isSubmitting}
            >
              {isSubmitting ? '提交中...' : '提交'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

