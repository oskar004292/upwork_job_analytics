from typing import Iterable
from app.schemas import JobIn


class ManualImportAdapter:
    """
    Temporary adapter.
    Replace with real Upwork ingestion later.
    """

    def fetch_jobs(self) -> Iterable[JobIn]:
        return []
