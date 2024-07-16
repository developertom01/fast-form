from fastapi import Depends
from .pagination import get_pagination_parameters
from internal.database import get_db
from app.models import User, PaginationParameters, Form, PaginationResource
from aiosqlite import Connection
from app.exceptions import NotFoundError
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
                        created_at,
                        published_key
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
    def _embed_user_where(self,form_id:str |None, published_key:str |None, user_id:str|None):
        if form_id is None and published_key is None:
            raise ValueError("Must provide either form key or published key")
        embedded_where = ""
        if form_id is not None:
            embedded_where = "id=?"
        elif published_key:
            embedded_where = "published_key=?"

        return f"{embedded_where} AND user_id=?" if user_id is not None else ""

    def _get_embedded_param(self, form_id:str, user_id:str | None):
        return (form_id, ) if user_id is None else (form_id, user_id, )
        
    async def fetch_questions(self, form_id: str|None, published_key:str | None, user_id:str | None = None) -> Form:
        # Check if form data has been cached
        form_data: Form | None = cache.get(f"form.{form_id}", None)
        if form_data is not None:
            return form_data

        data = []
        async with self.conn.execute(
            f"""
                WITH form_cte AS (
                     SELECT 
                        id,
                        title,
                        description,
                        user_id, 
                        published_at, 
                        created_at,
                        published_key
                    FROM forms
                    WHERE id=? {self._embed_user_where(user_id= user_id,form_id= form_id, published_key=published_key)}
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
            self._get_embedded_param(form_id or published_key,user_id),
        ) as cur:
            data = await cur.fetchall()
        if len(data) == 0:
            raise NotFoundError(f"Form with id {form_id} does not exist")

        form_data = Form.parse_joined_single(data)

        # Cache form data
        cache[f"form.{form_id}"] = form_data

        return form_data
