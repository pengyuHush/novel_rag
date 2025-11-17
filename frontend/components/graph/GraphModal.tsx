/**
 * 图谱可视化弹窗
 * 包含关系图谱和时间线两个标签页
 */

'use client';

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RelationGraph } from './RelationGraph';
import { Timeline } from './Timeline';

interface GraphModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  novelId: number | null;
}

export function GraphModal({ open, onOpenChange, novelId }: GraphModalProps) {
  if (!novelId) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent 
        className="!max-w-[98vw] w-[1400px] h-[92vh] flex flex-col p-4"
        data-resizable-dialog
      >
        <DialogHeader className="flex-shrink-0 pb-2">
          <DialogTitle className="text-lg">可视化分析</DialogTitle>
          <DialogDescription className="text-sm">
            查看角色关系图谱和事件时间线（可拖动右下角调整大小）
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="relations" className="flex-1 flex flex-col min-h-0 mt-2">
          <TabsList className="grid w-full grid-cols-2 flex-shrink-0">
            <TabsTrigger value="relations">角色关系图</TabsTrigger>
            <TabsTrigger value="timeline">时间线</TabsTrigger>
          </TabsList>

          <TabsContent value="relations" className="flex-1 min-h-0 mt-3">
            <RelationGraph novelId={novelId} />
          </TabsContent>

          <TabsContent value="timeline" className="flex-1 min-h-0 mt-3">
            <Timeline novelId={novelId} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

