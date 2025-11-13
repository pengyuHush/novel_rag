"""验证图谱文件"""
import pickle
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

graph_file = Path("data/graphs/novel_1_graph.pkl")

if not graph_file.exists():
    print(f"[ERROR] Graph file not found: {graph_file}")
    sys.exit(1)

try:
    with open(graph_file, 'rb') as f:
        G = pickle.load(f)
    
    print("[OK] Graph loaded successfully")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    
    if G.number_of_nodes() > 0:
        print("\nNode types:")
        from collections import Counter
        types = Counter([G.nodes[n].get("type", "unknown") for n in G.nodes()])
        for k, v in types.items():
            print(f"  {k}: {v}")
        
        print("\nTop 10 nodes:")
        for i, (node, attrs) in enumerate(list(G.nodes(data=True))[:10]):
            print(f"  {i+1}. {node} ({attrs.get('type', '?')})")
    
    print(f"\n[OK] Graph file is valid")
    
except Exception as e:
    print(f"[ERROR] Failed to load: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

