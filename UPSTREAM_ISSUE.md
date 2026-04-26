## 问题描述

`video-analyzer` MCP server 在直接调用 `kimi_cli.cli` 时，会触发 `asyncio.run()` 嵌套调用错误：

```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

这是因为：
1. MCP server（FastMCP）本身运行在 asyncio event loop 中
2. `kimi_cli.cli.cli()` 内部调用了 `asyncio.run(_reload_loop(session_id))`
3. Python 不允许在一个 running event loop 中再调用 `asyncio.run()`

## 复现步骤

1. 安装 kimi-cli 和 video-analyzer MCP server
2. 启动 MCP server（任何 asyncio 环境）
3. 调用 `analyze_video_file` 工具
4. 触发 `RuntimeError`

## 当前 workaround

通过 subprocess 调用 kimi CLI：

```python
import subprocess

result = subprocess.run(
    ["kimi", "--quiet", "--prompt", prompt],
    capture_output=True,
    text=True,
    timeout=300
)
return result.stdout
```

这个 workaround 能工作，但：
- 损失了直接调用的性能（需要 fork 新进程）
- 增加了资源开销
- 无法利用 Python 内部的缓存和优化

## 建议修复方案

### 方案 A：提供同步入口（推荐）

在 `kimi_cli.cli` 模块中提供一个**不依赖 asyncio.run()** 的同步入口：

```python
# kimi_cli/cli/__init__.py

def run_sync(prompt: str, **kwargs) -> str:
    """
    Synchronous entry point that does NOT use asyncio.run().
    Safe to call from within an existing asyncio event loop.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Already in an event loop, use run_coroutine_threadsafe or create_task
        future = asyncio.run_coroutine_threadsafe(
            _run_kimi_async(prompt, **kwargs),
            loop
        )
        return future.result()
    else:
        return asyncio.run(_run_kimi_async(prompt, **kwargs))
```

### 方案 B：检测已有 event loop

修改 `kimi()` 函数，在调用 `asyncio.run()` 前检测是否已在 event loop 中：

```python
def kimi(...):
    try:
        loop = asyncio.get_running_loop()
        # We're already in an event loop
        return loop.run_until_complete(_reload_loop(session_id))
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        switch_target, exit_code = asyncio.run(_reload_loop(session_id))
        return switch_target, exit_code
```

### 方案 C：提供 async API

暴露一个 `async def` 版本的入口函数：

```python
async def kimi_async(prompt: str, **kwargs) -> str:
    """Async version of kimi() for use in existing event loops."""
    ...
```

这样 MCP server 可以直接 `await kimi_async(prompt)` 而不需要 subprocess。

## 环境信息

- Python: 3.13+
- kimi-cli: 1.38.0
- 安装方式: `uv tool install kimi-cli`

## 相关代码

错误堆栈：
```
File "kimi_cli/cli/__init__.py", line 835, in kimi
    switch_target, exit_code = asyncio.run(_reload_loop(session_id))
File "asyncio/runners.py", line 191, in run
    raise RuntimeError(
RuntimeError: asyncio.run() cannot be called from a running event loop
```
