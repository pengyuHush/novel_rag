"""
修复已存在图谱的关系边

为已构建但缺少关系边的图谱添加基于共现的关系
"""
import sys
import pickle
from pathlib import Path
from collections import defaultdict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.init_db import get_database_url
from app.models.database import Novel
from app.services.nlp.entity_extractor import EntityExtractor
from app.services.graph.graph_builder import GraphBuilder
from app.utils.encoding_detector import EncodingDetector
import os

def fix_graph_relations(novel_id: int):
    """为指定小说的图谱添加关系边"""
    
    print(f"\n🔧 开始修复小说 {novel_id} 的图谱关系...")
    
    # 加载现有图谱
    graph_builder = GraphBuilder()
    graph = graph_builder.load_graph(novel_id)
    
    if graph is None:
        print(f"❌ 图谱文件不存在: novel_{novel_id}_graph.pkl")
        return False
    
    print(f"📊 当前图谱: {graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边")
    
    # 如果已经有边了，询问是否重建
    if graph.number_of_edges() > 0:
        response = input(f"图谱已有 {graph.number_of_edges()} 条边，是否重新构建？(y/N): ")
        if response.lower() != 'y':
            print("取消操作")
            return False
        
        # 清除现有边
        graph.remove_edges_from(list(graph.edges()))
        print("✅ 已清除现有边")
    
    # 从数据库加载章节和实体
    engine = create_engine(
        get_database_url(),
        connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel:
            print(f"❌ 小说 {novel_id} 不存在")
            return False
        
        from app.models.database import Chapter, Entity
        
        # 加载所有章节
        chapters = db.query(Chapter).filter(
            Chapter.novel_id == novel_id
        ).order_by(Chapter.chapter_num).all()
        
        if not chapters:
            print(f"❌ 小说 {novel_id} 没有章节数据")
            return False
        
        print(f"📚 加载了 {len(chapters)} 个章节")
        
        # 检查文件是否存在
        if not os.path.exists(novel.file_path):
            print(f"❌ 小说文件不存在: {novel.file_path}")
            return False
        
        # 检测文件编码
        detection = EncodingDetector.detect_file_encoding(novel.file_path)
        encoding = detection['encoding']
        
        # 处理常见编码别名
        if encoding and encoding.lower() in ['gb2312', 'gb18030']:
            encoding = 'gbk'
        
        print(f"📖 文件编码: {encoding}")
        
        # 重新提取实体（从原文）
        entity_extractor = EntityExtractor()
        chapter_entity_map = {}  # chapter_num -> set of character names
        
        print("📝 重新提取实体...")
        for i, chapter in enumerate(chapters, 1):
            if i % 10 == 0:
                print(f"  处理进度: {i}/{len(chapters)}")
            
            # 从文件读取章节内容
            try:
                with open(novel.file_path, 'r', encoding=encoding, errors='ignore') as f:
                    f.seek(chapter.start_pos)
                    chapter_content = f.read(chapter.end_pos - chapter.start_pos)
            except Exception as e:
                print(f"⚠️  读取章节 {chapter.chapter_num} 失败: {e}")
                continue
            
            chapter_entities = entity_extractor.extract_from_chapter(
                chapter_content, 
                chapter.chapter_num
            )
            
            # 只保留角色实体
            characters = set(chapter_entities.get('characters', []))
            
            # 过滤：只保留图谱中已存在的节点
            characters = {c for c in characters if c in graph.nodes()}
            
            if characters:
                chapter_entity_map[chapter.chapter_num] = characters
        
        print(f"✅ 实体提取完成，共 {len(chapter_entity_map)} 章有角色")
        
        # 构建共现关系
        print("🔗 构建共现关系...")
        cooccurrence_count = {}  # (entity1, entity2) -> count
        cooccurrence_chapters = {}  # (entity1, entity2) -> [chapter_nums]
        
        for chapter_num, entities in chapter_entity_map.items():
            entity_list = list(entities)
            # 对该章节的任意两个角色建立共现关系
            for i in range(len(entity_list)):
                for j in range(i + 1, len(entity_list)):
                    entity1, entity2 = sorted([entity_list[i], entity_list[j]])
                    pair = (entity1, entity2)
                    
                    if pair not in cooccurrence_count:
                        cooccurrence_count[pair] = 0
                        cooccurrence_chapters[pair] = []
                    
                    cooccurrence_count[pair] += 1
                    cooccurrence_chapters[pair].append(chapter_num)
        
        # 添加关系边
        min_cooccurrence = 3
        edge_count = 0
        
        for (entity1, entity2), count in cooccurrence_count.items():
            if count >= min_cooccurrence:
                chapters_list = cooccurrence_chapters[(entity1, entity2)]
                start_chapter = min(chapters_list)
                end_chapter = max(chapters_list)
                
                # 根据共现频率计算关系强度
                strength = min(count / 20.0, 1.0)
                
                graph.add_edge(
                    entity1,
                    entity2,
                    relation_type='共现',
                    start_chapter=start_chapter,
                    end_chapter=end_chapter,
                    strength=strength,
                    cooccurrence_count=count
                )
                edge_count += 1
        
        print(f"✅ 添加了 {edge_count} 条关系边")
        
        # 保存图谱
        print("💾 保存图谱...")
        graph_builder.save_graph(graph, novel_id)
        
        print(f"\n✨ 修复完成！")
        print(f"   节点数: {graph.number_of_nodes()}")
        print(f"   边数: {graph.number_of_edges()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_graph_relations.py <novel_id>")
        print("示例: python fix_graph_relations.py 1")
        sys.exit(1)
    
    try:
        novel_id = int(sys.argv[1])
        success = fix_graph_relations(novel_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print("错误: novel_id 必须是整数")
        sys.exit(1)

