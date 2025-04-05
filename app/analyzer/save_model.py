import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib
import os

nltk.download('stopwords')
nltk.download('punkt')
dataset_path = '/Users/flexonafft/Desktop/XackatonKolpaki2025/datasethahaton.csv'

data = pd.read_csv(dataset_path)
def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('russian'))
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

data['clean_content'] = data['content'].apply(preprocess_text)
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(data['clean_content'])
y = data['class_news']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = MultinomialNB()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model accuracy: {accuracy}')

current_dir = os.path.dirname(__file__)
joblib.dump(model, os.path.join(current_dir, 'model.pkl'))
joblib.dump(vectorizer, os.path.join(current_dir, 'vectorizer.pkl'))
print("Model and vectorizer saved successfully to:", current_dir)