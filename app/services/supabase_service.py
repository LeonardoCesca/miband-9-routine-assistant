from __future__ import annotations

from typing import Any

from supabase import Client


class SupabaseService:
    def __init__(self, client: Client) -> None:
        self._client = client

    def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._client.table(table).insert(payload).execute()
        data = response.data or []
        return data[0] if data else payload

    def select(
        self,
        table: str,
        *,
        filters: dict[str, Any] | None = None,
        columns: str = "*",
    ) -> list[dict[str, Any]]:
        query = self._client.table(table).select(columns)
        for key, value in (filters or {}).items():
            query = query.eq(key, value)
        response = query.execute()
        return list(response.data or [])

    def update(
        self,
        table: str,
        *,
        filters: dict[str, Any],
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        query = self._client.table(table).update(payload)
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        return list(response.data or [])

    def rpc(self, function_name: str, params: dict[str, Any]) -> Any:
        response = self._client.rpc(function_name, params).execute()
        return response.data
