from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


@dataclass
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(
    page: int = Query(1, ge=1, le=100000, description="1-based page number."),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)."),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def build_page(items: list, total: int, params: PageParams) -> dict:
    pages = max(1, -(-total // params.page_size))
    return {
        "items": items,
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "pages": pages,
    }
