from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import models, schemas, utils
from sqlalchemy.orm import Session


router = APIRouter(prefix="/users", tags=["Users"])  # Prefix for all routes in this router


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)  # response_model specifies the schema to use for the response
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)) -> schemas.UserResponse:
    """Create a new user and return it. The user parameter is a Pydantic 
       model that FastAPI will validate and parse from the request body."""
    hashed_password = utils.hash_password(user.password)    # Hash the password before storing it
    user.password = hashed_password                         # Replace the plain password with the hashed password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse )
def get_user(id: int, db: Session = Depends(get_db)) -> schemas.UserResponse:
    """Fetch a user by its ID from the database and return it. The id parameter
       is extracted from the URL path, and the db parameter provides a database session."""
    user = db.query(models.User).filter(models.User.id == id).first() 

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    
    return user