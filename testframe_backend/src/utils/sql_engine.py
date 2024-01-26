import re
from sqlalchemy import create_engine, text
from ...config import config


engine = create_engine(
    config.SQL_ENGINE
    # re.sub(r"^db\+", "", ),
    # echo=True,
)
