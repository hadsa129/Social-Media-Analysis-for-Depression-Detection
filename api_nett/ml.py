from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any
import re

# Variables globales pour les modèles
sentiment_analyzer = None
theme_classifier = None

# Thèmes des troubles mentaux
themes = [
    "Depression",
    "Anxiety",
    "Bipolar Disorder", 
    "Schizophrenia",
    "Eating Disorder",
    "Substance Abuse"
]

def load_models():
    """Charger les modèles ML"""
    global sentiment_analyzer, theme_classifier
    
    try:
        # Charger le modèle de sentiment
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        print("Modèle de sentiment chargé")
    except Exception as e:
        print(f" Erreur chargement modèle sentiment: {e}")
        sentiment_analyzer = None
    
    try:
        # Charger le modèle de thèmes
        theme_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        print("Modèle de thèmes chargé")
    except Exception as e:
        print(f" Erreur chargement modèle thèmes: {e}")
        theme_classifier = None

def predict_sentiment(text):
    """Prédire le sentiment d'un texte"""
    if not text:
        return {
            "label": "NEUTRAL", 
            "score": 0.5, 
        }
    
    if sentiment_analyzer is None:
        return {
            "label": "NEUTRAL",
            "score": 0.5,
            "error": "Modèle non chargé"
        }
    
    try:
        result = sentiment_analyzer(text)[0]
        label_mapping = {
            'positive': 'POSITIVE',
            'negative': 'NEGATIVE',
            'neutral': 'NEUTRAL',
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL', 
            'LABEL_2': 'POSITIVE'
        }
        
        predicted_label = label_mapping.get(result['label'], result['label'].upper())
        score = float(result['score'])
        
        return {
            "label": predicted_label,
            "score": score
        }
    except Exception as e:
        return {
            "label": "NEUTRAL",
            "score": 0.5,
            "error": str(e)
        }

def predict_theme(text):
    """Prédire le thème/le trouble mental d'un texte"""
    if not text:
        return {
            "predicted_theme": "Not Determined"
        }
    
    if theme_classifier is None:
        return {
            "predicted_theme": "Not Determined",
            "error": "Modèle non chargé"
        }
    
    try:
        result = theme_classifier(
            text, 
            themes,
            multi_label=True
        )
        main_theme = result['labels'][0]
        main_score = float(result['scores'][0])
        
        return {
            "predicted_theme": main_theme,
            "confidence": main_score
        }
    except Exception as e:
        return {
            "predicted_theme": "Not Determined",
            "error": str(e)
        }