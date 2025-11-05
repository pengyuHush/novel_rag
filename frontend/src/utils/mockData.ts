import type { 
  SearchResult, 
  Reference, 
  CharacterGraph, 
  Character, 
  Relationship,
  Novel,
  Chapter,
  ChapterContent,
  NovelProcessingStatus
} from '../types';

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

/**
 * Mock 小说数据
 */
export const MOCK_NOVELS: Novel[] = [
  {
    id: 'novel-1',
    title: '修仙传奇',
    author: '云中子',
    description: '一个少年从凡人逆袭成为仙界至尊的传奇故事。跨越三界，征战八方，最终证道成仙。',
    tags: ['修仙', '玄幻', '热血'],
    content: generateSampleNovelContent(1),
    chapters: generateSampleChapters('novel-1', 50),
    wordCount: 1250000,
    importedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    hasGraph: true
  },
  {
    id: 'novel-2',
    title: '都市风云',
    author: '墨香',
    description: '现代都市背景下，主角凭借智慧和勇气，在商场、情场游刃有余，最终成就一番事业。',
    tags: ['都市', '商战', '言情'],
    content: generateSampleNovelContent(2),
    chapters: generateSampleChapters('novel-2', 35),
    wordCount: 890000,
    importedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    hasGraph: true
  },
  {
    id: 'novel-3',
    title: '星际争霸',
    author: '银河系',
    description: '未来世界，人类征战星际，与外星文明展开史诗级的战争。充满科技感和想象力。',
    tags: ['科幻', '星际', '战争'],
    content: generateSampleNovelContent(3),
    chapters: generateSampleChapters('novel-3', 42),
    wordCount: 1050000,
    importedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    hasGraph: false
  }
];

/**
 * 生成示例小说内容
 */
function generateSampleNovelContent(novelIndex: number): string {
  const templates = [
    `【修仙传奇 - 完整内容】

第一章 偶遇奇缘

清晨的第一缕阳光洒在青云山上，山间薄雾缭绕，宛如仙境。

张三是青云村的一个普通少年，从小就向往修仙之路。这一天，他如往常一样上山采药，却在山林深处发现了一处隐秘的洞府。

洞府中，一位白发苍苍的老者正在打坐。老者睁开眼，目光如炬："小子，既然你能找到这里，说明你与我有缘。我乃青云真人，愿收你为徒。"

张三激动不已，当即跪拜："弟子愿拜师！"

从此，张三踏上了修仙之路...

第二章 初入修炼

在师父的指导下，张三开始修炼基础功法《吐纳心经》。每日清晨，他都会在山顶修炼，吸收天地灵气。

师父王五告诉他："修仙之路，贵在坚持。你要静心凝神，感受天地灵气的流动..."

[此处省略中间章节...]

第五十章 证道成仙

历经无数磨难，张三终于突破最后的瓶颈，渡过天劫，成功飞升仙界。

站在云端，俯瞰人间，张三感慨万千。他想起了当年的青云村，想起了师父的教诲，想起了与李四并肩作战的日子...

"这只是新的开始。"张三喃喃自语，转身飞向更广阔的仙界...`,

    `【都市风云 - 完整内容】

第一章 归国创业

李明刚从国外名校毕业归来，决心在国内创办自己的科技公司。

机场出口，多年未见的好友李四早已等候多时："李明，欢迎回国！"

两人相视一笑，当年的情谊依然如故...

[内容继续...]`,

    `【星际争霸 - 完整内容】

第一章 星际时代

公元2456年，人类文明已经扩展到银河系的各个角落。

星际舰队指挥官陈浩站在旗舰的指挥台上，望着窗外的星空...

[内容继续...]`
  ];

  return templates[novelIndex - 1] || templates[0];
}

/**
 * 生成示例章节列表
 */
