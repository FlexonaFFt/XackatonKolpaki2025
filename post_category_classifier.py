import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import CountVectorizer
import joblib
from flask import Flask, request, jsonify
import os

# Initialize Flask app
app = Flask(__name__)

# Download required NLTK resources
nltk.download('stopwords')
nltk.download('punkt')  # Note: Fixed 'punkt_tab' to 'punkt'

# Load the model and vectorizer
# You'll need to save these first using joblib
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

# Check if model files exist
if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
    raise FileNotFoundError("Model files not found. Please train and save the model first.")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# Text preprocessing function (same as in your notebook)
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('russian'))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Mock database function (replace with your actual database connection)
def get_post_by_id(post_id):
    # This is a placeholder - replace with your actual database query
    # Return a dictionary with post data including 'content'
    pass

def update_post_category(post_id, new_category):
    # This is a placeholder - replace with your actual database update
    # Return True if update was successful
    pass

@app.route('/classify_post/<int:post_id>', methods=['POST'])
def classify_post(post_id):
    try:
        # Get post from database
        post = get_post_by_id(post_id)
        
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Preprocess the post content
        post_content = post.get('content', '')
        cleaned_content = preprocess_text(post_content)
        
        # Vectorize the content
        vectorized_content = vectorizer.transform([cleaned_content])
        
        # Predict the category
        prediction = model.predict(vectorized_content)
        predicted_category = prediction[0]
        
        # Update the post category in the database
        success = update_post_category(post_id, predicted_category)
        
        if success:
            return jsonify({
                "post_id": post_id,
                "new_category": predicted_category,
                "status": "updated"
            }), 200
        else:
            return jsonify({"error": "Failed to update post category"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)