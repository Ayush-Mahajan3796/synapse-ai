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
    """Register a new user and store credentials in MySQL."""
    username = request.username.strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must not be empty"
        )

    # Check for duplicate username
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check for duplicate email
    if request.email and db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already in use"
        )

    # Hash the password
    salt = generate_salt()
    pw_hash = hash_password(request.password, salt)

    # Persist user
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
    """Authenticate a user against credentials stored in MySQL."""
    
    # --- OWNER OVERRIDE LOGIN ---
    # If MySQL fails or isn't set up, you can still log in with this account.
    if request.username == "ayush" and request.password == "993796":
        return AuthResponse(
            user_id=0,  # Special ID for owner
            username="ayush",
            message="Owner login successful (Bypassed MySQL)"
        )
    # ----------------------------

    try:
        db_user = db.query(User).filter(User.username == request.username).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to the MySQL database. Please check your connection."
        )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password"
        )

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
