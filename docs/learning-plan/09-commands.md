# 运行命令

## Python 依赖

安装 Python 依赖：

```powershell
pip install -r requirements.txt
```

运行测试：

```powershell
pytest
```

运行单个测试文件：

```powershell
pytest tests/test_todo_write_string_input.py
```

## 前端依赖

进入前端目录：

```powershell
cd web
```

安装前端依赖：

```powershell
npm install
```

启动前端开发服务：

```powershell
npm run dev
```

构建前端：

```powershell
npm run build
```

## 内容抽取

前端脚本会在 `predev` 和 `prebuild` 阶段自动执行：

```text
web/scripts/extract-content.ts
```

它会从根目录章节、文档和代码中抽取内容，生成 `web/src/data/generated` 下的数据。

也可以在 `web/` 目录手动执行：

```powershell
npm run extract
```

## 环境变量

运行 Python agent 示例通常需要：

```text
ANTHROPIC_API_KEY=...
MODEL_ID=...
```

参考 `.env.example`。
