import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import forbidden, not_found, unauthorized
from app.core.security import decode_access_token
from app.modules.users.models import User
from app.modules.workspaces.models import ROLE_RANK, Role, Workspace
from app.modules.workspaces.service import get_membership


def current_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise unauthorized()
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise unauthorized("Invalid or expired access token.")

    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise unauthorized("Account is unavailable.")
    return user


CurrentUser = User


@dataclass
class WorkspaceContext:
    workspace: Workspace
    role: Role
    user: User


def workspace_access(min_role: Role = Role.viewer):
    """Returns a FastAPI dependency enforcing workspace membership and a minimum role.

    A caller who is not a member gets 404 (not 403) so workspace existence cannot be probed.
    """

    def _dep(
        workspace_id: uuid.UUID = Path(...),
        user: User = Depends(current_user),
        db: Session = Depends(get_db),
    ) -> WorkspaceContext:
        workspace = db.get(Workspace, workspace_id)
        if workspace is None:
            raise not_found("Workspace")
        membership = get_membership(db, workspace_id, user.id)
        if membership is None:
            raise not_found("Workspace")
        role = Role(membership.role)
        if ROLE_RANK[role] < ROLE_RANK[min_role]:
            raise forbidden(f"This action requires the '{min_role.value}' role or higher.")
        return WorkspaceContext(workspace=workspace, role=role, user=user)

    return _dep
