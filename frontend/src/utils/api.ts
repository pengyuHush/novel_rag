import type {
  Novel,
  Chapter,
  ChapterContent,
  SearchResult,
  CharacterGraph,
  NovelProcessingStatus,
  Reference
} from '../types';

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// 通用请求函数
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData.code
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(`Network error: ${error.message}`, 0, 'NETWORK_ERROR');
  }
}

// 自定义错误类
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// 小说管理API
export const novelAPI = {
  // 获取所有小说
  async getAllNovels(): Promise<Novel[]> {
    return apiRequest<Novel[]>('/novels');
  },

  // 获取单个小说详情
  async getNovel(id: string): Promise<Novel> {
    return apiRequest<Novel>(`/novels/${id}`);
  },

  // 创建小说记录（步骤1：创建元数据）
  async createNovel(metadata: {
    title: string;
    author?: string;
    description?: string;
    tags?: string[];
  }): Promise<Novel> {
    const response = await apiRequest<{ message: string; novel: Novel }>('/novels', {
      method: 'POST',
      body: JSON.stringify(metadata),
    });
    return response.novel;
  },

  // 上传小说文件（步骤2：上传文本内容）
  async uploadNovelFile(novelId: string, file: File): Promise<{ message: string; status: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/novels/${novelId}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `Upload failed: ${response.statusText}`,
        response.status
      );
    }

    return response.json();
  },

  // 便捷方法：一步完成小说上传（供组件使用）
  async uploadNovel(file: File, metadata: {
    title: string;
    author?: string;
    description?: string;
    tags?: string[];
  }): Promise<string> {
    // 先创建小说记录
    const novel = await this.createNovel(metadata);
    
    // 再上传文件
    await this.uploadNovelFile(novel.id, file);
    
    return novel.id;
  },

  // 更新小说信息
  async updateNovel(id: string, updates: Partial<Novel>): Promise<Novel> {
    return apiRequest<Novel>(`/novels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // 删除小说
  async deleteNovel(id: string): Promise<void> {
    return apiRequest<void>(`/novels/${id}`, {
      method: 'DELETE',
    });
  },

  // 获取小说处理状态
  async getProcessingStatus(id: string): Promise<NovelProcessingStatus> {
    return apiRequest<NovelProcessingStatus>(`/novels/${id}/status`);
  },

  // 文件预验证（上传前快速检查文件是否合格）
  async validateFile(novelId: string, file: File): Promise<{
    valid: boolean;
    encoding?: string;
    wordCount?: number;
    chineseRatio?: number;
    estimatedChapters?: number;
    warnings: string[];
    errors: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/novels/${novelId}/validate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.message || `Validation failed: ${response.statusText}`,
        response.status
      );
    }

    return response.json();
  },

  // 获取小说章节列表
  async getChapters(novelId: string): Promise<Chapter[]> {
    return apiRequest<Chapter[]>(`/novels/${novelId}/chapters`);
  },

  // 获取单个章节内容（包含段落信息）
  async getChapter(novelId: string, chapterId: string): Promise<ChapterContent> {
    return apiRequest<ChapterContent>(`/novels/${novelId}/chapters/${chapterId}`);
  }
};

// 搜索和问答API
export const searchAPI = {
  // 执行搜索（使用POST方法 + JSON Body）
  async search(params: {
    query: string;
    novelIds?: string[];
    topK?: number;
    includeReferences?: boolean;
    saveHistory?: boolean;
  }): Promise<SearchResult> {
    return apiRequest<SearchResult>('/search', {
      method: 'POST',
      body: JSON.stringify({
        query: params.query,
        novelIds: params.novelIds || [],
        topK: params.topK || 5,
        includeReferences: params.includeReferences !== false,
        saveHistory: params.saveHistory !== false,
      }),
    });
  }
};

// 人物关系图谱API
export const graphAPI = {
  // 获取人物关系图谱
  async getGraph(novelId: string): Promise<CharacterGraph> {
    return apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
  },

  // 生成人物关系图谱
  async generateGraph(novelId: string): Promise<{ taskId: string }> {
    return apiRequest<{ taskId: string }>(`/novels/${novelId}/graph`, {
      method: 'POST',
    });
  },

  // 删除人物关系图谱
  async deleteGraph(novelId: string): Promise<void> {
    return apiRequest<void>(`/novels/${novelId}/graph`, {
      method: 'DELETE',
    });
  },

  // 获取人物列表
  async getCharacters(novelId: string): Promise<CharacterGraph['characters']> {
    const graph = await apiRequest<CharacterGraph>(`/novels/${novelId}/graph`);
    return graph.characters;
  }
};

// 系统管理API
export const systemAPI = {
  // 系统健康检查
  async checkHealth(): Promise<{
    status: string;
    version: string;
    services: Record<string, string>;
  }> {
    return apiRequest('/system/health');
  },

  // 系统信息
  async getSystemInfo(): Promise<{
    version: string;
    features: string[];
    limits: {
      maxFileSize: number;
      maxNovels: number;
    };
  }> {
    return apiRequest('/system/info');
  }
};

// 工具函数
export const apiUtils = {
  // 文件大小格式化
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  },

  // 字数格式化
  formatWordCount(count: number): string {
    if (count < 10000) {
      return count + '字';
    }
    return Math.round(count / 10000 * 10) / 10 + '万字';
  },

  // 获取小说统计信息
  async getStorageInfo(): Promise<{
    novelCount: number;
    totalWords: number;
    totalSize: number;
    formattedSize: string;
  }> {
    const novels = await novelAPI.getAllNovels();
    const novelCount = novels.length;
    const totalWords = novels.reduce((sum, novel) => sum + novel.wordCount, 0);

    // 估算文件大小（假设平均每个字符占用2字节）
    const totalSize = totalWords * 2;

    return {
      novelCount,
      totalWords,
      totalSize,
      formattedSize: this.formatFileSize(totalSize)
    };
  },

  // 轮询任务状态
  async pollStatus(
    novelId: string,
    onProgress?: (status: NovelProcessingStatus) => void,
    interval: number = 2000
  ): Promise<NovelProcessingStatus> {
    while (true) {
      const status = await novelAPI.getProcessingStatus(novelId);

      if (onProgress) {
        onProgress(status);
      }

      if (status.status === 'completed' || status.status === 'failed') {
        return status;
      }

      // 等待指定时间间隔后继续轮询
      await new Promise(resolve => setTimeout(resolve, interval));
    }
  }
};