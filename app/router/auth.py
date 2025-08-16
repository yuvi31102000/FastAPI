from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session


router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint to authenticate users. This endpoint will return a 
       token for authenticated users. The user_credentials parameter is
       a dependency that FastAPI will parse from the request body."""
    
    user = db.query(models.User).filter(models.User.email_id == user_credentials.username).first()  # Fetch the user by email_id
    
    if not user or not utils.verify_password(user_credentials.password, user.password): # Verify the password
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect username or password")  # Raise an exception if the user is not found or the password is incorrect
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})                            # Create an access token

    return {"access_token": access_token, "token_type": "bearer"}
    
   

