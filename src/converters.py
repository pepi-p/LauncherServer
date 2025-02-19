from sqlalchemy.orm import Session
import models, schemas, crud, models

# to schemas
def to_SendGameMetadata(gameMetadata: models.GameMetadata):
    return schemas.SendGameMetadata(
        id = gameMetadata.id,
        title = gameMetadata.title,
        author= gameMetadata.author,
        version= gameMetadata.version,
        description= gameMetadata.description,
        lastupdate= gameMetadata.lastupdate,
        exeName= gameMetadata.exeName,
        imgName = gameMetadata.imgName,
        tags = [tag.tag for tag in gameMetadata.tags]
    )

def to_GameTag(gameTag: schemas.GameTagBase):
    return models.GameTag(
        id = gameTag.id,
        tag = gameTag.tag
    )

# to models
def CreateGameMetadata_to_GameMetadata(db: Session, metadata: schemas.CreateGameMetadata):
    game_metadata = models.GameMetadata(
        title = metadata.title,
        author = metadata.author,
        version = metadata.version,
        description = metadata.description,
        lastupdate = metadata.lastupdate,
        exeName = metadata.exeName,
        imgName = metadata.imgName
    )

    # 新しいタグのみ追加
    new_tags = [crud.find_tag(db, t) for t in metadata.tags if crud.find_tag(db, t) is None]
    game_metadata.tags.extend([t for t in new_tags])

    return game_metadata

def UpdateGameMetadata_to_GameMetadata(db: Session, metadata: schemas.UpdateGameMetadata):
    return models.GameMetadata(
        id = metadata.id,
        title = metadata.title,
        author = metadata.author,
        version = metadata.version,
        description = metadata.description,
        lastupdate = metadata.lastupdate,
        exeName = metadata.exeName,
        imgName = metadata.imgName,
        tags = [crud.find_tag(db, t) for t in metadata.tags]
    )