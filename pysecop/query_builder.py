from typing import List, Any, Optional, Dict, Union

class QueryBuilder:
    """
    A simple SoQL (Socrata Query Language) builder.
    """
    def __init__(self):
        self._select: List[str] = []
        self._where: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._order: Optional[str] = None

    def select(self, columns: List[str]) -> "QueryBuilder":
        self._select.extend(columns)
        return self

    def where_in(self, column: str, values: List[Any]) -> "QueryBuilder":
        if not values:
            return self
        formatted_values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in values])
        self._where.append(f"{column} in ({formatted_values})")
        return self

    def where_custom(self, condition: str) -> "QueryBuilder":
        self._where.append(condition)
        return self

    def limit(self, value: int) -> "QueryBuilder":
        self._limit = value
        return self

    def offset(self, value: int) -> "QueryBuilder":
        self._offset = value
        return self

    def order(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self._order = f"{column} {direction}"
        return self

    def build(self) -> str:
        parts = []
        if self._select:
            parts.append(f"select {', '.join(self._select)}")
        
        if self._where:
            parts.append(f"where {' AND '.join(self._where)}")
            
        if self._order:
            parts.append(f"order {self._order}")
            
        if self._limit:
            parts.append(f"limit {self._limit}")
            
        if self._offset:
            parts.append(f"offset {self._offset}")
            
        return " ".join(parts)
