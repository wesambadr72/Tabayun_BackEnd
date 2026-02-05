from typing import Iterable, Optional
from urllib.parse import urljoin
from urllib.request import urlopen


class WorldLiiSpider:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def fetch(self, path: str) -> str:
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        with urlopen(url) as response:
            data = response.read()
        return data.decode("utf-8", errors="ignore")

    def parse(self, html: str) -> Iterable[str]:
        return []

    def run(self, start_path: str) -> Iterable[str]:
        html = self.fetch(start_path)
        return self.parse(html)

