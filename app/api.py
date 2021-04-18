import sys

sys.path.append('./')

import datetime
import os
from typing import List, Dict

from fastapi import Depends, Query
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.websockets import WebSocket

from app.config import HTML_DIR, IS_LOCAL
from app.controller import all_permanent, get_special, is_valid_menu_id, set_sold_out, get_likes_by_sub, like_this, \
    dislike_this, get_congestion, set_congestion
from app.model import get_db
from app.scheme import SoldOutPostRequest, MenuModel, PermanentModel, MyLikesModel, LikePostRequest, \
    CongestionPostRequest, CongestionModel
from app.utils import decode_google_jwt

app = FastAPI(
    title='Online Database Query Executor',
    description='This provides online environment to execute sql query and view database.',
    version='0.1 alpha'
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if not request.url.is_secure and not IS_LOCAL:
        if request.url.scheme == 'http':
            return RedirectResponse(url=str(request.url).replace('http', 'https', 1))
        elif request.url.scheme == 'ws':
            return RedirectResponse(url=str(request.url).replace('ws', 'wss', 1))
    return await call_next(request)


@app.get('/', response_class=HTMLResponse)
async def index(req: Request):
    with open(os.path.join(HTML_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.get('/api/v1/menu', response_model=MenuModel)
async def index(date: List[str] = Query(None), db: Session = Depends(get_db)):
    if not date:
        raise HTTPException(400, 'date(s) must be given')
    dates = []
    for d in date:
        try:
            month, day = d.split(':')
            month, day = int(month), int(day)
            dates.append(datetime.date.today().replace(month=month, day=day))
        except ValueError:
            raise HTTPException(400, 'bad date')

    item = get_special(dates, db)

    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data)


@app.get('/api/v1/menu/permanent', response_model=PermanentModel)
async def index(db: Session = Depends(get_db)):
    item = all_permanent(db)

    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data)


@app.post('/api/v1/sold-out')
async def sold_out(req: SoldOutPostRequest, db: Session = Depends(get_db), *, background_tasks: BackgroundTasks):
    if not is_valid_menu_id(req.menu_id, db):
        raise HTTPException(status_code=404, detail=f'menu not found: {req.menu_id}')
    data = decode_google_jwt(req.token)
    success = set_sold_out(req.menu_id, req.is_sold_out, data.sub, db)
    if success:
        background_tasks.add_task(send_sold_out, req.menu_id, req.is_sold_out)
    else:
        raise HTTPException(429)


@app.get('/api/v1/like/me', response_model=MyLikesModel)
async def like_me(token: str = Query(None), db: Session = Depends(get_db)):
    data = decode_google_jwt(token)
    liked = get_likes_by_sub(data.sub, db)

    json_compatible_item_data = jsonable_encoder(MyLikesModel(likes=liked))
    return JSONResponse(content=json_compatible_item_data)


@app.post('/api/v1/like')
async def like_post(req: LikePostRequest, db: Session = Depends(get_db)):
    data = decode_google_jwt(req.token)
    success = like_this(req.menu_id, data.sub, db)

    if not success:
        raise HTTPException(409)


@app.get('/api/v1/congestion', response_model=CongestionModel)
async def get_congestion_api(req: Request, db: Session = Depends(get_db)):
    congestion = get_congestion(db)

    return CongestionModel(congestion=congestion)


@app.post('/api/v1/congestion')
async def set_congestion_api(req: CongestionPostRequest, db: Session = Depends(get_db), *,
                             background_tasks: BackgroundTasks):
    data = decode_google_jwt(req.token)
    if req.congestion not in (0, 1, 2):
        raise HTTPException(400, f'congestion `{req.congestion}` is invalid')

    success = set_congestion(req.congestion, data.sub, db)
    if success:
        background_tasks.add_task(send_congestion, req.congestion)
    else:
        raise HTTPException(429)


@app.delete('/api/v1/like')
async def like_me(token: str = Query(None), menu_id: str = Query(None), db: Session = Depends(get_db)):
    data = decode_google_jwt(token)
    success = dislike_this(menu_id, data.sub, db)
    if not success:
        raise HTTPException(409)


clients: Dict[str, WebSocket] = {}


async def send_sold_out(menu_id: str, is_sold_out: bool):
    for client in clients.values():
        await client.send_json({'id': menu_id, 'is_sold_out': is_sold_out, 'method': 'sold_out'})


async def send_congestion(congestion: int):
    for client in clients.values():
        await client.send_json({'congestion': congestion, 'method': 'congestion'})


@app.websocket("/api/v1/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    key = ws.headers.get('sec-websocket-key')
    clients[key] = ws
    try:
        while True:
            await ws.receive_text()
    except:
        await ws.close()
        del clients[key]
