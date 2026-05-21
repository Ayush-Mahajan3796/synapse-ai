from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from database import crud
from database.models import User
from models.schemas import UserRegisterRequest, UserLoginRequest, AuthResponse
from utils.auth_utils import generate_salt, hash_password, verify_password

router = APIRouter()

@router.post("/register", response_model=AuthResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. Normalize input and check if username already exists
    username = request.username.strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must not be empty"
        )

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use"
            )
    
    # 2. Create salt & hash password
    salt = generate_salt()
    pw_hash = hash_password(request.password, salt)

    # 3. Persist user in the database
    try:
        db_user = crud.create_user(
            db,
            username=username,
            password_hash=pw_hash,
            salt=salt,
            email=request.email
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that username or email already exists"
        )

    return AuthResponse(
        user_id=db_user.id,
        username=db_user.username,
        message="Registration successful"
    )

@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    # 1. Fetch user by username
    db_user = db.query(User).filter(User.username == request.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
    
    # 2. Verify password hash
    if not verify_password(request.password, db_user.salt, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )
        
    return AuthResponse(
        user_id=db_user.id,
        username=db_user.username,
        message="Login successful"
    )
