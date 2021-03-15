#!/usr/bin python3

# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Python:
from typing import Union, AsyncGenerator, Dict, NamedTuple
from datetime import datetime, date

# 3rd party:

# Internal: 
from ..assets import get_latest_timestamp
from .request import Request

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'Response',
]


API_PREFIX = "/api/"
API_URL = "api.coronavirus.data.gov.uk"

ResponseContentType = Union[None, bytes, AsyncGenerator[bytes, None]]


class Response:
    _content: ResponseContentType
    _request: Request
    status_code: int
    headers: Dict[str, str]
    _latest_timestamp: Union[datetime, None] = None

    _content_types_lookup = {
        'json': 'application/vnd.PHE-COVID19.v2+json; charset=utf-8',
        'jsonl': 'application/vnd.PHE-COVID19.v2+jsonl; charset=utf-8',
        'xml': 'application/vnd.PHE-COVID19.v1+json; charset=utf-8',
        'csv': 'text/csv; charset=utf-8'
    }

    def __init__(self, content: ResponseContentType, status_code: int,
                 release_date: Union[date, None] = None, content_type: str = 'json',
                 request: Union[Request, None] = None):
        self._content = content
        self.status_code = status_code
        self._content_type = content_type
        self._request = request
        self._release_date = release_date

    @property
    async def latest_timestamp(self) -> Union[datetime, None]:
        if self._latest_timestamp is None:
            self._latest_timestamp = await get_latest_timestamp(self._request)
        return self._latest_timestamp

    @property
    async def headers(self):
        headers = {
            'Content-Type': self._content_types_lookup[self._content_type]
        }

        if self._content is not None:
            headers['Content-Disposition'] = (
                f'attachment; filename="data_{self._release_date:%Y-%m-%d}.{self._content_type}"'
            )

        # Additional headers for successful responses.
        if self.status_code < 400:
            url_path = self._request.url.path.removeprefix(API_PREFIX)
            permalink = f"https://{API_URL}/{url_path}?{self._request.url.query}"

            headers.update({
                "Cache-Control": "public, max-age=90, must-revalidate",
                "Content-Location": permalink,
                "Content-Language": "en-GB"
            })

        return headers

    @property
    def content(self):
        return self._content
