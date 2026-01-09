# Alpaca Local 量化交易平台 (基于 Trae)

这是一个基于 Trae IDE 和 Alpaca API 搭建的本地量化交易环境。它支持策略开发、历史回测以及模拟盘/实盘自动交易。

## 1. 快速上手 (Quick Start)

### 1.1 环境准备
1. **Python 环境**: 确保 macOS 已安装 Python 3.9+。
2. **依赖安装**:
   在 Trae 终端中运行以下命令安装所需库：
   ```bash
   pip3 install -r requirements.txt
   ```
3. **API 配置**:
   确保项目根目录下有 `paper_account_api_key.txt` 文件，格式如下：
   ```text
   Endpoint：https://paper-api.alpaca.markets/v2
   API Key ID：<YOUR_API_KEY>
   Secret Key：<YOUR_SECRET_KEY>
   ```

### 1.2 核心文件说明
- **[strategy.py](strategy.py)**: **策略逻辑核心**。在这里编写你的买卖信号逻辑。
- **[backtest.py](backtest.py)**: **回测工具**。拉取历史数据并跑策略，生成收益曲线图。
- **[main.py](main.py)**: **实盘/模拟盘执行脚本**。连接 Alpaca 账户，根据策略信号自动下单。
- **[utils.py](utils.py)**: 辅助工具，用于读取配置文件。

---

## 2. 如何使用 Trae 进行量化开发与迭代

Trae 的 AI 编程能力非常适合量化策略的快速迭代。推荐的工作流如下：

### 第一步：编写/修改策略 (Strategy)
打开 `strategy.py`，这是你唯一需要频繁修改的文件。
目前的示例是一个简单的 **双均线策略 (SMA Crossover)**。

**如何迭代：**
你可以直接告诉 Trae（在右侧 Chat 窗口）：
> "请帮我修改 strategy.py，把策略改为 RSI 超买超卖策略，当 RSI > 70 卖出，RSI < 30 买入。"

Trae 会自动帮你重写 `generate_signals` 函数。

### 第二步：进行回测 (Backtest)
策略修改完成后，需要验证其历史表现。
1. 打开终端（Terminal）。
2. 运行回测脚本：
   ```bash
   python3 backtest.py
   ```
3. **查看结果**：
   - 终端会输出 **策略总收益率** 和 **买入持有收益率**。
   - 脚本会生成一张 `backtest_result.png` 图片，直接在左侧文件列表中点击打开即可查看资金曲线对比图。

### 第三步：模拟盘交易 (Paper Trading)
回测满意后，可以进行模拟盘实战。
1. 确保你的 Alpaca Paper Account 有资金（如余额为0，请去官网 Dashboard 点击 Reset/Add Funds）。
2. 运行交易机器人：
   ```bash
   python3 main.py
   ```
3. **执行逻辑**：
   - 脚本会自动获取最新数据。
   - 调用 `strategy.py` 计算当前信号。
   - 检查当前持仓，如果信号变化（例如从空仓变多仓），会自动下单买入。

---

## 3. 常见问题 (FAQ)

### Q: 如何发布策略？
**A**: 在本地环境中，"发布"意味着将 `main.py` 设置为定时运行。
- **初级方案**: 手动每天运行一次 `python3 main.py`。
- **进阶方案**: 使用 macOS 的 `crontab` 设置定时任务（例如每个交易日早上 9:35 运行）。
- **云端方案**: 将整个项目上传到云服务器（AWS/GCP），使用 Docker 或 Supervisor 守护进程运行。

### Q: 为什么回测结果很好，实盘却亏损？
**A**: 回测通常存在"过度拟合"风险，且未完全考虑滑点(Slippage)和市场冲击。建议在 Paper Trading 模拟盘多跑一段时间验证。

### Q: 报错 "insufficient buying power"？
**A**: 模拟盘账户没钱了。请登录 Alpaca 官网重置模拟盘资金。

### Q: 报错 SSL 相关警告？
**A**: macOS 下 Python 的 SSL 库版本问题，代码中已做屏蔽处理，不影响交易功能。

## 4. 实盘追踪与自动化 (Live Trading & Tracking)

### 4.1 自动执行
为了在模拟盘持续跑 1-2 个月，你需要让脚本每天自动运行。
我们提供了 `scheduler.py`，它会在每个交易日的 **09:35 AM (美东时间)** 自动运行一次交易机器人。

**使用方法**:
1. 打开终端。
2. 运行调度器（建议使用 `nohup` 或在单独的终端窗口运行）：
   ```bash
   python3 scheduler.py
   ```
3. 保持该终端开启，或者将其部署到云服务器上。

### 4.2 收益追踪
每次 `main.py` 运行时，都会自动将当前的账户净值、持仓等信息记录到 **`performance_log.csv`** 文件中。

要查看可视化的收益曲线：
```bash
python3 track_performance.py
```
这会生成一张 **`live_performance.png`** 图片，展示你的实盘资金增长情况。
