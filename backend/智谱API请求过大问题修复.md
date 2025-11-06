# 智谱API请求过大问题修复

## 问题描述

在上传小说进行向量化处理时，遇到智谱AI API错误：

```
zai.core._errors.APIRequestFailedError: Error code: 400, with error text {"error":{"code":"1210","message":"API 调用参数有误，请检查文档。Request Entity Too Large"}}
```

**错误原因：**
1. 原来的 `CHUNK_SIZE = 500` 是指500个**段落**，而不是字符数
2. 500个段落可能包含几万个字符，远超智谱AI embedding-3 API的单文本限制（约2048个token，相当于3000-4000个中文字符）
3. 一次批量处理20个这样的超大chunk，导致请求体过大

## 修复方案

### 1. 修改配置 (config.py)

```python
# 修改前
CHUNK_SIZE: int = 500  # 500个段落
CHUNK_OVERLAP: int = 50  # 50个段落
# batch_size硬编码为20

# 修改后
CHUNK_SIZE: int = 800  # 800个字符
CHUNK_OVERLAP: int = 100  # 100个字符
EMBEDDING_BATCH_SIZE: int = 6  # 单次embedding请求最多6个文本
```

### 2. 修改文本分块逻辑 (text_processing_service.py)

**修改前：** 按段落数分块
```python
for i in range(0, len(paragraphs), chunk_size - overlap):
    segment = paragraphs[i : i + chunk_size]  # 取500个段落
    chunk_text = "\n".join(segment)
```

**修改后：** 按字符数分块
```python
pos = 0
while pos < len(text):
    chunk_end = min(pos + chunk_size, len(text))
    chunk_text = text[pos:chunk_end].strip()  # 取800个字符
    pos += chunk_size - overlap
```

### 3. 添加安全检查 (rag_service.py)

在 `embed_texts` 方法中添加：

1. **文本长度检查**：单个文本超过3000字符时自动截断
2. **批次大小警告**：批次大小超过10时发出警告
3. **详细错误信息**：捕获"Request Entity Too Large"错误并提供详细的诊断信息

```python
MAX_TEXT_LENGTH = 3000  # 建议每个文本不超过3000字符
for idx, text in enumerate(texts):
    if len(text) > MAX_TEXT_LENGTH:
        logger.warning(f"Text {idx} length ({len(text)}) exceeds limit, truncating")
        texts[idx] = text[:MAX_TEXT_LENGTH]
```

## 参数调优建议

### 当前推荐配置（已设置）：
- `CHUNK_SIZE = 800` ✅ 适合大多数场景
- `CHUNK_OVERLAP = 100` ✅ 保证上下文连贯性
- `EMBEDDING_BATCH_SIZE = 6` ✅ 平衡速度和稳定性

### 如果仍遇到问题：

1. **减小chunk大小**（提高稳定性，但会增加总chunk数）：
   ```python
   CHUNK_SIZE: int = 600
   ```

2. **减小批次大小**（更稳定但更慢）：
   ```python
   EMBEDDING_BATCH_SIZE: int = 3
   ```

3. **增大chunk大小**（减少API调用次数，但风险更高）：
   ```python
   CHUNK_SIZE: int = 1000  # 不建议超过1500
   ```

## 重新处理失败的小说

### 方法1：通过API重新上传

1. 删除失败的小说记录
2. 重新创建小说并上传文件

### 方法2：使用重新处理脚本

运行以下脚本自动重新处理状态为"failed"的小说：

```bash
cd backend
python check_processing_error.py  # 查看失败的小说
python reset_db.py --reprocess-failed  # 重新处理失败的小说
```

### 方法3：手动重置并重新处理

```python
# reprocess_failed_novel.py
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Novel
from app.services.text_processing_service import TextProcessingService
from app.core.config import settings

async def reprocess_novel(novel_id: str):
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Novel).where(Novel.id == novel_id)
        )
        novel = result.scalar_one_or_none()
        
        if not novel:
            print(f"Novel {novel_id} not found")
            return
        
        if not novel.file_path:
            print(f"Novel {novel_id} has no file_path")
            return
        
        file_path = Path(novel.file_path)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        # 重置状态
        novel.processing_status = "pending"
        novel.processing_error = None
        await session.commit()
        
        # 重新处理
        text_service = TextProcessingService(session)
        await text_service.process_novel(novel_id, file_path)
        print(f"Novel {novel_id} reprocessed successfully")

if __name__ == "__main__":
    novel_id = "0990e7f5ffcf4c55af40247107219886"  # 替换为你的小说ID
    asyncio.run(reprocess_novel(novel_id))
```

