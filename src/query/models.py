from dataclasses import dataclass, field
from typing import Any, Optional

# COntratos de dados

@dataclass
class PostgresPlan:
    tables: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    operation: Optional[str] = None
    aggregation: Optional[str] = None
    field: Optional[str] = None


@dataclass
class VectorPlan:
    semantic_query: Optional[str] = None
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryPlan:
    route: str
    intent: str
    confidence: float
    postgres: Optional[PostgresPlan] = None
    vector: Optional[VectorPlan] = None


@dataclass
class QueryRequest:
    query: str
    permission_level: str