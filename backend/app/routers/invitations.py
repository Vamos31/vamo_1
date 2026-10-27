from fastapi import APIRouter

# /teams/{team_id}/invitations と /invitations/{token} の2系統があるため、prefix は付けずパスを個別に書く
router = APIRouter(tags=["invitations"])
