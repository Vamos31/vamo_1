from fastapi import APIRouter

router = APIRouter(prefix="/teams/{team_id}/members", tags=["members"])
