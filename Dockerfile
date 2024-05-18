# 使用 Python 3.9.12 作为基础镜像
FROM python:3.9.12
# 安装pdm
RUN pip install pdm
# 设置工作目录
WORKDIR /app
# 将项目代码复制到容器中
COPY . /app/
# 初始化pdm，同步依赖，迁移数据库表结构
RUN pdm init \
    && pdm sync \
    && pdm run aerich_init \
    && pdm run init_db
# 启动应用程序
CMD ["pdm", "run", "pro"]
