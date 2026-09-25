from fastapi import APIRouter
from pydantic import BaseModel

from app.repositories import settings_repo

router = APIRouter(tags=["settings"])


class SettingUpdate(BaseModel):
    value: str


@router.get("/settings")
def get_settings():
    return settings_repo.get_all()


@router.put("/settings/{key}")
def put_setting(key: str, body: SettingUpdate):
    settings_repo.set_value(key, body.value)
    return {key: body.value}
