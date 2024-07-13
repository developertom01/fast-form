from fastapi import Depends
from .pagination import get_pagination_parameters
from internal.database import get_db
from application.models import User, PaginationParameters, Form, PaginationResource
from aiosqlite import Connection


class FetchPaginatedForm:
    def __init__(
        self,
        db_conn: Connection = Depends(get_db),
        pagination_params: PaginationParameters = Depends(get_pagination_parameters),
    ) -> None:
        self.conn = db_conn
        self.pagination_params = pagination_params

    async def fetch(self, user: User) -> PaginationResource[Form]:
        print("Limit", self.pagination_params.limit, user.id)
        forms_itr = []
        async with self.conn.execute(
            """
                WITH total_count AS (
                    SELECT 
                        COUNT(DISTINCT id) AS total 
                    FROM 
                        forms
                    WHERE 
                        user_id = ?
                ), limited_forms AS (
                    SELECT 
                        id, 
                        title, 
                        description, 
                        user_id, 
                        published_at, 
                        created_at
                    FROM 
                        forms
                    WHERE 
                        user_id = ?
                    LIMIT ?
                    OFFSET ?
                )
                SELECT 
                    tc.total AS count, 
                    lf.* 
                FROM 
                    limited_forms lf
                CROSS JOIN 
                    total_count tc;
            """,
            (
                user.id,
                user.id,
                self.pagination_params.limit,
                self.pagination_params.offset,

            ),
        ) as cur:
            forms_itr = await cur.fetchall()
        data, count = Form.parse_rows(forms_itr)
        return PaginationResource.get_paginated_object(
            count=count,
            data=data,
            size=self.pagination_params.limit,
            page=self.pagination_params.page,
        )
