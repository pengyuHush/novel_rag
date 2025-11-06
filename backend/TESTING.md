# 小说RAG系统 - 测试文档

## 📖 概述

本文档提供小说RAG系统的完整测试指南,包括快速入门、系统架构和详细使用说明。

## ✨ 特性

- ✅ **标准化架构**: 清晰的目录结构和命名规范
- ✅ **完整覆盖**: 单元、集成、E2E三层测试  
- ✅ **易于使用**: 统一的测试运行脚本
- ✅ **灵活配置**: 支持多种测试模式和标记
- ✅ **代码覆盖率**: 自动生成覆盖率报告
- ✅ **Mock支持**: 内置Mock fixtures,无需外部服务
- ✅ **测试工具**: 丰富的辅助函数和数据工厂

---

## 🚀 快速开始

### 1️⃣ 运行你的第一个测试

```bash
cd backend
python scripts/run_tests.py --type unit
```

预期输出:
```
╔============================================================╗
║                  小说 RAG 系统测试                         ║
╚============================================================╝

📝 测试类型: unit
📊 代码覆盖: 否
🌐 外部服务: 包含
⏱️  慢速测试: 包含

============================================================
🔍 运行测试
============================================================

tests/unit/test_schemas.py::TestNovelSchemas::test_novel_summary_serialization PASSED
tests/unit/test_repositories.py::TestNovelRepository::test_create_novel PASSED
...

✅ 运行测试成功

============================================================
🎉 所有测试通过!
============================================================
```

### 2️⃣ 常用测试命令

```bash
# 快速测试(开发时) - 只运行单元测试,跳过慢速测试
python scripts/run_tests.py --type unit --no-slow

# 完整测试(提交前) - 运行所有测试,跳过外部服务
python scripts/run_tests.py --no-external --coverage

# 生产级测试(CI/CD) - 运行所有测试并生成覆盖率报告
python scripts/run_tests.py --coverage

# 特定功能测试
poetry run pytest tests/ -k "novel"     # 测试Novel相关功能
poetry run pytest tests/ -k "rag"       # 测试RAG相关功能
poetry run pytest tests/e2e/            # 测试API端点
```

### 3️⃣ 配置环境(可选)

如果你想运行完整的集成测试(包括RAG功能),需要配置智谱AI API Key:

```bash
# 方法1: 环境变量
export ZAI_API_KEY="your-api-key-here"

# 方法2: .env文件
echo "ZAI_API_KEY=your-api-key-here" >> .env

# 验证配置
python -c "from app.core.config import settings; print('API Key:', settings.ZAI_API_KEY[:20] if settings.ZAI_API_KEY else 'Not configured')"
```

**提示**: 没有API Key也没关系!大部分测试使用Mock,不需要真实API。

---

## 🏗️ 测试架构

### 目录结构

```
backend/
├── pytest.ini              # Pytest配置文件
├── scripts/                # 测试脚本
│   ├── run_tests.py       # Python测试脚本(跨平台,推荐)
│   └── run_tests.ps1      # PowerShell测试脚本(Windows)
│
└── tests/                  # 测试根目录
    ├── conftest.py         # 全局fixtures和配置
    ├── README.md           # 详细测试指南
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
    │   ├── factories.py   # 测试数据工厂
    │   ├── assertions.py  # 自定义断言
    │   └── utils.py       # 工具函数
    │
    └── fixtures/          # 测试数据
```

### 测试分层

```
┌─────────────────────────────────────────┐
│         端到端测试 (E2E) - 10%           │
│   • 完整业务流程                          │
│   • API端点测试                          │
│   • 真实服务交互                          │
│   • 执行时间: 5-30秒                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         集成测试 (Integration) - 20%     │
│   • 组件交互测试                          │
│   • 数据库操作                           │
│   • 外部服务调用                          │
│   • 执行时间: 1-10秒                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         单元测试 (Unit) - 70%            │
│   • 单一功能测试                          │
│   • 纯函数测试                           │
│   • Mock外部依赖                         │
│   • 执行时间: < 1秒                      │
└─────────────────────────────────────────┘
```

---

## 📊 测试标记(Markers)

| 标记 | 说明 | 使用场景 |
|------|------|----------|
| `unit` | 单元测试 | 快速测试,无外部依赖 |
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
    """集成测试示例(需要外部服务)."""
    pass

@pytest.mark.e2e
@pytest.mark.slow
async def test_full_workflow():
    """端到端测试示例."""
    pass
```

### 使用Markers过滤测试

```bash
# 只运行单元测试
poetry run pytest -m unit

# 跳过外部服务测试
poetry run pytest -m "not external"

# 快速测试(单元测试且非慢速)
poetry run pytest -m "unit and not slow"
```

---

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

---

## 🔍 调试技巧

### 详细输出

```bash
# 详细输出模式
poetry run pytest tests/unit/test_schemas.py -vv

# 显示print输出
poetry run pytest tests/unit/test_schemas.py -s

# 详细的traceback
poetry run pytest --tb=long
```

### 使用调试器

```bash
# 失败时自动进入调试器
poetry run pytest tests/unit/test_schemas.py --pdb

# 进入调试器后
(Pdb) print(result)      # 打印变量
(Pdb) continue           # 继续执行
(Pdb) quit               # 退出
```

### 只运行失败的测试

```bash
# 第一次运行发现失败
poetry run pytest

