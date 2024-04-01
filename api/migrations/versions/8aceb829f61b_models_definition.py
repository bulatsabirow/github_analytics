"""Models definition

Revision ID: 8aceb829f61b
Revises: 
Create Date: 2024-03-25 21:46:42.214491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

from app.consts import (
    CREATE_REPOSITORIES_TABLE_QUERY,
    CREATE_REPOSITORY_ANALYTICS_TABLE_QUERY,
    DROP_REPOSITORIES_TABLE_QUERY,
    DROP_REPOSITORY_ANALYTICS_TABLE_QUERY,
)

# revision identifiers, used by Alembic.
revision: str = "8aceb829f61b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(text(CREATE_REPOSITORIES_TABLE_QUERY + ";"))
    connection.execute(text(CREATE_REPOSITORY_ANALYTICS_TABLE_QUERY + ";"))


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(text(DROP_REPOSITORIES_TABLE_QUERY + " CASCADE;"))
    connection.execute(text(DROP_REPOSITORY_ANALYTICS_TABLE_QUERY + " CASCADE;"))
