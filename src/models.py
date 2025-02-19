from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

# メタデータ-タグ間の中間タグ
class MetadataTagLink(Base):
    __tablename__ = "metadata_tag"
    metadata_id = Column(Integer, ForeignKey("game_metadata.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("game_tag.id"), primary_key=True)

# メタデータのテーブル
class GameMetadata(Base):
    __tablename__ = "game_metadata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    author = Column(String)
    version = Column(String)
    description = Column(String)
    lastupdate = Column(String)
    exeName = Column(String)
    imgName = Column(String)

    # relation
    tags = relationship("GameTag", secondary="metadata_tag", back_populates="game_metadata")

# タグのテーブル
class GameTag(Base):
    __tablename__ = "game_tag"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)

    # relation
    game_metadata = relationship("GameMetadata", secondary="metadata_tag", back_populates="tags")