# 只重新运行失败的测试
poetry run pytest --lf

# 先运行上次失败的,再运行其他
poetry run pytest --ff
```

### 查看最慢的测试

```bash
poetry run pytest --durations=10
```

---

## 📈 代码覆盖率

### 生成覆盖率报告

```bash
# 生成HTML报告
python scripts/run_tests.py --coverage

# 报告位置: backend/htmlcov/index.html
# 使用浏览器打开查看
```

### 覆盖率目标

- **单元测试**: ≥ 80%
- **集成测试**: ≥ 70%  
- **总体覆盖率**: ≥ 75%

### 查看覆盖率详情

```bash
# 在终端显示覆盖率
poetry run pytest --cov=app --cov-report=term-missing

# 显示未覆盖的行
poetry run pytest --cov=app --cov-report=term:skip-covered
```

---

## 🎯 最佳实践

### ✅ 推荐做法

1. **测试命名清晰**: `test_create_novel_with_valid_data`
2. **使用AAA模式**: Arrange(准备) → Act(执行) → Assert(断言)
3. **测试独立性**: 每个测试独立运行,不依赖其他测试
4. **使用fixtures**: 共享测试设置,避免重复代码
5. **适当使用Mock**: 隔离外部依赖,提高测试速度
6. **添加文档**: 使用docstring说明测试目的

### AAA模式示例

```python
@pytest.mark.unit
def test_novel_creation():
    """测试小说创建功能."""
    # Arrange - 准备测试数据
    title = "测试小说"
    author = "测试作者"
    
    # Act - 执行操作
    novel = Novel(title=title, author=author)
    
    # Assert - 验证结果
    assert novel.title == title
    assert novel.author == author
```

### ❌ 避免做法

1. **不要依赖测试顺序**: 测试应该能以任意顺序运行
2. **不要使用真实外部API**: 使用Mock或标记为external
3. **不要忽略清理**: 使用fixtures自动清理资源
4. **不要过度Mock**: 保持测试的真实性
5. **不要忽略边界情况**: 测试正常和异常情况

---

## 🎓 编写你的第一个测试

### 1. 创建测试文件

```python
# tests/unit/test_my_feature.py

import pytest
from app.models.novel import Novel

@pytest.mark.unit
def test_novel_creation():
    """测试小说创建."""
    # Arrange - 准备数据
    title = "测试小说"
    author = "测试作者"
    
    # Act - 执行操作
    novel = Novel(title=title, author=author)
    
    # Assert - 验证结果
    assert novel.title == title
    assert novel.author == author
```

### 2. 运行你的测试

```bash
poetry run pytest tests/unit/test_my_feature.py -v
```

### 3. 使用测试工具

```python
from tests.helpers import NovelFactory, assert_novel_equal

@pytest.mark.unit
def test_with_factory():
    """使用工厂创建测试数据."""
    # 快速创建测试数据
    novel_data = NovelFactory.create_novel_data()
    
    # 使用自定义断言
    assert_novel_equal(novel_data, {
        "title": novel_data["title"],
        "author": novel_data["author"],
    }, check_fields=["title", "author"])
```

---

## 🔄 CI/CD集成

### 快速测试(提交时)

```bash
# 跳过外部服务和慢速测试
python scripts/run_tests.py --no-external --no-slow --type unit
```

### 完整测试(PR时)

```bash
# 运行所有测试并生成覆盖率
python scripts/run_tests.py --coverage
```

### GitHub Actions示例

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Poetry
        run: pip install poetry
      
      - name: Install Dependencies
        run: cd backend && poetry install
      
      - name: Run Tests
        run: cd backend && python scripts/run_tests.py --coverage
        env:
          ZAI_API_KEY: ${{ secrets.ZAI_API_KEY }}
```

---

## 💡 常见问题

### Q: 测试太慢了?

```bash
# 只运行单元测试
python scripts/run_tests.py --type unit --no-slow
```

### Q: 某些测试需要API Key?

```bash
# 跳过外部服务测试
python scripts/run_tests.py --no-external
```

### Q: 如何并行运行测试?

```bash
# 安装pytest-xdist
poetry add -D pytest-xdist

# 并行运行(自动检测CPU核心数)
poetry run pytest -n auto
```

### Q: 如何查看测试统计?

```bash
# 查看所有可用测试
poetry run pytest --collect-only

# 查看所有markers
poetry run pytest --markers

# 查看所有fixtures
poetry run pytest --fixtures
```

---

## 📚 相关资源

- **测试详细指南**: [tests/README.md](tests/README.md)
- **Pytest官方文档**: https://docs.pytest.org/
- **FastAPI测试指南**: https://fastapi.tiangolo.com/tutorial/testing/
- **故障排查文档**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🤝 贡献指南

添加新测试时:

1. ✅ 选择合适的测试类型和目录
2. ✅ 使用清晰的命名和文档
3. ✅ 添加适当的pytest标记
4. ✅ 使用现有的fixtures和工具
5. ✅ 确保测试独立且可重复
6. ✅ 运行测试确保通过
7. ✅ 检查代码覆盖率

---

**测试系统版本**: 1.0.0  
**最后更新**: 2025-11-06  
**维护者**: 后端开发团队
