"""检查图谱文件的内容"""
import sys
import pickle
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_graph(novel_id: int):
    """检查图谱内容"""
    graph_file = Path(f"./data/graphs/novel_{novel_id}_graph.pkl")
    
    if not graph_file.exists():
        print(f"❌ 图谱文件不存在: {graph_file}")
        return
    
    try:
        with open(graph_file, 'rb') as f:
            graph = pickle.load(f)
        
        print(f"\n📊 图谱统计:")
        print(f"   节点数: {graph.number_of_nodes()}")
        print(f"   边数: {graph.number_of_edges()}")
        print(f"   图类型: {type(graph).__name__}")
        
        if graph.number_of_nodes() > 0:
            print(f"\n📝 前10个节点:")
            for i, (node_id, data) in enumerate(list(graph.nodes(data=True))[:10]):
                importance = data.get('importance', 0)
                node_type = data.get('type', 'unknown')
                print(f"   {i+1}. {node_id} ({node_type}) - 重要性: {importance:.2f}")
        
        if graph.number_of_edges() > 0:
            print(f"\n🔗 前10条边:")
            for i, (source, target, data) in enumerate(list(graph.edges(data=True))[:10]):
                rel_type = data.get('relation_type', 'unknown')
                strength = data.get('strength', 0)
                cooccur = data.get('cooccurrence_count', 0)
                print(f"   {i+1}. {source} --[{rel_type}({strength:.2f}, 共现{cooccur}次)]--> {target}")
        else:
            print(f"\n⚠️  图谱没有边！")
            print(f"   这意味着图谱构建时没有添加关系。")
        
        # 检查是否是 MultiDiGraph
        if graph.number_of_edges() > 0:
            # 检查第一条边的详细信息
            edge = list(graph.edges(data=True))[0]
            print(f"\n🔍 边详细信息示例:")
            print(f"   Source: {edge[0]}")
            print(f"   Target: {edge[1]}")
            print(f"   Data: {edge[2]}")
        
    except Exception as e:
        print(f"❌ 读取图谱失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_graph.py <novel_id>")
        sys.exit(1)
    
    novel_id = int(sys.argv[1])
    check_graph(novel_id)

