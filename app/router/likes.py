from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session


router = APIRouter(prefix="/like", tags=["Likes"])  # Prefix for all routes in this router


@router.post("/", status_code=status.HTTP_201_CREATED)
def like_post(like: schemas.Like, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id:{like.post_id} does not exist")

    liked_post_query = db.query(models.Like).filter(models.Like.post_id == like.post_id, models.Like.user_id == current_user.id)
    found_liked_post = liked_post_query.first()

    if (like.dir == 1):
        if found_liked_post:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This post was already liked")
        
        post_like = models.Like(post_id=like.post_id, user_id=current_user.id)
        db.add(post_like)
        db.commit()
        return {"message": "Successfully added like"}
    else:
        if not found_liked_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like does not exist")
        
        liked_post_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully removed like"} 
    
    