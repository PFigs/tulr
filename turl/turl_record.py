import json
import uuid
from dataclasses import dataclass


class Serializer(json.JSONEncoder):
    """Specialization of the JSON encoder"""

    # pylint: disable=method-hidden, arguments-differ
    def default(self, obj):
        """Handles serialization of common types"""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


@dataclass
class TurlRecord:
    url: str
    status_code: int
    elapsed: float
    last_check: str
    version: float = 1.0
    record_id: uuid.uuid4 = None
    host_id: uuid.uuid5 = None
    content_search_success: bool = None
    content_search_pattern: str = None

    def __post_init__(self):
        self.host_id = self.url_to_id(self.url)
        self.record_id = self.get_record_id()

    def to_dict(self):
        d = dict(
            version=self.version,
            host_id=self.host_id,
            record_id=self.record_id,
            url=self.url,
            status_code=self.status_code,
            response_time=self.elapsed,
            content_search_pattern=self.content_search_pattern,
            content_search_success=self.content_search_success,
            last_check=self.last_check,
        )
        return d

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d, cls=Serializer)

    def __str__(self):
        return self.to_json()

    @staticmethod
    def get_record_id():
        return uuid.uuid4()

    @staticmethod
    def url_to_id(url):
        return uuid.uuid5(uuid.NAMESPACE_DNS, url)
