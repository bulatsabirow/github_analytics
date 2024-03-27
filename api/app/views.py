from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.repo import RepositoryDatabaseService, get_repository_database_service
from app.schema import Repository, RepositoryQueryParams

router = APIRouter()


@router.get("/repositories", status_code=status.HTTP_200_OK, response_model=list[Repository])
async def repositories_list_view(
    repo: Annotated[RepositoryDatabaseService, Depends(get_repository_database_service)],
    query_params: Annotated[RepositoryQueryParams, Depends()],
):
    return await repo.select_all(query_params.sort, query_params.order)
