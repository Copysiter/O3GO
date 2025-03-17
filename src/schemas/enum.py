import enum
from dataclasses import dataclass, fields


@dataclass
class Enum:
    @classmethod
    def name(cls, value):
        for field in fields(cls):
            if getattr(cls, field.name) == value:
                return field.name
        return None
