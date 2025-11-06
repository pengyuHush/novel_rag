# 小说RAG系统 - 测试系统说明

## 📖 概述

本文档描述了小说RAG系统的测试架构和使用方法。我们采用了**标准化的pytest测试框架**，将测试分为**单元测试**、**集成测试**和**端到端测试**三个层次。

## ✨ 特性

- ✅ **标准化架构**: 清晰的目录结构和命名规范
- ✅ **完整覆盖**: 单元、集成、E2E三层测试
- ✅ **易于使用**: 统一的测试运行脚本
- ✅ **灵活配置**: 支持多种测试模式和标记
- ✅ **代码覆盖率**: 自动生成覆盖率报告
- ✅ **Mock支持**: 内置Mock fixtures，无需外部服务
- ✅ **测试工具**: 丰富的辅助函数和数据工厂

## 🏗️ 架构设计

### 目录结构

```
backend/
├── pytest.ini              # Pytest配置文件
├── run_tests.py            # Python测试运行脚本（跨平台）
├── run_tests.ps1           # PowerShell测试脚本（Windows）
│
└── tests/                  # 测试根目录
    ├── __init__.py
    ├── conftest.py         # 全局fixtures和配置
    ├── README.md           # 详细测试文档
    │
    ├── unit/               # 单元测试
    │   ├── test_schemas.py
    │   ├── test_repositories.py
    │   └── test_utils.py
    │
    ├── integration/        # 集成测试
    │   ├── test_rag_service.py
    │   └── test_external_services.py
    │
    ├── e2e/               # 端到端测试
    │   └── test_api_endpoints.py
    │
    ├── helpers/           # 测试辅助工具
    │   ├── __init__.py
    │   ├── factories.py   # 测试数据工厂
    │   ├── assertions.py  # 自定义断言
    │   └── utils.py       # 工具函数
    │
    └── fixtures/          # 测试数据
        └── __init__.py
```

### 测试分层

```
┌─────────────────────────────────────────┐
│         端到端测试 (E2E)                  │
│   • 完整业务流程                          │
│   • API端点测试                          │
│   • 真实服务交互                          │
│   • 执行时间: 5-30秒                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         集成测试 (Integration)            │
│   • 组件交互测试                          │
│   • 数据库操作                           │
│   • 外部服务调用                          │
│   • 执行时间: 1-10秒                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         单元测试 (Unit)                   │
│   • 单一功能测试                          │
│   • 纯函数测试                           │
│   • Mock外部依赖                         │
│   • 执行时间: < 1秒                      │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
poetry install
```

### 2. 运行测试

#### 使用Python脚本（推荐）

```bash
# 运行所有测试
python run_tests.py

# 运行单元测试（快速）
python run_tests.py --type unit

# 生成覆盖率报告
python run_tests.py --coverage

# 跳过外部服务测试
python run_tests.py --no-external

# 快速测试（单元测试 + 跳过慢速）
python run_tests.py --type unit --no-slow
```

#### 使用PowerShell脚本（Windows）

```powershell
# 运行所有测试
.\run_tests.ps1

# 运行单元测试
.\run_tests.ps1 -Type unit

# 生成覆盖率报告
.\run_tests.ps1 -Coverage
```

#### 直接使用Pytest

```bash
# 运行所有测试
poetry run pytest

# 运行特定类型
poetry run pytest tests/unit
poetry run pytest -m unit

# 使用markers
poetry run pytest -m "unit and not slow"
poetry run pytest -m "not external"
```

## 📊 测试标记 (Markers)

| 标记 | 说明 | 使用场景 |
|------|------|----------|
| `unit` | 单元测试 | 快速测试，无外部依赖 |
| `integration` | 集成测试 | 需要数据库等服务 |
| `e2e` | 端到端测试 | 完整流程测试 |
| `external` | 外部服务 | 需要智谱AI API |
| `slow` | 慢速测试 | 执行时间较长 |
| `skip_ci` | 跳过CI | CI环境中跳过 |

### 标记使用示例

```python
@pytest.mark.unit
def test_schema_validation():
    """单元测试示例."""
    pass

@pytest.mark.integration
@pytest.mark.external
async def test_rag_service():
    """集成测试示例（需要外部服务）."""
    pass

@pytest.mark.e2e
@pytest.mark.slow
async def test_full_workflow():
    """端到端测试示例."""
    pass
```

## 🛠️ 测试工具

### 1. Fixtures (conftest.py)

