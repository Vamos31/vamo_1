from fastapi import APIRouter

router = APIRouter(
    prefix="/teams/{team_id}/events/{event_id}/attendances", tags=["attendances"]
)
