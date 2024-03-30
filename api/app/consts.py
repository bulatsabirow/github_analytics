CREATE_REPOSITORIES_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS
    repositories(
    repo varchar(512) not null,
    owner varchar(256) not null,
    position_cur integer primary key,
    position_prev integer default null,
    stars integer not null,
    watchers integer not null,
    forks integer not null,
    open_issues integer not null,
    language varchar(128)
    )
"""

CREATE_REPOSITORY_ANALYTICS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS
    repo_analytics(
    position integer,
    date date not null,
    commits int not null,
    authors varchar(256)[],
    unique (position, date),
    foreign key(position) references repositories(position_cur) on delete cascade
    )
"""

DROP_REPOSITORIES_TABLE_QUERY = """
    DROP TABLE IF EXISTS repositories
"""

DROP_REPOSITORY_ANALYTICS_TABLE_QUERY = """
    DROP TABLE IF EXISTS repo_analytics
"""
