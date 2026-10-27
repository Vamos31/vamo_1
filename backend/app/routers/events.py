from fastapi import APIRouter

router = APIRouter(prefix="/teams/{team_id}/events", tags=["events"])
