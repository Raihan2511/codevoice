# src/tool_framework/tool_config.py
import os
import sys

# Add project root to path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.types.key_type import ToolConfigKeyType


class ToolConfiguration:
    """A class to define a configuration requirement for a tool or toolkit."""
    
    def __init__(
        self, 
        key: str, 
        key_type: ToolConfigKeyType, 
        is_required: bool = False, 
        is_secret: bool = False
    ):
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty string")
        if not isinstance(key_type, ToolConfigKeyType):
            raise ValueError(
                f"key_type must be an instance of ToolConfigKeyType, not {type(key_type)}"
            )
            
        self.key = key
        self.key_type = key_type
        self.is_required = bool(is_required)
        self.is_secret = bool(is_secret)

    def __repr__(self):
        return (
            f"ToolConfiguration(key='{self.key}', "
            f"key_type='{self.key_type.value}', "
            f"required={self.is_required}, "
            f"secret={self.is_secret})"
        )
