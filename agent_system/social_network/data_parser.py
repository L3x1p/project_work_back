from sqlalchemy.orm import Session
from postgres_db.models import User, SocialMedia


def get_reddit_data(user_id: int, db: Session):
    """
    Retrieve Reddit data for a user, including subreddits and comments, and return as a formatted string.
    """
    social_media = db.query(SocialMedia).filter(SocialMedia.user_id == user_id).first()
    if not social_media or not social_media.reddit_data:
        return None

    reddit_data = social_media.reddit_data
    subreddits = ", ".join(reddit_data.get("subreddits", []))
    comments = ", ".join(reddit_data.get("comments", []))
    return f"Subreddits: {subreddits}\nComments: {comments}"


def get_youtube_data(user_id, db):
    """
    Get YouTube data for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        List of YouTube keywords or empty list if no data
    """
    social_media = db.query(SocialMedia).filter(SocialMedia.user_id == user_id).first()
    if not social_media or not social_media.youtube_data:
        return []

    youtube_data = social_media.youtube_data

    # Handle the case where keywords is a string (which is the current format)
    if "keywords" in youtube_data and isinstance(youtube_data["keywords"], str):
        # If it's "No keywords found", return empty list
        if youtube_data["keywords"] == "No keywords found":
            return []

        # Otherwise, split the comma-separated string into a list
        return [
            keyword.strip()
            for keyword in youtube_data["keywords"].split(",")
            if keyword.strip()
        ]

    # Fallback for backward compatibility (if keywords were stored as a list of dictionaries)
    elif "keywords" in youtube_data and isinstance(youtube_data["keywords"], list):
        return [
            sub["title"] for sub in youtube_data.get("keywords", []) if "title" in sub
        ]

    # If no keywords found or in unexpected format
    return []
