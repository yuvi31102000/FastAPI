from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


###### Request Model ######

class PostBase(BaseModel):        # class PostBase is a Pydantic model used for request validation and parsing. When a request comes in, FastAPI will parse the JSON body into a Post object.
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):       # Inherits from PostBase, used for creating a new post
    pass

class UserCreate(BaseModel):      # Base model for user data
    email_id: EmailStr            # Using EmailStr for email validation
    password: str

class UserLogin(BaseModel):       # Base model for user login data
    email_id: EmailStr  
    password: str

class Like(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, ge=0, le=1)]  # must be 0 or 1

class TokenResponse(BaseModel):          # Base model for token response
    access_token: str
    token_type: str

class TokenData(BaseModel):       # Base model for token data
    id: str




###### Response Model ######

class UserResponse(BaseModel):   
    id: int
    email_id: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class PostResponse(PostBase):      # Inherits from PostBase, used for returning a post
    id: int
    created_at: datetime
    user_id: int
    user: UserResponse            # Include user information in the response

    class Config:                  # Config class to specify that the model should be serialized to JSON
        orm_mode = True            # This allows the model to work with SQLAlchemy ORM objects, enabling automatic conversion from SQLAlchemy models to Pydantic models.


class PostOut(BaseModel):
    Post: PostResponse
    likes: int

    class Config:
        orm_mode = True
  