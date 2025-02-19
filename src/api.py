from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Request, APIRouter, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.orm import Session, sessionmaker
import crud, models, schemas, database, websocket
import os
import json
import shutil

# データベースセッションを取得する
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ファイルパスの設定
base_path = os.path.dirname(os.path.dirname(__file__))
file_dir_path = os.path.join(base_path, "resources", "files")
template_path = os.path.join(base_path,"resources", "templates")
metadata_template = Jinja2Templates(directory=os.path.join(template_path, "metadata"))
gamelist_template = Jinja2Templates(directory=os.path.join(template_path, "gamelist"))

router = APIRouter()

# ヘルスチェック
@router.get("/api/health")
async def health():
    return {"status": "ok"}

# ゲーム情報を検索
@router.get("/api/search")
async def search(id: int = None, db: Session = Depends(get_db)):
    if id:
        db_game = crud.get_game_metadata(db, id)

        if db_game is None:
            raise HTTPException(status_code=404, detail="Game not found")
        return db_game
    else:
        db_games = crud.get_game_metadata_all(db)
        if db_games is None:
            raise HTTPException(status_code=500,detail="Internal Server Error")
        return db_games

# ビルドファイルをダウンロード
@router.get("/api/download/game/{id}")
async def download_game(id: int, db: Session = Depends(get_db)):
    if not crud.game_metadata_id_exist(db, id):
        print("Game not found")
        raise HTTPException(status_code=404, detail="Game not found")
    else:
        db_metadata = crud.get_game_metadata(db, id)
        file_path = os.path.join(file_dir_path, f'{db_metadata.id}', f'{db_metadata.title}.zip')
        print(f"download: {file_path}")
        response = FileResponse(path=file_path)
        return response

# ゲームのサムネイル画像をダウンロード
@router.get("/api/download/image/{id}")
async def download_image(id: int, db: Session = Depends(get_db)):
    if not crud.game_metadata_id_exist(db, id):
        print("Game not found")
        raise HTTPException(status_code=404, detail="Game not found")
    else:
        db_metadata = crud.get_game_metadata(db, id)
        image_path = os.path.join(file_dir_path, f'{db_metadata.id}', db_metadata.imgName)
        print(f"download: {image_path}")
        response = FileResponse(path=image_path)
        return response

# タグを取得
@router.get("/api/tag")
async def get_tag(db: Session = Depends(get_db)):
    return crud.get_tag(db)

# タグを追加
@router.post("/api/tag")
async def add_tag(tag: str, db: Session = Depends(get_db)):
    result = await crud.add_tag(db, tag)
    return result

# タグを削除
@router.post("/api/tag/remove")
async def delete_tag(id: int, db: Session = Depends(get_db)):
    result = await crud.delete_tag(db, id)
    return result

# ゲームをアップロード
@router.post("/api/upload")
async def upload_game(metadata: str = Form(...), build_file: UploadFile = File(...), image_file: UploadFile = File(...), db: Session = Depends(get_db)):
    metadata_dict = json.loads(metadata)
    metadata_obj = schemas.CreateGameMetadata(**metadata_dict)

    db_metadata = await crud.create_game(db, metadata_obj)

    dir_name = os.path.join(file_dir_path, f'{db_metadata.id}')
    if (not os.path.isdir(dir_name)): os.makedirs(dir_name)

    # ビルドファイルを保存
    build_file_content = await build_file.read()

    with open(os.path.join(dir_name, f'{db_metadata.title}.zip'), "wb") as f:
        f.write(build_file_content)

    # 画像ファイルを保存
    image_file_content = await image_file.read()
    
    with open(os.path.join(dir_name, db_metadata.imgName), "wb") as f:
        f.write(image_file_content)

    await websocket.launcher_ws_manager.broadcast("Create", db_metadata.id)

    return db_metadata

# ゲームを更新
@router.post("/api/update")
async def update_game(metadata: str = Form(...), build_file: UploadFile = File(None), image_file: UploadFile = File(None), db: Session = Depends(get_db)):
    metadata_dict = json.loads(metadata)
    metadata_obj = schemas.UpdateGameMetadata(
        id = metadata_dict["id"],
        title = metadata_dict["title"],
        author = metadata_dict["author"],
        version = metadata_dict["version"],
        description = metadata_dict["description"],
        lastupdate = metadata_dict["lastupdate"],
        exeName = metadata_dict["exeName"],
        imgName = metadata_dict["imgName"],
        tags = [t for t in metadata_dict["tags"]]
    )

    print("update")

    db_metadata = await crud.update_game_metadata(db, metadata_obj)

    dir_name = os.path.join(file_dir_path, f'{db_metadata.id}')
    if (not os.path.isdir(dir_name)): os.makedirs(dir_name)

    # ビルドファイルを保存
    if build_file:
        build_file_content = await build_file.read()

        with open(os.path.join(dir_name, f'{db_metadata.title}.zip'), "wb") as f:
            f.write(build_file_content)
        
        await websocket.launcher_ws_manager.broadcast("File", db_metadata.id)

    # 画像ファイルを保存
    if image_file:
        image_file_content = await image_file.read()
        
        with open(os.path.join(dir_name, db_metadata.imgName), "wb") as f:
            f.write(image_file_content)
        
        print("Image : " + db_metadata.imgName)
        await websocket.launcher_ws_manager.broadcast("Image", db_metadata.id)
    
    # 両方無効であれば呼び出し
    if not build_file and not image_file: await websocket.launcher_ws_manager.broadcast("Data", db_metadata.id)

    return db_metadata

# ゲームを削除
@router.post("/api/delete")
async def delete_game(id: int, db: Session = Depends(get_db)):
    delete_metadata = crud.delete_game_metadata(db, id)
    dir_name = os.path.join(file_dir_path, f'{id}')
    if (os.path.isdir(dir_name)): shutil.rmtree(dir_name)

    await websocket.launcher_ws_manager.broadcast("Delete", id)

    return delete_metadata

# Webページのルートエンドポイント
@router.get("/web/register/", response_class=HTMLResponse)
async def read_root(request: Request):
    return metadata_template.TemplateResponse("index.html", {"request": request, "message": "Register a game metadata"})

@router.get("/web/list/", response_class=HTMLResponse)
async def read_root(request: Request):
    return gamelist_template.TemplateResponse("index.html", {"request": request, "message": "List of games"})