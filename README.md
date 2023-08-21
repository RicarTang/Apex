# TestFrameworkBackend

## 概述
使用fastapi+tortoise-orm+mysql+casbin写的后台管理api，接口测试平台后端，用Vue构建前端。
## 技术架构
- 使用pythonweb框架fastapi
- 使用pipenv包管理工具（强烈推荐）
- ORM使用tortoise-orm，并使用aerich迁移工具
- casbin访问控制（参考@xingxingzaixian的FASTAPI-TORTOISE-CASBIN项目代码）
    - 记录一下casbin踩坑：使用的豆瓣源下载的casbin竟然和清华源下载的不一样，豆瓣源casbin会报错；并且casbin包需要放在casbin-tortoise-adapter这个包的前面。
- 使用tortoise-orm异步管理mysql数据库
- 使用gunicorn+uvicorn守护程序运行
- 因为pydanticV2版本改动过大,Fastapi与pydantic锁定版本
## 使用
默认超级管理员账号：superadmin,123456;
> Tips💡：需要在项目根目录新建一个.env文件,添加字段如下:
>   DB_URL: str   # 数据库地址，example： "mysql://root:Mayday990812@127.0.0.1:3306/tortoise"
>   REDIS_URL: str  # redis地址，example："redis://[[name]:[pwd]]127.0.0.1:6379/0"
>   SECRET_KEY: str  # jwt私钥，使用openssl rand -hex 32快捷生成
1. 安装依赖
```Bash
pipenv install
```
2. 初始化aerich
```Bash
pipenv run aerich_init # 需要在根目录
```
3. 初始化数据库表
```Bash
pipenv run init_db
```
4. 运行
```Bash
pipenv run dev
```
> Tips💡：如果有修改modules表结构，需要迁移同步数据库表结构。

```Bash
pipenv run migrate_db # 生成迁移文件
```
```Bash
pipenv run upgrade_db # 迁移，修改数据库表结构
```
5. api文档
```Text
http://127.0.0.1:4000/docs
```
