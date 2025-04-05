from fastapi import FastAPI, Depends, HTTPException, status, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, join
from typing import Optional
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import os

from app.database import get_db, User, Post, UserLike, create_tables
from app.schemas import UserCreate, UserResponse, PostCreate, PostResponse, LoginRequest, LoginResponse, TelegramLinkRequest
from app.schemas import UsernameRequest, UserLikeWithCategoryResponse, NewsCreate, ChangeRoleRequest
from app.auth import authenticate_user, get_password_hash, get_user_by_username
from app.recommendation import get_recommendations_for_user
from app.telegram_bot import get_bot_link, send_message_to_user, verify_and_link_user, setup_bot, start_bot, stop_bot, pending_users
from app.parser_service import start_parser_service

app = FastAPI(title="Forum API")
create_tables()

# Download required NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# Load the model and vectorizer
model_path = os.path.join(os.path.dirname(__file__), 'analyzer/model.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'analyzer/vectorizer.pkl')

# Check if model files exist
if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
    print("Warning: Model files not found in analyzer folder. Classification route will not work.")
    model = None
    vectorizer = None
else:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

CATEGORY_MAPPING = {
    "Наука и образование": 1,
    "Энергетика": 2,
    "Просвещение и образование": 3,
    "Фотоэлектроника": 4,
    "Исследования в области медицины": 5,
    "Наука и технологии": 6,
    "Биология и сельское хозяйство": 7,
    "Нанотехнологии": 8,
    "Наука и туризм": 9,
    "Нейробиология": 10,
    "Климат и устойчивое развитие": 11,
    "Фотоника и телеком": 12,
    "Научно-популярные проекты": 13
}

REVERSE_CATEGORY_MAPPING = {v: k for k, v in CATEGORY_MAPPING.items()}

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('russian'))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

@app.on_event("startup")
async def startup_event():
    await start_bot()
    start_parser_service()

@app.on_event("shutdown")
async def shutdown_event():
    await stop_bot()

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
    db_user = User(
        username=user.username, 
        password=hashed_password, 
        who_is_user=user.who_is_user,
        telegram_id=None 
    )
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


@app.get("/users/{username}/telegram")
async def check_telegram_status(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    
    if not user.telegram_id:
        return {
            "is_linked": False,
            "link": get_bot_link(),
            "message": "Пожалуйста, перейдите по ссылке и подключите Telegram бота"
        }
    
    await send_message_to_user(user.telegram_id, "Привет!")
    
    return {
        "is_linked": True,
        "message": "Telegram бот успешно подключен. Сообщение отправлено."
    }

@app.post("/users/{username}/send_post/{post_id}")
async def send_post_options(username: str, post_id: int, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not user.telegram_id:
        return {
            "success": False,
            "message": "Пользователь не подключил Telegram бота",
            "link": get_bot_link()
        }
    
    message = f"Статья: {post.title}\n\nВыберите формат для получения документа:"
    from app.telegram_bot import send_format_options
    await send_format_options(user.telegram_id, post_id, message)
    
    return {
        "success": True,
        "message": "Сообщение с выбором формата отправлено пользователю"
    }

@app.post("/posts/{post_id}/classify", response_model=dict)
def classify_post(post_id: int, db: Session = Depends(get_db)):
    # Check if model is loaded
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classification model not available"
        )
    
    # Get post from database
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Preprocess the post content
    post_content = post.content
    cleaned_content = preprocess_text(post_content)
    
    # Vectorize the content
    vectorized_content = vectorizer.transform([cleaned_content])
    
    # Predict the category
    prediction = model.predict(vectorized_content)
    predicted_category = prediction[0]
    
    # Convert text category to numerical if needed
    if isinstance(predicted_category, str) and predicted_category in CATEGORY_MAPPING:
        numerical_category = CATEGORY_MAPPING[predicted_category]
    elif isinstance(predicted_category, (int, float)):
        # If already numerical, ensure it's within our range
        numerical_category = int(predicted_category)
        if numerical_category < 1 or numerical_category > len(CATEGORY_MAPPING):
            # Default to category 1 if out of range
            numerical_category = 1
    else:
        # If unknown category, default to 1
        numerical_category = 1
    
    # Get old category
    old_category = post.category
    
    # Convert old category to numerical if it's a string
    if isinstance(old_category, str) and old_category in CATEGORY_MAPPING:
        old_numerical = CATEGORY_MAPPING[old_category]
    elif isinstance(old_category, (int, float)) and old_category is not None:
        old_numerical = int(old_category)
    else:
        old_numerical = None
    
    # Update the post category in the database with numerical value
    post.category = numerical_category
    db.commit()
    
    return {
        "post_id": post_id,
        "old_category": old_numerical,
        "new_category": numerical_category,
        "status": "updated"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)