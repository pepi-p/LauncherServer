from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from sqlalchemy.orm import Session, sessionmaker, joinedload
import database
import models
import schemas
import crud
import os
import zipfile
import json
import hashlib

# Path定義
base_path = os.path.dirname(os.path.dirname(__file__))
static_path = os.path.join(base_path, "resources", "static")

# DBの初期化
database.init_DB()

app = FastAPI()
app.mount(path="/static", app=StaticFiles(directory=static_path), name="static")

import api
import websocket

app.include_router(api.router)
app.include_router(websocket.router)