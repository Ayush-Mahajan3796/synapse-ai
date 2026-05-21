from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pymongo.errors import DuplicateKeyError

from database.connection import get_db, USE_MONGODB, get_mongo_users_collection
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

    if USE_MONGODB:
        users_coll = get_mongo_users_collection()
        existing_user = users_coll.find_one({"username": username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if request.email:
            existing_email = users_coll.find_one({"email": request.email})
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already in use"
                )
    else:
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

    # 3. Persist user in the SQL database so user_id remains numeric.
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

    if USE_MONGODB:
        users_coll = get_mongo_users_collection()
        try:
            users_coll.insert_one({
                "username": username,
                "email": request.email,
                "password_hash": pw_hash,
                "salt": salt,
                "created_at": datetime.utcnow(),
                "sql_user_id": db_user.id
            })
        except DuplicateKeyError:
            db.delete(db_user)
            db.commit()
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
    if USE_MONGODB:
        users_coll = get_mongo_users_collection()
        mongo_user = users_coll.find_one({"username": request.username})
        if not mongo_user or not verify_password(request.password, mongo_user["salt"], mongo_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username or password"
            )

        sql_user = db.query(User).filter(User.username == request.username).first()
        if not sql_user:
            try:
                sql_user = crud.create_user(
                    db,
                    username=request.username,
                    password_hash=mongo_user["password_hash"],
                    salt=mongo_user["salt"],
                    email=mongo_user.get("email")
                )
            except IntegrityError:
                db.rollback()
                sql_user = db.query(User).filter(User.username == request.username).first()
                if not sql_user:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to synchronize user with SQL backend"
                    )

        return AuthResponse(
            user_id=sql_user.id,
            username=sql_user.username,
            message="Login successful"
        )

    db_user = db.query(User).filter(User.username == request.username).first()
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
