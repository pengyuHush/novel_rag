'use client';

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">
          网络小说智能问答系统
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          基于RAG架构的网络小说智能问答系统
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 border rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-2">📚 小说管理</h2>
            <p className="text-gray-600">上传并管理您的小说文件</p>
          </div>
          
          <div className="p-6 border rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-2">💬 智能问答</h2>
            <p className="text-gray-600">对小说内容进行智能提问</p>
          </div>
          
          <div className="p-6 border rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-2">📖 在线阅读</h2>
            <p className="text-gray-600">按章节浏览小说内容</p>
          </div>
          
          <div className="p-6 border rounded-lg shadow-sm">
            <h2 className="text-2xl font-semibold mb-2">🕸️ 知识图谱</h2>
            <p className="text-gray-600">查看角色关系和时间线</p>
          </div>
        </div>
        
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800">
            ✅ 系统已初始化，请启动后端服务器
          </p>
        </div>
      </div>
    </main>
  );
}

