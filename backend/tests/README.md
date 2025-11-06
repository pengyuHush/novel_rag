# 测试系统文档

## 📁 目录结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py           # Pytest配置和共享fixtures
├── README.md             # 本文档
│
├── unit/                 # 单元测试（快速，无外部依赖）
│   ├── test_schemas.py   # Schema序列化和验证测试
│   ├── test_repositories.py  # Repository层测试
│   └── test_utils.py     # 工具函数测试
│
├── integration/          # 集成测试（需要外部服务）
│   ├── test_rag_service.py   # RAG服务集成测试
│   └── test_external_services.py  # 外部服务测试
│
├── e2e/                  # 端到端测试（完整流程）
│   └── test_api_endpoints.py  # API端点完整流程测试
│
├── helpers/              # 测试辅助工具
│   ├── __init__.py
│   ├── factories.py      # 测试数据工厂
│   ├── assertions.py     # 自定义断言
│   └── utils.py          # 测试工具函数
│
└── fixtures/             # 测试数据和fixtures
    └── __init__.py
```

## 🎯 测试分类

### 1. 单元测试 (Unit Tests)

**特点**:
- ✅ 快速执行（< 1秒）
- ✅ 不依赖外部服务
- ✅ 测试单个函数/类
- ✅ 使用Mock对象

**标记**: `@pytest.mark.unit`

**示例**:
```python
@pytest.mark.unit
def test_schema_serialization():
    novel = NovelSummary(...)
    data = novel.model_dump(by_alias=True)
    assert "wordCount" in data
```

### 2. 集成测试 (Integration Tests)

**特点**:
- ⏱️ 中等执行时间（1-10秒）
- 🌐 可能需要外部服务（数据库、Redis、Qdrant）
- 🔗 测试组件交互
- 📦 测试真实依赖

**标记**: `@pytest.mark.integration`

**示例**:
```python
@pytest.mark.integration
async def test_rag_service(db_session):
    service = RAGService(db_session)
    result = await service.search("query")
    assert result is not None
```

### 3. 端到端测试 (E2E Tests)

**特点**:
- ⏳ 较慢执行（5-30秒）
- 🌐 需要完整服务栈
- 📡 测试API端点
- ✨ 测试完整业务流程

**标记**: `@pytest.mark.e2e`

**示例**:
```python
@pytest.mark.e2e
async def test_full_workflow(api_client):
    # 创建小说
    response = await api_client.post("/api/v1/novels", ...)
    # 上传内容
    # 搜索
    # 删除
```

### 4. 特殊标记

- `@pytest.mark.external` - 需要外部API（智谱AI）
- `@pytest.mark.slow` - 执行时间较长
- `@pytest.mark.skip_ci` - CI环境中跳过

## 🚀 运行测试

### 使用Python脚本（推荐）

```bash
# 运行所有测试
python run_tests.py

# 运行特定类型测试
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type e2e

# 生成覆盖率报告
python run_tests.py --coverage

# 跳过外部服务测试
python run_tests.py --no-external

# 跳过慢速测试
python run_tests.py --no-slow

# 详细输出
python run_tests.py --verbose

# 自定义markers
python run_tests.py --markers "unit and not slow"
```

### 使用PowerShell脚本（Windows）

```powershell
# 运行所有测试
.\run_tests.ps1

# 运行特定类型测试
.\run_tests.ps1 -Type unit
.\run_tests.ps1 -Type integration

# 生成覆盖率报告
.\run_tests.ps1 -Coverage

# 跳过外部服务
.\run_tests.ps1 -NoExternal

# 跳过慢速测试
.\run_tests.ps1 -NoSlow
```

### 直接使用Pytest

```bash
# 运行所有测试
poetry run pytest

# 运行特定目录
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest tests/e2e

# 运行特定文件
poetry run pytest tests/unit/test_schemas.py

# 运行特定测试
poetry run pytest tests/unit/test_schemas.py::TestNovelSchemas::test_novel_summary_serialization

# 使用markers
poetry run pytest -m unit          # 只运行单元测试
poetry run pytest -m "not external"  # 跳过外部服务测试
poetry run pytest -m "unit and not slow"  # 快速单元测试

# 详细输出
poetry run pytest -vv

# 代码覆盖率
poetry run pytest --cov=app --cov-report=html

