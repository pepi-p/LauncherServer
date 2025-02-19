from pydantic import BaseModel
from typing import Optional, List

class GameTagBase(BaseModel):
    id: int
    tag: str

class CreateGameTag(BaseModel):
    id: int
    tag: str

class DeleteGameTag(BaseModel):
    id: int

class GameMetadataBase(BaseModel):
    id: int
    title: str
    author: str
    version: str
    description: str
    lastupdate: str
    exeName: str
    imgName: str
    tags: list[GameTagBase]

class SendGameMetadata(BaseModel):
    id: int
    title: str
    author: str
    version: str
    description: str
    lastupdate: str
    exeName: str
    imgName: str
    tags: list[str]

class CreateGameMetadata(BaseModel):
    title: str
    author: str
    version: str
    description: str
    lastupdate: str
    exeName: str
    imgName: str
    tags: list[str]

class UpdateGameMetadata(BaseModel):
    id: int
    title: str
    author: str
    version: str
    description: str
    lastupdate: str
    exeName: Optional[str]
    imgName: Optional[str]
    tags: list[str]