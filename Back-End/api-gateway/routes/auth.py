from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from middleware.auth import create_access_token
from datetime import timedelta
from config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - authenticate user and return JWT token
    
    Note: This is a simplified version. In production, you should:
    - Hash and verify passwords
    - Store user data in a database
    - Implement proper user management
    """
    # TODO: Implement proper authentication with database
    # For now, accept any login for development
    
    access_token = create_access_token(
        data={"sub": request.email, "email": request.email},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register endpoint - create new user account
    
    Note: This is a simplified version. In production, you should:
    - Hash passwords before storing
    - Validate email uniqueness
    - Store user data in a database
    - Send verification email
    """
    # TODO: Implement proper user registration with database
    # For now, accept any registration for development
    
    access_token = create_access_token(
        data={"sub": request.email, "email": request.email},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/refresh")
async def refresh_token():
    """Refresh JWT token"""
    # TODO: Implement token refresh logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )
