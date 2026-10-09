from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.jwt import create_access_token
from auth.password import verify_password
from database import get_db
from models.user import User
from schemas.auth import LoginRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    role_value = user.role.value if hasattr(user.role, "value") else user.role
    token = create_access_token({"sub": str(user.id), "role": role_value})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            role=role_value,
            department_id=user.department_id,
            linked_student_id=user.linked_student_id,
        ),
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    role_value = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else current_user.role
    )
    return UserProfile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=role_value,
        department_id=current_user.department_id,
        linked_student_id=current_user.linked_student_id,
    )
