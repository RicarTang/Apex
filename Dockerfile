# 使用 Python 3.9.12 作为基础镜像
FROM python:3.9.12
# 设置工作目录
WORKDIR /app
# 将项目代码复制到容器中
COPY . /app/
# 依赖安装到项目文件夹
CMD ["pdm","venv.in_project","true"]
# 安装 pipenv
# 安装项目Pipfile.lock依赖
# 迁移数据库表结构
RUN pdm install pipenv \
    && pdm install --deploy --ignore-pipfile \
    && pdm run aerich_init \
    && pdm run init_db
# 启动应用程序
CMD ["pdm", "run", "pro"]
