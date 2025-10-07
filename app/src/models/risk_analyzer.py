# src/models/risk_analyzer.py

import pandas as pd
import joblib

def predict_risk(new_text: str, model, vectorizer) -> dict:
    """
    Takes new text and pre-loaded model/vectorizer to predict risk.
    """
    # 1. Create the same features as our training data
    # Ensure all feature names are valid for DataFrames
    valid_column_names = vectorizer.get_feature_names_out()

    # Create text_length feature
    text_length_df = pd.DataFrame([{'text_length': len(new_text.split())}])

    # Create TF-IDF features for the new text
    tfidf_features = vectorizer.transform([new_text])
    tfidf_df = pd.DataFrame(tfidf_features.toarray(), columns=valid_column_names)
    
    # Combine all features
    features_df = pd.concat([text_length_df, tfidf_df], axis=1)
    
    # 2. Re-order columns to match the exact order used during training
    # This is critical to prevent errors.
    features_df = features_df[model.feature_names_in_]
    
    # 3. Make a prediction
    prediction = model.predict(features_df)[0]
    probabilities = model.predict_proba(features_df)[0]
    
    status = "Approved" if prediction == 1 else "Rejected"
    confidence = probabilities[prediction] * 100
    
    return {
        "predicted_status": status,
        "confidence_score": f"{confidence:.2f}%"
    }