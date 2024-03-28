from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.repo import (
    RepositoryDatabaseService,
    get_repository_database_service,
    RepositoryAnalyticsDatabaseService,
    get_repository_analytics_database_service,
)
from app.schema import Repository, RepositorySortingQueryParams, RepositoryAnalyticsSortingQueryParams
from core.repo import Between, Equals

router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.get("/top100", status_code=status.HTTP_200_OK, response_model=list[Repository])
async def repositories_list_view(
    db_service: Annotated[RepositoryDatabaseService, Depends(get_repository_database_service)],
    query_params: Annotated[RepositorySortingQueryParams, Depends()],
):
    return await db_service.select_all().order_by(**{query_params.sort: query_params.order}).execute()


@router.get("/{owner}/{repo}/activity")
async def repositories_activity_view(
    db_service: Annotated[RepositoryAnalyticsDatabaseService, Depends(get_repository_analytics_database_service)],
    query_params: Annotated[RepositoryAnalyticsSortingQueryParams, Depends()],
    owner: str,
    repo: str,
):
    return (
        await db_service.select_all()
        .join(joined_table="repositories", on=f"{db_service.table_name}.position = repositories.position_cur")
        .where(
            **{
                "repo": Equals(f'\'{"/".join([owner, repo])}\''),
                "date": Between(f"'{query_params.since}'", f"'{query_params.until}'"),
            }
        )
        .order_by(**{query_params.sort: query_params.order})
        .execute()
    )
