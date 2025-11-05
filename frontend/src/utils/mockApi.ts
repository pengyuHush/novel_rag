/**
 * Mock API 实现
 * 用于前端独立开发和功能预览
 */

import type { 
  Novel, 
  Chapter, 
  ChapterContent,
  SearchResult, 
  CharacterGraph,
  NovelProcessingStatus,
  ChapterWithoutContent
} from '../types';

import { 
  MOCK_NOVELS, 
  generateMockSearchResult, 
  generateMockCharacterGraph,
  generateMockChapterContent,
  generateMockProcessingStatus,
  mockDelay
} from './mockData';

// Mock 数据存储（模拟数据库）
let mockNovels = [...MOCK_NOVELS];
let mockGraphs: Record<string, CharacterGraph> = {};

/**
 * Mock Novel API
 */
export const mockNovelAPI = {
  /**
   * 上传小说
   */
  async uploadNovel(formData: FormData): Promise<{ novelId: string; taskId: string }> {
    await mockDelay(800);
    
    const file = formData.get('file') as File;
    const title = formData.get('title') as string || file.name.replace('.txt', '');
    const author = formData.get('author') as string || '未知作者';
    const description = formData.get('description') as string || '';
    const tags = formData.get('tags') as string || '';
    
    const novelId = `novel-${Date.now()}`;
    const taskId = `task-${Date.now()}`;
    
    const newNovel: Novel = {
      id: novelId,
      title,
      author,
      description,
      tags: tags ? tags.split(',') : [],
      content: '（Mock 小说内容）',
      chapters: [],
      wordCount: Math.floor(Math.random() * 500000) + 100000,
      importedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      hasGraph: false
    };
    
    // 模拟异步处理：先添加小说，然后异步添加章节
    setTimeout(() => {
      const novelIndex = mockNovels.findIndex(n => n.id === novelId);
      if (novelIndex !== -1) {
        mockNovels[novelIndex].chapters = Array.from({ length: 30 }, (_, i) => ({
          id: `${novelId}-chapter-${i + 1}`,
          novelId,
          chapterNumber: i + 1,
          title: `第${i + 1}章`,
          startPosition: i * 5000,
          endPosition: (i + 1) * 5000,
          wordCount: 5000
        }));
      }
    }, 2000);
    
    mockNovels.push(newNovel);
    
    return { novelId, taskId };
  },

  /**
   * 获取所有小说
   */
  async getAllNovels(): Promise<Novel[]> {
    console.log('📚 [Mock API] 获取所有小说...');
    await mockDelay(300);
    console.log('📚 [Mock API] 返回', mockNovels.length, '部小说');
    return [...mockNovels];
  },

  /**
   * 获取单个小说详情
   */
  async getNovel(id: string): Promise<Novel> {
    await mockDelay(200);
    
    const novel = mockNovels.find(n => n.id === id);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    return { ...novel };
  },

  /**
   * 更新小说信息
   */
  async updateNovel(id: string, data: Partial<Novel>): Promise<Novel> {
    await mockDelay(400);
    
    const index = mockNovels.findIndex(n => n.id === id);
    if (index === -1) {
      throw new Error('小说不存在');
    }
    
    mockNovels[index] = {
      ...mockNovels[index],
      ...data,
      id, // 确保 ID 不被修改
      updatedAt: new Date().toISOString()
    };
    
    return { ...mockNovels[index] };
  },

  /**
   * 删除小说
   */
  async deleteNovel(id: string): Promise<void> {
    await mockDelay(300);
    
    const index = mockNovels.findIndex(n => n.id === id);
    if (index === -1) {
      throw new Error('小说不存在');
    }
    
    mockNovels.splice(index, 1);
    delete mockGraphs[id];
  },

  /**
   * 获取处理状态
   */
  async getProcessingStatus(novelId: string): Promise<NovelProcessingStatus> {
    await mockDelay(200);
    
    // 模拟处理进度
    return generateMockProcessingStatus(novelId, 'completed');
  },

  /**
   * 获取章节列表
   */
  async getChapters(novelId: string): Promise<Chapter[]> {
    await mockDelay(300);
    
    const novel = mockNovels.find(n => n.id === novelId);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    return [...novel.chapters];
  },

  /**
   * 获取章节详情（带内容）
   */
  async getChapter(novelId: string, chapterId: string): Promise<ChapterWithoutContent> {
    await mockDelay(400);
    
    const novel = mockNovels.find(n => n.id === novelId);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    const chapter = novel.chapters.find(c => c.id === chapterId);
    if (!chapter) {
      throw new Error('章节不存在');
    }
    
    const chapterContent = generateMockChapterContent(chapterId, chapter);
    
    return {
      ...chapter,
      content: chapterContent.content,
      paragraphs: chapterContent.paragraphs
    };
  }
};

