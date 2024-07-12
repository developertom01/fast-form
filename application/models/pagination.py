from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")

class PaginationResource(BaseModel, Generic[T]):
    page:int
    size:int
    limit:int
    total:int
    data: list[T]
