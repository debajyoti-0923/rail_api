from .database import sessionlocal
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from . import crud
import datetime

oauth2=OAuth2PasswordBearer(tokenUrl="token")


SECRET_KEY = "rail_app_safe_key"
ALGORITHM = "HS256"
SECRET_ADMIN_KEY="$2b$12$fy.WtnZozI1ddNvNNA4EWeIlxaO0hQnEawfHtVev7Me13.tR1qcxq"
#secret-admin-key


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data:dict):
    toencode=data.copy()
    encoded=jwt.encode(toencode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded

def verify_password(plain_password, hashed_password):
    return crud.pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    user = crud.get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user_details(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user=crud.get_user(db=db,username=username)
    return user



# def get_hash_pass(password):
#     return crud.pwd_context.hash(password)


#--------------------------X---------------------------------------------
#admins

def authenticate_admin(password:str):
    return crud.pwd_context.verify(password, SECRET_ADMIN_KEY)

def get_admin_details(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        is_admin:bool=payload.get("admin")
        if username is None:
            raise credentials_exception
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="no admin rights",
            )
    except JWTError:
        raise credentials_exception

    user=crud.get_user(db=db,username=username)
    return user


