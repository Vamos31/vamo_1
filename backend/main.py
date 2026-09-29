from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("mysql+pymysql://root:rootpass@localhost:3306/vamo")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        return {"db": conn.execute(text("SELECT 1")).scalar()}
