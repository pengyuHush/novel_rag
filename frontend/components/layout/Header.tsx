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
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-background/80 border-b border-border/40 supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-8 max-w-[1920px] mx-auto">
        {/* 网站标题 */}
        <Link href="/" className="flex items-center space-x-2 transition-opacity hover:opacity-80">
          <h1 className="text-lg font-bold tracking-widest uppercase text-foreground/90">志异全考</h1>
        </Link>

        {/* 右侧按钮组 */}
        <div className="flex items-center gap-4">
          {onHistoryClick && (
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={onHistoryClick}
              className="text-muted-foreground hover:text-foreground hover:bg-transparent"
            >
              <History className="h-5 w-5 stroke-[1.5]" />
              <span className="sr-only">查询历史</span>
            </Button>
          )}
        <Link href="/settings">
          <Button 
            variant="ghost" 
            size="icon"
            className="text-muted-foreground hover:text-foreground hover:bg-transparent"
          >
            <Settings className="h-5 w-5 stroke-[1.5]" />
            <span className="sr-only">设置</span>
          </Button>
        </Link>
        </div>
      </div>
    </header>
  );
}
