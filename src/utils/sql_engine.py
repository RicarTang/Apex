"""同步sql引擎"""

# import re
from sqlalchemy import create_engine
from src.config import config


engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATEBASE}",
    pool_size=10,  # 常驻连接数（默认5）
    max_overflow=20,  # 允许临时创建的额外连接数（默认10）
    pool_timeout=30,  # 获取连接超时时间（秒）
    pool_recycle=3600,  # 连接最大生命周期（秒），避免数据库主动断开
    pool_pre_ping=True, # 使用前检查连接有效性（推荐生产环境启用）
    # re.sub(r"^db\+", "", ),
    # echo=True,
)
