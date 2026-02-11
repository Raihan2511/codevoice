# src/types/key_type.py
from enum import Enum


class ToolConfigKeyType(str, Enum):
    """Enumeration for tool configuration key types."""
    STRING = "STRING"
    INTEGER = "INTEGER"
    FILE = "FILE"
    BOOLEAN = "BOOLEAN"
