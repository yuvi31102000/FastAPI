from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional


router = APIRouter(prefix="/posts", tags=["Posts"])  # Prefix for all routes in this router and tags for documentation


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)  # response_model specifies the schema to use for the response
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)) -> schemas.PostResponse:
    """Create a new post and return it. The post parameter is a Pydantic 
       model that FastAPI will validate and parse from the request body"""
    new_post = models.Post(user_id=current_user.id, **post.dict())              # Create a new Post instance.  Converts the Pydantic Post object into a Python dictionary. Unpacks that dict into keyword args for the SQLAlchemy model constructor. Constructs a SQLAlchemy ORM object mapped to the posts table (but it’s not yet persisted to DB).
    db.add(new_post)                                                            # Add the new post to the session. This does not commit it to the database yet.
    db.commit()                                                                 # Commits the current transaction: SQLAlchemy issues an INSERT to the database and finalizes the transaction.
    db.refresh(new_post)                                                        # Refresh the instance to get the updated data from the database
    return new_post
    


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut]) # This endpoint will return a list of PostResponse objects, and FastAPI should validate and serialize the output accordingly.”
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), 
              limit: int = 10, skip: int = 0, search: Optional[str] = "")-> List[schemas.PostOut]:
    """Fetch all posts from the database and return them. The db parameter
       is a dependency that provides a database session."""
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()  # Fetch all posts from the database. This will return a list of Post objects.
    #posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()  # Fetch all posts from the database. The filter ensures that only posts belonging to the current user are returned.
     
    posts = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, 
                                                                                       models.Like.post_id == models.Post.id, 
                                                                                       isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    
    return posts    



@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)) -> schemas.PostOut:
    """Fetch a post by its ID from the database and return it. The id parameter
       is extracted from the URL path, and the db parameter provides a database session."""
    #post = db.query(models.Post).filter(models.Post.id == id).first()  # This will return the first post with the given id or None if not found.
    post = db.query(models.Post, func.count(models.Like.post_id).label("likes")).join(models.Like, 
                                                                                      models.Like.post_id == models.Post.id, 
                                                                                      isouter=True).group_by(models.Post.id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    
    return post



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)) -> None:
    """Delete a post by its ID from the database. The id parameter is extracted
       from the URL path, and the db parameter provides a database session."""
    post_query = db.query(models.Post).filter(models.Post.id == id) # Fetch the post with the given id from the database.
    post = post_query.first()  # Get the first post that matches the id

    if not post :  
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    
    if post.user_id != current_user.id:  # Check if the post belongs to the current user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")
    
    post_query.delete(synchronize_session=False)  # Delete the post from the database. The synchronize_session=False argument is used to avoid unnecessary session synchronization.
    db.commit()
    


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)) -> schemas.PostResponse:
    """Update a post by its ID with the provided data. The id parameter is extracted
       from the URL path, and the post parameter is a Pydantic model that contains the new updated post."""
    post_query = db.query(models.Post).filter(models.Post.id == id) # Fetch the post to return it.

    post = post_query.first()  # Get the first post that matches the id
    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to update this post.")
    
    post_query.update(updated_post.dict(), synchronize_session = False) 
    db.commit()

    return post_query.first()
