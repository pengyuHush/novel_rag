# API 规范质量检查清单

**目的**: 验证API规范的完整性、一致性和可实现性  
**创建日期**: 2025-11-13  
**检查级别**: 标准级（PR审查）  
**适用文档**: contracts/openapi.yaml, contracts/README.md

---

## API 定义完整性

- [ ] CHK121 - 是否为所有REST端点定义了完整的请求参数（路径参数、查询参数、请求体）？ [完整性，openapi.yaml]
- [ ] CHK122 - 是否为所有REST端点定义了所有可能的HTTP状态码及其响应格式？ [完整性，openapi.yaml]
- [ ] CHK123 - 是否为所有WebSocket端点定义了完整的消息类型和数据结构？ [完整性，README.md §WebSocket端点]
- [ ] CHK124 - 是否定义了所有API的认证和授权要求？ [缺口]
- [ ] CHK125 - 是否定义了所有API的速率限制（Rate Limiting）？ [缺口]
- [ ] CHK126 - 是否为分页API定义了统一的分页参数（page、pageSize）和响应格式？ [完整性，openapi.yaml §GET /novels]

## 请求规范

- [ ] CHK127 - 上传文件API（POST /novels/upload）是否明确了Content-Type为multipart/form-data？ [清晰度，openapi.yaml]
- [ ] CHK128 - 是否为所有必填字段添加了required标记？ [完整性，openapi.yaml]
- [ ] CHK129 - 是否为所有字符串字段定义了长度限制（minLength、maxLength）？ [完整性，openapi.yaml]
- [ ] CHK130 - 是否为所有数值字段定义了范围限制（minimum、maximum）？ [完整性，openapi.yaml]
- [ ] CHK131 - 是否为枚举类型字段定义了所有可能的值？ [完整性，如index_status枚举]
- [ ] CHK132 - 是否定义了日期时间字段的格式（如ISO 8601）？ [清晰度]

## 响应规范

- [ ] CHK133 - 是否为所有成功响应（2xx）定义了完整的数据结构？ [完整性，openapi.yaml]
- [ ] CHK134 - 是否为所有错误响应（4xx、5xx）定义了统一的错误格式？ [完整性，openapi.yaml §components/responses]
- [ ] CHK135 - 错误响应是否包含足够的调试信息（如错误码、错误消息、字段级别的验证错误）？ [完整性]
- [ ] CHK136 - 是否为分页响应定义了元数据（如totalCount、totalPages、currentPage）？ [缺口]
- [ ] CHK137 - 是否为异步操作（如索引构建）定义了任务状态查询接口？ [完整性，openapi.yaml §GET /novels/{id}/progress]

## 数据类型一致性

- [ ] CHK138 - novelId字段在所有API中的类型是否一致（integer）？ [一致性，openapi.yaml]
- [ ] CHK139 - 时间戳字段在所有API中的格式是否一致（如TIMESTAMP vs ISO 8601）？ [一致性]
- [ ] CHK140 - 枚举值在前后端是否保持一致（如'pending'、'processing'、'completed'、'failed'）？ [一致性]
- [ ] CHK141 - 是否所有浮点数字段定义了精度（如progress的0.0~1.0）？ [清晰度]
- [ ] CHK142 - 是否所有ID字段使用了一致的命名规范（如novelId vs novel_id）？ [一致性]

## WebSocket 规范

- [ ] CHK143 - 是否为WebSocket连接定义了握手参数和认证方式？ [缺口]
- [ ] CHK144 - 是否定义了WebSocket心跳消息的格式和频率？ [缺口]
- [ ] CHK145 - 是否定义了WebSocket断开重连的策略和客户端行为？ [缺口]
- [ ] CHK146 - 进度WebSocket（/ws/progress/{novelId}）的消息类型是否与代码实现一致？ [一致性]
- [ ] CHK147 - 查询流WebSocket（/api/query/stream）的5个阶段消息是否完整定义？ [完整性]
- [ ] CHK148 - 是否定义了WebSocket错误消息的统一格式？ [缺口]

## API 可用性

- [ ] CHK149 - 是否提供了所有API的cURL示例？ [完整性，README.md §使用示例]
- [ ] CHK150 - 是否提供了前端JavaScript调用示例？ [完整性，README.md §WebSocket查询]
- [ ] CHK151 - 是否说明了如何访问Swagger UI和Redoc文档？ [完整性，README.md §在线文档查看]
- [ ] CHK152 - 是否定义了开发环境和生产环境的API Base URL？ [完整性，openapi.yaml §servers]
- [ ] CHK153 - 是否提供了Postman Collection或API测试工具配置？ [缺口]

## 查询与过滤

