from __future__ import annotations

from fastapi import HTTPException, Request, status


def get_container(request: Request):
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application container is not ready",
        )
    return container

