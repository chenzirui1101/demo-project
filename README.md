# 兴宁旅游景点 App v1.0.0

## ⚙️ 环境要求

| 工具 | 版本 |
|------|------|
| Python | 3.8 ~ 3.10 |
| Node.js | 16.x 或 18.x |
| MySQL | 5.7 或 8.0 |


## 🚀 快速启动（3 步跑起来）

### 第 1 步：创建数据库

打开 MySQL 命令行或 phpMyAdmin，创建一个空数据库：

```sql
CREATE DATABASE meizhou CHARACTER SET utf8mb4;

数据库账号密码已配置好默认值（xingning / 514500），不修改也能直接用。
如需修改，编辑 Django/.env 文件。
```

### 第 2 步：修改前端 API 地址
打开 Vue3/.env.development 文件，找到这一行：

```ini
VITE_API_BASE_URL=http://xxx.xxx.x.xxx:8000/api
把 xxx.xxx.x.xxx 换成你电脑的局域网 IP 地址。

💡 查看 IP 的方法：

Windows：CMD 输入 ipconfig，找 IPv4 地址

Mac：终端输入 ifconfig，找 en0 的 inet

⚠️ 小程序调试必须用 IP，不能用 localhost
```
### 第 3 步：初始化数据库 + 启动项目
打开两个终端窗口：

终端 1 - 初始化数据库并启动后端：
```
bash
cd Django
pip install -r requirements.txt
python manage.py migrate          # 创建表
python manage.py seed_data        # 导入兴宁景点数据
python manage.py runserver
看到 Starting development server at http://127.0.0.1:8000/ 即成功。
```

终端 2 - 启动前端：
```
bash
cd Vue3
npm install
npm run dev:h5
访问 http://localhost:5173 即可预览。
```

### 📄 免责声明
本源码仅供学习参考，请勿直接用于商业上线。图片等资源版权归原作者所有，使用请自行替换。