from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db import engine
from app.routers import attendances, auth, events, invitations, members, teams

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # httpOnly Cookie を送受信するために必要
    allow_methods=["*"],
    allow_headers=["*"],
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
