# TestFrameworkBackend

## 概述
使用fastapi+tortoise-orm+mysql构建后台管理api，接口测试平台后端。
前端github地址（开发中）：https://github.com/RicarTang/testframework_vue3
## 技术架构
- 使用pythonweb异步框架fastapi
- 包管理工具使用pdm
- 使用异步ORMtortoise-orm，迁移工具使用aerich
- 基于rbac的权限控制
- 使用gunicorn+uvicorn守护程序运行(可选)
- pydanticV2
- 使用分布式队列celery运行pytest测试
- fastapi挂载使用allure-pytest对测试结果进行报告展示
    - config.py可配置ON_STATICFILES=False,可选nginx等web服务器代理转发(可选)
## TODO
- [] 性能测试；
- [] 使用httpx代替pytest进行接口套件测试；
- [] 改善用例与套件数据库表结构；
## 使用
默认超级管理员账号：superadmin,123456;
> Tips💡：需要在项目根目录新建一个.env文件,添加字段如下:<br>
>   DB_URL: str   # 数据库地址，example： "mysql://root:123456@127.0.0.1:3306/tortoise"（Dockerfile构建镜像时不能填本地回环地址,要指定ip）<br>
>   REDIS_URL: str  # redis地址，example："redis://[[name]:[pwd]]127.0.0.1:6379/0"<br>
>   SECRET_KEY: str  # jwt私钥，使用openssl rand -hex 32快捷生成<br>
>   CELERY_BROKER: str  # celery消息代理, 用来发送任务.example: "redis://[[name]:[pwd]]127.0.0.1:6379/0"<br>
>   CELERY_BACKEND: str  # celery消息后端,用来保存celery任务结果.example: "db+mysql+pymysql://root:123456@127.0.0.1:3306/tortoise"
### dev
1. 安装pdm包管理工具
```Bash
pip install pdm
```
2. 初始化项目
```Bash
pdm init
```
3. 同步pdm.lock依赖
```Bash
pdm sync
```
> Tips💡：迁移数据库前需要先在mysql中创建好数据库,orm不会自动创建。
4. 初始化aerich
```Bash
pdm run aerich_init # 需要在根目录
```
5. 初始化数据库表
```Bash
pdm run init_db
```
6. 运行
```Bash
pdm run dev
```
> Tips💡：如果有修改modules表结构，需要迁移同步数据库表结构。

```Bash
pdm run migrate_db # 生成迁移文件
```
```Bash
pdm run upgrade_db # 迁移，修改数据库表结构
```
7. api文档
```Text
http://127.0.0.1:4000/docs
```
### pro
#### Docker部署
1. 项目目录添加.env文件
2. 打包镜像
```Bash
docker build -t fastapi-image .
```
3. 启动容器
```Bash
docker run -d --name fastapi-pro -p 80:80 fastapi-image
```
4. api文档
```Text
http://127.0.0.1/docs
```