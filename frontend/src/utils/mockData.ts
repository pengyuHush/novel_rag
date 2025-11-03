import type { SearchResult, Reference, CharacterGraph, Character, Relationship } from '../types';

/**
 * 生成Mock搜索结果
 */
export function generateMockSearchResult(query: string, novelIds: string[]): SearchResult {
  const answers: Record<string, string> = {
    default: `根据小说内容分析，${query}的相关信息如下：这是一个基于RAG技术生成的智能回答示例。系统通过检索小说中的相关段落，结合语义理解，为您提供准确的答案。实际应用中，这里将显示根据小说内容生成的真实回答。`,
  };
  
  const answer = answers[query] || answers.default;
  
  const references: Reference[] = novelIds.flatMap((novelId, novelIndex) => [
    {
      novelId,
      novelTitle: `测试小说${novelIndex + 1}`,
      chapterId: 'chapter-5',
      chapterTitle: '第五章 重要转折',
      paragraphIndex: 3,
      excerpt: '这是一段示例原文，用于展示搜索结果的引用功能。在实际应用中，这里会显示从小说中检索到的真实段落内容。这段文字会根据用户的搜索关键词进行高亮显示，帮助用户快速定位关键信息。',
      relevance: 0.92 - novelIndex * 0.1,
      highlightRanges: [[5, 15], [30, 40]]
    },
    {
      novelId,
      novelTitle: `测试小说${novelIndex + 1}`,
      chapterId: 'chapter-12',
      chapterTitle: '第十二章 关键线索',
      paragraphIndex: 7,
      excerpt: '另一段相关的原文内容，展示系统如何从多个章节中检索相关信息。通过语义匹配技术，系统能够找到与用户问题最相关的段落，即使这些段落中没有直接出现搜索关键词。',
      relevance: 0.85 - novelIndex * 0.1,
      highlightRanges: [[10, 20]]
    }
  ]);
  
  return {
    answer,
    references: references.slice(0, 5), // 最多返回5个引用
    timestamp: new Date().toISOString()
  };
}

/**
 * 生成Mock人物关系图谱
 */
export function generateMockCharacterGraph(novelId: string): CharacterGraph {
  const characters: Character[] = [
    {
      id: 'char-1',
      name: '张三',
      frequency: 158,
      importance: 'major',
      chapters: ['chapter-1', 'chapter-2', 'chapter-3', 'chapter-5', 'chapter-8']
    },
    {
      id: 'char-2',
      name: '李四',
      frequency: 142,
      importance: 'major',
      chapters: ['chapter-1', 'chapter-3', 'chapter-5', 'chapter-10']
    },
    {
      id: 'char-3',
      name: '王五',
      frequency: 98,
      importance: 'major',
      chapters: ['chapter-2', 'chapter-5', 'chapter-8', 'chapter-12']
    },
    {
      id: 'char-4',
      name: '赵六',
      frequency: 76,
      importance: 'minor',
      chapters: ['chapter-3', 'chapter-7', 'chapter-11']
    },
    {
      id: 'char-5',
      name: '钱七',
      frequency: 54,
      importance: 'minor',
      chapters: ['chapter-4', 'chapter-9']
    },
    {
      id: 'char-6',
      name: '孙八',
      frequency: 45,
      importance: 'minor',
      chapters: ['chapter-6', 'chapter-13']
    }
  ];
  
  const relationships: Relationship[] = [
    {
      id: 'rel-1',
      from: 'char-1',
      to: 'char-2',
      type: 'friend',
      strength: 0.9,
      chapters: ['chapter-1', 'chapter-3', 'chapter-5'],
      representativeExcerpts: [
        '张三和李四从小一起长大，情同手足。',
        '在关键时刻，李四毫不犹豫地帮助了张三。'
      ]
    },
    {
      id: 'rel-2',
      from: 'char-1',
      to: 'char-3',
      type: 'mentor',
      strength: 0.8,
      chapters: ['chapter-2', 'chapter-5', 'chapter-8'],
      representativeExcerpts: [
        '王五是张三的师父，教导他许多重要的知识。',
        '张三对师父王五十分尊敬。'
      ]
    },
    {
      id: 'rel-3',
      from: 'char-2',
      to: 'char-4',
      type: 'family',
      strength: 0.95,
      chapters: ['chapter-3', 'chapter-7'],
      representativeExcerpts: [
        '赵六是李四的兄长，两人关系亲密。'
      ]
    },
    {
      id: 'rel-4',
      from: 'char-3',
      to: 'char-5',
      type: 'enemy',
      strength: 0.7,
      chapters: ['chapter-4', 'chapter-9'],
      representativeExcerpts: [
        '王五和钱七因为某些原因产生了矛盾。',
        '两人的对立在第九章达到了高潮。'
      ]
    },
    {
      id: 'rel-5',
      from: 'char-1',
      to: 'char-6',
      type: 'other',
      strength: 0.5,
      chapters: ['chapter-6'],
      representativeExcerpts: [
        '张三偶然遇到了孙八。'
      ]
    }
  ];
  
  return {
    novelId,
    characters,
    relationships
  };
}

/**
 * 生成示例搜索问题
 */
export const EXAMPLE_QUERIES = [
  '张三是谁？',
  '总结第5章的内容',
  '张三和李四的关系是什么？',
  '王五第一次出现在哪里？',
  '比较张三和李四的性格特点'
];

