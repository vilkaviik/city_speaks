import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from app.db.models import Post
from app.db.models import Trend
from app.db.models import Industry
import httpx
from sqlalchemy.orm import selectinload

class TrendDiscover:
    def __init__(self, api_key, folder_id, eps=0.15, min_samples=2):
        # eps 0.15 подобран под косинусное расстояние Yandex Embeddings
        self.model = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        self.api_key = api_key
        self.folder_id = folder_id

    async def discover_trends(self, db: Session):
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        posts = db.query(Post).filter(
            Post.created_at >= time_threshold,
            Post.embedding != None,
            Post.trends == None
        ).all()

        if not posts:
            print("Нет новых постов для анализа")
            return

        embeddings = np.array([p.embedding for p in posts])
        labels = self.model.fit_predict(embeddings)

        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(posts[idx])
        
        for label, cluster_posts in clusters.items():

            # Проверка на существование похожих трендовв
            centroid = np.mean([p.embedding for p in cluster_posts], axis=0).tolist()

            existing_trend = db.execute(
                text("""
                    SELECT id FROM trends 
                    WHERE (1 - (centroid <=> :centroid)) > 0.9 
                    AND updated_at > NOW() - INTERVAL '12 hours'
                    ORDER BY (1 - (centroid <=> :centroid)) DESC
                    LIMIT 1
                """),
                {"centroid": str(centroid)}
            ).fetchone()

            if existing_trend:
                trend_id = existing_trend[0]
                target_trend = db.query(Trend).get(trend_id)
                target_trend.updated_at = datetime.utcnow()
                print(f"Добавляю посты в существующий тренд: {target_trend.name}")

                for p in cluster_posts:
                    if p not in target_trend.posts:
                        target_trend.posts.append(p)

            else:
                print(f"Создаю новый тренд...")
                now = datetime.utcnow()
                
                industry_id = cluster_posts[0].industry_id if cluster_posts else None
                trend_title = await self._generate_llm_title(cluster_posts)

                post_ers = [p.er for p in cluster_posts if p.er is not None]

                if post_ers:
                    trend_er = sum(post_ers) / len(post_ers)
                else:
                    trend_er = 0.0

                new_trend = Trend(
                    name = trend_title, 
                    centroid = centroid, 
                    discovered_at = now,
                    updated_at = now, 
                    industry_id = industry_id,
                    er = trend_er
                )
                
                for p in cluster_posts:
                    new_trend.posts.append(p)
                db.add(new_trend)

        db.commit()
                
    async def _generate_llm_title(self, cluster_posts):
        context_texts = "\n---\n".join([p.cleaned_text[:300] for p in cluster_posts[:5]])

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }

        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {"temperature": 0.3, "maxTokens": 50},
            "messages": [
                {
                    "role": "system", 
                    "text": "Ты — аналитик новостей. Твоя задача: прочитать несколько текстов и придумать ОДНО общее краткое название темы (до 5-7 слов). Пиши только название, без лишних слов."
                },
                {
                    "role": "user", 
                    "text": f"Тексты постов:\n{context_texts}"
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
                result = response.json()
                title = result['result']['alternatives'][0]['message']['text']
                return title.strip().replace('"', '')
        except Exception as e:
            print(f"Ошибка YandexGPT: {e}")
            words = cluster_posts[0].text.split()
            return " ".join(words[:5]) + "..."








