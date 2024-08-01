from .management.user import router as user_api
from .management.admin import router as admin_api
from .autotest.testcase import router as testcase_api
from .autotest.testsuite import router as testsuite_api
from .autotest.testenv import router as testenv_api
from .autotest.config import router as config_api
from .default import router as default_api
from .management.menu import router as menu_api