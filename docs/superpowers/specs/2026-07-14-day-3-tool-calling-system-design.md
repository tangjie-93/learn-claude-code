# `Day 3` 工具调用系统表设计

## 目标

在既有 `Day 2` 学习记录 `docs/learning-note/2027-07-10.md` 后补充 `Day 3` 学习产出，使其满足 `docs/learning-plan/04-week-1-agent-basics.md` 定义的工具调用系统表要求。

## 范围

新增一个 `Day 3：工具调用系统` 小节，基于 `s02_tool_use/code.py`、`s02_tool_use/code_openai.py` 和 `agents/s02_tool_use.py` 记录：

1. `bash`、`read_file`、`write_file`、`edit_file`、`glob` 五个工具的输入、输出、风险和防护。
2. 从用户消息到模型最终回答的工具调用闭环。
3. `Anthropic` 的 `tool_use` / `tool_result` 与 `OpenAI Responses API` 的 `function_call` / `function_call_output` / `call_id` 对照。
4. 安全边界：`safe_path` 保护文件工具和 `glob`；`bash` 只有有限危险命令拦截，完整权限决策属于 `s03_permission`。

## 不在范围内

不修改 `s02` 的运行代码，不新增自动化测试，不把 `Day 4` 的 `list_files` 设计提前写入本节。

## 内容结构

小节按以下顺序组织：

1. 学习材料和目标。
2. 工具系统表。
3. 调用闭环图。
4. 提供商协议对照表。
5. 本节结论和下一步。

表格以代码实际行为为准。例如，`write_file` 的输出是成功字节数或错误文本，`edit_file` 仅替换首次匹配，`glob` 返回工作区内的相对路径或 `(no matches)`。

## 验证

完成后检查：

1. 五个工具均有一行，五列信息完整且与实现一致。
2. `safe_path` 的覆盖范围和 `bash` 的限制明确且不被夸大。
3. 两种工具调用协议的结果关联字段明确。
4. 所有英语技术名词、路径、符号、数量和日期遵循行内代码格式。
