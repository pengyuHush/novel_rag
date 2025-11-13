#!/usr/bin/env python3
"""
Phase 5 知识图谱功能验证脚本
"""

import sys
import pickle
from pathlib import Path
from collections import Counter

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Entity, Chapter, Novel
from app.services.graph.graph_query import get_graph_query


def verify_database(session, novel_id):
    """验证数据库中的实体数据"""
    print("=" * 60)
    print("✅ 检查点 1: 实体提取")
    print("=" * 60)
    
    # 查询实体
    entities = session.query(Entity).filter(Entity.novel_id == novel_id).all()
    
    if not entities:
        print("❌ 未找到实体数据，请确保已完成索引")
        return False
    
    # 统计
    entity_types = Counter([e.entity_type for e in entities])
    print(f"\n📊 实体统计: 共 {len(entities)} 个")
    for etype, count in entity_types.items():
        print(f"  - {etype}: {count}")
    
    # 示例
    print(f"\n📝 实体示例 (前10个):")
    for e in entities[:10]:
        print(f"  - {e.name} ({e.entity_type}): 章节 {e.first_chapter}-{e.last_chapter or '?'}")
    
    return True


def verify_graph(novel_id):
    """验证知识图谱"""
    print("\n" + "=" * 60)
    print("✅ 检查点 2: 知识图谱构建")
    print("=" * 60)
    
    graph_path = project_root / 'data' / 'graphs' / f'novel_{novel_id}_graph.pkl'
    
    if not graph_path.exists():
        print(f"❌ 图谱文件不存在: {graph_path}")
        return None
    
    # 加载图谱
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"\n📊 图谱统计:")
    print(f"  节点数: {G.number_of_nodes()}")
    print(f"  边数: {G.number_of_edges()}")
    
    if G.number_of_nodes() == 0:
        print("❌ 图谱为空")
        return None
    
    # 节点示例
    print(f"\n🔵 节点示例 (前5个):")
    for i, (node, attrs) in enumerate(list(G.nodes(data=True))[:5], 1):
        importance = attrs.get('importance', 0)
        node_type = attrs.get('type', 'N/A')
        ch_range = f"{attrs.get('first_chapter', '?')}-{attrs.get('last_chapter', '?')}"
        print(f"  {i}. {node} ({node_type})")
        print(f"     重要性: {importance:.4f}, 章节: {ch_range}")
    
    # 边示例
    if G.number_of_edges() > 0:
        print(f"\n🔗 关系示例 (前5条):")
        for i, (src, tgt, attrs) in enumerate(list(G.edges(data=True))[:5], 1):
            rel_type = attrs.get('relation_type', 'unknown')
            strength = attrs.get('strength', 0)
            ch_range = f"{attrs.get('start_chapter', '?')}-{attrs.get('end_chapter', '?')}"
            print(f"  {i}. {src} → {tgt}")
            print(f"     关系: {rel_type}, 强度: {strength:.2f}, 章节: {ch_range}")
    
    # PageRank排序
    print(f"\n⭐ 最重要的角色 (PageRank Top 10):")
    importance = {node: attrs.get('importance', 0) 
                  for node, attrs in G.nodes(data=True)}
    top_nodes = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (node, score) in enumerate(top_nodes, 1):
        print(f"  {i}. {node}: {score:.4f}")
    
    return G


def verify_chapter_importance(session, novel_id):
    """验证章节重要性"""
    print("\n" + "=" * 60)
    print("✅ 检查点 3: 章节重要性评分")
    print("=" * 60)
    
    chapters = session.query(Chapter)\
        .filter(Chapter.novel_id == novel_id)\
        .order_by(Chapter.importance_score.desc())\
        .limit(10)\
        .all()
    
    if not chapters:
        print("❌ 未找到章节数据")
        return
    
    print(f"\n📈 章节重要性排序 (Top 10):")
    for i, ch in enumerate(chapters, 1):
        score = ch.importance_score or 0
        title = ch.title or "(无标题)"
        print(f"  {i}. 第{ch.chapter_num}章: {score:.4f} - {title}")


def verify_graph_query(G, novel_id):
    """验证图谱查询功能"""
    if G is None or G.number_of_nodes() == 0:
        return
    
    print("\n" + "=" * 60)
    print("✅ 检查点 4: 图谱查询功能")
    print("=" * 60)
    
    # 获取主角（重要性最高的角色）
    importance = {node: attrs.get('importance', 0) 
                  for node, attrs in G.nodes(data=True) 
                  if attrs.get('type') == 'character'}
    
    if not importance:
        print("⚠️  未找到角色节点")
        return
    
    protagonist = max(importance.items(), key=lambda x: x[1])[0]
    
    # 获取图谱查询器实例
    graph_query = get_graph_query()
    
    # 测试1: 查询邻居
    print(f"\n🌐 {protagonist} 的直接关系:")
    neighbors = graph_query.get_entity_neighbors(G, protagonist, chapter_num=None, max_neighbors=10)
    for neighbor, relation, importance_score in neighbors[:5]:
        print(f"  - {neighbor}: {relation} (重要性: {importance_score:.3f})")
    
    # 测试2: 查询特定章节的关系
    test_chapter = 5
    print(f"\n📖 第{test_chapter}章的关系 (主角相关):")
    # 查询主角在指定章节的邻居
    chapter_neighbors = graph_query.get_entity_neighbors(G, protagonist, chapter_num=test_chapter, max_neighbors=5)
    for neighbor, relation, _ in chapter_neighbors:
        print(f"  {protagonist} → {neighbor}: {relation}")
    
    # 测试3: 查询章节范围实体
    print(f"\n🔍 第1-10章出现的实体:")
    entities_range = graph_query.get_entities_by_chapter_range(G, 1, 10)
    print(f"  共 {len(entities_range)} 个: {', '.join(list(entities_range)[:10])}")


def main():
    """主验证流程"""
    print("\n" + "=" * 60)
    print("🔍 Phase 5 知识图谱功能验证")
    print("=" * 60)
    
    # 获取小说ID
    if len(sys.argv) > 1:
        novel_id = int(sys.argv[1])
    else:
        novel_id = 1
        print(f"\n使用默认小说ID: {novel_id}")
        print("提示: 可通过命令行参数指定: python verify_phase5.py <novel_id>\n")
    
    # 连接数据库
    db_path = project_root / 'data' / 'novels.db'
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先上传小说并完成索引")
        return
    
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 检查小说是否存在
    novel = session.query(Novel).filter(Novel.id == novel_id).first()
    if not novel:
        print(f"❌ 未找到ID为 {novel_id} 的小说")
        print("\n可用的小说:")
        novels = session.query(Novel).all()
        for n in novels:
            print(f"  - ID {n.id}: {n.title}")
        return
    
    print(f"\n📚 正在验证小说: {novel.title} (ID: {novel_id})")
    
    # 执行验证
    try:
        # 1. 验证实体提取
        has_entities = verify_database(session, novel_id)
        
        # 2. 验证知识图谱
        G = verify_graph(novel_id)
        
        # 3. 验证章节重要性
        verify_chapter_importance(session, novel_id)
        
        # 4. 验证图谱查询
        verify_graph_query(G, novel_id)
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 验证总结")
        print("=" * 60)
        print(f"✅ 实体提取: {'通过' if has_entities else '失败'}")
        print(f"✅ 知识图谱: {'通过' if G and G.number_of_nodes() > 0 else '失败'}")
        print(f"✅ 图谱查询: {'通过' if G else '失败'}")
        print("\n💡 提示: Phase 5 的GraphRAG集成需要等待索引流程完成后才能完全体验")
        
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == '__main__':
    main()

