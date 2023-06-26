from casbin import Enforcer
from casbin_tortoise_adapter import TortoiseAdapter


adapter = TortoiseAdapter()
# casbin实例
e = Enforcer("../db/rbac_model.conf", adapter, True)
