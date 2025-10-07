# train_model.py

import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os

def create_feature_dataset(data_path: str = 'data/processed/knowledge_base.json'):
    """
    Loads the knowledge base and engineers features for the ML model.
    """
    print("--- Starting Feature Engineering ---")
    try:
        df = pd.read_json(data_path)
    except FileNotFoundError:
        print(f"Error: {data_path} not found.")
        return None, None, None
    df['text_length'] = df['full_text'].apply(lambda x: len(x.split()))
    tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1, 2))
    tfidf_features = tfidf_vectorizer.fit_transform(df['full_text'])
    tfidf_df = pd.DataFrame(tfidf_features.toarray(), columns=tfidf_vectorizer.get_feature_names_out())
    df['label'] = df['status'].apply(lambda x: 1 if str(x).lower() == 'approved' else 0)
    features_df = pd.concat([df[['text_length']], tfidf_df], axis=1)
    X = features_df
    y = df['label']
    print("--- Feature Engineering Complete ---")
    return X, y, tfidf_vectorizer

def train_and_save_model(X, y, vectorizer, model_dir="trained_models"):
    """
    Splits data, trains a model, evaluates it, and saves the model and vectorizer.
    """
    print("\n--- Starting Model Training ---")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training set size: {X_train.shape[0]} samples, Testing set size: {X_test.shape[0]} samples")

    model = LogisticRegression(max_iter=1000)
    print("Training Logistic Regression model...")
    model.fit(X_train, y_train)
    print("Model training complete.")

    print("\n--- Evaluating Model ---")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy on Test Set: {accuracy * 100:.2f}%")
    
    print("\n--- Saving Model and Vectorizer ---")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "risk_model.joblib")
    vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.joblib")
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")
    
    return model

# --- Main block for running the full ML pipeline ---
if __name__ == '__main__':
    X_dataset, y_dataset, tfidf_vectorizer = create_feature_dataset()
    
    if X_dataset is not None and y_dataset is not None:
        if len(y_dataset.unique()) < 2:
            print("\nError: The dataset has only one class. Cannot train a model.")
        else:
            train_and_save_model(X_dataset, y_dataset, tfidf_vectorizer)