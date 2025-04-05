import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sqlalchemy.orm import Session
from app.database import UserLike, Post

def get_recommendations_for_user(db: Session, user_id: int, top_n=5):
    likes = db.query(UserLike.user_id, UserLike.post_id).all()
    user_likes = [like for like in likes if like[0] == user_id]
    if len(user_likes) < 5:
        return None 
    
    df = pd.DataFrame(likes, columns=["user_id", "post_id"])
    df["liked"] = 1  
    
    user_ids = df["user_id"].astype("category").cat.codes
    post_ids = df["post_id"].astype("category").cat.codes
    
    user_id_mapping = dict(enumerate(df["user_id"].astype("category").cat.categories))
    post_id_mapping = dict(enumerate(df["post_id"].astype("category").cat.categories))
    reverse_user_mapping = {v: k for k, v in user_id_mapping.items()}
    
    num_users = user_ids.max() + 1
    num_posts = post_ids.max() + 1
    
    interaction_matrix = np.zeros((num_users, num_posts))
    
    for user, post, like in zip(user_ids, post_ids, df["liked"]):
        interaction_matrix[user, post] = like
    
    svd = TruncatedSVD(n_components=min(20, min(num_users, num_posts) - 1))
    latent_matrix = svd.fit_transform(interaction_matrix)
    predicted_matrix = np.dot(latent_matrix, svd.components_)
    user_code = reverse_user_mapping[user_id]
    user_ratings = predicted_matrix[user_code]
    
    liked_post_codes = [post_ids[i] for i in range(len(post_ids)) if user_ids[i] == user_code]
    for post_code in liked_post_codes:
        user_ratings[post_code] = -float('inf')
    
    recommended_post_codes = user_ratings.argsort()[-top_n:][::-1]
    recommended_post_ids = [post_id_mapping[code] for code in recommended_post_codes]
    post_categories = {}
    for post_id in recommended_post_ids:
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post_categories[post_id] = post.category
    
    return [{"post_id": post_id, "category": post_categories.get(post_id)} for post_id in recommended_post_ids]