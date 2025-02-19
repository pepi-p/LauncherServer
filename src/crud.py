from sqlalchemy.orm import Session
import models, schemas, websocket, converters
from sqlalchemy.future import select

# メタデータを取得
def get_game_metadata(db: Session, id: int):
    db_game = db.query(models.GameMetadata).filter(models.GameMetadata.id == id).first()
    return converters.to_SendGameMetadata(db_game)

# 全てのゲームのメタデータを取得
def get_game_metadata_all(db: Session):
    db_games = db.query(models.GameMetadata).all()
    return [converters.to_SendGameMetadata(game) for game in db_games]

# 指定idのメタデータの存在確認
def game_metadata_id_exist(db: Session, id: int):
    return db.query(models.GameMetadata).filter(models.GameMetadata.id == id).count() > 0

# タグを取得
def get_tag(db : Session):
    db_tags = db.query(models.GameTag).all()
    return [converters.to_GameTag(db_tag) for db_tag in db_tags]

# タグを追加
async def add_tag(db : Session, tag: str):
    print(f"add_tag :{tag}")
    db_tag = models.GameTag(tag=tag)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    await update_tag(db)
    return db_tag.id

# タグを削除
async def delete_tag(db : Session, id: int):
    db_tag = db.query(models.GameTag).filter(models.GameTag.id == id).first()
    db.delete(db_tag)
    db.commit()
    await update_tag(db)
    return {"message": f"{id}を削除しました"}

# タグを更新
async def update_tag(db: Session):
    db_tag_all = db.query(models.GameTag).all()
    await websocket.tag_ws_manager.broadcast(db_tag_all)

# タグを探す（引数のタグ文字列と同じタグがデータベースにあればそれを返却）
def find_tag(db: Session, tag: str):
    return db.query(models.GameTag).filter(models.GameTag.tag == tag).first()

# メタデータを新規作成
async def create_game(db: Session, game_metadata: schemas.CreateGameMetadata):
    db_metadata = converters.CreateGameMetadata_to_GameMetadata(db, game_metadata)
    
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)

    return db_metadata

# メタデータを更新
async def update_game_metadata(db: Session, game_metadata: schemas.UpdateGameMetadata):
    db_new_metadata = converters.UpdateGameMetadata_to_GameMetadata(db, game_metadata)
    # db_current_metadata = db.execute(select(models.GameMetadata).filter(models.GameMetadata.id == game_metadata.id)).scalars().first()
    db_current_metadata = db.get(models.GameMetadata, game_metadata.id)
    db_current_metadata = db.merge(db_current_metadata)

    db_current_metadata.title = db_new_metadata.title
    db_current_metadata.author = db_new_metadata.author
    db_current_metadata.version = db_new_metadata.version
    db_current_metadata.description = db_new_metadata.description
    db_current_metadata.lastupdate = db_new_metadata.lastupdate
    if not db_new_metadata.exeName is None: db_current_metadata.exeName = db_new_metadata.exeName
    if not db_new_metadata.imgName is None: db_current_metadata.imgName = db_new_metadata.imgName

    db_current_metadata.tags.clear()
    db_current_metadata.tags.extend(db_new_metadata.tags)

    db.commit()
    db.refresh(db_current_metadata)

    return db_current_metadata

# メタデータを削除
def delete_game_metadata(db: Session, id: int):
    db.query(models.GameMetadata).filter(models.GameMetadata.id == id).delete()
    
    db.commit()

    return id