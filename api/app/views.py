from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.repo import (
    RepositoryDatabaseService,
    get_repository_database_service,
    RepositoryAnalyticsDatabaseService,
    get_repository_analytics_database_service,
)
from app.schema import (
    Repository,
    RepositorySortingQueryParams,
    RepositoryAnalyticsSortingQueryParams,
    RepositoryAnalytics,
)
from core.db.operators import Between, Equals

router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.get("/top100", status_code=status.HTTP_200_OK, response_model=list[Repository])
async def repositories_list_view(
    db_service: Annotated[RepositoryDatabaseService, Depends(get_repository_database_service)],
    query_params: Annotated[RepositorySortingQueryParams, Depends()],
):
    return await db_service.fetch_repositories(sort=query_params.sort, order=query_params.order)


@router.get("/{owner}/{repo}/activity", response_model=list[RepositoryAnalytics])
async def repositories_activity_view(
    db_service: Annotated[RepositoryAnalyticsDatabaseService, Depends(get_repository_analytics_database_service)],
    query_params: Annotated[RepositoryAnalyticsSortingQueryParams, Depends()],
    owner: str,
    repo: str,
):
    return await db_service.fetch_repositories_analytics(
        owner=owner,
        repo=repo,
        sort=query_params.sort,
        order=query_params.order,
        since=query_params.since,
        until=query_params.until,
    )