function generateSampleChapters(novelId: string, count: number): Chapter[] {
  const chapters: Chapter[] = [];
  let position = 0;
  
  for (let i = 0; i < count; i++) {
    const chapterTitle = `第${i + 1}章 ${generateChapterTitle(i)}`;
    const wordCount = Math.floor(Math.random() * 5000) + 3000;
    
    chapters.push({
      id: `${novelId}-chapter-${i + 1}`,
      novelId,
      chapterNumber: i + 1,
      title: chapterTitle,
      startPosition: position,
      endPosition: position + wordCount,
      wordCount
    });
    
    position += wordCount;
  }
  
  return chapters;
}

/**
 * 生成章节标题
 */
function generateChapterTitle(index: number): string {
  const titles = [
    '偶遇奇缘', '初入修炼', '突破瓶颈', '江湖纷争', '重要转折',
    '生死危机', '获得传承', '闭关修炼', '出关惊世', '结识好友',
    '组建团队', '关键线索', '暗中较量', '正面交锋', '意外发现',
    '寻找真相', '揭开谜团', '绝地反击', '力挽狂澜', '胜利曙光',
    '新的挑战', '艰难抉择', '背水一战', '终极对决', '尘埃落定',
    '新的征程', '前路漫漫', '再次出发', '意外重逢', '往事如烟',
    '未来可期', '风云变幻', '暗流涌动', '山雨欲来', '惊天秘密',
    '真相大白', '恍然大悟', '柳暗花明', '绝处逢生', '凤凰涅槃',
    '浴火重生', '王者归来', '巅峰对决', '登峰造极', '天下无双',
    '独步天下', '笑傲江湖', '功成名就', '圆满结局', '新的开始'
  ];
  
  return titles[index % titles.length];
}

/**
 * 生成 Mock 章节内容
 */
export function generateMockChapterContent(chapterId: string, chapter: Chapter): ChapterContent {
  const content = `${chapter.title}

【正文】

清晨的阳光透过窗户洒进房间，新的一天开始了。

张三站在窗前，望着远方的群山，心中涌起无限感慨。自从踏上修炼之路以来，他经历了太多的风雨。

"师父，我一定不会辜负您的期望。"他暗暗发誓。

转身走出房间，张三来到练功场。李四已经在那里等候多时。

"张三，今天我们要进行实战训练。"李四说道。

两人相视一笑，随即展开了激烈的切磋...

【中段内容】

时间飞逝，转眼已是黄昏时分。

经过一天的训练，张三感觉自己的修为又精进了不少。他坐在山顶，开始静心打坐，吸收天地灵气。

突然，远处传来一阵异响...

【结尾】

这一天的经历，让张三明白了一个道理：修炼之路，永无止境。只有不断努力，才能达到更高的境界。

夜幕降临，星光璀璨。张三结束打坐，回到住处休息，为明天的修炼养精蓄锐。

（本章完）`;

  const paragraphs = content.split('\n\n').map((para, index) => ({
    index,
    content: para.trim(),
    startPosition: content.indexOf(para)
  })).filter(p => p.content.length > 0);

  return {
    chapter,
    content,
    paragraphs
  };
}

/**
 * 生成 Mock 处理状态
 */
export function generateMockProcessingStatus(
  novelId: string, 
  stage: 'uploading' | 'detecting_chapters' | 'vectorizing' | 'completed' = 'completed'
): NovelProcessingStatus {
  const stages = {
    uploading: {
      status: 'processing' as const,
      progress: 20,
      message: '正在上传文件...',
      stage: 'uploading' as const
    },
    detecting_chapters: {
      status: 'processing' as const,
      progress: 45,
      message: '正在识别章节结构...',
      stage: 'detecting_chapters' as const
    },
    vectorizing: {
      status: 'processing' as const,
      progress: 75,
      message: '正在构建向量索引...',
      stage: 'vectorizing' as const
    },
    completed: {
      status: 'completed' as const,
      progress: 100,
      message: '处理完成',
      stage: 'completed' as const
    }
  };

  return {
    novelId,
    ...stages[stage]
  };
}

/**
 * Mock 延迟函数（模拟网络请求）
 */
export function mockDelay(ms: number = 500): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

