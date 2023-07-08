# Fastapi+tortoise-orm框架实践

## 概述
使用fastapi+tortoise-orm+mysql+casbin写的后台管理api，打算做成接口测试平台后端，用Vue构建前端。
## 技术架构
- 使用pythonweb框架fastapi
- 使用pipenv包管理工具（强烈推荐）
- ORM使用tortoise-orm，并使用aerich迁移工具
- casbin访问控制（参考@xingxingzaixian的FASTAPI-TORTOISE-CASBIN项目代码）
    - 记录一下casbin踩坑：使用的豆瓣源下载的casbin竟然和清华源下载的不一样，豆瓣源casbin会报错；并且casbin包需要放在casbin-tortoise-adapter这个包的前面。
- 使用mysql数据库
## 使用
1. 安装依赖
```Bash
pipenv install
```
2. 迁移数据表
```Bash
pipenv run aerich_init # 需要在根目录
```
3. 运行
```Bash
pipenv run dev
```