```python
# 数据库session
async def test_with_db(db_session: AsyncSession):
    repo = NovelRepository(db_session)
    ...

# API客户端
async def test_with_api(api_client: AsyncClient):
    response = await api_client.get("/api/v1/novels")
    ...

# Mock客户端
def test_with_mock(mock_zhipu_client):
    rag = RAGService()
    rag.client = mock_zhipu_client
    ...
```

### 2. 数据工厂 (helpers/factories.py)

```python
from tests.helpers import NovelFactory, ChapterFactory

# 快速创建测试数据
novel_data = NovelFactory.create_novel_data()
novel_content = NovelFactory.create_novel_content(chapters=3)
chapter_data = ChapterFactory.create_chapter_data(novel_id="xxx")
```

### 3. 自定义断言 (helpers/assertions.py)

```python
from tests.helpers import (
    assert_response_success,
    assert_pagination,
    assert_novel_equal
)

# 断言API响应成功
assert_response_success(response, 200)

# 断言分页数据正确
assert_pagination(data, expected_page=1, expected_size=10)

# 断言小说数据相等
assert_novel_equal(actual, expected, check_fields=["title", "author"])
```

### 4. 工具函数 (helpers/utils.py)

```python
from tests.helpers.utils import (
    create_test_file,
    cleanup_test_files,
    create_mock_novel_file
)

# 创建测试文件
file_path = create_test_file(content, encoding="utf-8")

# 清理测试文件
cleanup_test_files(file_path1, file_path2)

# 创建模拟小说文件
novel_file = create_mock_novel_file(chapters=5)
```

## 📈 代码覆盖率

### 查看覆盖率报告

```bash
# 生成HTML报告
python run_tests.py --coverage

# 报告位置: backend/htmlcov/index.html
# 使用浏览器打开查看
```

### 覆盖率目标

- **单元测试**: ≥ 80%
- **集成测试**: ≥ 70%
- **总体覆盖率**: ≥ 75%

## 🎯 最佳实践

### ✅ 推荐做法

1. **测试命名清晰**: `test_create_novel_with_valid_data`
2. **使用AAA模式**: Arrange-Act-Assert
3. **测试独立性**: 每个测试独立运行
4. **使用fixtures**: 共享测试设置
5. **适当使用Mock**: 隔离外部依赖
6. **添加文档**: 使用docstring说明测试目的

### ❌ 避免做法

1. **不要依赖测试顺序**: 测试应该能以任意顺序运行
2. **不要使用真实外部API**: 使用Mock或标记为external
3. **不要忽略清理**: 使用fixtures自动清理资源
4. **不要过度Mock**: 保持测试的真实性
5. **不要忽略边界情况**: 测试正常和异常情况

## 🔍 调试技巧

```bash
# 进入调试器
poetry run pytest --pdb

# 只运行失败的测试
poetry run pytest --lf

# 显示print输出
poetry run pytest -s

# 详细的traceback
poetry run pytest --tb=long

# 显示最慢的10个测试
poetry run pytest --durations=10

# 详细输出
poetry run pytest -vv
```

## 🔄 CI/CD集成

### 快速测试（提交时）

```bash
# 跳过外部服务和慢速测试
python run_tests.py --no-external --no-slow --type unit
```

### 完整测试（PR时）

```bash
# 运行所有测试并生成覆盖率
python run_tests.py --coverage
```

### 环境变量配置

```bash
# 配置智谱AI API Key（集成测试需要）
export ZAI_API_KEY="your-api-key"

# 或在.env文件中配置
echo "ZAI_API_KEY=your-api-key" >> .env
```

## 📚 相关文档

- [详细测试文档](./tests/README.md) - 完整的测试指南
- [Pytest文档](https://docs.pytest.org/) - Pytest官方文档
- [FastAPI测试](https://fastapi.tiangolo.com/tutorial/testing/) - FastAPI测试指南

## 🤝 贡献指南

添加新测试时：

1. ✅ 选择合适的测试类型和目录
2. ✅ 使用清晰的命名和文档
3. ✅ 添加适当的pytest标记
4. ✅ 使用现有的fixtures和工具
5. ✅ 确保测试独立且可重复
6. ✅ 运行测试确保通过
7. ✅ 检查代码覆盖率

## 📞 获取帮助

- 查看 `tests/README.md` 获取详细指南
- 运行 `pytest --markers` 查看所有可用标记
- 运行 `pytest --fixtures` 查看所有可用fixtures

---

**测试系统版本**: 1.0.0  
**最后更新**: 2025-11-06  
**维护者**: 后端开发团队

