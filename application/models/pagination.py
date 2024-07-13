from pydantic import BaseModel
from typing import TypeVar, Generic
from config import config
T = TypeVar("T")

class PaginationResource(BaseModel, Generic[T]):
    page:int
    size:int
    last:str
    next: str
    data: list[T]

    @staticmethod
    def get_paginated_object(count:int, size:int, page:str, data: list[T]):
        app_url = config.get("app_url")
        last_page = count // size

        last = f"{app_url}/forms/?page={last_page}"
        next_page = f"{app_url}/forms/?page={page + 1}"

        return PaginationResource[T](page=page, size=size,last=last, next=next_page,data=data)


class PaginationParameters(BaseModel):
    offset:int
    limit:int
    page: int