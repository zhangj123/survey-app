# 问卷

参考问卷星的填写与编辑体验：注册 / 登录后可以自己创建问卷、添加题目并发布，其他人即可填写。

## 启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_survey
python manage.py runserver
```

打开 http://127.0.0.1:8000/ 进入「趣调研」首页。可浏览应用与问卷模版，右侧支持微信 / QQ 扫码登录，或使用「登录 / 免费注册」。登录后可创建、编辑、发布问卷，并在「填写」中作答。

可用题型：单选、多选、下拉、填空、简答、评分。

## 发布到 Render / Railway（试用）

代码已按生产环境配置：`gunicorn` + WhiteNoise 静态文件。本机开发不受影响。

### 方式 A：Render（推荐，网页点几下）

1. 把本仓库推到 GitHub。
2. 打开 https://dashboard.render.com 登录（可用 GitHub 账号）。
3. **New + → Blueprint**，选这个仓库；或 **New Web Service** 后填：
   - Build Command：`pip install -r requirements.txt`
   - Start Command：`bash start.sh`
4. 环境变量：
   - `DEBUG` = `0`
   - `SECRET_KEY` = 一串随机长密码（Render 可点 Generate）
5. 创建后等待几分钟，会得到 `https://xxxxx.onrender.com`。

免费实例第一次打开可能要等 30–60 秒唤醒。没有绑定 PostgreSQL 时用 SQLite，**重新部署后数据会清空**，适合试用。要保留账号和问卷，在 Render 再加一个 PostgreSQL，并把 `DATABASE_URL` 接到 Web 服务。

### 方式 B：Railway

1. 打开 https://railway.app 登录。
2. **New Project → Deploy from GitHub repo**。
3. Variables 里设置 `DEBUG=0` 和 `SECRET_KEY`。
4. 需要留存数据时：再 **Add PostgreSQL**，Railway 会自动注入 `DATABASE_URL`。

本地无法代替你登录这两个平台的账号，推送到 GitHub 后即可在网页上点部署。需要的话我可以帮你提交代码并推送。
