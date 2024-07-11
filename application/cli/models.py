from pydantic import BaseModel

class UserConf(BaseModel):
    id: str
    email: str
    name: str | None
    token: str

    def __str__(self) -> str:
        return self.name or self.email