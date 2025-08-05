from dataclasses import dataclass
from typing import Optional


@dataclass
class SnowflakeConfig:
    """Snowflake configuration for data warehouse connection"""
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema: str
    role: Optional[str] = None