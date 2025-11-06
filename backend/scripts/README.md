# 管理脚本说明

本目录包含了小说RAG系统的管理和维护脚本。

## 📜 脚本列表

### 1. verify_env.py - 环境验证脚本

**用途**: 验证系统环境配置是否正确

**使用**:
```bash
cd backend
poetry run python scripts/verify_env.py
```

**检查项目**:
- ✅ 环境变量配置(.env文件)
- ✅ SQLite 数据库连接
- ✅ Redis 连接
- ✅ Qdrant 向量数据库连接
- ✅ 智谱AI API 连接

**何时使用**: 
- 首次安装系统后
- 修改配置后
- 遇到连接问题时

---

### 2. init_db.py - 数据库初始化脚本

**用途**: 初始化或重置数据库表结构

**使用**:
```bash
cd backend
poetry run python scripts/init_db.py
```

**功能**:
- 创建所有数据库表
- 初始化表结构
- 适用于首次安装或数据库重置

**注意**: 不会删除现有数据,只会创建缺失的表

---

### 3. start.sh - Linux/Mac启动脚本

**用途**: 一键启动后端服务(Linux/Mac系统)

**使用**:
```bash
cd backend
chmod +x scripts/start.sh
./scripts/start.sh
```

**执行流程**:
1. 检查.env文件是否存在
2. 启动Docker服务(Redis + Qdrant)
3. 等待服务就绪
4. 验证环境配置
5. 启动FastAPI服务

**适用系统**: Linux, macOS, WSL

---

### 4. run_tests.py - 测试运行脚本(跨平台)

**用途**: 统一的测试运行入口,支持多种测试模式

**使用**:
```bash
# 基本用法
python scripts/run_tests.py

# 常用选项
python scripts/run_tests.py --type unit          # 只运行单元测试
python scripts/run_tests.py --coverage           # 生成覆盖率报告
python scripts/run_tests.py --no-external        # 跳过外部服务测试
python scripts/run_tests.py --no-slow            # 跳过慢速测试
```

**参数说明**:
- `--type`: 测试类型 (unit/integration/e2e/all)
- `--verbose`: 详细输出
- `--coverage`: 生成代码覆盖率报告
- `--no-external`: 跳过需要外部API的测试
- `--no-slow`: 跳过执行时间较长的测试
- `--markers`: 自定义pytest markers

**适用系统**: Windows, Linux, macOS

**详细文档**: 查看 [../TESTING.md](../TESTING.md)

---

### 5. run_tests.ps1 - PowerShell测试脚本

**用途**: Windows PowerShell环境下的测试脚本

**使用**:
```powershell
# 基本用法
.\scripts\run_tests.ps1

# 常用选项
.\scripts\run_tests.ps1 -Type unit              # 只运行单元测试
.\scripts\run_tests.ps1 -Coverage               # 生成覆盖率报告
.\scripts\run_tests.ps1 -NoExternal             # 跳过外部服务测试
.\scripts\run_tests.ps1 -NoSlow                 # 跳过慢速测试
```

**参数说明**:
- `-Type`: 测试类型
- `-Verbose`: 详细输出
- `-Coverage`: 生成覆盖率报告
- `-NoExternal`: 跳过外部服务测试
- `-NoSlow`: 跳过慢速测试

**适用系统**: Windows (PowerShell)

**提示**: 推荐使用 `run_tests.py` (跨平台通用)

---

## 🚀 快速使用指南

### 首次安装

```bash
# 1. 验证环境
poetry run python scripts/verify_env.py

# 2. 初始化数据库(如需要)
poetry run python scripts/init_db.py

# 3. 启动服务(Linux/Mac)
./scripts/start.sh

# 或手动启动(Windows)
docker-compose up -d
poetry run uvicorn app.main:app --reload
```

### 日常开发

```bash
# 快速测试
python scripts/run_tests.py --type unit --no-slow

# 提交前完整测试
python scripts/run_tests.py --coverage
```

---

## 💡 提示

1. **环境验证失败**: 检查Docker服务是否启动,配置文件是否正确
2. **测试失败**: 查看详细日志,参考 [TESTING.md](../TESTING.md)
3. **权限问题**: Linux/Mac下需要给.sh脚本执行权限 `chmod +x scripts/*.sh`

---

## 📚 相关文档

- [主文档 (README.md)](../README.md)
- [测试文档 (TESTING.md)](../TESTING.md)
- [故障排查 (TROUBLESHOOTING.md)](../TROUBLESHOOTING.md)

---

**最后更新**: 2025-11-06

