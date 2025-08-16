from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .router import post, user, auth, likes


models.Base.metadata.create_all(bind=engine)  # Create the database tables


# Initialize FastAPI app
app = FastAPI() 


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)  # Include the post router
app.include_router(user.router)  # Include the user router
app.include_router(auth.router)  # Include the auth router
app.include_router(likes.router) # Include the likes router

