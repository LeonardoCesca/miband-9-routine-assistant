from fastapi import APIRouter, Depends, status

from app.dependencies import get_container
from app.models import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, container=Depends(get_container)) -> UserRead:
    created = container.supabase_tool.create_user(payload.model_dump(mode="json"))
    return UserRead.model_validate(created)


@router.get("", response_model=list[UserRead])
def list_users(container=Depends(get_container)) -> list[UserRead]:
    return [UserRead.model_validate(item) for item in container.supabase_tool.list_users()]
