# Python版本说明

## 为什么使用Python 3.12而非3.14？

### 兼容性问题

Python 3.14是最新版本（2024年10月发布），许多第三方库尚未完全测试和适配。本项目使用的关键依赖中，有些在Python 3.14下可能存在兼容性问题：

| 库名 | 问题描述 | 状态 |
|------|----------|------|
| **HanLP 2.1** | 中文NLP库，依赖的底层C++扩展可能未针对3.14编译 | ⚠️ 未完全适配 |
| **ChromaDB 0.4** | 某些numpy/scipy依赖可能有兼容问题 | ⚠️ 需验证 |
| **LangChain** | 间接依赖可能受影响 | ⚠️ 需验证 |

### Python 3.12的优势

- ✅ **稳定性**: 已发布超过1年（2023年10月），生态成熟
- ✅ **性能提升**: 相比3.10/3.11有显著性能改进
- ✅ **库兼容性**: 主流库都已完全支持
- ✅ **生产就绪**: 适合生产环境部署

### Python版本时间线

- Python 3.10: 2021年10月 ✅ 成熟稳定
- Python 3.11: 2022年10月 ✅ 成熟稳定  
- **Python 3.12: 2023年10月** ✅ **推荐使用**
- Python 3.13: 2024年10月 ⚠️ 较新
- Python 3.14: 2025年10月 ⚠️ 最新版，库适配中

### 本项目要求

```toml
[tool.poetry.dependencies]
python = ">=3.12,<3.14"
```

- **最低版本**: Python 3.12
- **最高版本**: < 3.14（不包含3.14）
- **推荐版本**: Python 3.12.x（最新的3.12补丁版本）

### 如何检查当前Python版本

```bash
python --version
```

### 如何安装Python 3.12

1. 访问Python官网: https://www.python.org/downloads/
2. 下载Python 3.12.x最新版（当前3.12.7）
3. 安装时勾选"Add Python to PATH"
4. 验证安装: `python3.12 --version`

### 多版本共存

如果您需要同时使用多个Python版本：

**Windows - py启动器**:
```bash
py -3.12 --version   # 使用Python 3.12
py -3.14 --version   # 使用Python 3.14
```

**macOS/Linux - pyenv**:
```bash
# 安装pyenv
curl https://pyenv.run | bash

# 安装Python 3.12
pyenv install 3.12.7

# 设置项目Python版本
cd backend
pyenv local 3.12.7
```

### 未来升级计划

当所有依赖库完全适配Python 3.13/3.14后，我们会更新项目要求。

预计时间：
- Python 3.13支持: 2025年Q2
- Python 3.14支持: 2025年Q4

---

**最后更新**: 2025-11-13  
**当前推荐版本**: Python 3.12.7

