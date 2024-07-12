from pydantic import BaseModel

class PaginationParameters(BaseModel):
    offset:int
    limit:int

def get_pagination_parameters(page:int, size:int):
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
    
    limit = size
    offset = (page - 1) * size

    return PaginationParameters(limit=limit,offset=offset)
