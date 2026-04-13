from pydantic import BaseModel


class StatusMessage(BaseModel):
    content: str

