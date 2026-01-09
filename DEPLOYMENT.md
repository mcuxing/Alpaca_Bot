# 云服务器部署指南 (Cloud Deployment Guide)

本指南将帮助你将 Alpaca 量化交易机器人部署到云服务器上，实现 7x24 小时无人值守运行。

## 1. 高性价比云服务商推荐

对于这种轻量级的 Python 脚本，你不需要昂贵的服务器。以下是几个高性价比的选择：

### A. AWS Free Tier (亚马逊云) - **首选推荐**
- **优势**: 新用户首年免费 (EC2 t2.micro 或 t3.micro 实例)。
- **成本**: 免费 (12个月)，之后约 $8-10/月。
- **适合**: 想要学习主流云平台操作的用户。

### B. DigitalOcean / Vultr
- **优势**: 设置极其简单，价格透明，无需复杂的网络配置。
- **成本**: 最低配 (Basic Droplet) 约 **$4 - $6 / 月**。
- **适合**: 希望快速上手、不想折腾配置的用户。

### C. Google Cloud Platform (GCP)
- **优势**: e2-micro 实例在特定区域 (us-west1, us-central1 等) 提供"永久免费"额度。
- **成本**: 免费 (需绑定信用卡验证)。
- **适合**: 追求长期零成本的用户。

---

## 2. 部署前的准备工作

在购买服务器之前，请准备好以下内容：

1.  **代码**: 确保你的代码已上传到 GitHub (私有仓库) 或压缩成 zip 包。
2.  **API Key**: 你的 `paper_account_api_key.txt` 文件内容。
3.  **SSH 终端**: macOS 自带的 Terminal 即可。

---

## 3. 部署步骤 (以 Ubuntu Linux 为例)

无论你选择哪家服务商，购买一台安装了 **Ubuntu 20.04 或 22.04 LTS** 的服务器，操作步骤基本一致。

### 第一步：连接服务器
打开本地终端，使用服务商提供的 IP 地址登录：
```bash
ssh root@<你的服务器IP地址>
# 输入密码（或使用 SSH Key）
```

### 第二步：安装环境
登录成功后，更新系统并安装 Python 和 Git：
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip git -y
```

### 第三步：上传代码
**方法 A (推荐): 使用 Git**
```bash
git clone https://github.com/<你的用户名>/Alpaca-Bot.git
cd Alpaca-Bot
```
*注意：如果是私有仓库，需要配置 SSH Key 或使用 Token。*

**方法 B: 直接上传 (无需 Git)**
在**本地电脑**的终端运行：
```bash
scp -r /Users/huzhongxing/Trae_Project/Alpaca root@<服务器IP>:~/
```
然后在服务器上：
```bash
cd Alpaca
```

### 第四步：安装依赖与配置 Key
1. 安装 Python 库：
   ```bash
   pip3 install -r requirements.txt
   ```
2. 创建 API Key 文件 (如果未上传)：
   ```bash
   nano paper_account_api_key.txt
   # 粘贴你的 Key 内容
   # 按 Ctrl+O 保存，Enter 确认，Ctrl+X 退出
   ```
3. 设置时区为美东时间 (方便 scheduler 识别)：
   ```bash
   sudo timedatectl set-timezone America/New_York
   ```

### 第五步：设置后台自动运行 (Systemd)
为了防止 SSH 断开后程序停止，我们需要将其注册为系统服务。

1. 创建服务文件：
   ```bash
   sudo nano /etc/systemd/system/alpaca-bot.service
   ```

2. 粘贴以下内容 (注意修改路径)：
   ```ini
   [Unit]
   Description=Alpaca Trading Bot Scheduler
   After=network.target

   [Service]
   Type=simple
   # 将 /root/Alpaca 替换为你的实际代码路径
   WorkingDirectory=/root/Alpaca
   # 确保 python3 路径正确 (可用 which python3 查看)
   ExecStart=/usr/bin/python3 scheduler.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. 启动服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start alpaca-bot
   sudo systemctl enable alpaca-bot
   ```

### 第六步：验证与监控

- **查看运行状态**:
  ```bash
  sudo systemctl status alpaca-bot
  ```
  如果显示 `active (running)` 绿色字样，说明部署成功！

- **查看日志**:
  ```bash
  journalctl -u alpaca-bot -f
  ```
  这会实时显示 `scheduler.py` 的打印输出。

- **查看交易记录**:
  过几天后，你可以查看生成的 CSV 文件：
  ```bash
  cat performance_log.csv
  ```

---

## 4. 常见问题

**Q: 服务器在海外，连接 Alpaca 速度快吗？**
A: 非常快。大多数云服务器（AWS, DigitalOcean）的数据中心都在美国，连接 Alpaca API 的延迟极低，比国内本地运行更有优势。

**Q: 如何更新策略？**
A: 
1. 在本地修改 `strategy.py`。
2. 上传覆盖服务器上的文件 (使用 git pull 或 scp)。
3. 重启服务使更改生效：`sudo systemctl restart alpaca-bot`。
