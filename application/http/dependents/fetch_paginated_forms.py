from fastapi import Depends
from .pagination import get_pagination_parameters
from internal.database import get_db
from application.models import User, PaginationParameters, Form, PaginationResource
from aiosqlite import Connection
from application.exceptions import NotFoundError
from internal.cache import cache

class FetchPaginatedForm:
    def __init__(
        self,
        db_conn: Connection = Depends(get_db),
        pagination_params: PaginationParameters = Depends(get_pagination_parameters),
    ) -> None:
        self.conn = db_conn
        self.pagination_params = pagination_params

    async def fetch(self, user: User) -> PaginationResource[Form]:
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
                    ORDER BY created_at DESC
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

    async def fetch_questions(self, form_id: str)->Form:
        #Check if form data has been cached
        form_data:Form | None = cache.get(f"form.{form_id}", None)
        if form_data is not None:
            return form_data
        
        data = []
        async with self.conn.execute(
            """
                WITH form_cte AS (
                     SELECT 
                        id,
                        title,
                        description,
                        user_id, 
                        published_at, 
                        created_at
                    FROM forms
                    WHERE id=?
                    LIMIT 1
                )

                SELECT 
                    form.*,
                    fq.id AS question_id,
                    fq.question AS question_question,
                    fq.type AS question_type,
                    fq.is_required AS question_required,
                    fqc.choice AS  question_choice,
                    fqc.id AS  question_choice_id
                FROM form_cte AS form
                LEFT JOIN form_questions AS fq ON form.id=fq.form_id
                LEFT JOIN form_question_choices AS fqc ON fq.id=fqc.question_id
            """,
            (form_id,),
        ) as cur:
            data = await cur.fetchall()
        if len(data) == 0:
            raise NotFoundError(f"Form with id {form_id} does not exist")        
        
        form_data= Form.parse_joined_single(data)

        #Cache form data
        cache[f"form.{form_id}"] = form_data

        return form_data

