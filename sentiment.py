from textblob import TextBlob

def analyze_sentiment(text):
    """
    Analyze sentiment of a given text using TextBlob.
    Returns polarity (-1 to 1) and sentiment label.
    """
    if not text or text.strip() == "":
        return {"polarity": 0.0, "label": "neutral"}

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "polarity": polarity,
        "label": label
    }
