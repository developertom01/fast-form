from app.models import PaginationParameters
from fastapi import Query


def get_pagination_parameters(
    page: int | None = Query(default=1), size: int | None = Query(default=12)
):
    """
    Calculate the offset and limit for pagination.

    Args:
    page (int): The current page number (1-based).
    size (int): The number of items per page.

    Returns:
    tuple: A tuple containing the offset and limit.
    """
    if page < 1 or size < 1:
        raise ValueError("Page and size must be positive integers.")

    offset = (page - 1) * size
    return PaginationParameters(limit=size, offset=offset, page=page)
