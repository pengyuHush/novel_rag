/**
 * 顶部导航栏
 * 显示网站标题"志异全考"和设置按钮
 */

'use client';

import Link from 'next/link';
import { Settings, History } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  onHistoryClick?: () => void;
}

export function Header({ onHistoryClick }: HeaderProps) {
  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center justify-between px-6">
        {/* 网站标题 */}
        <Link href="/" className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold tracking-tight">志异全考</h1>
        </Link>

        {/* 右侧按钮组 */}
        <div className="flex items-center gap-2">
          {onHistoryClick && (
            <Button variant="ghost" size="icon" onClick={onHistoryClick}>
              <History className="h-5 w-5" />
              <span className="sr-only">查询历史</span>
            </Button>
          )}
        <Link href="/settings">
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
            <span className="sr-only">设置</span>
          </Button>
        </Link>
        </div>
      </div>
    </header>
  );
}

