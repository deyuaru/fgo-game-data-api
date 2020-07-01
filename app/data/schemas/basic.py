from pydantic import BaseModel, HttpUrl

from ..enums import NiceSvtType, SvtClass


class BasicServant(BaseModel):
    id: int
    collectionNo: int
    name: str
    type: NiceSvtType
    className: SvtClass
    rarity: int
    face: HttpUrl


class BasicEquip(BaseModel):
    id: int
    collectionNo: int
    name: str
    rarity: int
    face: HttpUrl