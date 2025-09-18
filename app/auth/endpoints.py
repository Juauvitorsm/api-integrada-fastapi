from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.auth import verify_password, create_access_token, create_refresh_token, decode_token, hash_password
from app.auth.schemas import Token, UserLogin
from app.auth.models import User
from database import get_db 

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(db: Session = Depends(get_db), token: Annotated[str, Depends(oauth2_scheme)] = None):
    payload = decode_token(token)
    if not payload or payload.get("sub") is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_email = payload.get("sub")
    user = get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("/register")
def register_user(user: UserLogin, db: Session = Depends(get_db)):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário cadastrado com sucesso!"}

@router.post("/token", response_model=Token)
async def login_for_access_and_refresh_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais de usuário ou senha incorretas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: Annotated[str, Form()], 
    db: Session = Depends(get_db)
):
    payload = decode_token(refresh_token)
    if not payload or payload.get("sub") is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de atualização inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_email = payload.get("sub")
    user = get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return {"email": current_user.email}