## 技术说明

### 智谱AI Embedding-3 API限制

根据智谱AI官方文档和实际测试：

| 参数 | 限制 | 说明 |
|------|------|------|
| 单文本最大长度 | ~2048 tokens | 约3000-4000个中文字符 |
| 单次请求input数组大小 | 建议≤10 | 过大可能导致请求超时或失败 |
| 请求体总大小 | ~100KB-1MB | 依赖于具体实现 |

### 为什么选择800字符？

1. **安全边界**：800字符远低于3000字符的限制，留有充足余量
2. **合理的语义完整性**：800字符约等于400个中文词，足够保持语义连贯
3. **效率平衡**：不会产生过多的chunk，减少API调用次数
4. **重叠优化**：100字符的重叠确保边界处的语义不丢失

### 性能影响

以一本30万字的小说为例：

**修改前（500段落/chunk）：**
- 假设每段50字，每chunk约25000字
- 总chunks：30万 / 25000 = 12个
- API调用：12 / 20 = 1次
- **但会失败❌**

**修改后（800字符/chunk）：**
- 每chunk：800字符
- 总chunks：30万 / (800-100) = 约428个
- API调用：428 / 6 = 约72次
- **稳定运行✅**

虽然API调用次数增加，但：
1. 每次调用更快（数据量小）
2. 避免失败和重试
3. 更好的搜索精度（chunk更细粒度）

## 验证修复

### 1. 检查配置
```bash
cd backend
python -c "from app.core.config import settings; print(f'CHUNK_SIZE: {settings.CHUNK_SIZE}'); print(f'EMBEDDING_BATCH_SIZE: {settings.EMBEDDING_BATCH_SIZE}')"
```

期望输出：
```
CHUNK_SIZE: 800
EMBEDDING_BATCH_SIZE: 6
```

### 2. 重新上传测试
1. 启动后端服务
2. 上传一本小说
3. 观察日志，应该看到：
   ```
   Starting vectorization of XXX chunks with batch_size=6
   Batch 1: 6 texts, max_len=800
   Batch 2: 6 texts, max_len=800
   ...
   ```

### 3. 检查处理状态
```bash
curl http://localhost:8000/api/v1/novels/{novel_id}
```

`processing_status` 应该变为 `"completed"`

## 总结

✅ **问题已解决**：
- 将chunk大小从"段落数"改为"字符数"
- 单个chunk从可能的几万字符减小到800字符
- 批次大小从20减小到6
- 添加了文本长度验证和自动截断
- 添加了详细的错误日志
- 修复了Qdrant点ID格式问题（使用UUID）
- 修复了Qdrant批量上传格式问题（使用Batch对象）

✅ **后续监控**：
- 观察日志中的chunk长度和批次大小
- 如果仍有问题，可以进一步减小参数
- 可以根据实际情况调整 `CHUNK_SIZE` 和 `EMBEDDING_BATCH_SIZE`

✅ **性能优化**：
- 虽然API调用次数增加，但每次调用更快更稳定
- 细粒度的chunk反而能提高搜索精度
- 可以通过增大 `EMBEDDING_BATCH_SIZE` 来加快速度（但需要测试稳定性）

## 附加修复：Qdrant数据格式问题

在修复智谱API问题后，可能会遇到Qdrant数据格式错误：

```
qdrant_client.http.exceptions.UnexpectedResponse: Unexpected Response: 400 (Bad Request)
Raw response content:
b'{"status":{"error":"Format error in JSON body: data did not match any variant of untagged enum PointInsertOperations"},"time":0.0}'
```

**原因**：
1. Qdrant的点ID必须是UUID格式，不能是普通字符串
2. 批量上传时需要使用`Batch`对象，不能直接传递`PointStruct`列表

**解决方案**：
1. 使用`uuid.uuid5`将字符串ID转换为确定性UUID
2. 使用`qmodels.Batch`对象包装数据

已在`rag_service.py`中修复。