- [ ] CHK154 - GET /novels API的过滤参数（status）是否与所有枚举值对应？ [完整性，openapi.yaml]
- [ ] CHK155 - 是否定义了排序参数（sort、order）的规范？ [缺口]
- [ ] CHK156 - 是否定义了搜索参数（search、keyword）的模糊匹配规则？ [缺口]
- [ ] CHK157 - GET /query/history是否定义了时间范围过滤参数？ [缺口]
- [ ] CHK158 - 是否定义了批量操作API（如批量删除小说）？ [缺口]

## 性能相关

- [ ] CHK159 - 是否为大文件上传定义了分块上传（Chunked Upload）机制？ [缺口]
- [ ] CHK160 - 是否定义了API响应的压缩方式（如gzip）？ [缺口]
- [ ] CHK161 - 是否定义了图片、静态资源的CDN缓存策略？ [缺口]
- [ ] CHK162 - 是否定义了长时间运行的API的超时时间？ [缺口]
- [ ] CHK163 - 是否为查询结果定义了缓存机制（如ETag、Last-Modified）？ [缺口]

## 版本控制

- [ ] CHK164 - 是否定义了API版本控制策略（URL路径 vs Header）？ [清晰度，README.md §版本控制]
- [ ] CHK165 - 是否定义了API废弃（Deprecated）的通知和迁移策略？ [缺口]
- [ ] CHK166 - 是否定义了向后兼容性的保证范围？ [缺口]

## 安全性

- [ ] CHK167 - 是否定义了HTTPS的强制使用要求？ [缺口]
- [ ] CHK168 - 是否定义了CORS策略的具体配置（允许的来源、方法、头部）？ [缺口]
- [ ] CHK169 - 是否定义了文件上传的大小限制和类型白名单？ [缺口]
- [ ] CHK170 - 是否定义了敏感数据（如API Key）的脱敏展示规则？ [缺口]
- [ ] CHK171 - 是否定义了SQL注入、XSS攻击的防护说明？ [缺口]

## 可观测性

- [ ] CHK172 - 是否定义了所有API的请求ID（Request ID）用于日志追踪？ [缺口]
- [ ] CHK173 - 是否定义了性能监控的埋点要求（如响应时间、错误率）？ [缺口]
- [ ] CHK174 - 是否定义了健康检查端点（Health Check）的详细信息？ [完整性，/health端点]
- [ ] CHK175 - 是否定义了API调用的审计日志要求？ [缺口]

## 测试支持

- [ ] CHK176 - 是否提供了Mock Server配置或测试数据生成工具？ [缺口]
- [ ] CHK177 - 是否为所有API定义了测试用例（Test Cases）？ [缺口]
- [ ] CHK178 - 是否定义了集成测试的API调用顺序和数据依赖？ [缺口]
- [ ] CHK179 - 是否定义了性能测试的基准数据和压测场景？ [缺口]

## 文档质量

- [ ] CHK180 - 是否所有API的描述清晰且无歧义？ [清晰度，openapi.yaml]
- [ ] CHK181 - 是否所有数据模型（Schema）都有详细的字段说明？ [完整性，openapi.yaml §components/schemas]
- [ ] CHK182 - 是否所有枚举值都有注释说明其含义？ [清晰度]
- [ ] CHK183 - 是否提供了完整的API变更日志（Changelog）？ [缺口]
- [ ] CHK184 - 是否链接到相关的数据模型文档（data-model.md）？ [追溯性，README.md §相关文档]

## 实现对齐

- [ ] CHK185 - openapi.yaml中定义的路径是否与后端实际路由一致？ [一致性，对比backend/app/api/]
- [ ] CHK186 - openapi.yaml中定义的Schema是否与backend/app/models/schemas.py一致？ [一致性]
- [ ] CHK187 - WebSocket消息类型是否与frontend/lib/websocket.ts中的类型定义一致？ [一致性]
- [ ] CHK188 - API响应格式是否与frontend/types/中的TypeScript定义一致？ [一致性]
- [ ] CHK189 - 是否所有API端点都在Swagger UI中可测试？ [可用性]
- [ ] CHK190 - 是否所有API的错误响应都经过实际测试验证？ [可验证性]

---

**检查清单统计**: 70项（CHK121-CHK190）  
**强制检查项**: CHK121-CHK150（API基础质量）  
**建议检查项**: CHK151-CHK190（深度质量提升）

**使用说明**:
- 在PR审查时，重点检查API定义的完整性和一致性
- 发现API规范与实现不一致时，要求更新openapi.yaml或修改代码
- 对于缺失的安全性、性能相关定义，要求补充到规范中
- 使用Swagger UI验证所有API的可用性

