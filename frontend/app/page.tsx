'use client';

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            网络小说智能问答系统
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            基于 RAG 技术的新一代小说阅读助手
          </p>
          
          <div className="flex gap-4 justify-center mb-12">
            <Link href="/novels">
              <button className="px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
                开始使用
              </button>
            </Link>
            <Link href="/query">
              <button className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors">
                智能问答
              </button>
            </Link>
          </div>
        </div>
        
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          <FeatureCard
            title="📚 小说管理"
            description="上传和管理您的小说库，支持TXT和EPUB格式，自动识别章节"
            link="/novels"
          />
          <FeatureCard
            title="🤖 智能问答"
            description="基于RAG技术，精准回答小说相关问题，支持流式输出"
            link="/query"
          />
          <FeatureCard
            title="🕸️ 知识图谱"
            description="自动构建人物关系和事件图谱（即将推出）"
            link="#"
          />
          <FeatureCard
            title="🔍 矛盾检测"
            description="智能发现剧情中的逻辑矛盾（即将推出）"
            link="#"
          />
          <FeatureCard
            title="📊 数据统计"
            description="Token使用和费用统计（即将推出）"
            link="#"
          />
          <FeatureCard
            title="🎯 高性能"
            description="优化的检索和生成流程，支持500万字小说"
            link="#"
          />
        </div>
      </main>
      
      <footer className="text-center py-8 text-sm text-gray-500">
        Powered by 智谱AI · FastAPI · Next.js · ChromaDB
      </footer>
    </div>
  );
}

function FeatureCard({ title, description, link }: { title: string; description: string; link: string }) {
  const content = (
    <div className="p-6 border rounded-lg hover:shadow-lg transition-all bg-white h-full hover:border-blue-400">
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
  
  if (link === '#') {
    return content;
  }
  
  return <Link href={link}>{content}</Link>;
}
