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
                ), paginated_data AS (
                    SELECT 
                        lf.id AS id,
                        lf.title AS title,
                        lf.description AS description,
                        lf.published_at AS published_at,
                        lf.created_at AS created_at,
                        fq.id AS question_id,
                        fq.question AS question_question,
                        fq.type AS question_type,
                        fq.is_required AS question_is_required,
                        fq.form_id AS question_form_id,
                        fqc.id AS question_choice_id,
                        fqc.choice AS question_choice_choice,
                        fqc.question_id AS choice_question_id,
                        lf.user_id AS user_id
                    FROM 
                        limited_forms lf
                    LEFT JOIN 
                        form_questions AS fq ON lf.id = fq.form_id
                    LEFT JOIN 
                        form_question_choices AS fqc ON fq.id = fqc.question_id
                )
                SELECT 
                    tc.total AS count, 
                    pd.* 
                FROM 
                    paginated_data pd
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
            forms_itr = await cur.fetchmany()

        data, count = Form.parse_rows(forms_itr)

        return PaginationResource.get_paginated_object(
            count=count,
            data=data,
            size=self.pagination_params.limit,
            page=self.pagination_params.page,
        )
