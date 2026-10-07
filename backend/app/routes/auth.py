from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas import (
    LoginRequest,
    LoginResponse,
    SignUpRequest,
    UserResponse,
)
from ..security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# SIGN UP
# =========================================================

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    user_data: SignUpRequest,
    db: Session = Depends(get_db),
):
    normalized_email = str(user_data.email).lower()

    existing_user = db.scalar(
        select(User).where(
            or_(
                User.username == user_data.username,
                User.email == normalized_email,
            )
        )
    )

    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already registered.",
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    new_user = User(
        username=user_data.username,
        email=normalized_email,
        password_hash=hash_password(
            user_data.password
        ),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    normalized_email = str(login_data.email).lower()

    user = db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )

    # Use the same error for unknown email and wrong
    # password so we don't reveal which emails exist.
    if not user or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    access_token = create_access_token(
        user_id=user.id,
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_minutes=(
            settings.jwt_access_token_expire_minutes
        ),
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )