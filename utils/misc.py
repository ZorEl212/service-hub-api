from datetime import datetime
from zoneinfo import ZoneInfo


class MiscUtils:
    @classmethod
    def datetime_to_gmt_str(cls, dt: datetime) -> str:
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))

        return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
