# 使用 Python 3.9.12 作为基础镜像
FROM python:3.9.12
# 设置工作目录
WORKDIR /app
# 将项目代码复制到容器中
COPY . /app/
# 定义环境变量,使pipenv安装的依赖保存在项目文件夹的.venv中
ENV PIPENV_VENV_IN_PROJECT=1
# 安装 pipenv
# 安装项目Pipfile.lock依赖
# 迁移数据库表结构
RUN pip install pipenv \
    && pipenv install --deploy --ignore-pipfile \
    && pipenv run aerich_init \
    && pipenv run init_db
# 启动应用程序
CMD ["pipenv", "run", "pro"]
