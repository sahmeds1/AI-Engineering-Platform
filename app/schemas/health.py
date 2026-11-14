
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    environment: str

class VersionResponse(BaseModel):
    application: str
    version: str