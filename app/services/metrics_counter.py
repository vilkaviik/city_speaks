from app.db.models import Post

def get_post_metrics(post_data):
    likes = post_data.get("likes", {}).get("count", 0)
    views = post_data.get("views", {}).get("count", 0)
    return likes, views