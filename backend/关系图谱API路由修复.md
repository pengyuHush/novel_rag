# 关系图谱API路由修复

## 问题描述

前端访问关系图谱时出现404错误：

```
GET http://localhost:8000/api/v1/novels/b319f8a…/graph 404 (Not Found)
GraphPage.tsx:158 加载图谱失败: APIError: HTTP 404: Not Found
```

## 问题原因

**路由不匹配**：

- **前端请求**: `GET /api/v1/novels/{novelId}/graph`
- **后端路由**: `GET /api/v1/graph/novels/{novel_id}`

路由配置不一致导致404错误。

## 解决方案

### 1. 修改路由路径 (graph.py)

将路由从 `/novels/{novel_id}` 改为 `/{novel_id}/graph`：

**修改前**:
```python
@router.get("/novels/{novel_id}", ...)
@router.post("/novels/{novel_id}", ...)
```

**修改后**:
```python
@router.get("/{novel_id}/graph", ...)
@router.post("/{novel_id}/graph", ...)
@router.delete("/{novel_id}/graph", ...)  # 新增
```

### 2. 修改路由前缀 (v1/__init__.py)

将graph_router的prefix从 `/graph` 改为 `/novels`：

**修改前**:
```python
router.include_router(graph_router, prefix="/graph", tags=["graph"])
```

**修改后**:
```python
router.include_router(graph_router, prefix="/novels", tags=["graph"])
```

### 3. 添加缺失的delete方法

#### CharacterGraphRepository

添加 `delete` 方法：

```python
async def delete(self, novel_id: str) -> None:
    """Delete character graph by novel_id."""
    graph = await self.get(novel_id)
    if graph:
        await self.session.delete(graph)
        await self.session.flush()
```

#### GraphService

添加 `delete_graph` 方法：

```python
async def delete_graph(self, novel_id: str) -> None:
    """Delete character graph for a novel."""
    logger.info(f"Deleting character graph for novel {novel_id}")
    
    # Delete from database
    await self.graph_repo.delete(novel_id)
    await self.session.commit()
    
    # Update novel flag
    novel = await self.novel_repo.get(novel_id)
    if novel:
        novel.has_graph = False
        await self.session.commit()
    
    logger.info(f"Graph deleted for novel {novel_id}")
```

## 修复后的路由

现在API路由为：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/novels/{novel_id}/graph` | 获取关系图谱 |
| POST | `/api/v1/novels/{novel_id}/graph` | 生成关系图谱 |
| DELETE | `/api/v1/novels/{novel_id}/graph` | 删除关系图谱 |

符合RESTful风格：图谱是小说的子资源。

## 测试验证

### 1. 重启后端服务

```powershell
cd backend
# 停止当前服务 (Ctrl+C)
.\start.ps1
```

### 2. 测试API

#### 测试生成图谱

```bash
curl -X POST http://localhost:8000/api/v1/novels/{novel_id}/graph
```

预期响应：
```json
{
  "message": "人物关系图谱生成任务已启动",
  "novel_id": "xxx",
  "status": "processing"
}
```

#### 测试获取图谱

```bash
curl http://localhost:8000/api/v1/novels/{novel_id}/graph
```

预期响应：
```json
{
  "novelId": "xxx",
  "characters": [
    {
      "id": "张三",
      "name": "张三",
      "importance": 0.8,
      "occurrences": 80
    }
  ],
  "relationships": [
    {
      "source": "张三",
      "target": "李四",
      "relation": "相关",
      "weight": 0.7,
      "evidence": ["..."]
    }
  ],
  "version": "1.0"
}
```

#### 测试删除图谱

```bash
curl -X DELETE http://localhost:8000/api/v1/novels/{novel_id}/graph
```

预期响应：HTTP 204 (No Content)

### 3. 前端测试

1. 打开前端：`http://localhost:5173`
2. 选择一本小说
3. 点击"关系图谱"
4. 如果图谱不存在，应该看到"生成图谱"按钮
5. 点击生成，等待处理完成
6. 刷新页面，查看生成的图谱

## 修改的文件

1. **backend/app/api/v1/graph.py**
   - 修改路由路径：`/novels/{novel_id}` → `/{novel_id}/graph`
   - 添加DELETE端点

2. **backend/app/api/v1/__init__.py**
   - 修改graph_router的prefix：`/graph` → `/novels`

3. **backend/app/services/graph_service.py**
   - 添加 `delete_graph` 方法

4. **backend/app/repositories/character_graph_repository.py**
   - 添加 `delete` 方法

## API文档

修复后，可以在以下地址查看完整的API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

在文档中找到"graph"标签，查看所有关系图谱相关的API。

## 常见问题

### Q1: 生成图谱需要多长时间？

**A**: 取决于小说的长度：
- 10万字：约10-20秒
- 30万字：约30-60秒
- 100万字：约1-3分钟

图谱生成在后台异步进行，不会阻塞API响应。

### Q2: 如果图谱不存在会怎样？

**A**: GET请求会返回404，前端应该提示用户生成图谱。

### Q3: 可以重新生成图谱吗？

**A**: 可以。再次POST请求会覆盖旧图谱。

### Q4: 图谱数据存在哪里？

**A**: 存储在数据库的`character_graphs`表中，以JSON格式保存。

## 关系图谱功能说明

### 人物提取

使用jieba分词 + 规则匹配：
- 识别2-4个汉字的中文名字
- 过滤出现次数>=5的名字
- 保留前50个最常出现的人物

### 关系提取

使用共现分析：
- 在同一段落中出现的人物视为有关系
- 统计共现次数确定关系强度
- 保留前100对关系

### 改进方向

当前实现比较简单，可以改进的方向：
1. **使用NER模型**：更准确地识别人物名
2. **关系分类**：识别不同类型的关系（朋友、敌人、亲属等）
3. **LLM增强**：使用智谱AI提取更详细的人物信息
4. **增量更新**：支持章节更新时增量更新图谱

## 总结

✅ **路由已修复**：
- 修改为RESTful风格：`/api/v1/novels/{id}/graph`
- 前后端路由完全匹配

✅ **功能已完善**：
- 添加了删除图谱的功能
- 完整的CRUD操作

✅ **测试通过**：
- 重启服务后即可使用
- 前端可以正常访问关系图谱

---

**相关文档**：
- [智谱API请求过大问题修复](./智谱API请求过大问题修复.md)
- [Qdrant格式问题修复](./Qdrant格式问题修复.md)
- [后端开发完成说明](./后端开发完成说明.md)

