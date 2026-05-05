import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from app.db import crud
import httpx
from sqlalchemy.orm import selectinload

class TrendDiscover:
    def __init__(self, api_key, folder_id, eps=0.18, min_samples=3):
        self.model = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        self.api_key = api_key
        self.folder_id = folder_id

    async def discover_trends(self, db: Session):
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        posts = crud.get_unprocessed_posts(db, time_threshold, 100)

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

            centroid = np.mean([p.embedding for p in cluster_posts], axis=0).tolist()

            existing_trend = db.execute(
                text("""
                    SELECT id FROM trends 
                    WHERE (1 - (centroid <=> :centroid)) > 0.9 
                    AND updated_at > NOW() - INTERVAL '24 hours'
                    ORDER BY (1 - (centroid <=> :centroid)) DESC
                    LIMIT 1
                """),
                {"centroid": str(centroid)}
            ).fetchone()

            if existing_trend:
                trend_id = existing_trend[0]
                target_trend = crud.get_trend_by_id(db, trend_id)
                
                all_embeddings = [p.embedding for p in target_trend.posts] + [p.embedding for p in cluster_posts]
                new_centroid = np.mean(all_embeddings, axis=0).tolist()
                target_trend.centroid = new_centroid
                
                target_trend.updated_at = datetime.utcnow()
                print(f"Добавляю посты в существующий тренд: {target_trend.name}")

                for p in cluster_posts:
                    if p not in target_trend.posts:
                        target_trend.posts.append(p)

            else:
                print(f"Создаю новый тренд...")

                refusal_phrases = [
                    "я не могу обсуждать эту тему",
                    "давайте поговорим о чём-нибудь ещё",
                    "я не могу на это ответить"
                    ]

                industry_id = cluster_posts[0].industry_id if cluster_posts else None
                
                trend_title = await self._generate_llm_title(cluster_posts)
                if not trend_title or any(phrase in trend_title.lower() for phrase in refusal_phrases):
                    print(f"Тренд пропущен: ИИ отказался генерировать название.")
                    continue 

                post_ers = [p.er for p in cluster_posts if p.er is not None]

                if post_ers:
                    trend_er = sum(post_ers) / len(post_ers)
                else:
                    trend_er = 0.0

                new_trend = crud.create_trend(
                    db = db,
                    trend_title = trend_title, 
                    centroid = centroid, 
                    industry_id = industry_id,
                    trend_er = trend_er
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








