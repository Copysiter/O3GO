from crud.base import CRUDBase  # noqa
from models.reg import Reg  # noqa
from schemas.reg import RegCreate, RegUpdate  # noqa


class CRUDReg(CRUDBase[Reg, RegCreate, RegUpdate]):
    pass


reg = CRUDReg(Reg)
