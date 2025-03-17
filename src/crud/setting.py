from typing import Any, Dict, Optional, Union  # noqa

from crud.base import CRUDBase  # noqa
from models.setting import SettingOption, Setting  # noqa
from schemas.setting import SettingCreate, SettingUpdate # noqa


class CRUDSetting(CRUDBase[Setting, SettingCreate, SettingUpdate]):
    pass


setting = CRUDSetting(Setting)
