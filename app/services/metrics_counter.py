from app.db.models import Post

def get_post_metrics(post_data):
    likes = post_data.get("likes", {}).get("count", 0)
    views = post_data.get("views", {}).get("count", 0)

    owner_id = post_data.get("owner_id")
    post_id = post_data.get("id")
    url = f"https://vk.com{owner_id}_{post_id}"

    return likes, views, url
