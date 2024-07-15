from pydantic import BaseModel
from typing import TypeVar, Generic
import math

T = TypeVar("T")


class PaginationResource(BaseModel, Generic[T]):
    page: int
    size: int
    last: int
    next: int
    data: list[T]

    @staticmethod
    def get_paginated_object(count: int, size: int, page: str, data: list[T]):
        last = 1
        if size != 0:
            last = math.ceil(count / size)
        
        next_page = page +1
        if page == last:
            next_page = page

        return PaginationResource[T](
            page=page, size=size, last=last, next=next_page, data=data
        )


class PaginationParameters(BaseModel):
    offset: int
    limit: int
    page: int
