import datetime
from pydantic import BaseModel, ConfigDict


class ProjectSchema(BaseModel):
    project_id: int | None = None
    user_id: int | None = None
    title: str
    description: str
    project_image: str | None = None
    visibility: str | None = "Private"
    project_data: dict | None = None
    created_at: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class VisibilitySchema(BaseModel):
    visibility: str

    model_config = ConfigDict(from_attributes=True)