import re
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from ...config import config


engine = create_engine(
    re.sub(r"^db\+", "", config.CELERY_BACKEND),
    # echo=True,
)
