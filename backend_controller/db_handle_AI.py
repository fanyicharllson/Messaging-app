
from datetime import datetime
import cohere
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
cohere_client = cohere.Client(cohere_api_key)

from backend_controller.db_handler import create_connection

def save_chat_message(user_id, message, ai_suggestions):
    conn = create_connection()
    cursor = conn.cursor()

    # Insert message into the database
    cursor.execute("""
        INSERT INTO chat_messages (user_id, message, ai_suggestions, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, message, ai_suggestions, datetime.now()))
    conn.commit()
    conn.close()

def load_chat_history(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message, ai_suggestions, timestamp 
        FROM chat_messages 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    """, (user_id,))
    messages = cursor.fetchall()
    conn.close()

    return messages

def get_smart_suggestions(user_message):
    """Get AI-generated smart suggestions using Cohere."""
    try:
        # Generate suggestions with Cohere
        response = cohere_client.generate(
            model='command-xlarge-nightly',  # Adjust model based on your plan
            prompt=f"Suggest 2 alternatives for this message: '{user_message}'",
            max_tokens=30,
            temperature=0.7,
            k=0,
            p=0.75,
            stop_sequences=["--"]  # Optional, can use to separate multiple outputs
        )

        # Extract and split suggestions
        generated_text = response.generations[0].text
        suggestions = generated_text.strip().split('\n')  # Split suggestions into a list
        return [suggestion.strip() for suggestion in suggestions if suggestion.strip()]
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return ["Sorry, I couldn't generate suggestions."]

def analyze_sentiment(message):
    """Analyze sentiment using Cohere's classify endpoint."""
    try:
        # Use Cohere's classify API for sentiment analysis
        response = cohere_client.classify(
            inputs=[message],
            model='large',  # Use Cohere's sentiment model (customizable if needed)
            examples=[
                cohere.ClassifyExample("I love this!", "positive"),
                cohere.ClassifyExample("This is the worst!", "negative"),
                cohere.ClassifyExample("It's okay, not great.", "neutral")
            ]
        )

        sentiment = response.classifications[0].prediction
        # Map sentiment to emojis
        sentiment_emojis = {
            "positive": "😊",
            "neutral": "😐",
            "negative": "😢"
        }
        return sentiment_emojis.get(sentiment, "🤔")
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "🤔"
