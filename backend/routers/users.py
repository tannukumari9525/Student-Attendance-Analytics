from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_role
from auth.password import hash_password
from database import get_db
from models.user import User, UserRole
from schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _user_to_read(u: User) -> UserRead:
    role_val = u.role.value if hasattr(u.role, "value") else u.role
    return UserRead(
        id=u.id,
        name=u.name,
        email=u.email,
        role=role_val,
        department_id=u.department_id,
        linked_student_id=u.linked_student_id,
        is_active=u.is_active,
    )


@router.get("/", response_model=list[UserRead])
def list_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    query = db.query(User)
    if role:
        try:
            role_enum = UserRole[role]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        query = query.filter(User.role == role_enum)
    return [_user_to_read(u) for u in query.all()]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        role_enum = UserRole[payload.role]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {payload.role}")
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=role_enum,
        department_id=payload.department_id,
        linked_student_id=payload.linked_student_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_read(user)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return _user_to_read(current_user)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    # Students/parents can only view themselves
    if role not in ("admin", "teacher") and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_read(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return _user_to_read(user)
