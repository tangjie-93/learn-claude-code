# Day 26 学习记录

## 1. 今天学习的文件
- `s18_worktree_isolation/README.md` - s18 的教学目标、工作流和观察点。
- `s18_worktree_isolation/code_openai.py` - OpenAI Responses API 版本的完整实现。

## 2. 本章要解决的问题

s17 已经解决了“谁来干活”和“怎么通信”，但还没有解决“干活在哪个目录里干”。

在多人并行修改时，共享一个工作目录会带来两个问题：
- 文件互相覆盖
- 最后很难确认某个改动属于哪一个任务

s18 把 `task` 和 `git worktree` 绑定起来，让每个任务有自己的目录和分支，Alice 和 Bob 可以在隔离目录里并行工作。

## 3. 核心机制

### 3.1 任务和 worktree 的绑定

任务结构新增了 `worktree` 字段：

```python
worktree: str | None = None
```

绑定逻辑由 `create_worktree(name, task_id)` 和 `bind_task_to_worktree(task_id, worktree_name)` 完成：

- `create_worktree()` 先校验名称
- 再执行 `git worktree add`
- 如果传了 `task_id`，就把任务写上 `worktree`
- 绑定只改目录信息，不改任务状态，任务仍然是 `pending`

这点很关键：Lead 可以先建任务、先建 worktree，队友后面再自动认领。

### 3.2 队友认领后切换到 worktree

队友在 `claim_task()` 成功后，如果任务带了 `worktree`，就把自己的 `wt_ctx["path"]` 切到对应目录。

```python
if task.worktree:
    wt_ctx["path"] = str(WORKTREES_DIR / task.worktree)
```

之后队友的 `bash`、`read_file`、`write_file` 都会在这个目录下执行。

### 3.3 自动认领不是“随机拿一个”

`idle_poll()` 会先扫任务板，再认领第一个满足条件的 pending 任务：

```python
unclaimed = scan_unclaimed_tasks()
if unclaimed:
    task_data = unclaimed[0]
    result = claim_task(task_data["id"], agent_name)
```

`scan_unclaimed_tasks()` 会同时检查：
- `status == "pending"`
- `owner` 为空
- `can_start(task["id"]) == True`

这意味着依赖没完成的任务不会被抢走。

### 3.4 完成任务后通知 Lead 清理 worktree

队友完成任务时，会先执行 `complete_task(task_id)`，然后如果这个任务绑定了 worktree，就给 Lead 发一条通知，提示删除对应 worktree。

这条通知目前是“请求删除”，不是自动删除：

```python
if "Completed" in result and task.worktree:
    BUS.send(
        name,
        "lead",
        f"Task {task.id} is complete. Please remove worktree '{task.worktree}'.",
        "message",
        {"task_id": task.id, "worktree": task.worktree, "action": "remove_worktree"},
    )
```

也就是说，s18 的默认策略是：
- worktree 创建时绑定 task
- 队友干活时切到自己的 worktree
- 完成后通知 Lead 决定是否删除

### 3.5 删除 worktree 的安全检查

`remove_worktree()` 不会无脑删：
- 先检查 worktree 名称是否合法
- 再检查目录是否存在
- 如果没传 `discard_changes=true`，会先看是否有未提交修改或未推送提交
- 只有通过后才执行 `git worktree remove`

这能避免把还没审完的改动直接清掉。

## 4. 执行日志

`code_openai.py` 里已经加了 `trace()` 风格的执行日志：
- Lead 调大模型
- Lead 工具调用和结果
- 队友线程启动、WORK / IDLE 状态
- 收件箱消息
- 自动认领
- 任务完成后的 worktree 清理通知

启动时会打印日志文件路径，方便回看整条执行链。

## 5. 我这次的结论

s18 的 worktree 机制不是“让模型知道有个目录”，而是把目录、任务和执行上下文绑成了一条链：

`create_task -> create_worktree -> bind_task_to_worktree -> claim_task -> 切换 cwd -> 干活 -> complete_task -> 通知清理`

这样才能把“谁在做什么”进一步扩展成“谁在什么目录里做什么”。
