from fastapi import APIRouter, HTTPException, status

from .schemas import PlayerSchema
from core.config import settings


router = APIRouter(
    prefix=settings.api.v1.players,  # /players
    tags=["Players"],
)
