# API 合约文档

**Created:** 2025-11-13  
**Version:** 1.0.0

## 概述

本目录包含网络小说智能问答系统的完整API规范，采用OpenAPI 3.1.0标准定义。

## 文件说明

| 文件 | 说明 |
|------|------|
| `openapi.yaml` | OpenAPI规范主文件，包含所有REST API和WebSocket定义 |

## API 分类

### 1. 小说管理（/novels）

- **POST** `/novels/upload` - 上传小说文件
- **GET** `/novels` - 获取小说列表
- **GET** `/novels/{novelId}` - 获取小说详情
- **DELETE** `/novels/{novelId}` - 删除小说
- **GET** `/novels/{novelId}/progress` - 获取索引进度

### 2. 章节阅读（/novels/{novelId}/chapters）

- **GET** `/novels/{novelId}/chapters` - 获取章节列表
- **GET** `/novels/{novelId}/chapters/{chapterNum}` - 获取章节内容

### 3. 智能问答（/query）

- **POST** `/query` - 提交查询（非流式）
- **GET** `/query/history` - 获取查询历史
- **GET** `/query/{queryId}` - 获取查询详情
- **POST** `/query/{queryId}/feedback` - 提交用户反馈

### 4. 可视化（/graph）

- **GET** `/graph/relations/{novelId}` - 获取角色关系图数据
- **GET** `/graph/timeline/{novelId}` - 获取时间线数据
- **GET** `/graph/statistics/{novelId}` - 获取统计数据

### 5. 配置管理（/config）

- **POST** `/config/test-connection` - 测试智谱AI连接
- **GET** `/config` - 获取系统配置
- **PUT** `/config` - 更新系统配置

### 6. 统计分析（/stats）

- **GET** `/stats/tokens` - 获取Token统计
- **GET** `/stats/tokens/operation/{operationId}` - 获取单次操作Token详情

## WebSocket 端点

### 1. 索引进度推送

**端点：** `ws://localhost:8000/ws/progress/{novelId}`

**消息类型：**
- `progress`: 进度更新
- `complete`: 索引完成
- `error`: 错误信息

### 2. 智能问答流式响应

**端点：** `ws://localhost:8000/api/query/stream`

**消息类型：**
- `stage_start`: 阶段开始
- `stage_complete`: 阶段完成
- `stream_token`: 流式Token
- `query_complete`: 查询完成
- `error`: 错误信息

## 使用示例

### 上传小说

```bash
curl -X POST http://localhost:8000/novels/upload \
  -F "file=@novel.txt" \
  -F "title=斗破苍穹" \
  -F "author=天蚕土豆"
```

### 提交查询

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "novelId": 1,
    "query": "萧炎和药老是什么时候相遇的？",
    "model": "glm-4"
  }'
```

### WebSocket查询（JavaScript）

```javascript
const ws = new WebSocket('ws://localhost:8000/api/query/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    novelId: 1,
    query: '萧炎和药老是什么时候相遇的？',
    model: 'glm-4'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'stream_token':
      console.log(message.token);
      break;
    case 'query_complete':
      console.log('完整结果:', message.data);
      break;
  }
};
```

## 在线文档查看

### 使用Swagger UI

1. 启动后端服务：
```bash
cd backend
uvicorn app.main:app --reload
```

2. 访问Swagger UI：
```
http://localhost:8000/docs
```

### 使用Redoc

访问Redoc文档：
```
http://localhost:8000/redoc
```

## 数据模型

所有数据模型的详细定义请参考：
- `openapi.yaml` 中的 `components/schemas` 部分
- `../data-model.md` 文档

## 错误处理

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 版本控制

API版本通过URL路径控制（未来如需要）：
```
http://localhost:8000/api/v1/novels
```

当前版本：`v1.0.0`（默认路径）

## 相关文档

- [数据模型](../data-model.md)
- [研究文档](../research.md)
- [实现计划](../plan.md)

---

**维护者：** Development Team  
**最后更新：** 2025-11-13

