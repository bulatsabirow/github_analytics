"""Models definition

Revision ID: 8aceb829f61b
Revises: 
Create Date: 2024-03-25 21:46:42.214491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "8aceb829f61b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        text(
            """
    CREATE TABLE IF NOT EXISTS
    repositories(
    id bigserial primary key,
    repo varchar(512) not null,
    owner varchar(256) not null,
    position_cur integer unique not null,
    position_prev integer default null,
    stars integer not null,
    watchers integer not null,
    forks integer not null,
    open_issues integer not null,
    language varchar(128)
    );
    """
        )
    )
    connection.execute(
        text(
            """
    CREATE TABLE IF NOT EXISTS
    repo_analytics(
    id bigserial primary key,
    repo_id integer,
    date date not null,
    commits int not null,
    authors varchar(256)[],
    foreign key(repo_id) references repositories(id) on delete cascade
    );
    """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        text(
            """
    DROP TABLE IF EXISTS repositories CASCADE;
    """
        )
    )
    connection.execute(
        text(
            """
    DROP TABLE IF EXISTS repo_analytics CASCADE;
    """
        )
    )
