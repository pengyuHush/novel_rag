/**
 * 顶部导航栏
 * 显示网站标题"志异全考"和设置按钮
 */

'use client';

import Link from 'next/link';
import { Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center justify-between px-6">
        {/* 网站标题 */}
        <Link href="/" className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold tracking-tight">志异全考</h1>
        </Link>

        {/* 右侧设置按钮 */}
        <Link href="/settings">
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
            <span className="sr-only">设置</span>
          </Button>
        </Link>
      </div>
    </header>
  );
}

