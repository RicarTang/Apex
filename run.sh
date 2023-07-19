#!/bin/bash
# gunicorn命令启动
#pipenv run python3 -m gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:4000 --log-level debug
# uvicorn命令启动
#pipev run python3 -m uvicorn main:app --host 0.0.0.0 --port 4000
# gunicorn配置文件启动,nohup后台运行
#nohup pipenv run python3 -m gunicorn -c gunicorn.conf.py main:app > nohup.out 2>&1 &
