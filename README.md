# Apex

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
- [x] 基于rbac的用户权限访问控制；
- [x] 单接口测试（用例执行）；
- [x] 使用pytest对测试套件测试（多接口测试临时方案）；
- [ ] 支持添加定时任务；
- [ ] 首页展示数据接口；
- [ ] 使用httpx代替pytest进行接口套件测试；
- [ ] 收集httpx执行的套件测试数据（自定义报告or使用allure报告？）；
- [ ] 使用atomic-bomb-engine实现接口性能测试；
- [ ] 改善用例与套件数据库表结构；
- [ ] 使用{{}}双大括号表示全局变量；
- [ ] 测试报告接口（列表与详情）；
## 使用
默认管理员账号：admin,123456;
> Tips💡：需要在项目根目录新建一个.env文件,添加字段如下:<br>
>   DB_HOST: str  # 数据库地址，<span style="color: red;">构建docker镜像时不能填本地回环地址,要指定ip</span><br>
>   DB_PORT: int  # 数据库端口<br>
>   DB_USER: str  # 数据库用户名<br>
>   DB_PASSWORD: str  # 数据库密码<br>
>   DB_DATEBASE: str  # 数据库名<br>
>   REDIS_URL: str  # redis地址，example："redis://[[name]:[pwd]]127.0.0.1:6379/0"<br>
>   SECRET_KEY: str  # jwt私钥，使用openssl rand -hex 32快捷生成<br>
>   CELERY_BROKER: str  # celery消息代理, 用来发送任务.example: "redis://[[name]:[pwd]]127.0.0.1:6379/0"<br>
>   CELERY_BACKEND: str  # celery消息后端,用来保存celery任务结果.example: "db+mysql+pymysql://root:123456@127.0.0.1:3306/tortoise"<br>
### 本地启动
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
### 服务器docker-compose部署
1. 项目目录添加.env文件,对比上面新增3个字段
```Text
REDIS_PASSWORD: str  # redis密码
MYSQL_ROOT_PASSWORD: str  # mysql root用户密码
MYSQL_DATABASE: str  # 初始创建的数据库名
TZ="Asia/Shanghai"  ## 可选
```
2. 执行docker-compose部署
```Bash
docker-compose up -d
```
3. api文档
```Text
http://127.0.0.1:4000/docs
```