# 只显示失败的测试
poetry run pytest -v --tb=short

# 并行运行（需要安装pytest-xdist）
poetry run pytest -n auto
```

## 📊 代码覆盖率

查看覆盖率报告：

```bash
# 生成并打开HTML报告
python run_tests.py --coverage
# 报告位于: htmlcov/index.html

# 或直接使用pytest
poetry run pytest --cov=app --cov-report=html
```

覆盖率目标：
- 单元测试: **80%+**
- 集成测试: **70%+**
- 总体覆盖率: **75%+**

## 🔧 编写测试指南

### 1. 使用Fixtures

```python
async def test_with_db(db_session: AsyncSession):
    """使用数据库session fixture."""
    repo = NovelRepository(db_session)
    ...

async def test_with_api_client(api_client: AsyncClient):
    """使用API客户端fixture."""
    response = await api_client.get("/api/v1/novels")
    ...
```

### 2. 使用工厂函数

```python
from tests.helpers import NovelFactory

def test_create_novel():
    # 快速创建测试数据
    novel_data = NovelFactory.create_novel_data()
    novel_content = NovelFactory.create_novel_content(chapters=3)
```

### 3. 使用自定义断言

```python
from tests.helpers import assert_response_success, assert_pagination

async def test_list_novels(api_client):
    response = await api_client.get("/api/v1/novels")
    assert_response_success(response, 200)
    assert_pagination(response.json(), expected_page=1)
```

### 4. Mock外部服务

```python
def test_with_mock_zhipu(mock_zhipu_client):
    """使用Mock的智谱AI客户端."""
    rag = RAGService()
    rag.client = mock_zhipu_client
    ...
```

## 📝 测试最佳实践

### ✅ 做什么

1. **测试命名清晰**: `test_create_novel_with_valid_data`
2. **使用Arrange-Act-Assert模式**:
   ```python
   def test_example():
       # Arrange - 准备测试数据
       data = {...}
       
       # Act - 执行被测试代码
       result = function(data)
       
       # Assert - 验证结果
       assert result == expected
   ```
3. **测试边界情况**: 空输入、最大值、错误输入
4. **使用fixtures共享设置**: 避免重复代码
5. **添加docstring**: 说明测试目的

### ❌ 不要做什么

1. **不要测试依赖**: 只测试自己的代码
2. **不要依赖测试顺序**: 每个测试应独立
3. **不要使用真实外部API**: 使用Mock或跳过
4. **不要忽略慢速测试**: 使用标记分类
5. **不要省略清理**: 使用fixtures自动清理

## 🔍 调试测试

```bash
# 进入调试器
poetry run pytest --pdb

# 只运行失败的测试
poetry run pytest --lf

# 显示print输出
poetry run pytest -s

# 详细的traceback
poetry run pytest --tb=long

# 显示测试执行时间
poetry run pytest --durations=10
```

## 📈 持续集成

在CI环境中运行测试：

```bash
# 快速测试（跳过外部服务和慢速测试）
python run_tests.py --no-external --no-slow

# 完整测试（需要配置API密钥）
python run_tests.py --coverage
```

## 🆘 常见问题

### Q: 测试失败怎么办？

1. 查看错误信息和traceback
2. 使用 `-vv` 查看详细输出
3. 使用 `--pdb` 进入调试器
4. 检查fixtures和mock配置

### Q: 如何跳过特定测试？

```python
@pytest.mark.skip(reason="暂时跳过")
def test_something():
    ...

@pytest.mark.skipif(condition, reason="条件跳过")
def test_something():
    ...
```

### Q: 如何测试异步代码？

使用 `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Q: 如何参数化测试？

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

## 📚 相关资源

- [Pytest文档](https://docs.pytest.org/)
- [Pytest-asyncio文档](https://pytest-asyncio.readthedocs.io/)
- [Httpx测试文档](https://www.python-httpx.org/advanced/#testing)
- [FastAPI测试文档](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 贡献指南

添加新测试时：

1. 选择合适的目录（unit/integration/e2e）
2. 使用清晰的命名和文档
3. 添加适当的标记（markers）
4. 确保测试独立且可重复
5. 运行测试确保通过
6. 更新本文档（如有必要）

---

**最后更新**: 2025-11-06

