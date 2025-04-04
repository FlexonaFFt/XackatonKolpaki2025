from fastapi import FastAPI, Depends, HTTPException, status, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, join
from typing import Optional

from app.database import get_db, User, Post, UserLike, create_tables
from app.schemas import UserCreate, UserResponse, PostCreate, PostResponse, LoginRequest, LoginResponse
from app.schemas import UsernameRequest, UserLikeWithCategoryResponse, NewsCreate, ChangeRoleRequest
from app.auth import authenticate_user, get_password_hash, get_user_by_username
from app.recommendation import get_recommendations_for_user

app = FastAPI(title="Forum API")
create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login", response_model=LoginResponse)
async def login_json(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {
        "success": True, 
        "user_id": user.id, 
        "username": user.username,
        "who_is_user": user.who_is_user 
    }

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password) 
    db_user = User(username=user.username, password=hashed_password, who_is_user=user.who_is_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, post.username)
    post_data = post.dict() if hasattr(post, 'dict') else post.model_dump()
    post_data.pop('username')  
    
    db_post = Post(
        **post_data,
        type="post",
        author_username=current_user.username
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.post("/news/", response_model=PostResponse)
def create_news(news: NewsCreate, username: str, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, username)
    if current_user.who_is_user not in ["admin", "redactor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and redactors can create news"
        )
    
    news_data = news.dict() if hasattr(news, 'dict') else news.model_dump()
    
    db_news = Post(
        **news_data,
        type="news",
        author_username=None  
    )
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@app.get("/posts/", response_model=list[PostResponse])
def read_posts(skip: int = 0, limit: int = 50, post_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Post)
    if post_type:
        query = query.filter(Post.type == post_type)
    
    posts = query.offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/posts/{post_id}/like")
def like_post(post_id: int, username_data: UsernameRequest, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, username_data.username)
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.post_id == post_id
    ).first()
    
    if like:
        raise HTTPException(status_code=400, detail="Post already liked")
    
    new_like = UserLike(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    db.commit()
    return {"message": "Post liked successfully"}

@app.delete("/posts/{post_id}/unlike")
def unlike_post(post_id: int, username_data: UsernameRequest, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, username_data.username)
    like = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.post_id == post_id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}

@app.get("/recommended_data/{username}", response_model=list[UserLikeWithCategoryResponse])
def get_user_likes(username: str, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, username)
    results = db.query(
        UserLike.post_id,
        Post.category
    ).join(
        Post, UserLike.post_id == Post.id
    ).filter(
        UserLike.user_id == current_user.id
    ).all()
    
    if not results:
        return []
    
    response_data = [{"post_id": post_id, "category": category} for post_id, category in results]
    return response_data

@app.get("/recommendations/{username}", response_model=list[UserLikeWithCategoryResponse])
def get_recommendations(username: str, db: Session = Depends(get_db)):
    current_user = get_user_by_username(db, username)
    recommendations = get_recommendations_for_user(db, current_user.id)
    
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User needs at least 5 likes to get recommendations"
        )
    
    return recommendations



@app.post("/users/{username}/role")
def change_user_role(username: str, role_data: ChangeRoleRequest, db: Session = Depends(get_db)):
    admin_user = get_user_by_username(db, role_data.admin_username)
    if admin_user.who_is_user != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user roles"
        )
    
    target_user = get_user_by_username(db, username)
    if target_user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot change their own role"
        )
    
    target_user.who_is_user = role_data.new_role
    db.commit()
    
    return {
        "success": True,
        "username": target_user.username,
        "new_role": target_user.who_is_user
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)