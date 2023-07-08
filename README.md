# Fastapi+tortoise-orm框架实践

- 使用pipenv包管理工具（强烈推荐）
- ORM使用tortoise-orm，并使用aerich迁移工具
- casbin访问控制（参考@xingxingzaixian的FASTAPI-TORTOISE-CASBIN项目代码）
    - 记录一下casbin踩坑：使用的豆瓣源下载的casbin竟然和清华源下载的不一样，豆瓣源casbin会报错；并且casbin包需要放在casbin-tortoise-adapter这个包的前面。
- 使用mysql数据库