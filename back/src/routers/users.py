import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..models.user import User
from ..service.auth import hash_password


router = APIRouter()
logger = logging.getLogger("api.users")


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    logger.info("Attempting to create user '%s'", payload.username)
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        logger.warning("Username '%s' already taken", payload.username)
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning("IntegrityError: username '%s' conflict on commit", payload.username)
        raise HTTPException(status_code=409, detail="Username already taken")
    except Exception as exc:
        db.rollback()
        logger.error("Unexpected error creating user '%s': %s", payload.username, exc)
        raise HTTPException(status_code=500, detail="Failed to create user")

    db.refresh(user)
    logger.info("User '%s' created with id=%s", user.username, user.id)
    return user
