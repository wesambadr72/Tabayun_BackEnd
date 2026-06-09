import re

import httpx
from bs4 import BeautifulSoup


class SourceFetcher:
    """Fetches readable text from legal source URLs for RAG grounding."""

    def __init__(self, timeout_seconds: float = 8.0, max_chars: int = 6000):
        self.timeout_seconds = timeout_seconds
        self.max_chars = max_chars

    async def fetch_text(self, url: str | None) -> str | None:
        if not url:
            return None

        response_text = None
        for verify in (True, False):
            response_text = await self._fetch(url, verify=verify)
            if response_text:
                break

        if not response_text:
            return None

        text = self._extract_text(response_text)
        if len(text) < 80:
            return None
        return text[: self.max_chars]

    async def _fetch(self, url: str, verify: bool) -> str | None:
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds,
                follow_redirects=True,
                verify=verify,
                headers={
                    "User-Agent": "TabayunBot/1.0 (+legal-reference-check)"
                },
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
        except Exception:
            return None
        return response.text

    def _extract_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.body or soup
        text = main.get_text(" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()
