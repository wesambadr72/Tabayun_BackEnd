from typing import Any


class BasePipeline:
    def process_item(self, item: Any) -> Any:
        return item

