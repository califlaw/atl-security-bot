import asyncio
from typing import Any, Dict

import httpx

from src.core.settings import settings
from src.core.utils import serialize_orjson


class VirusTotal:
    timeout: float = settings.getfloat("virus.total", "timeout")
    default_headers = {
        "x-apikey": settings.get("virus.total", "token"),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async def request_query(
        self,
        url: str,
        data: Dict[str, Any] | str | None = None,
        method: str = "post",
        headers: Dict[str, str] | None = None,
        raise_error: bool = True,
    ) -> httpx.Response | None:
        async with httpx.AsyncClient(
            http2=True,
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=10),
        ) as client:  # type: httpx.AsyncClient
            if method != "get" and data is not None:
                data: Dict = serialize_orjson(  # type: ignore
                    content=data
                ).decode()
                if headers is None:
                    headers = self.default_headers

            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers or {},
            }

            if data is not None and method.lower() != "get":
                request_kwargs["data"] = data
            elif data is not None:
                request_kwargs["params"] = data

            res: httpx.Response = await client.request(**request_kwargs)

            if not raise_error:
                return res

            try:
                res.raise_for_status()
                return res
            except httpx.HTTPStatusError:
                return None

    async def _wait_for_analysis_completion(self, analysis):
        while True:
            analysis = await self.get_object("/analyses/{}", analysis.id)
            if analysis.status == "completed":
                break
            await asyncio.sleep(20)
        return analysis

    async def scan_url(self, url: str, wait_for_completion: bool = False):
        result = await self.request_query(
            "/urls", data={"url": url}, method="post"
        )
        if wait_for_completion:
            await self._wait_for_analysis_completion(analysis=result)

        return result
