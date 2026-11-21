from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db import engine
from app.errors import error_response, register_exception_handlers
from app.routers import attendances, auth, events, invitations, members, teams

app = FastAPI()
register_exception_handlers(app)

_WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@app.middleware("http")
async def check_origin(request: Request, call_next):
    """CSRF 対策: 書き込み系は Origin が FRONTEND_ORIGIN と一致するものだけ通す。

    Origin ヘッダがないリクエスト (curl やテストなど、ブラウザ以外) は通す。
    ブラウザは書き込み系の fetch に必ず Origin を付けるため、他サイトからの攻撃は防げる。
    """
    if request.method in _WRITE_METHODS:
        origin = request.headers.get("origin")
        if origin is not None and origin != settings.frontend_origin:
            return error_response(
                403, "CSRF_ORIGIN_MISMATCH", "許可されていない Origin からのリクエストです"
            )
    return await call_next(request)


# 後から追加したミドルウェアほど外側になる。CORS を最後に足し、403 の応答にも CORS ヘッダを付ける
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],  # "*" は Cookie と併用できない
    allow_credentials=True,  # httpOnly Cookie を送受信するために必要
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

for module in (auth, teams, members, invitations, events, attendances):
    app.include_router(module.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        return {"db": conn.execute(text("SELECT 1")).scalar()}