/**
 * Mock Search API
 */
export const mockSearchAPI = {
  /**
   * 执行搜索
   */
  async search(query: string, novelIds: string[]): Promise<SearchResult> {
    await mockDelay(1000); // 模拟 LLM 处理时间
    
    // 验证小说是否存在
    const validNovelIds = novelIds.filter(id => 
      mockNovels.some(n => n.id === id)
    );
    
    if (validNovelIds.length === 0) {
      throw new Error('请至少选择一部小说');
    }
    
    return generateMockSearchResult(query, validNovelIds);
  }
};

/**
 * Mock Graph API
 */
export const mockGraphAPI = {
  /**
   * 获取人物关系图
   */
  async getGraph(novelId: string): Promise<CharacterGraph> {
    await mockDelay(300);
    
    const novel = mockNovels.find(n => n.id === novelId);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    // 如果已生成图谱，直接返回
    if (mockGraphs[novelId]) {
      return { ...mockGraphs[novelId] };
    }
    
    // 如果小说标记有图谱但未缓存，生成新的
    if (novel.hasGraph) {
      const graph = generateMockCharacterGraph(novelId);
      mockGraphs[novelId] = graph;
      return { ...graph };
    }
    
    throw new Error('该小说尚未生成人物关系图');
  },

  /**
   * 生成人物关系图
   */
  async generateGraph(novelId: string): Promise<{ taskId: string; message: string }> {
    await mockDelay(500);
    
    const novel = mockNovels.find(n => n.id === novelId);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    const taskId = `graph-task-${Date.now()}`;
    
    // 模拟异步生成：2秒后完成
    setTimeout(() => {
      const graph = generateMockCharacterGraph(novelId);
      mockGraphs[novelId] = graph;
      
      // 更新小说的 hasGraph 标记
      const index = mockNovels.findIndex(n => n.id === novelId);
      if (index !== -1) {
        mockNovels[index].hasGraph = true;
      }
    }, 2000);
    
    return {
      taskId,
      message: '人物关系图生成任务已启动'
    };
  },

  /**
   * 删除人物关系图
   */
  async deleteGraph(novelId: string): Promise<void> {
    await mockDelay(200);
    
    const novel = mockNovels.find(n => n.id === novelId);
    if (!novel) {
      throw new Error('小说不存在');
    }
    
    delete mockGraphs[novelId];
    
    // 更新小说的 hasGraph 标记
    const index = mockNovels.findIndex(n => n.id === novelId);
    if (index !== -1) {
      mockNovels[index].hasGraph = false;
    }
  },

  /**
   * 获取人物列表
   */
  async getCharacters(novelId: string): Promise<CharacterGraph['characters']> {
    await mockDelay(200);
    
    const graph = await this.getGraph(novelId);
    return graph.characters;
  }
};

/**
 * 重置 Mock 数据（用于测试）
 */
export function resetMockData() {
  mockNovels = [...MOCK_NOVELS];
  mockGraphs = {};
}

