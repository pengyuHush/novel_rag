# 智谱AI Embedding问题修复 - 快速指南

## 🎯 问题已修复

✅ **问题1**: 调用智谱AI embedding API时出现"Request Entity Too Large"错误  
✅ **根本原因**: 每个chunk包含500个段落（可能几万字符），远超API限制  
✅ **解决方案**: 改为按字符数分块，每个chunk最多800字符

✅ **问题2**: Qdrant向量数据库插入失败"Format error in JSON body"  
✅ **根本原因**: 点ID必须是UUID格式，批量上传需要使用Batch对象  
✅ **解决方案**: 使用uuid.uuid5生成确定性UUID，使用qmodels.Batch包装数据

## 🚀 快速开始

### 1. 重启后端服务

修改已经完成，重启后端服务即可生效：

```powershell
# Windows PowerShell
cd backend
.\start.ps1
```

```bash
# Linux/Mac
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

### 2. 验证修复（可选）

运行测试脚本验证配置是否正确：

```powershell
cd backend
poetry run python test_embedding_fix.py
```

### 3. 重新处理失败的小说

#### 方法A: 重新处理所有失败的小说

```powershell
cd backend
.\reprocess_failed.ps1
```

或者：

```bash
poetry run python reprocess_failed.py
```

#### 方法B: 重新处理指定的小说

```powershell
cd backend
.\reprocess_failed.ps1 <小说ID>
```

例如：
```powershell
.\reprocess_failed.ps1 0990e7f5ffcf4c55af40247107219886
```

### 4. 上传新小说

现在可以正常上传小说了！打开前端界面：

```
http://localhost:5173
```

点击"导入小说"上传TXT文件，系统会自动处理。

## 📊 配置说明

修改后的配置位于 `backend/app/core/config.py`:

```python
CHUNK_SIZE: int = 800              # 每个chunk的字符数
CHUNK_OVERLAP: int = 100           # chunk之间的重叠字符数
EMBEDDING_BATCH_SIZE: int = 6      # 单次API请求的文本数量
```

### 何时需要调整配置？

#### 如果仍然遇到"Request Too Large"错误：

1. **减小CHUNK_SIZE**（更保守）：
   ```python
   CHUNK_SIZE: int = 600
   ```

2. **减小EMBEDDING_BATCH_SIZE**（更稳定）：
   ```python
   EMBEDDING_BATCH_SIZE: int = 3
   ```

#### 如果想加快处理速度：

1. **增大EMBEDDING_BATCH_SIZE**（需要测试稳定性）：
   ```python
   EMBEDDING_BATCH_SIZE: int = 10
   ```

⚠️ **注意**: 不建议将CHUNK_SIZE增大到1500以上，可能导致API错误

## 🔍 监控和调试

### 查看处理日志

后端服务运行时会输出详细的处理日志：

```
Starting vectorization of 428 chunks with batch_size=6
Batch 1: 6 texts, max_len=800
Batch 2: 6 texts, max_len=800
...
```

### 检查小说处理状态

```bash
# 方法1: 通过API
curl http://localhost:8000/api/v1/novels

# 方法2: 使用检查脚本
poetry run python check_processing_error.py
```

### 查看失败原因

如果小说处理失败，查看详细错误信息：

```bash
poetry run python check_processing_error.py
```

## 📝 技术细节

### 修改的文件

1. **backend/app/core/config.py**
   - CHUNK_SIZE: 500 → 800 (改为字符数)
   - CHUNK_OVERLAP: 50 → 100 (改为字符数)
   - 新增 EMBEDDING_BATCH_SIZE: 6

2. **backend/app/services/text_processing_service.py**
   - `_vectorize_novel` 方法：从按段落分块改为按字符分块
   - 添加详细的日志和错误处理

3. **backend/app/services/rag_service.py**
   - 导入 `uuid` 模块
   - `embed_texts` 方法：添加文本长度验证
   - 超过3000字符自动截断
   - 添加更好的错误提示
   - `upsert_chunks` 方法：
     - 使用uuid.uuid5将字符串ID转换为UUID
     - 使用qmodels.Batch包装上传数据

### 为什么是800字符？

| 考虑因素 | 说明 |
|---------|------|
| **API限制** | 智谱AI embedding-3约2048 tokens (≈3000-4000字符) |
| **安全余量** | 800字符远低于限制，留有充足余量 |
| **语义完整性** | 800字符足够保持语义连贯 |
| **检索精度** | 适中的chunk大小，平衡覆盖范围和精确度 |

### 性能对比

以30万字小说为例：

| 方案 | Chunk数量 | API调用次数 | 结果 |
|-----|----------|------------|------|
| 修改前 (500段落) | ~12 | ~1 | ❌ 失败 |
| 修改后 (800字符) | ~428 | ~72 | ✅ 成功 |

虽然API调用次数增加，但：
- 单次调用更快（数据量小）
- 稳定性大幅提升
- 搜索精度更高（chunk更细粒度）

## ❓ 常见问题

### Q1: 为什么不用更大的chunk？

**A**: 更大的chunk会导致：
- API请求失败风险增加
- 搜索精度下降（chunk太大，相关性模糊）
- 处理失败时浪费更多时间

### Q2: 可以同时处理多本小说吗？

**A**: 可以，但建议：
- 同时处理不超过2-3本（受限于 `MAX_BACKGROUND_CONCURRENCY`）
- 大小说（>50万字）建议单独处理

### Q3: 如何知道小说正在处理？

**A**: 查看小说状态：
- `pending`: 等待处理
- `processing`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

### Q4: 处理大约需要多长时间？

**A**: 取决于小说大小和网络状况：
- 10万字 ≈ 1-2分钟
- 30万字 ≈ 3-5分钟
- 100万字 ≈ 10-15分钟

## 🔗 相关文档

- [详细修复说明](./智谱API请求过大问题修复.md)
- [后端开发文档](./后端开发完成说明.md)
- [启动指南](./启动前必读.md)
- [问题排查](./TROUBLESHOOTING.md)

## 💡 下一步

1. ✅ 重启后端服务
2. ✅ 运行测试验证配置
3. ✅ 重新处理失败的小说
4. ✅ 上传新小说测试

问题已完全解决，可以正常使用了！🎉

---

**最后更新**: 2025-11-06  
**相关错误码**: 1210 - Request Entity Too Large

