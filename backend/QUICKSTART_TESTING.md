# 测试系统快速入门 ⚡

## 5分钟快速开始

### 1️⃣ 运行你的第一个测试

```bash
cd backend
python run_tests.py --type unit
```

预期输出：
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

### 2️⃣ 查看所有可用的测试

```bash
# 查看测试统计
poetry run pytest --collect-only

# 查看测试树
poetry run pytest --collect-only -q
```

### 3️⃣ 运行特定测试

```bash
# 运行特定文件
poetry run pytest tests/unit/test_schemas.py

# 运行特定测试类
poetry run pytest tests/unit/test_schemas.py::TestNovelSchemas

# 运行特定测试方法
poetry run pytest tests/unit/test_schemas.py::TestNovelSchemas::test_novel_summary_serialization
```

## 🎨 常用测试场景

### 场景1: 本地快速测试（开发时）

```bash
# 只运行单元测试，跳过慢速测试
python run_tests.py --type unit --no-slow
```

**执行时间**: < 10秒  
**适用于**: 频繁修改代码时的快速验证

### 场景2: 完整测试（提交前）

```bash
# 运行所有测试，但跳过需要API key的外部服务
python run_tests.py --no-external --coverage
```

**执行时间**: 30-60秒  
**适用于**: 提交代码前的完整验证

### 场景3: 生产级测试（CI/CD）

```bash
# 运行所有测试，生成覆盖率报告
python run_tests.py --coverage
```

**执行时间**: 1-3分钟  
**适用于**: CI/CD流水线和发布前验证

### 场景4: 测试特定功能模块

```bash
# 测试Novel相关功能
poetry run pytest tests/ -k "novel"

# 测试RAG相关功能
poetry run pytest tests/ -k "rag"

# 测试API端点
poetry run pytest tests/e2e/
```

## 🔧 配置环境

### 可选: 配置智谱AI API（集成测试）

如果你想运行完整的集成测试（包括RAG功能），需要配置API Key：

```bash
# 方法1: 环境变量
export ZAI_API_KEY="your-api-key-here"

# 方法2: .env文件
echo "ZAI_API_KEY=your-api-key-here" >> .env

# 验证配置
python -c "from app.core.config import settings; print('API Key:', settings.ZAI_API_KEY[:20] if settings.ZAI_API_KEY else 'Not configured')"
```

没有API Key？没关系！大部分测试使用Mock，不需要真实API。

## 📊 理解测试输出

### 成功的测试

```
tests/unit/test_schemas.py::TestNovelSchemas::test_novel_summary_serialization PASSED [25%]
```

- ✅ `PASSED` - 测试通过
- `[25%]` - 完成进度

### 失败的测试

```
tests/unit/test_schemas.py::TestNovelSchemas::test_validation FAILED [50%]

================================ FAILURES =================================
_______________ TestNovelSchemas.test_validation _______________

    def test_validation():
>       assert result == expected
E       AssertionError: assert 'actual' == 'expected'

tests/unit/test_schemas.py:45: AssertionError
```

- ❌ `FAILED` - 测试失败
- 显示具体的错误位置和原因

### 跳过的测试

```
tests/integration/test_rag_service.py::TestRAGService::test_embedding SKIPPED [75%]
```

- ⏭️ `SKIPPED` - 测试被跳过（通常因为缺少外部依赖）

## 🎯 测试金字塔

```
      /\          E2E Tests (少量)
     /  \         - 完整流程
    /────\        - API端点
   /      \       
  /────────\      Integration Tests (中等)
 /          \     - 组件交互
/────────────\    - 数据库操作
               
────────────────  Unit Tests (大量)
                  - 纯函数测试
                  - 快速执行
```

**建议比例**: 单元测试 70% | 集成测试 20% | E2E测试 10%

## 🐛 调试失败的测试

### 方法1: 详细输出

```bash
poetry run pytest tests/unit/test_schemas.py -vv
```

### 方法2: 进入调试器

```bash
poetry run pytest tests/unit/test_schemas.py --pdb
```

失败时会自动进入Python调试器（pdb）：
```python
> /path/to/test_schemas.py(45)test_validation()
-> assert result == expected
(Pdb) print(result)
'actual value'
(Pdb) print(expected)
'expected value'
```

### 方法3: 显示print输出

```bash
poetry run pytest tests/unit/test_schemas.py -s
```

### 方法4: 只运行失败的测试

```bash
# 第一次运行发现失败
poetry run pytest

# 只重新运行失败的测试
poetry run pytest --lf
```

## 📝 编写你的第一个测试

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

## 🎓 下一步

- 📖 阅读 [完整测试文档](tests/README.md)
- 📋 查看 [测试系统说明](TESTING.md)
- 🔍 探索现有测试文件获取灵感
- ✍️ 为你的功能编写测试

## 💡 提示

- 💻 使用 `pytest --markers` 查看所有测试标记
- 🔧 使用 `pytest --fixtures` 查看所有可用fixtures
- 📊 使用 `pytest --durations=10` 查看最慢的测试
- 🎯 使用 `-k "关键词"` 按名称过滤测试

## ❓ 常见问题

**Q: 测试太慢了？**
```bash
# 只运行单元测试
python run_tests.py --type unit --no-slow
```

**Q: 某些测试需要API Key？**
```bash
# 跳过外部服务测试
python run_tests.py --no-external
```

**Q: 如何并行运行测试？**
```bash
# 安装pytest-xdist
poetry add -D pytest-xdist

# 并行运行
poetry run pytest -n auto
```

**Q: 如何查看代码覆盖率？**
```bash
python run_tests.py --coverage
# 打开 htmlcov/index.html 查看报告
```

---

**🎉 祝测试愉快！如有问题，请查阅完整文档或联系团队。**

