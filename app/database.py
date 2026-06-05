from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    settings = get_settings()
    supabase_url = settings.supabase_url.strip()
    service_role_key = settings.supabase_service_role_key.strip()

    if not supabase_url:
        raise RuntimeError(
            "SUPABASE_URL is missing in .env. Use the base project URL, for example "
            "https://your-project.supabase.co"
        )

    if "/rest/v1" in supabase_url:
        raise RuntimeError(
            "SUPABASE_URL must be the base project URL, not the REST endpoint. "
            "Use https://your-project.supabase.co instead of .../rest/v1/"
        )

    if not service_role_key:
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is missing in .env. Copy the service_role key from "
            "Supabase Project Settings > API."
        )

    if service_role_key.startswith("sb_publishable_"):
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is using a publishable key. Replace it with the "
            "service_role key from Supabase Project Settings > API."
        )

    return create_client(supabase_url, service_role_key)
