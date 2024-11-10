import re
from sqlalchemy import create_engine, text
from ...config import config


engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_DATEBASE}"
    # re.sub(r"^db\+", "", ),
    # echo=True,
)
