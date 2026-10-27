from fastapi import APIRouter

# /auth/signup, /auth/login, /auth/logout と /me をまとめて扱うため、prefix は付けずパスを個別に書く
router = APIRouter(tags=["auth"])
