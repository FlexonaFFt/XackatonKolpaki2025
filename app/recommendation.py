import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import UserLike, Post

def get_recommendations_for_user(db: Session, user_id: int, top_n=5):
    # Get all likes from the database
    likes = db.query(UserLike.user_id, UserLike.post_id).all()
    
    # Check if there are any likes in the system
    if not likes:
        return None
    
    # Get likes for the current user
    user_likes = [like for like in likes if like[0] == user_id]
    if len(user_likes) < 1:  # Changed from 5 to 1 to be less restrictive
        return None 
    
    # Create DataFrame from likes
    df = pd.DataFrame(likes, columns=["user_id", "post_id"])
    df["liked"] = 1  
    
    # Check if we have enough unique users and posts
    if len(df["user_id"].unique()) < 2 or len(df["post_id"].unique()) < 2:
        # Not enough data for collaborative filtering
        # Return some popular posts instead
        popular_posts = db.query(UserLike.post_id, Post.category)\
            .join(Post, UserLike.post_id == Post.id)\
            .group_by(UserLike.post_id, Post.category)\
            .order_by(func.count(UserLike.post_id).desc())\
            .limit(top_n)\
            .all()
        
        if not popular_posts:
            return None
            
        return [{"post_id": post_id, "category": category} for post_id, category in popular_posts]
    
    # Continue with SVD-based recommendation
    user_ids = df["user_id"].astype("category").cat.codes
    post_ids = df["post_id"].astype("category").cat.codes
    
    user_id_mapping = dict(enumerate(df["user_id"].astype("category").cat.categories))
    post_id_mapping = dict(enumerate(df["post_id"].astype("category").cat.categories))
    reverse_user_mapping = {v: k for k, v in user_id_mapping.items()}
    
    # Check if user_id exists in the mapping
    if user_id not in reverse_user_mapping:
        return None
    
    num_users = user_ids.max() + 1
    num_posts = post_ids.max() + 1
    
    # Check if we have enough data for SVD
    if num_users < 2 or num_posts < 2:
        return None
    
    interaction_matrix = np.zeros((num_users, num_posts))
    
    for user, post, like in zip(user_ids, post_ids, df["liked"]):
        interaction_matrix[user, post] = like
    
    # Ensure n_components is valid
    n_components = min(10, min(num_users, num_posts) - 1)
    if n_components < 1:
        n_components = 1
    
    try:
        svd = TruncatedSVD(n_components=n_components)
        latent_matrix = svd.fit_transform(interaction_matrix)
        predicted_matrix = np.dot(latent_matrix, svd.components_)
        
        user_code = reverse_user_mapping[user_id]
        user_ratings = predicted_matrix[user_code]
        
        # Get posts the user has already liked
        liked_post_codes = [post_ids[i] for i in range(len(post_ids)) if user_ids[i] == user_code]
        
        # Set already liked posts to negative infinity to exclude them
        for post_code in liked_post_codes:
            user_ratings[post_code] = -float('inf')
        
        # Get top N recommendations
        recommended_post_codes = user_ratings.argsort()[-top_n:][::-1]
        recommended_post_ids = [post_id_mapping[code] for code in recommended_post_codes]
        
        # Get categories for recommended posts
        post_categories = {}
        for post_id in recommended_post_ids:
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post_categories[post_id] = post.category
        
        return [{"post_id": post_id, "category": post_categories.get(post_id)} for post_id in recommended_post_ids]
    
    except Exception as e:
        # If SVD fails, fall back to popular posts
        popular_posts = db.query(UserLike.post_id, Post.category)\
            .join(Post, UserLike.post_id == Post.id)\
            .group_by(UserLike.post_id, Post.category)\
            .order_by(func.count(UserLike.post_id).desc())\
            .limit(top_n)\
            .all()
        
        if not popular_posts:
            return None
            
        return [{"post_id": post_id, "category": category} for post_id, category in popular_posts]