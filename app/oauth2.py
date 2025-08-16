from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from . import models, schemas
from .database import get_db
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # This tells FastAPI: “When a route depends on oauth2_scheme, look for a Bearer token in the Authorization header.”


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    """Create a JWT access token with an expiration time.
    Args:
        data (dict): The data to encode in the token."""
    to_encode = data.copy()

    if ACCESS_TOKEN_EXPIRE_MINUTES:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Compute expiry in UTC (important so all servers agree on time)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode['exp'] = expire   # Add the standard JWT claim "exp" to the payload.                                                             
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):   # FastAPI extracts the raw token string from the Authorization header and injects it here.
    """Get the current logged in user from the token.
    Args:
        token (str): The JWT token.
        credentials_exception: Exception to raise if credentials are invalid.
        db (Session): Database session.
    Returns:
        User object if the token is valid, otherwise raises an HTTPException."""
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=str(id))  # Validate the token data against the TokenData schema

    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(token_data.id)).first()  # Fetch the user from the database using the id from the token data

    if user is None:    
        raise credentials_exception
    
    return user  # Return the user object if found
    
    
    

