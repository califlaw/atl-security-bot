import asyncio
from typing import Any, Dict
from urllib.parse import urlencode, urljoin

import httpx

from src.core.settings import settings
from src.core.transliterate import R
from src.core.utils import decode_url_b64, serialize_orjson


class VirusTotal:
    _version: int = settings.getint("virus.total", "version", fallback=3)
    _base_url = f"https://www.virustotal.com/api/v{_version}/"
    timeout: float = settings.getfloat("virus.total", "timeout")
    default_headers = {
        "X-Apikey": settings.get("virus.total", "token"),
        "Content-Type": "application/x-www-form-urlencoded",
    }

    @staticmethod
    def translate_type(value: str, default: str | None = None) -> str:
        return {
            "confirmed-timeout": R.string.analysing_conf_timeout,
            "failure": R.string.analysing_failure,
            "harmless": R.string.analysing_harmless,
            "malicious": R.string.analysing_malicious,
            "suspicious": R.string.analysing_suspicious,
            "timeout": R.string.analysing_timeout,
            "undetected": R.string.analysing_undetected,
        }.get(value, default or R.string.analysing_undetected)

    async def request_query(
        self,
        part_url: str,
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
            if headers is None:
                headers = self.default_headers

            request_kwargs = {
                "method": method,
                "headers": headers,
                "url": urljoin(self._base_url, part_url),
            }

            if (
                data is not None
                and method.lower() != "get"
                and headers["Content-Type"] == "application/json"
            ):
                request_kwargs["data"] = serialize_orjson(
                    content=data
                ).decode()
            elif (
                data is not None
                and headers.get("Content-Type")
                == "application/x-www-form-urlencoded"
            ):
                request_kwargs["data"] = urlencode(data)
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

    async def _wait_for_analysis_completion(self, hash_link: str):
        while True:
            analysis: Dict = (
                (
                    await self.request_query(
                        f"urls/{hash_link}", method="get", raise_error=False
                    )
                ).json()
                or {}
            ).get("data", {})
            if status := analysis.get("attributes", {}).get("status"):
                if status not in (
                    "creating",
                    "starting",
                ):
                    await asyncio.sleep(20)
            break
        return analysis

    @staticmethod
    def _detect_reason_analyse(stats: Dict):
        return max(stats, key=stats.get)

    async def scan_url(
        self, url: str, wait_for_completion: bool = False
    ) -> str:
        result_url_response = (
            (
                await self.request_query(
                    "urls", data={"url": url}, raise_error=False
                )
            )
            .json()
            .get("data", {})
        )
        if wait_for_completion:
            result = await self._wait_for_analysis_completion(
                hash_link=decode_url_b64(link=url)
            )
            return self._detect_reason_analyse(
                stats=result["attributes"]["last_analysis_stats"]
            )

        return result_url_response.get("id")
