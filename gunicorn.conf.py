#import multiprocessing

#预加载资源
#preload_app = True

# 并行工作进程数

workers = 2

# 指定每个工作者的线程数
threads = 5


worker_class = 'uvicorn.workers.UvicornWorker'

# 绑定端口
bind = '0.0.0.0:4000'

# 设置守护进程,false将进程交给supervisor管理
daemon = 'false'




# 设置最大并发量
worker_connections = 2000

# 设置进程文件目录
pidfile = '/var/run/gunicorn.pid'

# 日志标准输出
accesslog = "./testframe_backend/src/log/gunicorn_access.log"
errorlog = "./testframe_backend/src/log/gunicorn_error.log"

# 设置日志记录水平 
loglevel = 'info'


